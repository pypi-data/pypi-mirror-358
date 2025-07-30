"""
Kafka producer for trace events using confluent_kafka.

Provides high-performance, reliable message production with proper partitioning
and error handling for observability data.
"""

import hashlib
import logging
import os
import time
from typing import Any, Dict, Optional, Callable, List

# Optional Kafka imports
try:
    from confluent_kafka import Producer, KafkaError
    from confluent_kafka.admin import AdminClient, NewTopic

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    # Create dummy classes for type checking
    Producer = object
    KafkaError = Exception
    AdminClient = object
    NewTopic = object

from .schemas import TraceEvent, CompleteTrace, LLMCallEvent


logger = logging.getLogger(__name__)


class KafkaTraceProducer:
    """
    High-performance Kafka producer for trace events.

    Features:
    - Automatic partitioning by trace_id for ordered processing
    - Async delivery with callbacks
    - Automatic topic creation
    - Connection pooling and reuse
    - Comprehensive error handling and retries
    """

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str = "genesis-traces",
        client_id: str = "genesis-studio-tracer",
        # Authentication parameters
        kafka_username: Optional[str] = None,
        kafka_password: Optional[str] = None,
        security_protocol: str = "PLAINTEXT",
        sasl_mechanism: str = "PLAIN",
        **kafka_config: Any,
    ):
        """
        Initialize Kafka producer.

        Args:
            bootstrap_servers: Kafka broker addresses
            topic: Kafka topic name for trace events
            client_id: Client identifier for producer
            kafka_username: Optional SASL username for authentication
            kafka_password: Optional SASL password for authentication
            security_protocol: Security protocol (PLAINTEXT, SASL_SSL, etc.)
            sasl_mechanism: SASL mechanism (PLAIN, SCRAM-SHA-256, etc.)
            **kafka_config: Additional Kafka configuration
        """
        if not KAFKA_AVAILABLE:
            raise ImportError(
                "confluent-kafka is not installed. "
                "Install it with: pip install confluent-kafka"
            )

        self.topic = topic
        self.client_id = client_id

        # Default Kafka configuration optimized for performance - simplified
        default_config = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id,
        }

        # Add authentication if provided
        if kafka_username and kafka_password:
            auth_config = {
                "security.protocol": security_protocol,
                "sasl.mechanisms": sasl_mechanism,
                "sasl.username": kafka_username,
                "sasl.password": kafka_password,
            }
            default_config.update(auth_config)
            logger.debug(
                f"Kafka authentication configured with protocol: {security_protocol}"
            )

        # Merge with user-provided config
        self.config = {**default_config, **kafka_config}

        # Initialize producer and admin client
        self._producer = None
        self._admin_client = None
        self._topic_created = False

        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_failed": 0,
            "last_sent": None,
            "last_error": None,
        }

        logger.info(f"Kafka trace producer initialized for topic: {topic}")

    def _get_producer(self) -> Producer:
        """Get or create Kafka producer instance."""
        if self._producer is None:
            self._producer = Producer(self.config)
            logger.debug("Created new Kafka producer instance")
        return self._producer

    def _get_admin_client(self) -> AdminClient:
        """Get or create Kafka admin client."""
        if self._admin_client is None:
            admin_config = {
                "bootstrap.servers": self.config["bootstrap.servers"],
                "client.id": f"{self.client_id}-admin",
            }

            # Copy authentication settings if present
            auth_keys = [
                "security.protocol",
                "sasl.mechanisms",
                "sasl.username",
                "sasl.password",
            ]
            for key in auth_keys:
                if key in self.config:
                    admin_config[key] = self.config[key]

            self._admin_client = AdminClient(admin_config)
            logger.debug("Created new Kafka admin client")
        return self._admin_client

    def _ensure_topic_exists(
        self, num_partitions: int = 3, replication_factor: int = 1
    ):
        """Ensure the topic exists, create if necessary."""
        if self._topic_created:
            return

        try:
            admin_client = self._get_admin_client()

            # Check if topic already exists
            metadata = admin_client.list_topics(timeout=10)
            if self.topic in metadata.topics:
                logger.debug(f"Topic {self.topic} already exists")
                self._topic_created = True
                return

            # Create topic
            topic_config = {
                "cleanup.policy": "delete",
                "retention.ms": str(7 * 24 * 60 * 60 * 1000),  # 7 days
                "compression.type": "snappy",
            }

            new_topic = NewTopic(
                topic=self.topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                config=topic_config,
            )

            futures = admin_client.create_topics([new_topic])

            # Wait for topic creation
            for topic_name, future in futures.items():
                try:
                    future.result(timeout=30)
                    logger.info(f"Created Kafka topic: {topic_name}")
                    self._topic_created = True
                except Exception as e:
                    if "TopicExistsException" in str(e):
                        logger.debug(f"Topic {topic_name} already exists")
                        self._topic_created = True
                    else:
                        logger.error(f"Failed to create topic {topic_name}: {e}")
                        raise

        except Exception as e:
            logger.warning(f"Could not ensure topic exists: {e}")
            # Continue anyway, topic might exist or be auto-created

    def _calculate_partition(self, trace_id: str, num_partitions: int = 3) -> int:
        """
        Calculate partition for trace_id to ensure ordering.

        Uses consistent hashing to ensure same trace_id always goes to same partition.
        """
        # Use SHA256 for consistent hashing
        hash_value = hashlib.sha256(trace_id.encode("utf-8")).hexdigest()
        # Convert to int and mod by partition count
        return int(hash_value, 16) % num_partitions

    def _delivery_callback(self, error: Optional[KafkaError], message) -> None:
        """Callback for message delivery confirmation."""
        if error:
            self.stats["messages_failed"] += 1
            self.stats["last_error"] = str(error)
            logger.error(f"Message delivery failed: {error}")
        else:
            self.stats["messages_sent"] += 1
            self.stats["last_sent"] = int(time.time() * 1000)
            logger.debug(
                f"Message delivered to topic {message.topic()} "
                f"partition {message.partition()} offset {message.offset()}"
            )

    def send_event(
        self,
        event: TraceEvent,
        callback: Optional[Callable] = None,
        timeout: float = 1.0,
    ) -> bool:
        """
        Send a trace event to Kafka.

        Args:
            event: TraceEvent to send
            callback: Optional callback for delivery confirmation
            timeout: Timeout for sending message

        Returns:
            bool: True if message was queued successfully
        """
        try:
            # Ensure topic exists
            self._ensure_topic_exists()

            # Get producer
            producer = self._get_producer()

            # Calculate partition
            partition = self._calculate_partition(event.trace_id)

            # Serialize event
            key = event.get_partition_key()
            value = event.to_json()

            # Send message
            producer.produce(
                topic=self.topic,
                key=key,
                value=value,
                partition=partition,
                callback=callback or self._delivery_callback,
                timestamp=int(time.time() * 1000),
            )

            # Trigger delivery (non-blocking)
            producer.poll(0)

            logger.debug(
                f"Queued {event.event_type} event for trace {event.trace_id} "
                f"to partition {partition}"
            )

            return True

        except Exception as e:
            self.stats["messages_failed"] += 1
            self.stats["last_error"] = str(e)
            logger.error(f"Failed to send trace event: {e}")
            return False

    def send_trace_start(
        self,
        trace_id: str,
        flow_id: str,
        flow_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send a trace start event."""
        event = TraceEvent.create_trace_start(
            trace_id=trace_id,
            flow_id=flow_id,
            flow_name=flow_name,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
        )
        return self.send_event(event)

    def send_trace_end(
        self,
        trace_id: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> bool:
        """Send a trace end event."""
        event = TraceEvent.create_trace_end(
            trace_id=trace_id, duration_ms=duration_ms, metadata=metadata, error=error
        )
        return self.send_event(event)

    def send_span_start(
        self,
        trace_id: str,
        span_id: str,
        component_id: str,
        component_name: str,
        parent_span_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send a span start event."""
        event = TraceEvent.create_span_start(
            trace_id=trace_id,
            span_id=span_id,
            component_id=component_id,
            component_name=component_name,
            parent_span_id=parent_span_id,
            input_data=input_data,
            metadata=metadata,
        )
        return self.send_event(event)

    def send_span_end(
        self,
        trace_id: str,
        span_id: str,
        duration_ms: float,
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> bool:
        """Send a span end event."""
        event = TraceEvent.create_span_end(
            trace_id=trace_id,
            span_id=span_id,
            duration_ms=duration_ms,
            output_data=output_data,
            metadata=metadata,
            error=error,
        )
        return self.send_event(event)

    def send_custom_event(
        self,
        trace_id: str,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send a custom event (e.g., cost tracking)."""
        try:
            # Prepare event data
            event_data = data.copy()

            # Ensure timestamp exists - use from data if available, otherwise generate
            if "timestamp" not in event_data:
                from datetime import datetime, timezone

                event_data["timestamp"] = datetime.now(timezone.utc).isoformat()

            # Create a custom TraceEvent
            event = TraceEvent(
                trace_id=trace_id,
                event_type=event_type,
                metadata=metadata or {},
                **event_data,
            )
            return self.send_event(event)
        except Exception as e:
            logger.error(f"Failed to send custom event: {e}")
            return False

    def send_complete_trace(
        self,
        complete_trace: CompleteTrace,
        callback: Optional[Callable] = None,
        timeout: float = 1.0,
    ) -> bool:
        """
        Send a complete trace to Kafka.

        Args:
            complete_trace: CompleteTrace object to send
            callback: Optional callback for delivery confirmation
            timeout: Timeout for sending message

        Returns:
            bool: True if message was queued successfully
        """
        try:
            # Ensure topic exists
            self._ensure_topic_exists()

            # Get producer
            producer = self._get_producer()

            # Calculate partition
            partition = self._calculate_partition(complete_trace.trace_id)

            # Serialize trace
            key = complete_trace.get_partition_key()
            value = complete_trace.to_json()

            # Send message
            producer.produce(
                topic=self.topic,
                key=key,
                value=value,
                partition=partition,
                callback=callback or self._delivery_callback,
                timestamp=int(time.time() * 1000),
            )

            # Trigger delivery (non-blocking)
            producer.poll(0)

            logger.debug(
                f"Queued complete trace for {complete_trace.flow_name} "
                f"(trace_id: {complete_trace.trace_id}) to partition {partition}"
            )

            return True

        except Exception as e:
            self.stats["messages_failed"] += 1
            self.stats["last_error"] = str(e)
            logger.error(f"Failed to send complete trace: {e}")
            return False

    def send_llm_event(
        self,
        event: LLMCallEvent,
        callback: Optional[Callable] = None,
        timeout: float = 1.0,
    ) -> bool:
        """
        Send an LLM call event to Kafka.

        Args:
            event: LLMCallEvent to send
            callback: Optional callback for delivery confirmation
            timeout: Timeout for sending message

        Returns:
            bool: True if message was queued successfully
        """
        try:
            # Ensure topic exists
            self._ensure_topic_exists()

            # Get producer
            producer = self._get_producer()

            # Calculate partition based on call_id for ordering
            partition_key = event.get_partition_key()

            # Serialize event
            message_value = event.to_json().encode("utf-8")

            # Send message
            producer.produce(
                topic=self.topic,
                key=partition_key.encode("utf-8"),
                value=message_value,
                on_delivery=callback or self._delivery_callback,
            )

            # Poll to ensure delivery
            producer.poll(timeout)

            self.stats["messages_sent"] += 1
            self.stats["last_sent"] = int(time.time() * 1000)
            self.stats["last_error"] = None

            logger.debug(f"Sent LLM event {event.event_type} for call {event.call_id}")
            return True

        except Exception as e:
            self.stats["messages_failed"] += 1
            self.stats["last_error"] = str(e)
            logger.error(f"Failed to send LLM event: {e}")
            return False

    def send_llm_start(
        self,
        call_id: str,
        model: str,
        provider: str,
        messages: List[Dict],
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an LLM call start event."""
        event = LLMCallEvent.create_llm_start(
            call_id=call_id,
            model=model,
            provider=provider,
            messages=messages,
            params=params,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
        )
        return self.send_llm_event(event)

    def send_llm_end(
        self,
        call_id: str,
        model: str,
        provider: str,
        duration_ms: float,
        usage: Dict[str, int],
        response: Optional[str] = None,
        cost: Optional[float] = None,
        error: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an LLM call end event."""
        event = LLMCallEvent.create_llm_end(
            call_id=call_id,
            model=model,
            provider=provider,
            duration_ms=duration_ms,
            usage=usage,
            response=response,
            cost=cost,
            error=error,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
        )
        return self.send_llm_event(event)

    def send_llm_metric(
        self,
        call_id: str,
        metrics: Dict[str, float],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an LLM metrics event."""
        event = LLMCallEvent.create_llm_metric(
            call_id=call_id,
            metrics=metrics,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
        )
        return self.send_llm_event(event)

    def flush(self, timeout: float = 10.0) -> int:
        """
        Flush pending messages.

        Args:
            timeout: Maximum time to wait for messages to be delivered

        Returns:
            Number of messages still pending after timeout
        """
        if self._producer:
            return self._producer.flush(timeout)
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get producer statistics."""
        return {
            "messages_sent": self.stats["messages_sent"],
            "messages_failed": self.stats["messages_failed"],
            "last_sent": self.stats["last_sent"],
            "last_error": self.stats["last_error"],
            "topic": self.topic,
            "client_id": self.client_id,
        }

    def close(self):
        """Close producer and admin client."""
        if self._producer:
            self._producer.flush(10.0)  # Wait up to 10 seconds for pending messages
            self._producer = None

        if self._admin_client:
            self._admin_client = None

        logger.info("Kafka trace producer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
