"""
Unit Tests for AgentMeter SDK Models
Tests all data models, validation, and serialization.
"""

import unittest
from datetime import datetime
from agentmeter.models import (
    PaymentType, APIRequestPayEvent, TokenBasedPayEvent, InstantPayEvent,
    UserMeter, BillingRecord, MeterStats, Project, AgentMeterConfig
)


class TestPaymentType(unittest.TestCase):
    """Test PaymentType enum"""
    
    def test_payment_type_values(self):
        """Test payment type enum values"""
        self.assertEqual(PaymentType.API_REQUEST_PAY.value, "api_request_pay")
        self.assertEqual(PaymentType.TOKEN_BASED_PAY.value, "token_based_pay")
        self.assertEqual(PaymentType.INSTANT_PAY.value, "instant_pay")
    
    def test_payment_type_from_string(self):
        """Test creating payment type from string"""
        self.assertEqual(PaymentType("api_request_pay"), PaymentType.API_REQUEST_PAY)
        self.assertEqual(PaymentType("token_based_pay"), PaymentType.TOKEN_BASED_PAY)
        self.assertEqual(PaymentType("instant_pay"), PaymentType.INSTANT_PAY)


class TestAPIRequestPayEvent(unittest.TestCase):
    """Test APIRequestPayEvent model"""
    
    def test_create_event(self):
        """Test creating API request pay event"""
        event = APIRequestPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            api_calls=3,
            unit_price=0.25,
            total_cost=0.75,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            metadata={"source": "api"}
        )
        
        self.assertEqual(event.id, "evt_123")
        self.assertEqual(event.project_id, "proj_123")
        self.assertEqual(event.agent_id, "agent_123")
        self.assertEqual(event.user_id, "user_123")
        self.assertEqual(event.api_calls, 3)
        self.assertEqual(event.unit_price, 0.25)
        self.assertEqual(event.total_cost, 0.75)
        self.assertEqual(event.payment_type, PaymentType.API_REQUEST_PAY)
        self.assertEqual(event.metadata, {"source": "api"})
    
    def test_calculate_cost(self):
        """Test cost calculation"""
        event = APIRequestPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            api_calls=5,
            unit_price=0.10,
            total_cost=0.0,  # Will be calculated
            timestamp=datetime.now()
        )
        
        # Manually calculate cost
        expected_cost = 5 * 0.10
        self.assertEqual(event.api_calls * event.unit_price, expected_cost)
    
    def test_from_dict(self):
        """Test creating event from dictionary"""
        data = {
            "id": "evt_123",
            "project_id": "proj_123",
            "agent_id": "agent_123",
            "user_id": "user_123",
            "api_calls": 2,
            "unit_price": 0.15,
            "total_cost": 0.30,
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {"test": "data"}
        }
        
        event = APIRequestPayEvent.from_dict(data)
        
        self.assertEqual(event.id, "evt_123")
        self.assertEqual(event.api_calls, 2)
        self.assertEqual(event.unit_price, 0.15)
        self.assertEqual(event.total_cost, 0.30)
    
    def test_to_dict(self):
        """Test converting event to dictionary"""
        event = APIRequestPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            api_calls=1,
            unit_price=0.20,
            total_cost=0.20,
            timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )
        
        data = event.to_dict()
        
        self.assertEqual(data["id"], "evt_123")
        self.assertEqual(data["api_calls"], 1)
        self.assertEqual(data["unit_price"], 0.20)
        self.assertEqual(data["total_cost"], 0.20)
        self.assertEqual(data["payment_type"], "api_request_pay")


class TestTokenBasedPayEvent(unittest.TestCase):
    """Test TokenBasedPayEvent model"""
    
    def test_create_event(self):
        """Test creating token-based pay event"""
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
        self.assertEqual(event.input_token_price, 0.00001)
        self.assertEqual(event.output_token_price, 0.00002)
        self.assertEqual(event.total_cost, 0.02)
        self.assertEqual(event.payment_type, PaymentType.TOKEN_BASED_PAY)
    
    def test_calculate_cost(self):
        """Test token cost calculation"""
        event = TokenBasedPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            tokens_in=2000,
            tokens_out=1000,
            input_token_price=0.000015,
            output_token_price=0.000025,
            total_cost=0.0,
            timestamp=datetime.now()
        )
        
        # Calculate expected cost
        input_cost = 2000 * 0.000015
        output_cost = 1000 * 0.000025
        expected_total = input_cost + output_cost
        
        calculated_cost = (event.tokens_in * event.input_token_price) + \
                         (event.tokens_out * event.output_token_price)
        
        self.assertAlmostEqual(calculated_cost, expected_total, places=6)
    
    def test_total_tokens_property(self):
        """Test total tokens property"""
        event = TokenBasedPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            tokens_in=750,
            tokens_out=250,
            input_token_price=0.00001,
            output_token_price=0.00002,
            total_cost=0.0125,
            timestamp=datetime.now()
        )
        
        self.assertEqual(event.total_tokens, 1000)


class TestInstantPayEvent(unittest.TestCase):
    """Test InstantPayEvent model"""
    
    def test_create_event(self):
        """Test creating instant pay event"""
        event = InstantPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            amount=4.99,
            description="Premium Feature Access",
            total_cost=4.99,
            timestamp=datetime.now(),
            metadata={"feature": "analytics"}
        )
        
        self.assertEqual(event.amount, 4.99)
        self.assertEqual(event.description, "Premium Feature Access")
        self.assertEqual(event.total_cost, 4.99)
        self.assertEqual(event.payment_type, PaymentType.INSTANT_PAY)
        self.assertEqual(event.metadata["feature"], "analytics")
    
    def test_amount_equals_total_cost(self):
        """Test that amount equals total cost for instant pay"""
        event = InstantPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            amount=9.99,
            description="Premium Subscription",
            total_cost=9.99,
            timestamp=datetime.now()
        )
        
        self.assertEqual(event.amount, event.total_cost)


class TestUserMeter(unittest.TestCase):
    """Test UserMeter model"""
    
    def test_create_user_meter(self):
        """Test creating user meter"""
        meter = UserMeter(
            project_id="proj_123",
            user_id="user_123",
            threshold_amount=100.0,
            current_usage=25.50,
            last_reset_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 15, 12, 0, 0)
        )
        
        self.assertEqual(meter.project_id, "proj_123")
        self.assertEqual(meter.user_id, "user_123")
        self.assertEqual(meter.threshold_amount, 100.0)
        self.assertEqual(meter.current_usage, 25.50)
    
    def test_remaining_budget_property(self):
        """Test remaining budget calculation"""
        meter = UserMeter(
            project_id="proj_123",
            user_id="user_123",
            threshold_amount=50.0,
            current_usage=15.75,
            last_reset_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        expected_remaining = 50.0 - 15.75
        self.assertEqual(meter.remaining_budget, expected_remaining)
    
    def test_usage_percentage_property(self):
        """Test usage percentage calculation"""
        meter = UserMeter(
            project_id="proj_123",
            user_id="user_123",
            threshold_amount=200.0,
            current_usage=50.0,
            last_reset_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        expected_percentage = (50.0 / 200.0) * 100
        self.assertEqual(meter.usage_percentage, expected_percentage)
    
    def test_is_over_limit_property(self):
        """Test over limit detection"""
        # Under limit
        meter_under = UserMeter(
            project_id="proj_123",
            user_id="user_123",
            threshold_amount=100.0,
            current_usage=75.0,
            last_reset_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.assertFalse(meter_under.is_over_limit)
        
        # Over limit
        meter_over = UserMeter(
            project_id="proj_123",
            user_id="user_123",
            threshold_amount=100.0,
            current_usage=125.0,
            last_reset_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.assertTrue(meter_over.is_over_limit)
    
    def test_zero_threshold_edge_case(self):
        """Test edge case with zero threshold"""
        meter = UserMeter(
            project_id="proj_123",
            user_id="user_123",
            threshold_amount=0.0,
            current_usage=5.0,
            last_reset_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.assertEqual(meter.remaining_budget, -5.0)
        self.assertTrue(meter.is_over_limit)
        # Usage percentage should handle division by zero
        self.assertEqual(meter.usage_percentage, 0.0)


class TestMeterStats(unittest.TestCase):
    """Test MeterStats model"""
    
    def test_create_stats(self):
        """Test creating meter statistics"""
        stats = MeterStats(
            total_api_calls=1500,
            total_tokens_in=75000,
            total_tokens_out=25000,
            total_cost=150.75,
            timeframe="30 days"
        )
        
        self.assertEqual(stats.total_api_calls, 1500)
        self.assertEqual(stats.total_tokens_in, 75000)
        self.assertEqual(stats.total_tokens_out, 25000)
        self.assertEqual(stats.total_cost, 150.75)
        self.assertEqual(stats.timeframe, "30 days")
    
    def test_total_tokens_property(self):
        """Test total tokens calculation"""
        stats = MeterStats(
            total_api_calls=100,
            total_tokens_in=30000,
            total_tokens_out=15000,
            total_cost=50.0,
            timeframe="7 days"
        )
        
        self.assertEqual(stats.total_tokens, 45000)
    
    def test_average_cost_per_call_property(self):
        """Test average cost per call calculation"""
        stats = MeterStats(
            total_api_calls=200,
            total_tokens_in=10000,
            total_tokens_out=5000,
            total_cost=40.0,
            timeframe="1 day"
        )
        
        expected_avg = 40.0 / 200
        self.assertEqual(stats.average_cost_per_call, expected_avg)
    
    def test_zero_api_calls_edge_case(self):
        """Test edge case with zero API calls"""
        stats = MeterStats(
            total_api_calls=0,
            total_tokens_in=1000,
            total_tokens_out=500,
            total_cost=5.0,
            timeframe="1 hour"
        )
        
        # Should handle division by zero gracefully
        self.assertEqual(stats.average_cost_per_call, 0.0)


class TestProject(unittest.TestCase):
    """Test Project model"""
    
    def test_create_project(self):
        """Test creating project"""
        project = Project(
            id="proj_123",
            name="Test Project",
            description="A test project for AgentMeter",
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 15, 12, 0, 0)
        )
        
        self.assertEqual(project.id, "proj_123")
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.description, "A test project for AgentMeter")
    
    def test_project_without_description(self):
        """Test creating project without description"""
        project = Project(
            id="proj_456",
            name="Simple Project",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.assertEqual(project.name, "Simple Project")
        self.assertIsNone(project.description)


class TestBillingRecord(unittest.TestCase):
    """Test BillingRecord model"""
    
    def test_create_billing_record(self):
        """Test creating billing record"""
        record = BillingRecord(
            id="bill_123",
            project_id="proj_123",
            period_start=datetime(2024, 1, 1, 0, 0, 0),
            period_end=datetime(2024, 1, 31, 23, 59, 59),
            amount=125.50,
            status="paid",
            created_at=datetime(2024, 2, 1, 0, 0, 0),
            updated_at=datetime(2024, 2, 1, 12, 0, 0)
        )
        
        self.assertEqual(record.id, "bill_123")
        self.assertEqual(record.project_id, "proj_123")
        self.assertEqual(record.amount, 125.50)
        self.assertEqual(record.status, "paid")
    
    def test_billing_period_calculation(self):
        """Test billing period calculation"""
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 31, 23, 59, 59)
        
        record = BillingRecord(
            id="bill_123",
            project_id="proj_123",
            period_start=start_date,
            period_end=end_date,
            amount=100.0,
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        period_duration = record.period_end - record.period_start
        self.assertEqual(period_duration.days, 30)  # January has 31 days, but we're calculating the difference


class TestAgentMeterConfig(unittest.TestCase):
    """Test AgentMeterConfig model"""
    
    def test_create_config(self):
        """Test creating configuration"""
        config = AgentMeterConfig(
            api_key="test_key_123",
            project_id="proj_123",
            agent_id="agent_456",
            user_id="user_789",
            base_url="https://api.agentmeter.com",
            timeout=30,
            retry_attempts=3,
            batch_size=100
        )
        
        self.assertEqual(config.api_key, "test_key_123")
        self.assertEqual(config.project_id, "proj_123")
        self.assertEqual(config.agent_id, "agent_456")
        self.assertEqual(config.user_id, "user_789")
        self.assertEqual(config.base_url, "https://api.agentmeter.com")
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.retry_attempts, 3)
        self.assertEqual(config.batch_size, 100)
    
    def test_config_defaults(self):
        """Test configuration defaults"""
        config = AgentMeterConfig(
            api_key="test_key",
            project_id="test_project"
        )
        
        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.project_id, "test_project")
        self.assertIsNone(config.agent_id)
        self.assertIsNone(config.user_id)
        self.assertEqual(config.base_url, "https://api.staging.agentmeter.money")
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.retry_attempts, 3)
        self.assertEqual(config.batch_size, 50)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test invalid timeout
        with self.assertRaises(ValueError):
            AgentMeterConfig(
                api_key="test_key",
                project_id="test_project",
                timeout=-1
            )
        
        # Test invalid retry attempts
        with self.assertRaises(ValueError):
            AgentMeterConfig(
                api_key="test_key",
                project_id="test_project",
                retry_attempts=-1
            )
        
        # Test invalid batch size
        with self.assertRaises(ValueError):
            AgentMeterConfig(
                api_key="test_key",
                project_id="test_project",
                batch_size=0
            )


class TestModelSerialization(unittest.TestCase):
    """Test model serialization and deserialization"""
    
    def test_api_request_event_serialization(self):
        """Test API request event serialization"""
        original_event = APIRequestPayEvent(
            id="evt_123",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            api_calls=2,
            unit_price=0.25,
            total_cost=0.50,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            metadata={"source": "test"}
        )
        
        # Serialize to dict
        event_dict = original_event.to_dict()
        
        # Deserialize from dict
        reconstructed_event = APIRequestPayEvent.from_dict(event_dict)
        
        self.assertEqual(original_event.id, reconstructed_event.id)
        self.assertEqual(original_event.api_calls, reconstructed_event.api_calls)
        self.assertEqual(original_event.unit_price, reconstructed_event.unit_price)
        self.assertEqual(original_event.total_cost, reconstructed_event.total_cost)
        self.assertEqual(original_event.metadata, reconstructed_event.metadata)
    
    def test_user_meter_serialization(self):
        """Test user meter serialization"""
        original_meter = UserMeter(
            project_id="proj_123",
            user_id="user_123",
            threshold_amount=100.0,
            current_usage=35.75,
            last_reset_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 15, 12, 0, 0)
        )
        
        # Serialize to dict
        meter_dict = original_meter.to_dict()
        
        # Deserialize from dict
        reconstructed_meter = UserMeter.from_dict(meter_dict)
        
        self.assertEqual(original_meter.project_id, reconstructed_meter.project_id)
        self.assertEqual(original_meter.user_id, reconstructed_meter.user_id)
        self.assertEqual(original_meter.threshold_amount, reconstructed_meter.threshold_amount)
        self.assertEqual(original_meter.current_usage, reconstructed_meter.current_usage)


if __name__ == '__main__':
    unittest.main() 