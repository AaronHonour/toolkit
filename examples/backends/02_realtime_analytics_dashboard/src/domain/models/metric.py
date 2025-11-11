"""Metric domain models for analytics aggregations.

Metrics represent aggregated measurements over time.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from collections import defaultdict


class MetricType(str, Enum):
    """Types of metrics."""

    COUNTER = "counter"  # Monotonically increasing count
    GAUGE = "gauge"  # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    RATE = "rate"  # Events per time unit


class AggregationWindow(str, Enum):
    """Time window for aggregations."""

    SECOND = "1s"
    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    HOUR = "1h"
    DAY = "1d"


@dataclass
class Counter:
    """Counter metric (monotonically increasing).

    Memory optimized with __slots__.
    """

    __slots__ = ('name', 'value', 'labels', 'updated_at')

    name: str
    value: int
    labels: Dict[str, str]
    updated_at: datetime

    @classmethod
    def create(cls, name: str, labels: Optional[Dict[str, str]] = None) -> "Counter":
        """Create new counter.

        Args:
            name: Counter name
            labels: Optional labels for grouping

        Returns:
            New Counter instance
        """
        return cls(
            name=name,
            value=0,
            labels=labels or {},
            updated_at=datetime.utcnow(),
        )

    def increment(self, amount: int = 1) -> "Counter":
        """Increment counter.

        Args:
            amount: Amount to increment by

        Returns:
            Updated Counter instance
        """
        return Counter(
            name=self.name,
            value=self.value + amount,
            labels=self.labels,
            updated_at=datetime.utcnow(),
        )

    def reset(self) -> "Counter":
        """Reset counter to zero.

        Returns:
            Reset Counter instance
        """
        return Counter(
            name=self.name,
            value=0,
            labels=self.labels,
            updated_at=datetime.utcnow(),
        )


@dataclass
class Gauge:
    """Gauge metric (point-in-time value).

    Memory optimized with __slots__.
    """

    __slots__ = ('name', 'value', 'labels', 'updated_at')

    name: str
    value: float
    labels: Dict[str, str]
    updated_at: datetime

    @classmethod
    def create(cls, name: str, initial_value: float = 0.0, labels: Optional[Dict[str, str]] = None) -> "Gauge":
        """Create new gauge.

        Args:
            name: Gauge name
            initial_value: Initial value
            labels: Optional labels for grouping

        Returns:
            New Gauge instance
        """
        return cls(
            name=name,
            value=initial_value,
            labels=labels or {},
            updated_at=datetime.utcnow(),
        )

    def set(self, value: float) -> "Gauge":
        """Set gauge value.

        Args:
            value: New value

        Returns:
            Updated Gauge instance
        """
        return Gauge(
            name=self.name,
            value=value,
            labels=self.labels,
            updated_at=datetime.utcnow(),
        )

    def increment(self, amount: float = 1.0) -> "Gauge":
        """Increment gauge.

        Args:
            amount: Amount to increment by

        Returns:
            Updated Gauge instance
        """
        return self.set(self.value + amount)

    def decrement(self, amount: float = 1.0) -> "Gauge":
        """Decrement gauge.

        Args:
            amount: Amount to decrement by

        Returns:
            Updated Gauge instance
        """
        return self.set(self.value - amount)


@dataclass
class Histogram:
    """Histogram metric (distribution of values).

    Memory optimized with __slots__.
    """

    __slots__ = ('name', 'buckets', 'count', 'sum', 'labels', 'updated_at')

    name: str
    buckets: Dict[float, int]  # bucket upper bound -> count
    count: int
    sum: float
    labels: Dict[str, str]
    updated_at: datetime

    @classmethod
    def create(
        cls,
        name: str,
        buckets: Optional[List[float]] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> "Histogram":
        """Create new histogram.

        Args:
            name: Histogram name
            buckets: Bucket boundaries (e.g., [0.1, 0.5, 1.0, 5.0, 10.0])
            labels: Optional labels for grouping

        Returns:
            New Histogram instance
        """
        default_buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        bucket_dict = {b: 0 for b in (buckets or default_buckets)}

        return cls(
            name=name,
            buckets=bucket_dict,
            count=0,
            sum=0.0,
            labels=labels or {},
            updated_at=datetime.utcnow(),
        )

    def observe(self, value: float) -> "Histogram":
        """Observe a value.

        Args:
            value: Value to observe

        Returns:
            Updated Histogram instance
        """
        new_buckets = self.buckets.copy()

        # Increment buckets
        for bucket in sorted(new_buckets.keys()):
            if value <= bucket:
                new_buckets[bucket] += 1

        return Histogram(
            name=self.name,
            buckets=new_buckets,
            count=self.count + 1,
            sum=self.sum + value,
            labels=self.labels,
            updated_at=datetime.utcnow(),
        )

    @property
    def mean(self) -> float:
        """Calculate mean value.

        Returns:
            Mean value
        """
        return self.sum / self.count if self.count > 0 else 0.0

    def percentile(self, p: float) -> float:
        """Calculate percentile.

        Args:
            p: Percentile (0.0 to 1.0)

        Returns:
            Percentile value
        """
        if self.count == 0:
            return 0.0

        target_count = int(self.count * p)
        cumulative = 0

        for bucket in sorted(self.buckets.keys()):
            cumulative += self.buckets[bucket]
            if cumulative >= target_count:
                return bucket

        return max(self.buckets.keys())


@dataclass
class TimeSeries:
    """Time-series data points.

    Memory optimized with __slots__.
    """

    __slots__ = ('name', 'data_points', 'window', 'updated_at')

    name: str
    data_points: List[tuple[datetime, float]]  # (timestamp, value)
    window: AggregationWindow
    updated_at: datetime

    @classmethod
    def create(cls, name: str, window: AggregationWindow = AggregationWindow.MINUTE) -> "TimeSeries":
        """Create new time series.

        Args:
            name: Series name
            window: Aggregation window

        Returns:
            New TimeSeries instance
        """
        return cls(
            name=name,
            data_points=[],
            window=window,
            updated_at=datetime.utcnow(),
        )

    def add_point(self, timestamp: datetime, value: float) -> "TimeSeries":
        """Add data point.

        Args:
            timestamp: Point timestamp
            value: Point value

        Returns:
            Updated TimeSeries instance
        """
        new_points = self.data_points.copy()
        new_points.append((timestamp, value))

        # Keep only recent data (last 1000 points)
        if len(new_points) > 1000:
            new_points = new_points[-1000:]

        return TimeSeries(
            name=self.name,
            data_points=new_points,
            window=self.window,
            updated_at=datetime.utcnow(),
        )

    def get_range(self, start: datetime, end: datetime) -> List[tuple[datetime, float]]:
        """Get points within time range.

        Args:
            start: Start time
            end: End time

        Returns:
            List of points in range
        """
        return [(ts, val) for ts, val in self.data_points if start <= ts <= end]

    def get_last_n(self, n: int) -> List[tuple[datetime, float]]:
        """Get last N points.

        Args:
            n: Number of points

        Returns:
            Last N points
        """
        return self.data_points[-n:] if len(self.data_points) >= n else self.data_points

    @property
    def latest_value(self) -> Optional[float]:
        """Get latest value.

        Returns:
            Latest value or None
        """
        return self.data_points[-1][1] if self.data_points else None

    @property
    def latest_timestamp(self) -> Optional[datetime]:
        """Get latest timestamp.

        Returns:
            Latest timestamp or None
        """
        return self.data_points[-1][0] if self.data_points else None


@dataclass
class MetricSnapshot:
    """Snapshot of all metrics at a point in time.

    Memory optimized with __slots__.
    """

    __slots__ = ('timestamp', 'counters', 'gauges', 'histograms', 'time_series')

    timestamp: datetime
    counters: Dict[str, Counter]
    gauges: Dict[str, Gauge]
    histograms: Dict[str, Histogram]
    time_series: Dict[str, TimeSeries]

    @classmethod
    def create(cls) -> "MetricSnapshot":
        """Create empty metric snapshot.

        Returns:
            New MetricSnapshot instance
        """
        return cls(
            timestamp=datetime.utcnow(),
            counters={},
            gauges={},
            histograms={},
            time_series={},
        )

    def to_dict(self) -> Dict[str, any]:
        """Convert snapshot to dictionary.

        Returns:
            Snapshot as dictionary
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'counters': {
                name: {'value': c.value, 'labels': c.labels}
                for name, c in self.counters.items()
            },
            'gauges': {
                name: {'value': g.value, 'labels': g.labels}
                for name, g in self.gauges.items()
            },
            'histograms': {
                name: {
                    'count': h.count,
                    'sum': h.sum,
                    'mean': h.mean,
                    'p50': h.percentile(0.5),
                    'p95': h.percentile(0.95),
                    'p99': h.percentile(0.99),
                }
                for name, h in self.histograms.items()
            },
            'time_series': {
                name: {
                    'latest': ts.latest_value,
                    'latest_ts': ts.latest_timestamp.isoformat() if ts.latest_timestamp else None,
                    'window': ts.window.value,
                }
                for name, ts in self.time_series.items()
            },
        }
