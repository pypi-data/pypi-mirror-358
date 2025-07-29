#!/usr/bin/env python3
"""
Basic usage examples for the AgentMeter SDK supporting three payment types

This example demonstrates:
1. API Request Pay - Charge based on number of API calls
2. Token-based Pay - Charge based on input/output tokens
3. Instant Pay - Charge arbitrary amounts immediately

Usage:
    python basic_usage.py

Requirements:
    - AgentMeter API credentials configured
    - Python 3.7+
"""

import os
from agentmeter import (
    AgentMeterClient, create_client,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    PaymentType, quick_api_request_pay, quick_token_based_pay, quick_instant_pay
)

# Configuration - replace with your actual values
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
PROJECT_ID = "proj_123"
AGENT_ID = "agent_456"
USER_ID = "user_789"

def main():
    """Main demonstration function"""
    print("🚀 AgentMeter SDK Usage Examples")
    print("=" * 50)
    
    # Create client instance
    client = create_client(
        api_key=API_KEY,
        project_id=PROJECT_ID,
        agent_id=AGENT_ID,
        user_id=USER_ID
    )
    
    # Test API health
    try:
        health = client.health_check()
        print(f"✅ API Health: {health}")
    except Exception as e:
        print(f"❌ API Health Check Failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("📊 Payment Type Examples")
    print("=" * 50)
    
    # Example 1: API Request Pay
    print("\n=== API Request Pay Example ===")
    api_request_pay_examples(client)
    
    # Example 2: Token-based Pay  
    print("\n=== Token-based Pay Example ===")
    token_based_pay_examples(client)
    
    # Example 3: Instant Pay
    print("\n=== Instant Pay Example ===")
    instant_pay_examples(client)
    
    # Example 4: User Meter Management
    print("\n4️⃣ User Meter Management")
    user_meter_examples(client)
    
    # Example 5: Project and Billing Management
    print("\n5️⃣ Project and Billing Management")
    project_billing_examples(client)


def api_request_pay_examples(client: AgentMeterClient):
    """Examples for API request payment"""
    print("API Request Pay - Charge $0.3 per API call")
    
    # Method 1: Direct client call
    try:
        response = client.record_api_request_pay(
            api_calls=1,
            unit_price=0.3,
            metadata={"endpoint": "/api/search", "method": "POST"}
        )
        print(f"✅ Recorded API request pay: {response.total_cost}")
    except Exception as e:
        print(f"❌ Failed to record API request pay: {e}")
    
    # Method 2: Context manager
    try:
        with track_api_request_pay(client, PROJECT_ID, AGENT_ID, unit_price=0.3) as usage:
            # Simulate API call
            print("   🔍 Performing search operation...")
            usage["api_calls"] = 1
            usage["metadata"]["operation"] = "search"
            usage["metadata"]["query"] = "python tutorials"
        print("✅ Context manager tracking completed")
    except Exception as e:
        print(f"❌ Context manager tracking failed: {e}")
    
    # Method 3: Decorator
    @meter_api_request_pay(client, unit_price=0.3)
    def search_api(query: str):
        """Example search API function"""
        print(f"   🔍 Searching for: {query}")
        return f"Results for {query}"
    
    try:
        result = search_api("machine learning")
        print(f"✅ Decorator tracking completed: {result}")
    except Exception as e:
        print(f"❌ Decorator tracking failed: {e}")
    
    # Method 4: Quick function
    try:
        response = quick_api_request_pay(client, api_calls=1, unit_price=0.3)
        print(f"✅ Quick API request pay recorded: {response.total_cost}")
    except Exception as e:
        print(f"❌ Quick API request pay failed: {e}")


def token_based_pay_examples(client: AgentMeterClient):
    """Examples for token-based payment"""
    print("Token-based Pay - Charge $0.004/input token, $0.0001/output token")
    
    # Method 1: Direct client call
    try:
        response = client.record_token_based_pay(
            tokens_in=1000,
            tokens_out=500,
            input_token_price=0.004,
            output_token_price=0.0001,
            metadata={"model": "gpt-4", "task": "summarization"}
        )
        print(f"✅ Recorded token-based pay: {response.total_cost}")
    except Exception as e:
        print(f"❌ Failed to record token-based pay: {e}")
    
    # Method 2: Context manager
    try:
        with track_token_based_pay(
            client, PROJECT_ID, AGENT_ID,
            input_token_price=0.004,
            output_token_price=0.0001
        ) as usage:
            # Simulate LLM call
            print("   🤖 Calling LLM model...")
            usage["tokens_in"] = 1500
            usage["tokens_out"] = 750
            usage["metadata"]["model"] = "gpt-4"
            usage["metadata"]["temperature"] = 0.7
        print("✅ Token-based context tracking completed")
    except Exception as e:
        print(f"❌ Token-based context tracking failed: {e}")
    
    # Method 3: Decorator with token extraction
    def extract_tokens(*args, result=None, **kwargs):
        """Extract token counts from function arguments or result"""
        # In a real scenario, you'd extract this from the LLM response
        prompt = args[0] if args else ""
        input_tokens = len(prompt.split()) * 1.3  # Rough estimation
        output_tokens = len(result.split()) * 1.3 if result else 0
        return int(input_tokens), int(output_tokens)
    
    @meter_token_based_pay(
        client,
        input_token_price=0.004,
        output_token_price=0.0001,
        tokens_extractor=extract_tokens
    )
    def llm_summarize(text: str):
        """Example LLM summarization function"""
        print(f"   🤖 Summarizing text ({len(text)} chars)...")
        return f"Summary of: {text[:50]}..."
    
    try:
        summary = llm_summarize("This is a long text that needs to be summarized...")
        print(f"✅ LLM decorator tracking completed: {summary}")
    except Exception as e:
        print(f"❌ LLM decorator tracking failed: {e}")
    
    # Method 4: Quick function
    try:
        response = quick_token_based_pay(
            client, tokens_in=800, tokens_out=400,
            input_token_price=0.004, output_token_price=0.0001
        )
        print(f"✅ Quick token-based pay recorded: {response.total_cost}")
    except Exception as e:
        print(f"❌ Quick token-based pay failed: {e}")


def instant_pay_examples(client: AgentMeterClient):
    """Examples for instant payment"""
    print("Instant Pay - Charge $4.99 for premium features")
    
    # Method 1: Direct client call
    try:
        response = client.record_instant_pay(
            amount=4.99,
            description="Premium search feature unlock",
            metadata={"feature": "advanced_search", "tier": "premium"}
        )
        print(f"✅ Recorded instant pay: ${response.total_cost}")
    except Exception as e:
        print(f"❌ Failed to record instant pay: {e}")
    
    # Method 2: Context manager
    try:
        with track_instant_pay(
            client, PROJECT_ID, AGENT_ID,
            description="Premium analysis"
        ) as usage:
            # Simulate premium feature usage
            print("   ⭐ Using premium analysis feature...")
            usage["amount"] = 9.99
            usage["metadata"]["feature"] = "ai_analysis"
            usage["metadata"]["complexity"] = "high"
        print("✅ Instant pay context tracking completed")
    except Exception as e:
        print(f"❌ Instant pay context tracking failed: {e}")
    
    # Method 3: Conditional decorator
    def should_charge(*args, **kwargs):
        """Determine if premium features should be charged"""
        return kwargs.get('premium', False)
    
    @meter_instant_pay(
        client,
        amount=7.99,
        description="Premium export feature",
        condition_func=should_charge
    )
    def export_data(data, premium=False):
        """Example export function with premium option"""
        if premium:
            print("   ⭐ Exporting with premium features...")
            return f"Premium export of {len(data)} items"
        else:
            print("   📄 Basic export...")
            return f"Basic export of {len(data)} items"
    
    try:
        # Free export - no charge
        result1 = export_data(["item1", "item2"], premium=False)
        print(f"✅ Free export completed: {result1}")
        
        # Premium export - charged
        result2 = export_data(["item1", "item2", "item3"], premium=True)
        print(f"✅ Premium export completed: {result2}")
    except Exception as e:
        print(f"❌ Export decorator tracking failed: {e}")
    
    # Method 4: Quick function
    try:
        response = quick_instant_pay(client, amount=2.99, description="One-time feature")
        print(f"✅ Quick instant pay recorded: ${response.total_cost}")
    except Exception as e:
        print(f"❌ Quick instant pay failed: {e}")


def user_meter_examples(client: AgentMeterClient):
    """Examples for user meter management"""
    print("User Meter Management")
    
    try:
        # Set user meter threshold
        user_meter = client.set_user_meter(threshold_amount=100.0)
        print(f"✅ Set user meter threshold: ${user_meter.threshold_amount}")
        
        # Get current meter status
        current_meter = client.get_user_meter()
        print(f"📊 Current usage: ${current_meter.current_usage}/${current_meter.threshold_amount}")
        
        # Increment usage
        updated_meter = client.increment_user_meter(amount=15.50)
        print(f"💰 Updated usage: ${updated_meter.current_usage}")
        
        # Reset meter
        reset_meter = client.reset_user_meter()
        print(f"🔄 Meter reset. New usage: ${reset_meter.current_usage}")
        
    except Exception as e:
        print(f"❌ User meter management failed: {e}")


def project_billing_examples(client: AgentMeterClient):
    """Examples for project and billing management"""
    print("Project and Billing Management")
    
    try:
        # Get meter statistics
        stats = client.get_meter_stats(timeframe="7 days")
        print(f"📈 7-day stats - Total cost: ${stats.total_cost}")
        print(f"   API calls: {stats.total_api_calls}")
        print(f"   Tokens: {stats.total_tokens_in + stats.total_tokens_out}")
        
        # List recent events
        events = client.get_events(limit=5)
        print(f"📋 Recent events: {len(events)} found")
        
        # List projects (if you have permissions)
        try:
            projects = client.list_projects()
            print(f"🏢 Available projects: {len(projects)}")
        except Exception:
            print("ℹ️  Project listing requires admin permissions")
        
    except Exception as e:
        print(f"❌ Project/billing management failed: {e}")


if __name__ == "__main__":
    print("AgentMeter SDK Example")
    print("Please set your AGENTMETER_API_KEY environment variable")
    print("Or update the API_KEY variable in this script")
    print()
    
    if API_KEY == "your_api_key_here":
        print("⚠️  Please configure your API key before running examples")
    else:
        main()