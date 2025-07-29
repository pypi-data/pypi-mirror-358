"""
Data models for AgentMeter SDK
Defines the structure for events, user meters, and other API objects
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List, Literal, Union
from pydantic import BaseModel, Field, field_validator
import uuid


class PaymentType(str, Enum):
    """Payment types supported by AgentMeter"""
    API_REQUEST_PAY = "api_request_pay"
    TOKEN_BASED_PAY = "token_based_pay"
    INSTANT_PAY = "instant_pay"


class EventType(str, Enum):
    """Event types for backwards compatibility"""
    API_CALL = "api_call"
    TOKEN_USAGE = "token_usage"
    INSTANT_PAYMENT = "instant_payment"


class MeterEvent(BaseModel):
    """Base model for all metering events"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    agent_id: str
    user_id: str
    total_cost: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('total_cost')
    @classmethod
    def validate_cost(cls, v):
        if v < 0:
            raise ValueError("Cost cannot be negative")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = self.model_dump()
        result['timestamp'] = self.timestamp.isoformat()
        
        # Convert enum values to strings
        for key, value in result.items():
            if hasattr(value, 'value'):  # Check if it's an enum
                result[key] = value.value
                
        return result


class APIRequestPayEvent(MeterEvent):
    """Event for API request-based payments"""
    event_type: Literal[EventType.API_CALL] = EventType.API_CALL
    payment_type: Literal[PaymentType.API_REQUEST_PAY] = PaymentType.API_REQUEST_PAY
    api_calls: int = 1
    unit_price: float
    
    @field_validator('api_calls')
    @classmethod
    def validate_api_calls(cls, v):
        if v < 0:
            raise ValueError("API calls cannot be negative")
        return v
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIRequestPayEvent':
        """Create instance from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = self.model_dump()
        result['timestamp'] = self.timestamp.isoformat()
        
        # Convert enum values to strings
        for key, value in result.items():
            if hasattr(value, 'value'):  # Check if it's an enum
                result[key] = value.value
                
        return result


class TokenBasedPayEvent(MeterEvent):
    """Event for token-based payments"""
    event_type: Literal[EventType.TOKEN_USAGE] = EventType.TOKEN_USAGE
    payment_type: Literal[PaymentType.TOKEN_BASED_PAY] = PaymentType.TOKEN_BASED_PAY
    tokens_in: int = 0
    tokens_out: int = 0
    input_token_price: float
    output_token_price: float
    
    @field_validator('tokens_in', 'tokens_out')
    @classmethod
    def validate_tokens(cls, v):
        if v < 0:
            raise ValueError("Token count cannot be negative")
        return v
    
    @property
    def total_tokens(self) -> int:
        """Total tokens used"""
        return self.tokens_in + self.tokens_out
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenBasedPayEvent':
        """Create instance from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = self.model_dump()
        result['timestamp'] = self.timestamp.isoformat()
        
        # Convert enum values to strings
        for key, value in result.items():
            if hasattr(value, 'value'):  # Check if it's an enum
                result[key] = value.value
                
        return result


class InstantPayEvent(MeterEvent):
    """Event for instant payments"""
    event_type: Literal[EventType.INSTANT_PAYMENT] = EventType.INSTANT_PAYMENT
    payment_type: Literal[PaymentType.INSTANT_PAY] = PaymentType.INSTANT_PAY
    amount: float
    description: str
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InstantPayEvent':
        """Create instance from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = self.model_dump()
        result['timestamp'] = self.timestamp.isoformat()
        
        # Convert enum values to strings
        for key, value in result.items():
            if hasattr(value, 'value'):  # Check if it's an enum
                result[key] = value.value
                
        return result


class MeterEventResponse(BaseModel):
    """Response model for meter event operations"""
    success: bool = True
    event_id: str
    cost: float = 0.0
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeterEventResponse':
        """Create instance from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return cls(**data)


class MeterEventsResponse(BaseModel):
    """Response model for multiple meter events"""
    events: List[Dict[str, Any]] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 50
    has_more: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MeterEventsResponse':
        """Create instance from dictionary"""
        return cls(**data)


class UserMeter(BaseModel):
    """User subscription meter for tracking usage limits"""
    project_id: str
    user_id: str
    threshold_amount: float
    current_usage: float = 0.0
    last_reset_at: datetime
    updated_at: datetime
    
    @property
    def remaining_budget(self) -> float:
        """Remaining budget amount"""
        return self.threshold_amount - self.current_usage
    
    @property
    def usage_percentage(self) -> float:
        """Usage as percentage of threshold"""
        if self.threshold_amount == 0:
            return 0.0
        return (self.current_usage / self.threshold_amount) * 100
    
    @property
    def is_over_limit(self) -> bool:
        """Whether usage exceeds threshold"""
        return self.current_usage > self.threshold_amount
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMeter':
        """Create instance from dictionary"""
        for field in ['last_reset_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = self.model_dump()
        result['last_reset_at'] = self.last_reset_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        return result


class MeterStats(BaseModel):
    """Usage statistics for a project/agent/user"""
    total_api_calls: int = 0
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_cost: float = 0.0
    timeframe: str = "30 days"
    
    @property
    def total_tokens(self) -> int:
        """Total tokens across input and output"""
        return self.total_tokens_in + self.total_tokens_out
    
    @property
    def average_cost_per_call(self) -> float:
        """Average cost per API call"""
        if self.total_api_calls == 0:
            return 0.0
        return self.total_cost / self.total_api_calls


class Project(BaseModel):
    """Project information"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create instance from dictionary"""
        for field in ['created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        return cls(**data)


class BillingRecord(BaseModel):
    """Billing record for a project"""
    id: str
    project_id: str
    period_start: datetime
    period_end: datetime
    amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BillingRecord':
        """Create instance from dictionary"""
        for field in ['period_start', 'period_end', 'created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        return cls(**data)


class AgentMeterConfig(BaseModel):
    """Configuration for AgentMeter client"""
    api_key: str
    project_id: str
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    base_url: str = "https://api.staging.agentmeter.money"
    timeout: int = 30
    retry_attempts: int = 3
    batch_size: int = 50
    
    @field_validator('timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v
    
    @field_validator('retry_attempts')
    @classmethod
    def validate_retry_attempts(cls, v):
        if v < 0:
            raise ValueError("Retry attempts cannot be negative")
        return v
    
    @field_validator('batch_size')
    @classmethod
    def validate_batch_size(cls, v):
        if v <= 0:
            raise ValueError("Batch size must be positive")
        return v


# Request Models
class ProjectCreateRequest(BaseModel):
    """Request model for creating a project"""
    name: str
    description: Optional[str] = None


class UserMeterSetRequest(BaseModel):
    """Request model for setting user meter threshold"""
    threshold_amount: float
    
    @field_validator('threshold_amount')
    @classmethod
    def validate_threshold(cls, v):
        if v < 0:
            raise ValueError("Threshold amount cannot be negative")
        return v


class UserMeterIncrementRequest(BaseModel):
    """Request model for incrementing user meter usage"""
    amount: float
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class UserMeterResetRequest(BaseModel):
    """Request model for resetting user meter"""
    pass  # No additional fields needed for reset


class BillingRecordCreateRequest(BaseModel):
    """Request model for creating a billing record"""
    project_id: str
    period_start: str  # ISO format date string
    period_end: str    # ISO format date string
    amount: float
    status: str = "pending"
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class BillingRecordUpdateRequest(BaseModel):
    """Request model for updating a billing record"""
    status: Optional[str] = None
    amount: Optional[float] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError("Amount cannot be negative")
        return v