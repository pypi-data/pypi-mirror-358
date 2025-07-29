"""
Unit Tests for AgentMeter SDK Tracker
Tests the tracker module including context managers and usage tracking.
"""

import unittest
from unittest.mock import Mock, patch
import time
import threading
from agentmeter.tracker import (
    UsageContext, AgentMeterTracker,
    track_api_request_pay, track_token_based_pay, track_instant_pay
)
from agentmeter.models import PaymentType


class TestUsageContext(unittest.TestCase):
    """Test UsageContext functionality"""
    
    def test_create_usage_context(self):
        """Test creating usage context"""
        context = UsageContext(
            client=Mock(),
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.API_REQUEST_PAY
        )
        
        self.assertEqual(context.project_id, "proj_123")
        self.assertEqual(context.agent_id, "agent_123")
        self.assertEqual(context.user_id, "user_123")
        self.assertEqual(context.payment_type, PaymentType.API_REQUEST_PAY)
        self.assertIsInstance(context.data, dict)
    
    def test_context_data_manipulation(self):
        """Test manipulating context data"""
        context = UsageContext(
            client=Mock(),
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.API_REQUEST_PAY
        )
        
        # Test setting data
        context["api_calls"] = 5
        context["metadata"] = {"source": "test"}
        
        self.assertEqual(context["api_calls"], 5)
        self.assertEqual(context["metadata"]["source"], "test")
        
        # Test getting data with default
        self.assertEqual(context.get("api_calls"), 5)
        self.assertEqual(context.get("nonexistent", "default"), "default")
    
    def test_context_enter_exit(self):
        """Test context manager protocol"""
        mock_client = Mock()
        mock_client.record_api_request_pay.return_value = Mock()
        
        context = UsageContext(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.API_REQUEST_PAY,
            unit_price=0.10
        )
        
        # Test enter
        with context as usage:
            usage["api_calls"] = 3
            usage["metadata"] = {"test": "data"}
        
        # Verify client was called on exit
        mock_client.record_api_request_pay.assert_called_once_with(
            api_calls=3,
            unit_price=0.10,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            metadata={"test": "data"}
        )
    
    def test_context_token_based_pay(self):
        """Test token-based pay context"""
        mock_client = Mock()
        mock_client.record_token_based_pay.return_value = Mock()
        
        context = UsageContext(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.TOKEN_BASED_PAY,
            input_token_price=0.00001,
            output_token_price=0.00002
        )
        
        with context as usage:
            usage["tokens_in"] = 1000
            usage["tokens_out"] = 500
        
        mock_client.record_token_based_pay.assert_called_once_with(
            tokens_in=1000,
            tokens_out=500,
            input_token_price=0.00001,
            output_token_price=0.00002,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            metadata={}
        )
    
    def test_context_instant_pay(self):
        """Test instant pay context"""
        mock_client = Mock()
        mock_client.record_instant_pay.return_value = Mock()
        
        context = UsageContext(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.INSTANT_PAY,
            amount=4.99,
            description="Premium Feature"
        )
        
        with context as usage:
            usage["metadata"] = {"feature": "analytics"}
        
        mock_client.record_instant_pay.assert_called_once_with(
            amount=4.99,
            description="Premium Feature",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            metadata={"feature": "analytics"}
        )
    
    def test_context_error_handling(self):
        """Test context error handling"""
        mock_client = Mock()
        mock_client.record_api_request_pay.side_effect = Exception("API Error")
        
        context = UsageContext(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.API_REQUEST_PAY,
            unit_price=0.10
        )
        
        # Should not raise exception on exit even if recording fails
        with context as usage:
            usage["api_calls"] = 1
        
        # Client should have been called despite the error
        mock_client.record_api_request_pay.assert_called_once()


class TestAgentMeterTracker(unittest.TestCase):
    """Test AgentMeterTracker functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.tracker = AgentMeterTracker(
            client=self.mock_client,
            project_id="proj_123",
            agent_id="agent_123"
        )
    
    def test_tracker_initialization(self):
        """Test tracker initialization"""
        self.assertEqual(self.tracker.client, self.mock_client)
        self.assertEqual(self.tracker.project_id, "proj_123")
        self.assertEqual(self.tracker.agent_id, "agent_123")
        self.assertIsInstance(self.tracker._contexts, dict)
        self.assertIsNotNone(self.tracker._lock)
    
    def test_track_api_request_pay(self):
        """Test API request pay tracking"""
        mock_client = Mock()
        mock_client.record_api_request_pay.return_value = Mock()
        
        tracker = AgentMeterTracker(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123"
        )
        
        context = tracker.track_api_request_pay(
            user_id="user_123",
            unit_price=0.15
        )
        
        self.assertIsInstance(context, UsageContext)
        self.assertEqual(context.payment_type, PaymentType.API_REQUEST_PAY)
        self.assertEqual(context.user_id, "user_123")
    
    def test_track_token_based_pay(self):
        """Test token-based pay tracking"""
        context = self.tracker.track_token_based_pay(
            user_id="user_123",
            input_token_price=0.00001,
            output_token_price=0.00002
        )
        
        self.assertIsInstance(context, UsageContext)
        self.assertEqual(context.payment_type, PaymentType.TOKEN_BASED_PAY)
        self.assertEqual(context.user_id, "user_123")
    
    def test_track_instant_pay(self):
        """Test instant pay tracking"""
        context = self.tracker.track_instant_pay(
            user_id="user_123",
            amount=2.99,
            description="Premium Feature"
        )
        
        self.assertIsInstance(context, UsageContext)
        self.assertEqual(context.payment_type, PaymentType.INSTANT_PAY)
        self.assertEqual(context.user_id, "user_123")
    
    def test_context_storage(self):
        """Test context storage and retrieval"""
        context1 = self.tracker.track_api_request_pay(
            user_id="user_1",
            unit_price=0.10
        )
        
        context2 = self.tracker.track_token_based_pay(
            user_id="user_2",
            input_token_price=0.00001,
            output_token_price=0.00002
        )
        
        # Contexts should be stored
        self.assertIn(context1.context_id, self.tracker._contexts)
        self.assertIn(context2.context_id, self.tracker._contexts)
        
        # Contexts should be different
        self.assertNotEqual(context1.context_id, context2.context_id)
    
    def test_context_cleanup(self):
        """Test context cleanup after use"""
        mock_client = Mock()
        mock_client.record_api_request_pay.return_value = Mock()
        
        tracker = AgentMeterTracker(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123"
        )
        
        context = tracker.track_api_request_pay(
            user_id="user_123",
            unit_price=0.10
        )
        
        context_id = context.context_id
        
        # Context should be stored initially
        self.assertIn(context_id, tracker._contexts)
        
        # Use context
        with context as usage:
            usage["api_calls"] = 1
        
        # Context should be cleaned up after use
        self.assertNotIn(context_id, tracker._contexts)
    
    def test_concurrent_contexts(self):
        """Test handling concurrent contexts"""
        mock_client = Mock()
        mock_client.record_api_request_pay.return_value = Mock()
        
        tracker = AgentMeterTracker(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123"
        )
        
        contexts = []
        
        def create_context(user_id):
            context = tracker.track_api_request_pay(
                user_id=f"user_{user_id}",
                unit_price=0.10
            )
            contexts.append(context)
            with context as usage:
                usage["api_calls"] = 1
                time.sleep(0.1)  # Simulate work
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_context, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All contexts should have been processed
        self.assertEqual(len(contexts), 5)
        self.assertEqual(mock_client.record_api_request_pay.call_count, 5)
        
        # All contexts should be cleaned up
        self.assertEqual(len(tracker._contexts), 0)


class TestContextManagerFunctions(unittest.TestCase):
    """Test context manager functions"""
    
    def test_track_api_request_pay_function(self):
        """Test track_api_request_pay function"""
        mock_client = Mock()
        mock_client.record_api_request_pay.return_value = Mock()
        
        with track_api_request_pay(
            mock_client, "proj_123", "agent_123",
            user_id="user_123", unit_price=0.20
        ) as usage:
            usage["api_calls"] = 2
            usage["metadata"] = {"source": "function_test"}
        
        mock_client.record_api_request_pay.assert_called_once_with(
            api_calls=2,
            unit_price=0.20,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            metadata={"source": "function_test"}
        )
    
    def test_track_token_based_pay_function(self):
        """Test track_token_based_pay function"""
        mock_client = Mock()
        mock_client.record_token_based_pay.return_value = Mock()
        
        with track_token_based_pay(
            mock_client, "proj_123", "agent_123",
            user_id="user_123",
            input_token_price=0.000015,
            output_token_price=0.000025
        ) as usage:
            usage["tokens_in"] = 800
            usage["tokens_out"] = 400
        
        mock_client.record_token_based_pay.assert_called_once_with(
            tokens_in=800,
            tokens_out=400,
            input_token_price=0.000015,
            output_token_price=0.000025,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            metadata={}
        )
    
    def test_track_instant_pay_function(self):
        """Test track_instant_pay function"""
        mock_client = Mock()
        mock_client.record_instant_pay.return_value = Mock()
        
        with track_instant_pay(
            mock_client, "proj_123", "agent_123",
            user_id="user_123", amount=1.99,
            description="Function Test Feature"
        ) as usage:
            usage["metadata"] = {"test": "function"}
        
        mock_client.record_instant_pay.assert_called_once_with(
            amount=1.99,
            description="Function Test Feature",
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            metadata={"test": "function"}
        )


class TestTrackerEdgeCases(unittest.TestCase):
    """Test tracker edge cases and error scenarios"""
    
    def test_context_without_client_call(self):
        """Test context that doesn't make client call"""
        mock_client = Mock()
        
        context = UsageContext(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.API_REQUEST_PAY,
            unit_price=0.10
        )
        
        # Use context but don't set required data
        with context as usage:
            usage["metadata"] = {"test": "no_calls"}
            # Don't set api_calls
        
        # Client should still be called with default values
        mock_client.record_api_request_pay.assert_called_once()
    
    def test_context_with_exception(self):
        """Test context behavior when exception occurs"""
        mock_client = Mock()
        mock_client.record_api_request_pay.return_value = Mock()
        
        context = UsageContext(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.API_REQUEST_PAY,
            unit_price=0.10
        )
        
        try:
            with context as usage:
                usage["api_calls"] = 1
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected
        
        # Client should still be called even when exception occurs
        mock_client.record_api_request_pay.assert_called_once()
    
    def test_tracker_thread_safety(self):
        """Test tracker thread safety"""
        mock_client = Mock()
        mock_client.record_api_request_pay.return_value = Mock()
        
        tracker = AgentMeterTracker(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123"
        )
        
        results = []
        
        def worker(worker_id):
            try:
                context = tracker.track_api_request_pay(
                    user_id=f"user_{worker_id}",
                    unit_price=0.10
                )
                with context as usage:
                    usage["api_calls"] = worker_id
                    time.sleep(0.01)  # Small delay
                results.append(worker_id)
            except Exception as e:
                results.append(f"error_{worker_id}: {e}")
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All workers should have completed successfully
        self.assertEqual(len(results), 10)
        self.assertEqual(mock_client.record_api_request_pay.call_count, 10)
        
        # No errors should have occurred
        error_results = [r for r in results if str(r).startswith("error_")]
        self.assertEqual(len(error_results), 0)
    
    def test_context_data_types(self):
        """Test context with different data types"""
        mock_client = Mock()
        mock_client.record_api_request_pay.return_value = Mock()
        
        context = UsageContext(
            client=mock_client,
            project_id="proj_123",
            agent_id="agent_123",
            user_id="user_123",
            payment_type=PaymentType.API_REQUEST_PAY,
            unit_price=0.10
        )
        
        with context as usage:
            usage["api_calls"] = 5
            usage["metadata"] = {
                "string_value": "test",
                "int_value": 42,
                "float_value": 3.14,
                "bool_value": True,
                "list_value": [1, 2, 3],
                "dict_value": {"nested": "data"}
            }
        
        # Should handle all data types properly
        call_args = mock_client.record_api_request_pay.call_args[1]
        metadata = call_args["metadata"]
        
        self.assertEqual(metadata["string_value"], "test")
        self.assertEqual(metadata["int_value"], 42)
        self.assertEqual(metadata["float_value"], 3.14)
        self.assertEqual(metadata["bool_value"], True)
        self.assertEqual(metadata["list_value"], [1, 2, 3])
        self.assertEqual(metadata["dict_value"], {"nested": "data"})


if __name__ == '__main__':
    unittest.main() 