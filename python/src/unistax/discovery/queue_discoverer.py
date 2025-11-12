"""Message queue discovery for detecting pub/sub dependencies."""

from typing import Any

from unistax.discovery.base import (
    DependencyDiscoverer,
    DiscoveryResult,
    DiscoverySource,
)


class MessageQueueDiscoverer(DependencyDiscoverer):
    """Discovers message queue dependencies (publishers and subscribers)."""

    def __init__(
        self,
        service_name: str,
        publishers: list[str] | None = None,
        subscribers: list[str] | None = None,
        queue_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize message queue discoverer.

        Args:
            service_name: Name of the service being analyzed
            publishers: List of topics/queues this service publishes to
            subscribers: List of topics/queues this service subscribes to
            queue_config: Configuration data for queue connections
        """
        super().__init__(service_name)
        self.publishers = publishers or []
        self.subscribers = subscribers or []
        self.queue_config = queue_config or {}

    async def discover(self) -> list[DiscoveryResult]:
        """Discover message queue dependencies.

        Returns:
            List of discovered queue dependencies
        """
        results: list[DiscoveryResult] = []

        # Discover publishing dependencies
        results.extend(self._discover_publishers())

        # Discover subscription dependencies
        results.extend(self._discover_subscribers())

        # Discover from configuration
        results.extend(self._discover_from_config())

        # Update cache
        self._discovered.update(results)

        return results

    def _discover_publishers(self) -> list[DiscoveryResult]:
        """Discover topics/queues this service publishes to."""
        results: list[DiscoveryResult] = []

        for topic in self.publishers:
            # For publishers, the service sends messages TO the queue
            result = DiscoveryResult(
                source_service=self.service_name,
                target_service=f"queue-{topic}",
                dependency_type="message_queue",
                source=DiscoverySource.MESSAGE_QUEUE,
                confidence=1.0,
                metadata={
                    "role": "publisher",
                    "topic": topic,
                    "direction": "outgoing",
                },
            )
            results.append(result)

        return results

    def _discover_subscribers(self) -> list[DiscoveryResult]:
        """Discover topics/queues this service subscribes to."""
        results: list[DiscoveryResult] = []

        for topic in self.subscribers:
            # For subscribers, the queue sends messages TO the service
            # So the dependency is FROM the queue TO this service
            result = DiscoveryResult(
                source_service=f"queue-{topic}",
                target_service=self.service_name,
                dependency_type="message_queue",
                source=DiscoverySource.MESSAGE_QUEUE,
                confidence=1.0,
                metadata={
                    "role": "subscriber",
                    "topic": topic,
                    "direction": "incoming",
                },
            )
            results.append(result)

        return results

    def _discover_from_config(self) -> list[DiscoveryResult]:
        """Discover queue connections from configuration."""
        results: list[DiscoveryResult] = []

        # Look for queue broker configurations
        queue_types = ["rabbitmq", "kafka", "redis", "sqs", "pubsub"]

        for queue_type in queue_types:
            if queue_type in self.queue_config:
                config = self.queue_config[queue_type]

                # Extract broker/host information
                if isinstance(config, dict):
                    host = config.get("host", "unknown")
                    broker_name = f"{queue_type}-{host}"

                    # This service connects to the broker
                    result = DiscoveryResult(
                        source_service=self.service_name,
                        target_service=broker_name,
                        dependency_type="message_queue",
                        source=DiscoverySource.CONFIGURATION,
                        confidence=0.9,
                        metadata={
                            "broker_type": queue_type,
                            "host": host,
                            "port": config.get("port"),
                        },
                    )
                    results.append(result)

        return results


class TopicSubscriberMapper:
    """Maps topics to their publishers and subscribers for dependency inference."""

    def __init__(self) -> None:
        """Initialize the topic mapper."""
        self._publishers: dict[str, set[str]] = {}  # topic -> set of publishers
        self._subscribers: dict[str, set[str]] = {}  # topic -> set of subscribers

    def register_publisher(self, service: str, topic: str) -> None:
        """Register a service as a publisher to a topic."""
        if topic not in self._publishers:
            self._publishers[topic] = set()
        self._publishers[topic].add(service)

    def register_subscriber(self, service: str, topic: str) -> None:
        """Register a service as a subscriber to a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = set()
        self._subscribers[topic].add(service)

    def infer_dependencies(self) -> list[DiscoveryResult]:
        """Infer service-to-service dependencies via topics.

        For each topic, creates dependencies from publishers to subscribers.

        Returns:
            List of inferred dependencies
        """
        results: list[DiscoveryResult] = []

        # Get all topics
        all_topics = set(self._publishers.keys()) | set(self._subscribers.keys())

        for topic in all_topics:
            publishers = self._publishers.get(topic, set())
            subscribers = self._subscribers.get(topic, set())

            # Create dependencies: publisher -> subscriber (via topic)
            for publisher in publishers:
                for subscriber in subscribers:
                    if publisher != subscriber:
                        result = DiscoveryResult(
                            source_service=publisher,
                            target_service=subscriber,
                            dependency_type="message_queue",
                            source=DiscoverySource.MESSAGE_QUEUE,
                            confidence=0.85,  # Inferred, so slightly lower confidence
                            metadata={
                                "topic": topic,
                                "inferred": True,
                                "via": "topic_mapping",
                            },
                        )
                        results.append(result)

        return results
