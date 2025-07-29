"""
Unit Tests for AgentMeter SDK Client
Tests all core functionality including three payment types, user meters, and API interactions.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from datetime import datetime
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    meter_function, meter_agent, PaymentType,
    quick_api_request_pay, quick_token_based_pay, quick_instant_pay
)
from agentmeter.models import (
    APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent,
    UserMeter, BillingRecord, MeterStats, Project
)
from agentmeter.exceptions import AgentMeterError, RateLimitError


class TestAgentMeterClient(unittest.TestCase):
    """Test AgentMeter client core functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.project_id = "test_project"
        self.agent_id = "test_agent"
        self.user_id = "test_user"
        
        # Mock successful response
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            "id": "evt_123",
            "total_cost": 0.10,
            "api_calls": 1,
            "tokens_in": 100,
            "tokens_out": 50,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with patch('agentmeter.client.requests.post', return_value=self.mock_response):
            self.client = AgentMeterClient(
                api_key=self.api_key,
                project_id=self.project_id,
                agent_id=self.agent_id,
                user_id=self.user_id
            )
    
    def test_client_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.project_id, self.project_id)
        self.assertEqual(self.client.agent_id, self.agent_id)
        self.assertEqual(self.client.user_id, self.user_id)
        self.assertIsNotNone(self.client.session)
    
    @patch('agentmeter.client.requests.get')
    def test_health_check(self, mock_get):
        """Test health check endpoint"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "healthy"}
        
        result = self.client.health_check()
        
        self.assertEqual(result["status"], "healthy")
        mock_get.assert_called_once()
    
    @patch('agentmeter.client.requests.post')
    def test_record_api_request_pay(self, mock_post):
        """Test API request payment recording"""
        mock_post.return_value = self.mock_response
        
        response = self.client.record_api_request_pay(
            api_calls=2,
            unit_price=0.25,
            user_id=self.user_id,
            metadata={"test": "data"}
        )
        
        self.assertIsInstance(response, APIRequestPayEvent)
        self.assertEqual(response.total_cost, 0.10)
        mock_post.assert_called_once()
        
        # Check request payload
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]['data'])
        self.assertEqual(payload['api_calls'], 2)
        self.assertEqual(payload['unit_price'], 0.25)
    
    @patch('agentmeter.client.requests.post')
    def test_record_token_based_pay(self, mock_post):
        """Test token-based payment recording"""
        mock_post.return_value = self.mock_response
        
        response = self.client.record_token_based_pay(
            tokens_in=1000,
            tokens_out=500,
            input_token_price=0.00001,
            output_token_price=0.00002,
            user_id=self.user_id
        )
        
        self.assertIsInstance(response, TokenBasedPayEvent)
        mock_post.assert_called_once()
        
        # Check request payload
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]['data'])
        self.assertEqual(payload['tokens_in'], 1000)
        self.assertEqual(payload['tokens_out'], 500)
    
    @patch('agentmeter.client.requests.post')
    def test_record_instant_pay(self, mock_post):
        """Test instant payment recording"""
        mock_post.return_value = self.mock_response
        
        response = self.client.record_instant_pay(
            amount=4.99,
            description="Premium Feature",
            user_id=self.user_id
        )
        
        self.assertIsInstance(response, InstantPayEvent)
        mock_post.assert_called_once()
        
        # Check request payload
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]['data'])
        self.assertEqual(payload['amount'], 4.99)
        self.assertEqual(payload['description'], "Premium Feature")
    
    @patch('agentmeter.client.requests.put')
    def test_set_user_meter(self, mock_put):
        """Test setting user meter"""
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {
            "project_id": self.project_id,
            "user_id": self.user_id,
            "threshold_amount": 100.0,
            "current_usage": 0.0,
            "last_reset_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        meter = self.client.set_user_meter(
            threshold_amount=100.0,
            user_id=self.user_id
        )
        
        self.assertIsInstance(meter, UserMeter)
        self.assertEqual(meter.threshold_amount, 100.0)
        mock_put.assert_called_once()
    
    @patch('agentmeter.client.requests.get')
    def test_get_user_meter(self, mock_get):
        """Test getting user meter"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "project_id": self.project_id,
            "user_id": self.user_id,
            "threshold_amount": 100.0,
            "current_usage": 25.50,
            "last_reset_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        meter = self.client.get_user_meter(user_id=self.user_id)
        
        self.assertIsInstance(meter, UserMeter)
        self.assertEqual(meter.current_usage, 25.50)
        mock_get.assert_called_once()
    
    @patch('agentmeter.client.requests.post')
    def test_increment_user_meter(self, mock_post):
        """Test incrementing user meter"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "project_id": self.project_id,
            "user_id": self.user_id,
            "threshold_amount": 100.0,
            "current_usage": 35.50,
            "last_reset_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        meter = self.client.increment_user_meter(
            amount=10.0,
            user_id=self.user_id
        )
        
        self.assertIsInstance(meter, UserMeter)
        self.assertEqual(meter.current_usage, 35.50)
        mock_post.assert_called_once()
    
    @patch('agentmeter.client.requests.post')
    def test_reset_user_meter(self, mock_post):
        """Test resetting user meter"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "project_id": self.project_id,
            "user_id": self.user_id,
            "threshold_amount": 100.0,
            "current_usage": 0.0,
            "last_reset_at": "2024-01-01T01:00:00Z",
            "updated_at": "2024-01-01T01:00:00Z"
        }
        
        meter = self.client.reset_user_meter(user_id=self.user_id)
        
        self.assertIsInstance(meter, UserMeter)
        self.assertEqual(meter.current_usage, 0.0)
        mock_post.assert_called_once()
    
    @patch('agentmeter.client.requests.get')
    def test_get_events(self, mock_get):
        """Test getting events"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "id": "evt_1",
                "total_cost": 0.10,
                "api_calls": 1,
                "timestamp": "2024-01-01T00:00:00Z"
            },
            {
                "id": "evt_2",
                "total_cost": 0.20,
                "api_calls": 2,
                "timestamp": "2024-01-01T01:00:00Z"
            }
        ]
        
        events = self.client.get_events(user_id=self.user_id, limit=10)
        
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].id, "evt_1")
        mock_get.assert_called_once()
    
    @patch('agentmeter.client.requests.get')
    def test_get_meter_stats(self, mock_get):
        """Test getting meter statistics"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "total_api_calls": 1000,
            "total_tokens_in": 50000,
            "total_tokens_out": 25000,
            "total_cost": 100.50,
            "timeframe": "30 days"
        }
        
        stats = self.client.get_meter_stats(timeframe="30 days")
        
        self.assertIsInstance(stats, MeterStats)
        self.assertEqual(stats.total_api_calls, 1000)
        self.assertEqual(stats.total_cost, 100.50)
        mock_get.assert_called_once()
    
    def test_error_handling_rate_limit(self):
        """Test rate limit error handling"""
        with patch('agentmeter.client.requests.post') as mock_post:
            mock_post.return_value.status_code = 429
            mock_post.return_value.json.return_value = {
                "error": {"code": "rate_limit_exceeded", "message": "Too many requests"}
            }
            
            with self.assertRaises(RateLimitError):
                self.client.record_api_request_pay(
                    api_calls=1,
                    unit_price=0.10,
                    user_id=self.user_id
                )
    
    def test_error_handling_client_error(self):
        """Test client error handling"""
        with patch('agentmeter.client.requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = {
                "error": {"code": "invalid_request", "message": "Bad request"}
            }
            
            with self.assertRaises(AgentMeterError):
                self.client.record_api_request_pay(
                    api_calls=1,
                    unit_price=0.10,
                    user_id=self.user_id
                )
    
    def test_error_handling_server_error(self):
        """Test server error handling"""
        with patch('agentmeter.client.requests.post') as mock_post:
            mock_post.return_value.status_code = 500
            mock_post.return_value.json.return_value = {
                "error": {"code": "internal_error", "message": "Server error"}
            }
            
            with self.assertRaises(AgentMeterError):
                self.client.record_api_request_pay(
                    api_calls=1,
                    unit_price=0.10,
                    user_id=self.user_id
                )


class TestCreateClient(unittest.TestCase):
    """Test client creation helper"""
    
    def test_create_client_basic(self):
        """Test basic client creation"""
        with patch('agentmeter.client.AgentMeterClient') as mock_client:
            create_client(
                api_key="test_key",
                project_id="test_project"
            )
            
            mock_client.assert_called_once_with(
                api_key="test_key",
                project_id="test_project",
                agent_id=None,
                user_id=None,
                base_url="https://api.staging.agentmeter.money"
            )
    
    def test_create_client_full(self):
        """Test client creation with all parameters"""
        with patch('agentmeter.client.AgentMeterClient') as mock_client:
            create_client(
                api_key="test_key",
                project_id="test_project",
                agent_id="test_agent",
                user_id="test_user",
                base_url="https://custom.url"
            )
            
            mock_client.assert_called_once_with(
                api_key="test_key",
                project_id="test_project",
                agent_id="test_agent",
                user_id="test_user",
                base_url="https://custom.url"
            )


class TestDecorators(unittest.TestCase):
    """Test decorator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_client.record_api_request_pay.return_value = Mock(total_cost=0.10)
        self.mock_client.record_token_based_pay.return_value = Mock(total_cost=0.05)
        self.mock_client.record_instant_pay.return_value = Mock(total_cost=2.99)
    
    def test_meter_api_request_pay_decorator(self):
        """Test API request pay decorator"""
        @meter_api_request_pay(self.mock_client, unit_price=0.10)
        def test_function(data):
            return f"processed: {data}"
        
        result = test_function("test_data")
        
        self.assertEqual(result, "processed: test_data")
        self.mock_client.record_api_request_pay.assert_called_once()
    
    def test_meter_token_based_pay_decorator(self):
        """Test token-based pay decorator"""
        def token_extractor(*args, result=None, **kwargs):
            return 100, 50  # input_tokens, output_tokens
        
        @meter_token_based_pay(
            self.mock_client,
            input_token_price=0.00001,
            output_token_price=0.00002,
            tokens_extractor=token_extractor
        )
        def test_function(prompt):
            return f"AI response to: {prompt}"
        
        result = test_function("test prompt")
        
        self.assertEqual(result, "AI response to: test prompt")
        self.mock_client.record_token_based_pay.assert_called_once()
    
    def test_meter_instant_pay_decorator(self):
        """Test instant pay decorator"""
        def condition_func(*args, **kwargs):
            return kwargs.get('premium', False)
        
        @meter_instant_pay(
            self.mock_client,
            amount=2.99,
            description="Premium Feature",
            condition_func=condition_func
        )
        def test_function(data, premium=False):
            if premium:
                return f"premium: {data}"
            return f"basic: {data}"
        
        # Test without premium (no charge)
        result1 = test_function("data", premium=False)
        self.assertEqual(result1, "basic: data")
        self.mock_client.record_instant_pay.assert_not_called()
        
        # Test with premium (should charge)
        result2 = test_function("data", premium=True)
        self.assertEqual(result2, "premium: data")
        self.mock_client.record_instant_pay.assert_called_once()
    
    def test_meter_function_decorator(self):
        """Test generic function decorator"""
        @meter_function(
            self.mock_client,
            payment_type=PaymentType.API_REQUEST_PAY,
            unit_price=0.15
        )
        def test_function(x, y):
            return x + y
        
        result = test_function(2, 3)
        
        self.assertEqual(result, 5)
        self.mock_client.record_api_request_pay.assert_called_once()
    
    def test_meter_agent_decorator(self):
        """Test agent class decorator"""
        @meter_agent(
            client=self.mock_client,
            payment_type=PaymentType.API_REQUEST_PAY,
            unit_price=0.20,
            methods_to_meter=['process']
        )
        class TestAgent:
            def process(self, data):
                return f"processed: {data}"
            
            def free_method(self, data):
                return f"free: {data}"
        
        agent = TestAgent()
        
        # Metered method
        result1 = agent.process("test")
        self.assertEqual(result1, "processed: test")
        self.mock_client.record_api_request_pay.assert_called_once()
        
        # Non-metered method
        result2 = agent.free_method("test")
        self.assertEqual(result2, "free: test")
        # Should still be called only once
        self.assertEqual(self.mock_client.record_api_request_pay.call_count, 1)


class TestContextManagers(unittest.TestCase):
    """Test context manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_client.record_api_request_pay.return_value = Mock(total_cost=0.10)
        self.mock_client.record_token_based_pay.return_value = Mock(total_cost=0.05)
        self.mock_client.record_instant_pay.return_value = Mock(total_cost=2.99)
    
    def test_track_api_request_pay(self):
        """Test API request pay context manager"""
        with track_api_request_pay(
            self.mock_client, "proj", "agent",
            user_id="user", unit_price=0.10
        ) as usage:
            usage["api_calls"] = 3
            usage["metadata"] = {"test": "data"}
        
        self.mock_client.record_api_request_pay.assert_called_once()
        call_args = self.mock_client.record_api_request_pay.call_args[1]
        self.assertEqual(call_args['api_calls'], 3)
        self.assertEqual(call_args['metadata'], {"test": "data"})
    
    def test_track_token_based_pay(self):
        """Test token-based pay context manager"""
        with track_token_based_pay(
            self.mock_client, "proj", "agent",
            user_id="user",
            input_token_price=0.00001,
            output_token_price=0.00002
        ) as usage:
            usage["tokens_in"] = 1000
            usage["tokens_out"] = 500
        
        self.mock_client.record_token_based_pay.assert_called_once()
        call_args = self.mock_client.record_token_based_pay.call_args[1]
        self.assertEqual(call_args['tokens_in'], 1000)
        self.assertEqual(call_args['tokens_out'], 500)
    
    def test_track_instant_pay(self):
        """Test instant pay context manager"""
        with track_instant_pay(
            self.mock_client, "proj", "agent",
            user_id="user", amount=4.99,
            description="Premium Feature"
        ) as usage:
            usage["metadata"] = {"feature": "export"}
        
        self.mock_client.record_instant_pay.assert_called_once()
        call_args = self.mock_client.record_instant_pay.call_args[1]
        self.assertEqual(call_args['amount'], 4.99)
        self.assertEqual(call_args['description'], "Premium Feature")


class TestQuickHelpers(unittest.TestCase):
    """Test quick helper functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_client.record_api_request_pay.return_value = Mock(total_cost=0.10)
        self.mock_client.record_token_based_pay.return_value = Mock(total_cost=0.05)
        self.mock_client.record_instant_pay.return_value = Mock(total_cost=2.99)
    
    def test_quick_api_request_pay(self):
        """Test quick API request pay helper"""
        response = quick_api_request_pay(
            self.mock_client, "proj", "agent",
            user_id="user", api_calls=2, unit_price=0.15
        )
        
        self.assertEqual(response.total_cost, 0.10)
        self.mock_client.record_api_request_pay.assert_called_once()
    
    def test_quick_token_based_pay(self):
        """Test quick token-based pay helper"""
        response = quick_token_based_pay(
            self.mock_client, "proj", "agent",
            user_id="user",
            tokens_in=1000, tokens_out=500,
            input_token_price=0.00001,
            output_token_price=0.00002
        )
        
        self.assertEqual(response.total_cost, 0.05)
        self.mock_client.record_token_based_pay.assert_called_once()
    
    def test_quick_instant_pay(self):
        """Test quick instant pay helper"""
        response = quick_instant_pay(
            self.mock_client, "proj", "agent",
            user_id="user", amount=2.99,
            description="Premium Feature"
        )
        
        self.assertEqual(response.total_cost, 2.99)
        self.mock_client.record_instant_pay.assert_called_once()


class TestModels(unittest.TestCase):
    """Test data models"""
    
    def test_api_request_pay_event(self):
        """Test API request pay event model"""
        event = APIRequestPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            api_calls=2,
            unit_price=0.25,
            total_cost=0.50,
            timestamp=datetime.now(),
            metadata={"test": "data"}
        )
        
        self.assertEqual(event.id, "evt_123")
        self.assertEqual(event.api_calls, 2)
        self.assertEqual(event.total_cost, 0.50)
    
    def test_token_based_pay_event(self):
        """Test token-based pay event model"""
        event = TokenBasedPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            tokens_in=1000,
            tokens_out=500,
            input_token_price=0.00001,
            output_token_price=0.00002,
            total_cost=0.02,
            timestamp=datetime.now()
        )
        
        self.assertEqual(event.tokens_in, 1000)
        self.assertEqual(event.tokens_out, 500)
        self.assertEqual(event.total_cost, 0.02)
    
    def test_instant_pay_event(self):
        """Test instant pay event model"""
        event = InstantPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            amount=4.99,
            description="Premium Feature",
            total_cost=4.99,
            timestamp=datetime.now()
        )
        
        self.assertEqual(event.amount, 4.99)
        self.assertEqual(event.description, "Premium Feature")
        self.assertEqual(event.total_cost, 4.99)
    
    def test_user_meter(self):
        """Test user meter model"""
        meter = UserMeter(
            project_id="proj_123",
            user_id="user_123",
            threshold_amount=100.0,
            current_usage=25.50,
            last_reset_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.assertEqual(meter.threshold_amount, 100.0)
        self.assertEqual(meter.current_usage, 25.50)
        self.assertEqual(meter.remaining_budget, 74.50)
        self.assertEqual(meter.usage_percentage, 25.5)
    
    def test_meter_stats(self):
        """Test meter statistics model"""
        stats = MeterStats(
            total_api_calls=1000,
            total_tokens_in=50000,
            total_tokens_out=25000,
            total_cost=100.50,
            timeframe="30 days"
        )
        
        self.assertEqual(stats.total_api_calls, 1000)
        self.assertEqual(stats.total_tokens, 75000)
        self.assertEqual(stats.total_cost, 100.50)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = AgentMeterClient(
            api_key="test_key",
            project_id="test_project"
        )
    
    def test_rate_limit_error(self):
        """Test rate limit error creation"""
        error = RateLimitError("Rate limit exceeded", retry_after=60)
        
        self.assertEqual(str(error), "Rate limit exceeded")
        self.assertEqual(error.retry_after, 60)
    
    def test_agent_meter_error(self):
        """Test AgentMeter error creation"""
        error = AgentMeterError("Invalid request", error_code="invalid_request")
        
        self.assertEqual(str(error), "Invalid request")
        self.assertEqual(error.error_code, "invalid_request")
    
    def test_validation_errors(self):
        """Test input validation"""
        with patch('agentmeter.client.requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = {
                "error": {"code": "validation_error", "message": "Invalid input"}
            }
            
            with self.assertRaises(AgentMeterError):
                # Test negative values
                self.client.record_api_request_pay(
                    api_calls=-1,
                    unit_price=0.10,
                    user_id="test_user"
                )


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        
        # Set up different response types
        self.mock_client.record_api_request_pay.return_value = Mock(total_cost=0.10)
        self.mock_client.record_token_based_pay.return_value = Mock(total_cost=0.05)
        self.mock_client.record_instant_pay.return_value = Mock(total_cost=2.99)
        
        self.mock_client.set_user_meter.return_value = Mock(
            threshold_amount=100.0,
            current_usage=0.0
        )
        self.mock_client.get_user_meter.return_value = Mock(
            threshold_amount=100.0,
            current_usage=25.50
        )
    
    def test_e_commerce_workflow(self):
        """Test e-commerce integration workflow"""
        # Set user subscription
        self.mock_client.set_user_meter(threshold_amount=50.0, user_id="user_123")
        
        # Product search (API request pay)
        @meter_api_request_pay(self.mock_client, unit_price=0.05)
        def search_products(query):
            return ["product1", "product2", "product3"]
        
        products = search_products("laptop")
        self.assertEqual(len(products), 3)
        
        # AI recommendations (token-based pay)
        def extract_tokens(*args, **kwargs):
            return 200, 100
        
        @meter_token_based_pay(
            self.mock_client,
            input_token_price=0.00001,
            output_token_price=0.00002,
            tokens_extractor=extract_tokens
        )
        def generate_recommendations(user_data):
            return ["rec1", "rec2", "rec3"]
        
        recommendations = generate_recommendations({"history": ["laptop"]})
        self.assertEqual(len(recommendations), 3)
        
        # Premium checkout (instant pay)
        @meter_instant_pay(
            self.mock_client,
            amount=1.99,
            description="Priority Checkout",
            condition_func=lambda *args, **kwargs: kwargs.get('priority', False)
        )
        def checkout(items, priority=False):
            return {"order_id": "ord_123", "priority": priority}
        
        order = checkout(["laptop"], priority=True)
        self.assertTrue(order["priority"])
        
        # Verify all meters were called
        self.mock_client.record_api_request_pay.assert_called()
        self.mock_client.record_token_based_pay.assert_called()
        self.mock_client.record_instant_pay.assert_called()
    
    def test_ai_agent_workflow(self):
        """Test AI agent integration workflow"""
        # Create metered agent
        @meter_agent(
            client=self.mock_client,
            payment_type=PaymentType.TOKEN_BASED_PAY,
            input_token_price=0.000015,
            output_token_price=0.000025,
            methods_to_meter=['process_query', 'generate_response']
        )
        class AIAgent:
            def process_query(self, query):
                return f"processed: {query}"
            
            def generate_response(self, processed_query):
                return f"response to: {processed_query}"
            
            def internal_method(self, data):
                return f"internal: {data}"
        
        agent = AIAgent()
        
        # Test metered methods
        processed = agent.process_query("test query")
        response = agent.generate_response(processed)
        
        # Test non-metered method
        internal = agent.internal_method("data")
        
        self.assertEqual(processed, "processed: test query")
        self.assertEqual(response, "response to: processed: test query")
        self.assertEqual(internal, "internal: data")
        
        # Should be called twice (for two metered methods)
        self.assertEqual(self.mock_client.record_token_based_pay.call_count, 2)
    
    def test_batch_processing_workflow(self):
        """Test batch processing workflow"""
        # Process multiple items with context manager
        with track_api_request_pay(
            self.mock_client, "proj", "agent",
            user_id="batch_user", unit_price=0.02  # Batch discount
        ) as usage:
            items = ["item1", "item2", "item3", "item4", "item5"]
            processed_items = []
            
            for item in items:
                # Simulate processing
                time.sleep(0.01)
                processed_items.append(f"processed_{item}")
            
            # Set batch usage
            usage["api_calls"] = len(items)
            usage["metadata"] = {
                "batch_size": len(items),
                "processing_type": "batch"
            }
        
        self.assertEqual(len(processed_items), 5)
        self.mock_client.record_api_request_pay.assert_called_once()
        
        # Verify batch parameters
        call_args = self.mock_client.record_api_request_pay.call_args[1]
        self.assertEqual(call_args['api_calls'], 5)
        self.assertEqual(call_args['unit_price'], 0.02)


if __name__ == '__main__':
    unittest.main()