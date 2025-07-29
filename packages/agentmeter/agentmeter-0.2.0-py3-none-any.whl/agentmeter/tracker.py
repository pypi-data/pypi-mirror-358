"""
AgentMeter Usage Tracker
"""

import threading
import time
from typing import Optional, Dict, Any, List, Union, Callable
from contextlib import contextmanager
from .models import (
    MeterEvent, EventType, APIRequestPayEvent, 
    TokenBasedPayEvent, InstantPayEvent, PaymentType
)
from .client import AgentMeterClient


class UsageContext:
    """Context object for tracking usage within a context manager"""
    
    def __init__(
        self,
        client: AgentMeterClient,
        project_id: str,
        agent_id: str,
        user_id: Optional[str] = None,
        payment_type: PaymentType = PaymentType.API_REQUEST_PAY,
        **kwargs
    ):
        self.client = client
        self.project_id = project_id
        self.agent_id = agent_id
        self.user_id = user_id or "anonymous"
        self.payment_type = payment_type
        self.kwargs = kwargs
        self.data = {
            "tokens_in": 0,
            "tokens_out": 0,
            "api_calls": 1,
            "amount": kwargs.get("amount", 0.0),
            "metadata": {}
        }
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        # Keep user metadata separate from timing metadata
        user_metadata = self.data["metadata"].copy()
        
        # Add timing metadata to a separate copy for internal use
        # but don't modify the user's metadata dict
        timing_metadata = {
            "duration_seconds": duration,
            "start_time": self.start_time,
            "end_time": self.end_time
        }
        
        try:
            # Record appropriate event based on payment type
            if self.payment_type == PaymentType.API_REQUEST_PAY:
                self.client.record_api_request_pay(
                    api_calls=self.data["api_calls"],
                    unit_price=self.kwargs.get("unit_price"),
                    project_id=self.project_id,
                    agent_id=self.agent_id,
                    user_id=self.user_id,
                    metadata=user_metadata
                )
            elif self.payment_type == PaymentType.TOKEN_BASED_PAY:
                self.client.record_token_based_pay(
                    tokens_in=self.data["tokens_in"],
                    tokens_out=self.data["tokens_out"],
                    input_token_price=self.kwargs.get("input_token_price"),
                    output_token_price=self.kwargs.get("output_token_price"),
                    project_id=self.project_id,
                    agent_id=self.agent_id,
                    user_id=self.user_id,
                    metadata=user_metadata
                )
            elif self.payment_type == PaymentType.INSTANT_PAY:
                amount = self.data["amount"] or self.kwargs.get("amount", 0.0)
                if amount > 0:
                    self.client.record_instant_pay(
                        amount=amount,
                        description=self.kwargs.get("description"),
                        project_id=self.project_id,
                        agent_id=self.agent_id,
                        user_id=self.user_id,
                        metadata=user_metadata
                    )
        except Exception as e:
            # Log error but don't raise to avoid breaking user code
            print(f"Warning: Failed to record AgentMeter event: {e}")


class AgentMeterTracker:
    """Enhanced thread-safe tracker for AgentMeter events with multiple payment types"""
    
    def __init__(
        self,
        client: AgentMeterClient,
        project_id: str,
        agent_id: str,
        user_id: Optional[str] = None,
        auto_flush: bool = True,
        flush_interval: int = 10,
        batch_size: int = 10,
        # Default pricing configuration
        default_api_price: float = 0.001,
        default_input_token_price: float = 0.000004,
        default_output_token_price: float = 0.000001
    ):
        self.client = client
        self.project_id = project_id
        self.agent_id = agent_id
        self.user_id = user_id or "anonymous"
        self.auto_flush = auto_flush
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        
        # Pricing configuration
        self.default_api_price = default_api_price
        self.default_input_token_price = default_input_token_price
        self.default_output_token_price = default_output_token_price
        
        self._events: List[Dict[str, Any]] = []
        self._contexts: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._last_flush = time.time()
        self._should_stop = False
        
        if auto_flush:
            self._start_flush_timer()
    
    def _start_flush_timer(self):
        """Start background timer for auto-flushing"""
        def flush_timer():
            while not self._should_stop:
                time.sleep(self.flush_interval)
                if not self._should_stop:
                    self.flush()
        
        timer_thread = threading.Thread(target=flush_timer, daemon=True)
        timer_thread.start()
    
    def stop(self):
        """Stop the auto-flush timer and flush remaining events"""
        self._should_stop = True
        self.flush()
    
    def track_api_request(
        self,
        user_id: str,
        api_calls: int = 1,
        unit_price: Optional[float] = None,
        metadata: Optional[Dict] = None
    ):
        """Track API request payment event"""
        return UsageContext(
            client=self.client,
            project_id=self.project_id,
            agent_id=self.agent_id,
            user_id=user_id,
            payment_type=PaymentType.API_REQUEST_PAY,
            unit_price=unit_price or self.default_api_price
        )
    
    def track_token_usage(
        self,
        user_id: str,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        input_token_price: Optional[float] = None,
        output_token_price: Optional[float] = None,
        metadata: Optional[Dict] = None
    ):
        """Track token-based payment event"""
        return UsageContext(
            client=self.client,
            project_id=self.project_id,
            agent_id=self.agent_id,
            user_id=user_id,
            payment_type=PaymentType.TOKEN_BASED_PAY,
            input_token_price=input_token_price or self.default_input_token_price,
            output_token_price=output_token_price or self.default_output_token_price
        )
    
    def track_instant_payment(
        self,
        user_id: str,
        amount: float,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Track instant payment event"""
        return UsageContext(
            client=self.client,
            project_id=self.project_id,
            agent_id=self.agent_id,
            user_id=user_id,
            payment_type=PaymentType.INSTANT_PAY,
            amount=amount,
            description=description
        )
    
    def track_event(
        self,
        event_type: EventType = EventType.API_CALL,
        tokens_in: int = 0,
        tokens_out: int = 0,
        api_calls: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track a generic event (legacy method for backward compatibility)"""
        event = MeterEvent(
            project_id=self.project_id,
            agent_id=self.agent_id,
            user_id=self.user_id,
            event_type=event_type,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            api_calls=api_calls,
            metadata=metadata or {}
        )
        
        event_data = {
            'method': 'record_event',
            'args': {'event': event}
        }
        self._add_event(event_data)
    
    def _add_event(self, event_data: Dict[str, Any]):
        """Add event to the queue"""
        with self._lock:
            self._events.append(event_data)
            
            # Auto-flush if batch size reached
            if len(self._events) >= self.batch_size:
                self._flush_events()
    
    def flush(self):
        """Manually flush all pending events"""
        with self._lock:
            self._flush_events()
    
    def _flush_events(self):
        """Internal method to flush events (must be called with lock held)"""
        if not self._events:
            return
        
        events_to_send = self._events.copy()
        self._events.clear()
        self._last_flush = time.time()
        
        # Send events (outside of lock to avoid blocking)
        for event_data in events_to_send:
            try:
                method_name = event_data['method']
                args = event_data['args']
                
                # Call the appropriate client method
                method = getattr(self.client, method_name)
                method(**args)
                
            except Exception as e:
                print(f"Warning: Failed to record AgentMeter event: {e}")


# Context managers for different payment types

def track_api_request_pay(
    client: AgentMeterClient,
    project_id: str,
    agent_id: str,
    user_id: Optional[str] = None,
    unit_price: Optional[float] = None
) -> UsageContext:
    """
    Context manager for tracking API request payment
    
    Example:
        with track_api_request_pay(client, "proj_123", "agent_456", unit_price=0.3) as usage:
            # API call happens here
            usage["api_calls"] = 1
            usage["metadata"]["endpoint"] = "/api/search"
    """
    return UsageContext(
        client=client,
        project_id=project_id,
        agent_id=agent_id,
        user_id=user_id,
        payment_type=PaymentType.API_REQUEST_PAY,
        unit_price=unit_price
    )


def track_token_based_pay(
    client: AgentMeterClient,
    project_id: str,
    agent_id: str,
    user_id: Optional[str] = None,
    input_token_price: Optional[float] = None,
    output_token_price: Optional[float] = None
) -> UsageContext:
    """
    Context manager for tracking token-based payment
    
    Example:
        with track_token_based_pay(client, "proj_123", "agent_456") as usage:
            # AI model call happens here
            usage["tokens_in"] = 1000
            usage["tokens_out"] = 500
            usage["metadata"]["model"] = "gpt-4"
    """
    return UsageContext(
        client=client,
        project_id=project_id,
        agent_id=agent_id,
        user_id=user_id,
        payment_type=PaymentType.TOKEN_BASED_PAY,
        input_token_price=input_token_price or self.default_input_token_price,
        output_token_price=output_token_price or self.default_output_token_price
    )


def track_instant_pay(
    client: AgentMeterClient,
    project_id: str,
    agent_id: str,
    user_id: Optional[str] = None,
    amount: Optional[float] = None,
    description: Optional[str] = None
) -> UsageContext:
    """
    Context manager for tracking instant payment
    
    Example:
        with track_instant_pay(client, "proj_123", "agent_456", description="Premium feature") as usage:
            # Premium feature usage
            usage["amount"] = 4.99
            usage["metadata"]["feature"] = "advanced_search"
    """
    return UsageContext(
        client=client,
        project_id=project_id,
        agent_id=agent_id,
        user_id=user_id,
        payment_type=PaymentType.INSTANT_PAY,
        amount=amount,
        description=description
    )


def track_usage(
    client: AgentMeterClient,
    project_id: str,
    agent_id: str,
    user_id: Optional[str] = None,
    payment_type: PaymentType = PaymentType.API_REQUEST_PAY,
    **kwargs
) -> UsageContext:
    """
    Generic context manager for tracking usage with different payment types
    
    Args:
        client: AgentMeter client instance
        project_id: Project identifier
        agent_id: Agent identifier
        user_id: User identifier (optional)
        payment_type: Type of payment to track
        **kwargs: Additional parameters specific to payment type
    
    Returns:
        Context manager that yields a dict for tracking usage data
    """
    return UsageContext(
        client=client,
        project_id=project_id,
        agent_id=agent_id,
        user_id=user_id,
        payment_type=payment_type,
        **kwargs
    )