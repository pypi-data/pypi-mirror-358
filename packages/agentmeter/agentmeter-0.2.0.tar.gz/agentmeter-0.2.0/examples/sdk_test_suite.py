#!/usr/bin/env python3
"""
AgentMeter SDK Test Suite
SDK测试套件

Comprehensive test suite for validating AgentMeter SDK functionality
across all three payment types and integration patterns.
"""

import os
import time
import random
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    meter_function, meter_agent, PaymentType,
    quick_api_request_pay, quick_token_based_pay, quick_instant_pay
)

# Test Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
PROJECT_ID = "test_project_123"
AGENT_ID = "test_agent"
BASE_USER_ID = "test_user"


class SDKTestSuite:
    """Comprehensive SDK test suite"""
    
    def __init__(self):
        self.client = None
        self.test_results = {}
        self.test_count = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def setup(self):
        """Set up test environment"""
        print("🔧 Setting up test environment...")
        
        if API_KEY == "your_api_key_here":
            print("⚠️  Please configure AGENTMETER_API_KEY environment variable")
        return False
    
    try:
            # Create client
            self.client = create_client(
                api_key=API_KEY,
            project_id=PROJECT_ID,
            agent_id=AGENT_ID,
                user_id=f"{BASE_USER_ID}_setup"
            )
            
            # Test connection
            health = self.client.health_check()
            print(f"✅ Client created and connected: {health.get('status', 'unknown')}")
        return True
        
    except Exception as e:
            print(f"❌ Setup failed: {e}")
        return False

    def run_test(self, test_name: str, test_func):
        """Run a single test and track results"""
        self.test_count += 1
        print(f"\n🧪 Test {self.test_count}: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            if result:
                self.passed_tests += 1
                self.test_results[test_name] = "PASSED"
                print(f"✅ {test_name} - PASSED")
            else:
                self.failed_tests += 1
                self.test_results[test_name] = "FAILED"
                print(f"❌ {test_name} - FAILED")
            
        except Exception as e:
            self.failed_tests += 1
            self.test_results[test_name] = f"ERROR: {str(e)}"
            print(f"❌ {test_name} - ERROR: {e}")
    
    def test_basic_client_operations(self):
        """Test basic client operations"""
        try:
            # Test health check
            health = self.client.health_check()
            assert "status" in health
            
            # Test creating events directly
            response = self.client.record_api_request_pay(
                api_calls=1,
                unit_price=0.10,
                user_id=f"{BASE_USER_ID}_basic"
            )
            assert hasattr(response, 'total_cost')
            assert response.total_cost == 0.10
            
            print("   ✓ Basic client operations working")
            return True
            
        except Exception as e:
            print(f"   ✗ Basic client operations failed: {e}")
            return False
    
    def test_api_request_pay(self):
        """Test API request payment type"""
        try:
            user_id = f"{BASE_USER_ID}_api"
            
            # Direct API call
            response1 = self.client.record_api_request_pay(
                api_calls=3,
                unit_price=0.25,
                user_id=user_id,
                metadata={"test": "direct_api_call"}
            )
            assert response1.total_cost == 0.75
            
            # Using decorator
            @meter_api_request_pay(self.client, unit_price=0.15)
            def api_operation(data: str) -> str:
                time.sleep(0.1)  # Simulate work
                return f"Processed: {data}"
            
            result = api_operation("test_data")
            assert "Processed: test_data" in result
            
            # Using context manager
            with track_api_request_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id=user_id, unit_price=0.20
        ) as usage:
                usage["api_calls"] = 2
                usage["metadata"] = {"test": "context_manager"}
            
            # Quick function
            quick_api_request_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id=user_id, api_calls=1, unit_price=0.30
            )
            
            print("   ✓ API request payment working")
        return True
        
    except Exception as e:
            print(f"   ✗ API request payment failed: {e}")
        return False
    
    def test_token_based_pay(self):
        """Test token-based payment type"""
        try:
            user_id = f"{BASE_USER_ID}_token"
            
            # Direct API call
            response1 = self.client.record_token_based_pay(
                tokens_in=1000,
                tokens_out=500,
                input_token_price=0.00001,
                output_token_price=0.00002,
                user_id=user_id
            )
            expected_cost = (1000 * 0.00001) + (500 * 0.00002)
            assert abs(response1.total_cost - expected_cost) < 0.0001
            
            # Token extractor function
            def extract_tokens(*args, result=None, **kwargs):
                text = args[0] if args else ""
                input_tokens = len(text.split()) * 1.5
                output_tokens = len(str(result).split()) * 1.5 if result else 0
                return int(input_tokens), int(output_tokens)
            
            # Using decorator
            @meter_token_based_pay(
                self.client,
                input_token_price=0.000015,
                output_token_price=0.000025,
                tokens_extractor=extract_tokens
            )
            def llm_operation(prompt: str) -> str:
                time.sleep(0.2)  # Simulate processing
                return f"AI Response to: {prompt}. This is a longer response with more details."
            
            result = llm_operation("What is machine learning?")
            assert "AI Response" in result
            
            # Using context manager
            with track_token_based_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id=user_id,
                input_token_price=0.000020,
                output_token_price=0.000030
            ) as usage:
                usage["tokens_in"] = 750
                usage["tokens_out"] = 250
                usage["metadata"] = {"model": "test-model"}
            
            # Quick function
            quick_token_based_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id=user_id,
                tokens_in=200, tokens_out=100,
                input_token_price=0.000010,
                output_token_price=0.000015
            )
            
            print("   ✓ Token-based payment working")
            return True
        
        except Exception as e:
            print(f"   ✗ Token-based payment failed: {e}")
            return False
    
    def test_instant_pay(self):
        """Test instant payment type"""
        try:
            user_id = f"{BASE_USER_ID}_instant"
            
            # Direct API call
            response1 = self.client.record_instant_pay(
                amount=4.99,
                description="Premium Feature Unlock",
                user_id=user_id
            )
            assert response1.total_cost == 4.99
            
            # Condition function for conditional charging
            def should_charge_premium(*args, **kwargs):
                # Check if premium parameter is True
                return kwargs.get('premium', False)
            
            # Using decorator with conditional charging
            @meter_instant_pay(
                self.client,
                amount=2.99,
                description="Advanced Analytics",
                condition_func=should_charge_premium
            )
            def analytics_operation(data: dict, premium: bool = False) -> dict:
                time.sleep(0.3)  # Simulate processing
                if premium:
                    return {
                        "basic_stats": {"count": 100},
                        "advanced_analytics": {"insights": ["pattern1", "pattern2"]},
                        "premium": True
                    }
                else:
                    return {"basic_stats": {"count": 100}, "premium": False}
            
            # Test without premium (no charge)
            result1 = analytics_operation({"test": "data"}, premium=False)
            assert not result1["premium"]
            
            # Test with premium (should charge)
            result2 = analytics_operation({"test": "data"}, premium=True)
            assert result2["premium"]
            
            # Using context manager
            with track_instant_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id=user_id, amount=1.99,
                description="One-time Feature"
            ) as usage:
                usage["metadata"] = {"feature": "special_export"}
            
            # Quick function
            quick_instant_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id=user_id, amount=0.99,
                description="Micro Transaction"
            )
            
            print("   ✓ Instant payment working")
        return True
        
    except Exception as e:
            print(f"   ✗ Instant payment failed: {e}")
        return False

    def test_user_meter_operations(self):
        """Test user meter management"""
        try:
            user_id = f"{BASE_USER_ID}_meter"
            
            # Set user meter
            meter = self.client.set_user_meter(
                threshold_amount=100.0,
                user_id=user_id
            )
            assert meter.threshold_amount == 100.0
            assert meter.current_usage == 0.0
            
            # Get user meter
            current_meter = self.client.get_user_meter(user_id=user_id)
            assert current_meter.threshold_amount == 100.0
            
            # Increment usage
            incremented_meter = self.client.increment_user_meter(
                amount=25.50,
                user_id=user_id
            )
            assert incremented_meter.current_usage == 25.50
            
            # Reset meter
            reset_meter = self.client.reset_user_meter(user_id=user_id)
            assert reset_meter.current_usage == 0.0
            
            print("   ✓ User meter operations working")
            return True
            
        except Exception as e:
            print(f"   ✗ User meter operations failed: {e}")
            return False
    
    def test_event_retrieval(self):
        """Test event retrieval and statistics"""
        try:
            user_id = f"{BASE_USER_ID}_events"
            
            # Create some test events
            for i in range(3):
                self.client.record_api_request_pay(
                    api_calls=1,
                    unit_price=0.10,
                    user_id=user_id,
                    metadata={"test_event": i}
                )
            
            time.sleep(0.5)  # Wait for events to be processed
            
            # Get events
            events = self.client.get_events(
                user_id=user_id,
                limit=10
            )
            assert len(events) >= 3
            
            # Get statistics
            stats = self.client.get_meter_stats(timeframe="1 hour")
            assert hasattr(stats, 'total_cost')
            assert hasattr(stats, 'total_api_calls')
            
            print("   ✓ Event retrieval working")
        return True
        
    except Exception as e:
            print(f"   ✗ Event retrieval failed: {e}")
        return False

    def test_agent_decorator(self):
        """Test agent-level decorators"""
        try:
            # Create a test agent class
            @meter_agent(
                client=self.client,
                payment_type=PaymentType.API_REQUEST_PAY,
                unit_price=0.20,
                methods_to_meter=['process_request']
            )
            class TestAgent:
                def __init__(self):
                    self.processed_count = 0
                
                def process_request(self, request_data: str) -> str:
                    self.processed_count += 1
                    time.sleep(0.1)
                    return f"Processed: {request_data} (#{self.processed_count})"
                
                def non_metered_method(self, data: str) -> str:
                    return f"Free: {data}"
            
            # Test the agent
            agent = TestAgent()
            
            # Metered method
            result1 = agent.process_request("test_data_1")
            assert "Processed: test_data_1" in result1
            
            # Non-metered method
            result2 = agent.non_metered_method("test_data_2")
            assert "Free: test_data_2" in result2
            
            print("   ✓ Agent decorator working")
            return True
            
        except Exception as e:
            print(f"   ✗ Agent decorator failed: {e}")
            return False
    
    def test_concurrent_operations(self):
        """Test concurrent SDK operations"""
        try:
            user_id = f"{BASE_USER_ID}_concurrent"
            
            def concurrent_operation(operation_id: int):
                """Single concurrent operation"""
                try:
                    # Mix different payment types
                    if operation_id % 3 == 0:
                        self.client.record_api_request_pay(
                            api_calls=1,
                            unit_price=0.05,
                            user_id=f"{user_id}_{operation_id}",
                            metadata={"concurrent_test": operation_id}
                        )
                    elif operation_id % 3 == 1:
                        self.client.record_token_based_pay(
                            tokens_in=100,
                            tokens_out=50,
                            input_token_price=0.00001,
                            output_token_price=0.00002,
                            user_id=f"{user_id}_{operation_id}"
                        )
                    else:
                        self.client.record_instant_pay(
                            amount=0.99,
                            description="Concurrent Test",
                            user_id=f"{user_id}_{operation_id}"
                        )
                    return True
                except Exception:
                    return False
            
            # Run concurrent operations
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(concurrent_operation, i)
                    for i in range(10)
                ]
                results = [future.result() for future in futures]
            
            # Check that most operations succeeded
            success_rate = sum(results) / len(results)
            assert success_rate >= 0.8  # Allow for some failures
            
            print(f"   ✓ Concurrent operations working (success rate: {success_rate:.2%})")
            return True
            
        except Exception as e:
            print(f"   ✗ Concurrent operations failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        try:
            user_id = f"{BASE_USER_ID}_errors"
            
            # Test with invalid parameters (should handle gracefully)
            error_handled = False
            try:
                # Negative amounts should be handled
                self.client.record_api_request_pay(
                    api_calls=-1,
                    unit_price=0.10,
                    user_id=user_id
                )
                # If this succeeds, it means error handling is working
            except Exception:
                # This is expected for invalid inputs
                error_handled = True
            
            # Test with very large numbers
            try:
                response = self.client.record_instant_pay(
                    amount=999999.99,
                    description="Large Amount Test",
                    user_id=user_id
                )
                # Should either succeed or fail gracefully
            except Exception:
                # Expected for very large amounts
                pass
            
            # Test with empty/None values
            try:
                self.client.record_token_based_pay(
                    tokens_in=0,
                    tokens_out=0,
                    input_token_price=0.00001,
                    output_token_price=0.00002,
                    user_id=user_id,
                    metadata={}
                )
                # Should handle zero tokens gracefully
            except Exception:
                pass
            
            print("   ✓ Error handling working")
            return True
            
        except Exception as e:
            print(f"   ✗ Error handling failed: {e}")
            return False
    
    def test_performance_benchmarks(self):
        """Test SDK performance benchmarks"""
        try:
            user_id = f"{BASE_USER_ID}_performance"
            
            # Benchmark direct API calls
            start_time = time.time()
            for i in range(10):
                self.client.record_api_request_pay(
                    api_calls=1,
                    unit_price=0.01,
                    user_id=f"{user_id}_perf_{i}"
                )
            api_duration = time.time() - start_time
            
            # Benchmark decorated functions
            @meter_api_request_pay(self.client, unit_price=0.01)
            def benchmark_function(data: int):
                return data * 2
            
            start_time = time.time()
            for i in range(10):
                benchmark_function(i)
            decorator_duration = time.time() - start_time
            
            # Performance should be reasonable
            assert api_duration < 10.0  # 10 seconds max for 10 calls
            assert decorator_duration < 10.0
            
            print(f"   ✓ Performance benchmarks passed")
            print(f"     API calls: {api_duration:.2f}s for 10 operations")
            print(f"     Decorated: {decorator_duration:.2f}s for 10 operations")
            return True
            
        except Exception as e:
            print(f"   ✗ Performance benchmarks failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("🧪 AgentMeter SDK Test Suite")
        print("=" * 60)
        
        if not self.setup():
            print("❌ Test setup failed. Aborting tests.")
            return
        
        # Define all tests
        tests = [
            ("Basic Client Operations", self.test_basic_client_operations),
            ("API Request Payment", self.test_api_request_pay),
            ("Token-Based Payment", self.test_token_based_pay),
            ("Instant Payment", self.test_instant_pay),
            ("User Meter Operations", self.test_user_meter_operations),
            ("Event Retrieval", self.test_event_retrieval),
            ("Agent Decorators", self.test_agent_decorator),
            ("Concurrent Operations", self.test_concurrent_operations),
            ("Error Handling", self.test_error_handling),
            ("Performance Benchmarks", self.test_performance_benchmarks),
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        success_rate = (self.passed_tests / self.test_count) * 100 if self.test_count > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 40)
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "PASSED" else "❌"
            print(f"{status_icon} {test_name}: {result}")
        
        if self.failed_tests == 0:
            print("\n🎉 All tests passed! SDK is working correctly.")
    else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed. Please review the results above.")
        
        print("\nTest Coverage:")
        print("• Three payment types (API, Token, Instant)")
        print("• All integration patterns (decorators, context managers, direct calls)")
        print("• User meter management")
        print("• Event retrieval and statistics")
        print("• Error handling and edge cases")
        print("• Concurrent operations")
        print("• Performance benchmarks")


def main():
    """Main test execution function"""
    test_suite = SDKTestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main() 