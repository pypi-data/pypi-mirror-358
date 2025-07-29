"""AgentMeter API Client"""

import requests
from typing import Optional, Dict, Any, List, Union
from .models import (
    MeterEvent, MeterEventResponse, MeterEventsResponse, 
    APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent,
    Project, ProjectCreateRequest, UserMeter, UserMeterSetRequest,
    UserMeterIncrementRequest, UserMeterResetRequest, MeterStats,
    BillingRecord, BillingRecordCreateRequest, BillingRecordUpdateRequest,
    AgentMeterConfig
)
from .exceptions import AgentMeterAPIError, AgentMeterError
import time
import logging

logger = logging.getLogger(__name__)

class AgentMeterClient:
    """Client for interacting with AgentMeter API"""
    
    def __init__(
        self, 
        api_key: str,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = "anonymous",
        base_url: str = "https://api.staging.agentmeter.money"
    ):
        """
        Initialize AgentMeter client
        
        Args:
            api_key: The project secret key for authentication
            project_id: Default project ID for operations
            agent_id: Default agent ID for operations
            user_id: Default user ID for operations
            base_url: The base URL for the AgentMeter API
        """
        self.api_key = api_key
        self.project_id = project_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'AgentMeter-Python-SDK/0.2.0'
        })
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=30)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, params=params, timeout=30)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, json=data, params=params, timeout=30)
                elif method.upper() == 'PATCH':
                    response = self.session.patch(url, json=data, params=params, timeout=30)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, params=params, timeout=30)
                else:
                    raise AgentMeterError(f"Unsupported HTTP method: {method}")
                
                # Handle different response status codes
                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 401:
                    raise AgentMeterAPIError("Authentication failed. Check your API key.", 401)
                elif response.status_code == 403:
                    raise AgentMeterAPIError("Access forbidden. Check your permissions.", 403)
                elif response.status_code == 404:
                    raise AgentMeterAPIError("Resource not found.", 404)
                elif response.status_code == 429:
                    # Rate limited - check retry headers
                    retry_after = response.headers.get('X-RateLimit-Reset', '60')
                    raise AgentMeterAPIError(f"Rate limited. Retry after {retry_after} seconds.", 429)
                elif response.status_code >= 500:
                    # Server error - retry
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Server error {response.status_code}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    raise AgentMeterAPIError(f"Server error: {response.status_code}", response.status_code)
                else:
                    # Client error - don't retry
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                    except:
                        error_msg = f'HTTP {response.status_code}'
                    raise AgentMeterAPIError(error_msg, response.status_code)
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed: {e}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                raise AgentMeterError(f"Request failed: {e}")
        
        raise AgentMeterError("Max retries exceeded")
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._request('GET', '/health')
    
    # === Metering Events ===
    
    def record_event(self, event: Union[MeterEvent, APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent]) -> MeterEventResponse:
        """Record a usage event"""
        # Use to_dict() if available, otherwise manually serialize datetime fields
        if hasattr(event, 'to_dict'):
            event_data = event.to_dict()
        else:
            event_data = event.model_dump()
            # Convert datetime objects to ISO strings
            if 'timestamp' in event_data and hasattr(event_data['timestamp'], 'isoformat'):
                event_data['timestamp'] = event_data['timestamp'].isoformat()
        
        response_data = self._request('POST', '/api/meter/event', data=event_data)
        return MeterEventResponse(**response_data)
    
    async def record_api_request_pay(
        self,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_calls: int = 1,
        unit_price: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> MeterEventResponse:
        """Record an API request payment event"""
        event = APIRequestPayEvent(
            project_id=project_id or self.project_id,
            agent_id=agent_id or self.agent_id,
            user_id=user_id or self.user_id,
            api_calls=api_calls,
            unit_price=unit_price,
            metadata=metadata or {}
        )
        return self.record_event(event)
    
    async def record_token_based_pay(
        self,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        input_token_price: Optional[float] = None,
        output_token_price: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> MeterEventResponse:
        """Record a token-based payment event"""
        event = TokenBasedPayEvent(
            project_id=project_id or self.project_id,
            agent_id=agent_id or self.agent_id,
            user_id=user_id or self.user_id,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            input_token_price=input_token_price,
            output_token_price=output_token_price,
            metadata=metadata or {}
        )
        return self.record_event(event)
    
    async def record_instant_pay(
        self,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        amount: float = 0.0,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> MeterEventResponse:
        """Record an instant payment event"""
        event = InstantPayEvent(
            project_id=project_id or self.project_id,
            agent_id=agent_id or self.agent_id,
            user_id=user_id or self.user_id,
            amount=amount,
            description=description,
            metadata=metadata or {}
        )
        return self.record_event(event)
    
    def get_events(
        self,
        project_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve events with filtering options"""
        params = {}
        if project_id or self.project_id:
            params['project_id'] = project_id or self.project_id
        if agent_id:
            params['agent_id'] = agent_id
        if user_id:
            params['user_id'] = user_id
        if event_type:
            params['event_type'] = event_type
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if limit:
            params['limit'] = limit
        
        response_data = self._request('GET', '/api/meter/events', params=params)
        return response_data
    
    def get_meter_stats(
        self,
        project_id: Optional[str] = None,
        timeframe: str = "30 days"
    ) -> MeterStats:
        """Get metering statistics"""
        params = {
            'project_id': project_id or self.project_id,
            'timeframe': timeframe
        }
        response_data = self._request('GET', '/api/meter/stats', params=params)
        return MeterStats(**response_data)
    
    # === User Meter Management ===
    
    def get_user_meter(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> UserMeter:
        """Get user meter information"""
        params = {
            'project_id': project_id or self.project_id,
            'user_id': user_id or self.user_id
        }
        response_data = self._request('GET', '/api/meter/usage', params=params)
        return UserMeter(**response_data)
    
    def set_user_meter(
        self,
        threshold_amount: float,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> UserMeter:
        """Set user meter threshold"""
        data = {
            'project_id': project_id or self.project_id,
            'user_id': user_id or self.user_id,
            'threshold_amount': threshold_amount
        }
        response_data = self._request('PUT', '/api/meter', data=data)
        return UserMeter(**response_data)
    
    def increment_user_meter(
        self,
        amount: float,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> UserMeter:
        """Increment user meter usage"""
        data = {
            'project_id': project_id or self.project_id,
            'user_id': user_id or self.user_id,
            'amount': amount
        }
        response_data = self._request('POST', '/api/meter/increment', data=data)
        return UserMeter(**response_data)
    
    def reset_user_meter(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> UserMeter:
        """Reset user meter usage"""
        data = {
            'project_id': project_id or self.project_id,
            'user_id': user_id or self.user_id
        }
        response_data = self._request('POST', '/api/meter/reset', data=data)
        return UserMeter(**response_data)
    
    # === Project Management ===
    
    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """Create a new project"""
        data = {'name': name}
        if description:
            data['description'] = description
        response_data = self._request('POST', '/projects', data=data)
        return Project(**response_data)
    
    def get_project(self, project_id: str) -> Project:
        """Get project information"""
        response_data = self._request('GET', f'/projects/{project_id}')
        return Project(**response_data)
    
    def list_projects(self) -> List[Project]:
        """List all projects"""
        response_data = self._request('GET', '/projects')
        return [Project(**project) for project in response_data]
    
    def update_project(
        self, 
        project_id: str, 
        name: Optional[str] = None, 
        description: Optional[str] = None
    ) -> Project:
        """Update project information"""
        data = {}
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        response_data = self._request('PATCH', f'/projects/{project_id}', data=data)
        return Project(**response_data)
    
    def delete_project(self, project_id: str) -> Dict[str, bool]:
        """Delete a project"""
        return self._request('DELETE', f'/projects/{project_id}')
    
    # === Billing Records ===
    
    def create_billing_record(
        self,
        project_id: str,
        period_start: str,
        period_end: str,
        amount: float,
        status: str = "pending"
    ) -> BillingRecord:
        """Create a billing record"""
        data = {
            'project_id': project_id,
            'period_start': period_start,
            'period_end': period_end,
            'amount': amount,
            'status': status
        }
        response_data = self._request('POST', '/billing-records', data=data)
        return BillingRecord(**response_data)
    
    def list_billing_records(self, project_id: Optional[str] = None) -> List[BillingRecord]:
        """List billing records for a project"""
        params = {'project_id': project_id or self.project_id}
        response_data = self._request('GET', '/billing-records', params=params)
        return [BillingRecord(**record) for record in response_data]
    
    def update_billing_record(
        self,
        record_id: str,
        status: Optional[str] = None,
        amount: Optional[float] = None
    ) -> BillingRecord:
        """Update a billing record"""
        data = {}
        if status:
            data['status'] = status
        if amount:
            data['amount'] = amount
        response_data = self._request('PATCH', f'/billing-records/{record_id}', data=data)
        return BillingRecord(**response_data)