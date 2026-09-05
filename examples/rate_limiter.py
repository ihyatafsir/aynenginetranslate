"""
AYNENGINE: Sliding-Window Rate Limiter with Token Bucket Fallback
=================================================================
5-Pillar Classical Epistemic Implementation

Pillar 1 (Al-Mufradāt): Every entity has explicit teleology
Pillar 2 (Asās al-Balāghah): Literal thread-safety, metaphorical windowing
Pillar 3 (Lisān al-ʿArab): Complete lifecycle and error state coverage
Pillar 4 (Kitāb al-ʿAyn): Atomic primitives, orthogonal decomposition
Pillar 5 (Al-Kitāb): Strict governance hierarchy, zero circularity
"""

import threading
import time
import heapq
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from typing import Deque, Dict, List, Optional, Tuple
import logging

# Configure telemetric logging for lifecycle observability
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# ═══════════════════════════════════════════════════════════════════════════
# PILLAR 1: ONTOLOGICAL DOMAIN MODELING (Al-Mufradāt)
# ═══════════════════════════════════════════════════════════════════════════

class RateLimitState(Enum):
    """Lifecycle states of the rate limiter (Lisān al-ʿArab: full state coverage)."""
    INITIALIZING = auto()   # Construction phase, pre-activation
    ACTIVE = auto()         # Normal operation, admitting requests
    DEGRADED = auto()       # Fallback engaged, reduced capacity
    CLOSED = auto()         # Explicitly shut down, rejecting all
    FAILED = auto()         # Irrecoverable internal error


class AdmissionVerdict(Enum):
    """Tri-state outcome of an admission request."""
    ADMITTED = auto()       # Request passes through
    DEFERRED = auto()       # Token bucket fallback engaged
    REJECTED = auto()       # Both primary and fallback exhausted


@dataclass(frozen=True)
class RateLimitDecision:
    """Immutable decision record with full teleological context."""
    verdict: AdmissionVerdict
    timestamp: float
    retry_after_ms: Optional[int] = None  # When DEFERRED/REJECTED
    bucket_level: Optional[float] = None  # Token bucket state at decision
    window_utilization: Optional[float] = None  # Window occupancy ratio


class WindowState:
    """
    Temporal ledger of admission events within the sliding window.
    
    Ghāyah: Maintain an exact, ordered record of timestamps for
    precise window boundary computation and event purging.
    
    Invariants:
    - Events are always chronologically ordered
    - No event timestamp exceeds the current window boundary
    - Purging is idempotent and thread-safe
    """
    
    __slots__ = ('_events', '_lock', '_window_seconds')
    
    def __init__(self, window_seconds: float) -> None:
        """
        Initialize the temporal ledger.
        
        Args:
            window_seconds: Duration of the sliding window in seconds
            
        Raises:
            ValueError: If window_seconds is non-positive
        """
        if window_seconds <= 0:
            raise ValueError(f"Window duration must be positive, got: {window_seconds}")
        
        self._events: Deque[float] = deque()
        self._lock = threading.Lock()
        self._window_seconds = window_seconds
    
    def purge_expired(self, now: float) -> int:
        """
        Remove events that have fallen outside the window boundary.
        
        Args:
            now: Current epoch time in seconds
            
        Returns:
            Number of purged events
            
        Note: Idempotent operation - safe to call multiple times
        """
        boundary = now - self._window_seconds
        purged_count = 0
        
        with self._lock:
            while self._events and self._events[0] <= boundary:
                self._events.popleft()
                purged_count += 1
        
        return purged_count
    
    def add_event(self, timestamp: float) -> None:
        """
        Record a new admission event.
        
        Args:
            timestamp: Epoch time of the admission
            
        Raises:
            RuntimeError: If timestamp is in the past beyond window boundary
        """
        with self._lock:
            # Validate temporal ordering (Lisān al-ʿArab: no silent corruption)
            if self._events and timestamp < self._events[-1]:
                raise RuntimeError(
                    f"Timestamp regression detected: {timestamp} < {self._events[-1]}"
                )
            self._events.append(timestamp)
    
    def count_in_window(self, now: float) -> int:
        """
        Count events within the current window.
        
        Args:
            now: Current epoch time
            
        Returns:
            Number of active events in window
        """
        self.purge_expired(now)
        with self._lock:
            return len(self._events)
    
    def oldest_event(self) -> Optional[float]:
        """Return the oldest event timestamp or None if empty."""
        with self._lock:
            return self._events[0] if self._events else None
    
    def snapshot(self) -> List[float]:
        """Return a thread-safe copy of all event timestamps."""
        with self._lock:
            return list(self._events)


class TokenBucket:
    """
    Token bucket for burst absorption and fallback admission.
    
    Ghāyah: Provide controlled burst capacity with linear refill,
    serving as the secondary admission mechanism when the primary
    sliding window is saturated.
    
    Invariants:
    - Token count never exceeds capacity
    - Refill is monotonic and time-proportional
    - All operations are atomic under contention
    """
    
    __slots__ = ('_capacity', '_tokens', '_refill_rate', '_last_refill', '_lock')
    
    def __init__(self, capacity: float, refill_rate: float) -> None:
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum token count (burst size)
            refill_rate: Tokens added per second
            
        Raises:
            ValueError: If capacity or refill_rate is non-positive
        """
        if capacity <= 0:
            raise ValueError(f"Bucket capacity must be positive, got: {capacity}")
        if refill_rate <= 0:
            raise ValueError(f"Refill rate must be positive, got: {refill_rate}")
        
        self._capacity = capacity
        self._tokens = float(capacity)  # Start full for immediate burst
        self._refill_rate = refill_rate
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()
    
    def _refill(self, now: float) -> None:
        """
        Add tokens based on elapsed time since last refill.
        
        Args:
            now: Current monotonic time
        """
        elapsed = now - self._last_refill
        if elapsed > 0:
            self._tokens = min(
                self._capacity,
                self._tokens + elapsed * self._refill_rate
            )
            self._last_refill = now
    
    def try_consume(self, tokens: float = 1.0) -> Tuple[bool, float]:
        """
        Attempt to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume (default: 1)
            
        Returns:
            Tuple of (success, remaining_tokens)
        """
        if tokens <= 0:
            raise ValueError(f"Token consumption must be positive, got: {tokens}")
        
        with self._lock:
            now = time.monotonic()
            self._refill(now)
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True, self._tokens
            
            # Calculate wait time for next available token
            deficit = tokens - self._tokens
            wait_time = deficit / self._refill_rate
            return False, wait_time
    
    def current_level(self) -> float:
        """Return current token level after refill."""
        with self._lock:
            self._refill(time.monotonic())
            return self._tokens


class RateLimiter:
    """
    Sliding-window rate limiter with token bucket fallback.
    
    Ghāyah: Govern request admission through a dual-mechanism
    approach - primary sliding window for steady-state control,
    secondary token bucket for burst absorption.
    
    Architecture (Pillar 5 - Al-Kitāb):
    ʿĀmil (Governor): RateLimiter - controls all admission logic
    Maʿmūl (Governed): WindowState, TokenBucket - passive data stores
    
    Thread Safety: All public methods are atomic and safe for
    concurrent invocation from multiple threads.
    
    Lifecycle: INITIALIZING → ACTIVE → DEGRADED → CLOSED/FAILED
    """
    
    __slots__ = (
        '_window', '_bucket', '_max_requests', '_window_seconds',
        '_state', '_state_lock', '_degraded_threshold', '_closed_event'
    )
    
    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        burst_capacity: Optional[int] = None,
        refill_rate: Optional[float] = None,
        degraded_threshold: float = 0.9
    ) -> None:
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Sliding window duration in seconds
            burst_capacity: Token bucket capacity (default: max_requests // 4)
            refill_rate: Token refill rate per second (default: max_requests / window_seconds)
            degraded_threshold: Window utilization ratio triggering DEGRADED state
            
        Raises:
            ValueError: On invalid parameters
        """
        # Validate core parameters (Lisān al-ʿArab: exhaustive validation)
        if max_requests <= 0:
            raise ValueError(f"max_requests must be positive, got: {max_requests}")
        if window_seconds <= 0:
            raise ValueError(f"window_seconds must be positive, got: {window_seconds}")
        if not 0 < degraded_threshold <= 1.0:
            raise ValueError(f"degraded_threshold must be in (0, 1], got: {degraded_threshold}")
        
        # State: INITIALIZING (Pillar 3: full lifecycle coverage)
        self._state = RateLimitState.INITIALIZING
        self._state_lock = threading.Lock()
        self._closed_event = threading.Event()
        
        # Primary mechanism: Sliding window
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._window = WindowState(window_seconds)
        
        # Secondary mechanism: Token bucket fallback
        if burst_capacity is None:
            burst_capacity = max(1, max_requests // 4)
        if refill_rate is None:
            refill_rate = max_requests / window_seconds
        
        self._bucket = TokenBucket(burst_capacity, refill_rate)
        self._degraded_threshold = degraded_threshold
        
        # Transition to ACTIVE
        self._transition_state(RateLimitState.ACTIVE)
        logger.info(
            f"RateLimiter initialized: max={max_requests}/window={window_seconds}s, "
            f"burst={burst_capacity}, refill={refill_rate:.2f}/s"
        )
    
    def _transition_state(self, new_state: RateLimitState) -> None:
        """
        Thread-safe state transition with validation.
        
        Args:
            new_state: Target state
            
        Raises:
            RuntimeError: If transition is invalid from current state
        """
        valid_transitions = {
            RateLimitState.INITIALIZING: {RateLimitState.ACTIVE, RateLimitState.FAILED},
            RateLimitState.ACTIVE: {RateLimitState.DEGRADED, RateLimitState.CLOSED, RateLimitState.FAILED},
            RateLimitState.DEGRADED: {RateLimitState.ACTIVE, RateLimitState.CLOSED, RateLimitState.FAILED},
            RateLimitState.CLOSED: set(),  # Terminal state
            RateLimitState.FAILED: set(),  # Terminal state
        }
        
        with self._state_lock:
            if new_state not in valid_transitions[self._state]:
                raise RuntimeError(
                    f"Invalid state transition: {self._state} → {new_state}"
                )
            
            old_state = self._state
            self._state = new_state
            
            if new_state == RateLimitState.CLOSED:
                self._closed_event.set()
            
            logger.info(f"State transition: {old_state} → {new_state}")
    
    def _check_state(self) -> None:
        """
        Verify limiter is in an operational state.
        
        Raises:
            RuntimeError: If limiter is CLOSED or FAILED
        """
        with self._state_lock:
            if self._state in (RateLimitState.CLOSED, RateLimitState.FAILED):
                raise RuntimeError(f"RateLimiter is in terminal state: {self._state}")
    
    def allow_request(self) -> RateLimitDecision:
        """
        Determine if a request should be admitted.
        
        This is the primary admission control method.
        
        Returns:
            RateLimitDecision with verdict and diagnostic information
            
        Raises:
            RuntimeError: If limiter is CLOSED or FAILED
        """
        # State validation (Pillar 3: no silent failures)
        self._check_state()
        
        now = time.time()
        
        # Primary check: Sliding window
        current_count = self._window.count_in_window(now)
        window_utilization = current_count / self._max_requests
        
        # Update state based on utilization (Pillar 3: DEGRADED state)
        if window_utilization >= self._degraded_threshold:
            if self._state == RateLimitState.ACTIVE:
                self._transition_state(RateLimitState.DEGRADED)
        elif self._state == RateLimitState.DEGRADED:
            self._transition_state(RateLimitState.ACTIVE)
        
        if current_count < self._max_requests:
            # Primary admission path
            try:
                self._window.add_event(now)
            except RuntimeError as e:
                # Temporal anomaly - transition to FAILED (Pillar 3)
                logger.error(f"Window integrity violation: {e}")
                self._transition_state(RateLimitState.FAILED)
                raise
            
            return RateLimitDecision(
                verdict=AdmissionVerdict.ADMITTED,
                timestamp=now,
                window_utilization=window_utilization,
                bucket_level=self._bucket.current_level()
            )
        
        # Primary saturated - attempt token bucket fallback
        success, wait_time = self._bucket.try_consume()
        
        if success:
            # Fallback admission
            self._window.add_event(now)  # Track in window for consistency
            return RateLimitDecision(
                verdict=AdmissionVerdict.DEFERRED,
                timestamp=now,
                retry_after_ms=0,
                window_utilization=window_utilization,
                bucket_level=self._bucket.current_level()
            )
        
        # Both mechanisms exhausted - REJECTED
        retry_ms = int(wait_time * 1000) + 1  # Ceiling to next millisecond
        
        return RateLimitDecision(
            verdict=AdmissionVerdict.REJECTED,
            timestamp=now,
            retry_after_ms=retry_ms,
            window_utilization=window_utilization,
            bucket_level=0.0
        )
    
    def try_acquire(self, timeout_ms: Optional[int] = None) -> RateLimitDecision:
        """
        Attempt to acquire permission with optional blocking.
        
        Args:
            timeout_ms: Maximum time to wait in milliseconds.
                      None means non-blocking (immediate return).
                      0 means block indefinitely.
        
        Returns:
            RateLimitDecision with final verdict
        """
        if timeout_ms is None:
            # Non-blocking mode
            return self.allow_request()
        
        deadline = time.monotonic() + (timeout_ms / 1000.0)
        
        while True:
            decision = self.allow_request()
            
            if decision.verdict != AdmissionVerdict.REJECTED:
                return decision
            
            if timeout_ms == 0:
                # Block indefinitely until admitted
                time.sleep(min(0.01, decision.retry_after_ms / 1000.0 if decision.retry_after_ms else 0.01))
                continue
            
            if time.monotonic() >= deadline:
                return decision  # Timed out, return rejection
            
            # Sleep for retry interval or remaining time
            remaining = deadline - time.monotonic()
            sleep_time = min(
                remaining,
                (decision.retry_after_ms or 10) / 1000.0
            )
            time.sleep(max(0.001, sleep_time))
    
    def get_metrics(self) -> Dict[str, float]:
        """
        Retrieve current operational metrics.
        
        Returns:
            Dictionary with window utilization, bucket level, and state
        """
        now = time.time()
        current_count = self._window.count_in_window(now)
        
        return {
            'window_utilization': current_count / self._max_requests,
            'active_requests': current_count,
            'bucket_level': self._bucket.current_level(),
            'bucket_capacity': self._bucket._capacity,
            'state': self._state.name,
        }
    
    def close(self) -> None:
        """
        Gracefully shut down the rate limiter.
        
        Transitions to CLOSED state and rejects all subsequent requests.
        """
        self._transition_state(RateLimitState.CLOSED)
        logger.info("RateLimiter closed")
    
    def reset(self) -> None:
        """
        Reset the limiter to initial state.
        
        Clears all window events and refills token bucket.
        Only valid from CLOSED or FAILED states.
        """
        with self._state_lock:
            if self._state not in (RateLimitState.CLOSED, RateLimitState.FAILED):
                raise RuntimeError(
                    f"Cannot reset from state: {self._state}. Must be CLOSED or FAILED."
                )
            
            # Reset internal state
            self._window = WindowState(self._window_seconds)
            self._bucket = TokenBucket(
                self._bucket._capacity,
                self._bucket._refill_rate
            )
            self._closed_event.clear()
            self._state = RateLimitState.ACTIVE
        
        logger.info("RateLimiter reset to ACTIVE state")
    
    @property
    def state(self) -> RateLimitState:
        """Current lifecycle state."""
        with self._state_lock:
            return self._state
    
    def __enter__(self) -> 'RateLimiter':
        """Context manager entry."""
        self._check_state()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - always close."""
        self.close()


# ═══════════════════════════════════════════════════════════════════════════
# CONCURRENCY UTILITIES (Pillar 4: Atomic Primitives)
# ═══════════════════════════════════════════════════════════════════════════

class ConcurrentRateLimiter:
    """
    Thread-safe wrapper providing batched admission for concurrent workloads.
    
    Ghāyah: Provide a high-level concurrent interface with automatic
    retry and backoff for multi-threaded request admission.
    
    This is a Majāz (metaphor) layer - the Ḥaqīqah (reality) is the
    underlying RateLimiter with its atomic operations.
    """
    
    __slots__ = ('_limiter', '_max_concurrent', '_active', '_condition')
    
    def __init__(self, limiter: RateLimiter, max_concurrent: int = 100) -> None:
        """
        Initialize concurrent wrapper.
        
        Args:
            limiter: Underlying RateLimiter instance
            max_concurrent: Maximum concurrent admissions allowed
        """
        if max_concurrent <= 0:
            raise ValueError(f"max_concurrent must be positive, got: {max_concurrent}")
        
        self._limiter = limiter
        self._max_concurrent = max_concurrent
        self._active = 0
        self._condition = threading.Condition()
    
    def acquire(self, timeout_ms: Optional[int] = None) -> RateLimitDecision:
        """
        Acquire admission with concurrency limiting.
        
        Args:
            timeout_ms: Timeout for the entire operation
            
        Returns:
            RateLimitDecision
        """
        with self._condition:
            # Wait for concurrency slot
            deadline = time.monotonic() + (timeout_ms / 1000.0) if timeout_ms else None
            
            while self._active >= self._max_concurrent:
                if deadline and time.monotonic() >= deadline:
                    return RateLimitDecision(
                        verdict=AdmissionVerdict.REJECTED,
                        timestamp=time.time(),
                        retry_after_ms=100,
                        window_utilization=1.0,
                        bucket_level=0.0
                    )
                remaining = deadline - time.monotonic() if deadline else 0.1
                self._condition.wait(timeout=max(0.001, remaining))
            
            # Acquire concurrency slot
            self._active += 1
        
        try:
            # Delegate to underlying limiter
            decision = self._limiter.try_acquire(timeout_ms)
            return decision
        finally:
            with self._condition:
                self._active -= 1
                self._condition.notify_all()
    
    def release(self) -> None:
        """Explicitly release a concurrency slot (for manual management)."""
        with self._condition:
            self._active = max(0, self._active - 1)
            self._condition.notify_all()


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE (Pillar 2: Eloquent demonstration)
# ═══════════════════════════════════════════════════════════════════════════

def demonstrate_rate_limiter() -> None:
    """
    Demonstrate the rate limiter with a realistic scenario.
    
    Ghāyah: Validate correct behavior under burst and steady-state load.
    """
    # Create limiter: 10 requests per 5 seconds, burst capacity of 5
    limiter = RateLimiter(
        max_requests=10,
        window_seconds=5.0,
        burst_capacity=5,
        refill_rate=2.0  # 2 tokens per second
    )
    
    print("=== Rate Limiter Demonstration ===")
    print(f"State: {limiter.state}")
    
    # Simulate burst of 15 requests
    print("\n--- Burst Test (15 rapid requests) ---")
    results = []
    for i in range(15):
        decision = limiter.allow_request()
        results.append(decision.verdict)
        print(f"Request {i+1:2d}: {decision.verdict.name:10s} "
              f"(window: {decision.window_utilization:.2f}, "
              f"bucket: {decision.bucket_level:.1f})")
    
    admitted = sum(1 for r in results if r == AdmissionVerdict.ADMITTED)
    deferred = sum(1 for r in results if r == AdmissionVerdict.DEFERRED)
    rejected = sum(1 for r in results if r == AdmissionVerdict.REJECTED)
    
    print(f"\nSummary: {admitted} admitted, {deferred} deferred, {rejected} rejected")
    
    # Wait for window to slide
    print("\n--- Waiting 6 seconds for window reset ---")
    time.sleep(6.0)
    
    # Test recovery
    print("\n--- Recovery Test ---")
    decision = limiter.allow_request()
    print(f"Request after window reset: {decision.verdict.name}")
    
    # Test concurrent access
    print("\n--- Concurrent Access Test ---")
    concurrent_limiter = ConcurrentRateLimiter(limiter, max_concurrent=5)
    
    def worker(worker_id: int) -> None:
        decision = concurrent_limiter.acquire(timeout_ms=1000)
        print(f"Worker {worker_id}: {decision.verdict.name}")
    
    threads = []
    for i in range(8):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Cleanup
    limiter.close()
    print(f"\nFinal state: {limiter.state}")
    
    # Test reset
    limiter.reset()
    print(f"After reset: {limiter.state}")
    
    # Verify rejection after close
    limiter.close()
    try:
        limiter.allow_request()
    except RuntimeError as e:
        print(f"Expected error after close: {e}")


if __name__ == "__main__":
    demonstrate_rate_limiter()