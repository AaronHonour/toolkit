"""Analytics projections for CQRS read side.

Maintains materialized views of analytics data for fast queries.
"""

from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from examples.02_realtime_analytics_dashboard.src.domain.models.event import Event, EventBatch
from examples.02_realtime_analytics_dashboard.src.domain.models.metric import (
    Counter as MetricCounter,
    Gauge,
    Histogram,
    TimeSeries,
    MetricSnapshot,
    AggregationWindow,
)


class AnalyticsProjection:
    """Analytics projection maintaining real-time aggregations.

    This is the read model in CQRS pattern, optimized for queries.
    """

    __slots__ = (
        '_event_counts',
        '_user_activity',
        '_time_series',
        '_histograms',
        '_gauges',
        '_last_update',
        '_window_size',
    )

    def __init__(self, window_size: timedelta = timedelta(hours=1)):
        """Initialize analytics projection.

        Args:
            window_size: Time window for aggregations
        """
        # Event counters
        self._event_counts: Dict[str, int] = defaultdict(int)

        # User activity tracking
        self._user_activity: Dict[str, List[Event]] = defaultdict(list)

        # Time series data
        self._time_series: Dict[str, TimeSeries] = {}

        # Histograms for distributions
        self._histograms: Dict[str, Histogram] = {}

        # Gauges for point-in-time values
        self._gauges: Dict[str, Gauge] = {}

        self._last_update = datetime.utcnow()
        self._window_size = window_size

    def handle_event(self, event: Event) -> None:
        """Handle single event and update projections.

        Args:
            event: Event to process
        """
        # Update event counts
        self._event_counts[event.event_type] += 1
        self._event_counts['total'] += 1

        # Track user activity
        self._user_activity[event.user_id].append(event)

        # Update time series
        self._update_time_series(event)

        # Update histograms if event has duration
        if 'duration_ms' in event.properties:
            self._update_histogram(event)

        # Update gauges
        self._update_gauges(event)

        self._last_update = datetime.utcnow()

    def handle_batch(self, batch: EventBatch) -> None:
        """Handle event batch and update projections.

        Args:
            batch: Event batch to process
        """
        for event in batch.events:
            self.handle_event(event)

    def _update_time_series(self, event: Event) -> None:
        """Update time series data.

        Args:
            event: Event to process
        """
        # Aggregate by event type
        series_name = f"events.{event.event_type}.count"

        if series_name not in self._time_series:
            self._time_series[series_name] = TimeSeries.create(
                name=series_name,
                window=AggregationWindow.MINUTE,
            )

        # Add data point (count increments)
        current_count = self._event_counts[event.event_type]
        self._time_series[series_name] = self._time_series[series_name].add_point(
            timestamp=event.timestamp,
            value=current_count,
        )

    def _update_histogram(self, event: Event) -> None:
        """Update histogram with event duration.

        Args:
            event: Event to process
        """
        histogram_name = f"events.{event.event_type}.duration"

        if histogram_name not in self._histograms:
            self._histograms[histogram_name] = Histogram.create(
                name=histogram_name,
                buckets=[10, 50, 100, 500, 1000, 5000],  # milliseconds
            )

        duration_ms = event.properties.get('duration_ms', 0)
        if duration_ms > 0:
            self._histograms[histogram_name] = self._histograms[histogram_name].observe(
                duration_ms
            )

    def _update_gauges(self, event: Event) -> None:
        """Update gauges with current values.

        Args:
            event: Event to process
        """
        # Active users gauge
        gauge_name = "active_users"
        if gauge_name not in self._gauges:
            self._gauges[gauge_name] = Gauge.create(gauge_name)

        # Update with unique user count
        unique_users = len(self._user_activity)
        self._gauges[gauge_name] = self._gauges[gauge_name].set(float(unique_users))

        # Events per second gauge
        gauge_name = "events_per_second"
        if gauge_name not in self._gauges:
            self._gauges[gauge_name] = Gauge.create(gauge_name)

        # Calculate rate (simplified)
        total_events = self._event_counts['total']
        self._gauges[gauge_name] = self._gauges[gauge_name].set(float(total_events))

    def get_event_counts(self) -> Dict[str, int]:
        """Get event counts by type.

        Returns:
            Dictionary of event type to count
        """
        return dict(self._event_counts)

    def get_top_users(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most active users.

        Args:
            limit: Number of top users

        Returns:
            List of (user_id, event_count) tuples
        """
        user_counts = Counter({
            user_id: len(events)
            for user_id, events in self._user_activity.items()
        })
        return user_counts.most_common(limit)

    def get_time_series(
        self,
        metric_name: str,
        last_n: Optional[int] = None,
    ) -> List[Tuple[datetime, float]]:
        """Get time series data.

        Args:
            metric_name: Name of metric
            last_n: Number of recent points

        Returns:
            List of (timestamp, value) tuples
        """
        if metric_name not in self._time_series:
            return []

        series = self._time_series[metric_name]
        if last_n:
            return series.get_last_n(last_n)
        return series.data_points

    def get_histogram_percentiles(
        self,
        metric_name: str,
    ) -> Dict[str, float]:
        """Get histogram percentiles.

        Args:
            metric_name: Name of histogram metric

        Returns:
            Dictionary with percentiles
        """
        if metric_name not in self._histograms:
            return {}

        hist = self._histograms[metric_name]
        return {
            'count': hist.count,
            'sum': hist.sum,
            'mean': hist.mean,
            'p50': hist.percentile(0.5),
            'p95': hist.percentile(0.95),
            'p99': hist.percentile(0.99),
        }

    def get_gauge_value(self, gauge_name: str) -> Optional[float]:
        """Get gauge value.

        Args:
            gauge_name: Name of gauge

        Returns:
            Gauge value or None
        """
        if gauge_name not in self._gauges:
            return None
        return self._gauges[gauge_name].value

    def get_snapshot(self) -> MetricSnapshot:
        """Get complete metrics snapshot.

        Returns:
            MetricSnapshot with all current metrics
        """
        # Convert internal metrics to snapshot format
        counters = {
            name: MetricCounter.create(name).increment(count)
            for name, count in self._event_counts.items()
        }

        return MetricSnapshot(
            timestamp=datetime.utcnow(),
            counters=counters,
            gauges=self._gauges.copy(),
            histograms=self._histograms.copy(),
            time_series=self._time_series.copy(),
        )

    def get_user_events(
        self,
        user_id: str,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """Get events for a user.

        Args:
            user_id: User ID
            limit: Maximum number of events

        Returns:
            List of user events
        """
        events = self._user_activity.get(user_id, [])
        if limit:
            return events[-limit:]
        return events

    def get_recent_events(
        self,
        duration: timedelta,
        event_type: Optional[str] = None,
    ) -> List[Event]:
        """Get recent events within duration.

        Args:
            duration: Time duration to look back
            event_type: Filter by event type (optional)

        Returns:
            List of recent events
        """
        cutoff = datetime.utcnow() - duration
        recent = []

        for events in self._user_activity.values():
            for event in events:
                if event.timestamp >= cutoff:
                    if event_type is None or event.event_type == event_type:
                        recent.append(event)

        return sorted(recent, key=lambda e: e.timestamp, reverse=True)

    def cleanup_old_data(self) -> None:
        """Clean up data outside the time window."""
        cutoff = datetime.utcnow() - self._window_size

        # Clean up user activity
        for user_id in list(self._user_activity.keys()):
            events = self._user_activity[user_id]
            recent_events = [e for e in events if e.timestamp >= cutoff]

            if recent_events:
                self._user_activity[user_id] = recent_events
            else:
                del self._user_activity[user_id]

    @property
    def stats(self) -> dict:
        """Get projection statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            'total_events': self._event_counts.get('total', 0),
            'unique_users': len(self._user_activity),
            'event_types': len([k for k in self._event_counts.keys() if k != 'total']),
            'time_series_metrics': len(self._time_series),
            'histograms': len(self._histograms),
            'gauges': len(self._gauges),
            'last_update': self._last_update.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"AnalyticsProjection(events={self._event_counts.get('total', 0)}, "
            f"users={len(self._user_activity)})"
        )
