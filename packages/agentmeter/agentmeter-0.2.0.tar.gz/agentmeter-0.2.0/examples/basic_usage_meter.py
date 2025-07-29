"""
AgentMeter SDK - Basic Usage Demonstration
==========================================

PURPOSE:
This example showcases the major features of AgentMeter SDK in the most basic way.
It demonstrates the three payment types and various integration patterns to help
developers understand how to integrate usage-based billing into their applications.

SCENARIO:
We're building a simple AI assistant API that offers different services:
1. Basic API calls (search, calculations) - charged per request
2. AI processing (text generation) - charged by token usage  
3. Premium features (exports, analytics) - one-time payments

APPLICATION STRUCTURE:
- SimpleAIAssistant: Main service class
- Three service types with different pricing models
- User subscription management
- Usage monitoring and analytics

PRICING MODEL:
1. API Request Pay: $0.05 per basic operation
2. Token-based Pay: $0.000015 per input token, $0.000025 per output token
3. Instant Pay: $2.99 for premium features

This example shows how AgentMeter makes it simple to track and bill for
different types of usage patterns in a single application.
"""

import os
import time
from typing import Dict, List, Any, Optional
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    quick_api_request_pay, quick_token_based_pay, quick_instant_pay,
    PaymentType
)

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
PROJECT_ID = "basic_ai_assistant"
AGENT_ID = "simple_assistant"


class SimpleAIAssistant:
    """
    A simple AI assistant demonstrating AgentMeter integration
    
    This class shows how to integrate all three payment types:
    - API calls for basic operations
    - Token usage for AI processing
    - Instant payments for premium features
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
        self.knowledge_base = {
            "python": "Python is a programming language",
            "ai": "AI stands for Artificial Intelligence",
            "machine learning": "ML is a subset of AI",
            "agentmeter": "AgentMeter helps track usage and billing"
        }
    
    # =================================================================
    # 1. API REQUEST PAY - Charge per operation/API call
    # =================================================================
    
    @meter_api_request_pay(client=None, unit_price=0.05)  # $0.05 per call
    def search_knowledge(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Search the knowledge base - charged per search operation
        Basic service charged by number of API calls
        """
        # Inject client (in real app, this would be handled differently)
        SimpleAIAssistant.search_knowledge.__wrapped__.__globals__['client'] = self.client
        
        print(f"🔍 Searching for: '{query}'")
        
        results = []
        query_lower = query.lower()
        
        for topic, description in self.knowledge_base.items():
            if query_lower in topic or query_lower in description.lower():
                results.append({
                    "topic": topic,
                    "description": description,
                    "relevance": 0.8 + (len(query_lower) / 20)  # Simple relevance score
                })
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "charged_as": "api_request_pay",
            "cost_per_search": 0.05
        }
    
    def calculate_math(self, expression: str, user_id: str) -> Dict[str, Any]:
        """
        Mathematical calculations - using context manager for API request pay
        Shows how to use context managers for flexible usage tracking
        """
        with track_api_request_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id, unit_price=0.03  # Cheaper for simple calculations
        ) as usage:
            
            print(f"🧮 Calculating: {expression}")
            
            try:
                # Simple expression evaluation (be careful in production!)
                result = eval(expression)
                usage["api_calls"] = 1
                usage["metadata"] = {
                    "operation": "calculation",
                    "expression": expression,
                    "success": True
                }
                
                return {
                    "expression": expression,
                    "result": result,
                    "charged_as": "api_request_pay",
                    "cost_per_calculation": 0.03
                }
                
            except Exception as e:
                usage["api_calls"] = 1
                usage["metadata"] = {
                    "operation": "calculation",
                    "expression": expression,
                    "success": False,
                    "error": str(e)
                }
                
                return {
                    "expression": expression,
                    "error": str(e),
                    "charged_as": "api_request_pay",
                    "note": "Still charged for failed calculations"
                }
    
    # =================================================================
    # 2. TOKEN-BASED PAY - Charge by input/output tokens
    # =================================================================
    
    def extract_text_tokens(self, *args, result=None, **kwargs):
        """
        Extract token counts from text processing
        Simple estimation: ~4 characters per token
        """
        prompt = args[0] if args else ""
        input_tokens = len(prompt) // 4
        output_tokens = len(str(result)) // 4 if result else 0
        return int(input_tokens), int(output_tokens)
    
    @meter_token_based_pay(
        client=None,
        input_token_price=0.000015,   # $0.000015 per input token
        output_token_price=0.000025,  # $0.000025 per output token  
        tokens_extractor=lambda self, *args, **kwargs: self.extract_text_tokens(*args, **kwargs)
    )
    def generate_text(self, prompt: str, user_id: str) -> Dict[str, Any]:
        """
        AI text generation - charged by token usage
        This simulates an LLM call where you pay for input and output tokens
        """
        # Inject client
        SimpleAIAssistant.generate_text.__wrapped__.__globals__['client'] = self.client
        
        print(f"🤖 Generating text for: '{prompt[:50]}...'")
        
        # Simulate AI processing time
        time.sleep(0.5)
        
        # Simple text generation (in reality, this would call an LLM API)
        if "story" in prompt.lower():
            response = f"Once upon a time, there was a topic about '{prompt}'. This is a generated story response that demonstrates token-based pricing where you pay for both input and output tokens."
        elif "code" in prompt.lower():
            response = f"# Generated code for: {prompt}\ndef example_function():\n    return 'This is generated code'\n\nprint(example_function())"
        else:
            response = f"This is an AI-generated response to your prompt: '{prompt}'. The response length affects the output token cost, while your prompt length affects input token cost."
        
        # Calculate token usage
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        
        return {
            "prompt": prompt,
            "response": response,
            "token_usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            },
            "charged_as": "token_based_pay",
            "pricing": {
                "input_token_price": 0.000015,
                "output_token_price": 0.000025,
                "estimated_cost": (input_tokens * 0.000015) + (output_tokens * 0.000025)
            }
        }
    
    def translate_text(self, text: str, target_language: str, user_id: str) -> Dict[str, Any]:
        """
        Text translation - using context manager for token-based pay
        Shows flexible token tracking for different operations
        """
        with track_token_based_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id,
            input_token_price=0.000010,  # Cheaper for translation
            output_token_price=0.000015
        ) as usage:
            
            print(f"🌍 Translating to {target_language}: '{text[:30]}...'")
            
            # Simulate translation (in reality, would call translation API)
            time.sleep(0.3)
            
            translations = {
                "spanish": f"Texto traducido: {text}",
                "french": f"Texte traduit: {text}",
                "german": f"Übersetzter Text: {text}",
                "default": f"Translated text: {text}"
            }
            
            translated = translations.get(target_language.lower(), translations["default"])
            
            # Set token usage
            input_tokens = len(text) // 4
            output_tokens = len(translated) // 4
            
            usage["tokens_in"] = input_tokens
            usage["tokens_out"] = output_tokens
            usage["metadata"] = {
                "operation": "translation",
                "source_language": "english",
                "target_language": target_language,
                "character_count": len(text)
            }
            
            return {
                "original_text": text,
                "translated_text": translated,
                "target_language": target_language,
                "token_usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                },
                "charged_as": "token_based_pay"
            }
    
    # =================================================================
    # 3. INSTANT PAY - One-time payments for premium features
    # =================================================================
    
    def should_charge_for_export(self, *args, **kwargs):
        """Determine if export feature should be charged"""
        return kwargs.get('premium_export', False)
    
    @meter_instant_pay(
        client=None,
        amount=2.99,
        description="Premium Data Export",
        condition_func=lambda self, *args, **kwargs: self.should_charge_for_export(*args, **kwargs)
    )
    def export_data(self, data: List[Dict], format: str, user_id: str, premium_export: bool = False) -> Dict[str, Any]:
        """
        Export data in various formats - instant payment for premium features
        Basic exports are free, premium exports (CSV, PDF) cost $2.99
        """
        # Inject client
        SimpleAIAssistant.export_data.__wrapped__.__globals__['client'] = self.client
        
        print(f"📊 Exporting {len(data)} records as {format}")
        
        if format.lower() in ['csv', 'pdf', 'excel'] and premium_export:
            # Premium export with formatting, charts, etc.
            export_content = f"PREMIUM_{format.upper()}_EXPORT:\n"
            for i, item in enumerate(data[:5]):  # Limit for demo
                export_content += f"  Row {i+1}: {item}\n"
            export_content += f"... and {len(data)-5} more rows with premium formatting"
            
            return {
                "export_content": export_content,
                "format": format,
                "record_count": len(data),
                "charged_as": "instant_pay",
                "feature": "premium_export",
                "cost": 2.99
            }
        else:
            # Basic export (free)
            export_content = f"BASIC_{format.upper()}_EXPORT:\n"
            for i, item in enumerate(data[:3]):  # More limited for basic
                export_content += f"  {item}\n"
            
            return {
                "export_content": export_content,
                "format": format,
                "record_count": len(data),
                "charged_as": "free",
                "note": "Basic export - no charge"
            }
    
    def get_analytics(self, user_id: str, detailed: bool = False) -> Dict[str, Any]:
        """
        Get usage analytics - using context manager for instant pay
        Basic analytics are free, detailed analytics cost $1.99
        """
        if detailed:
            with track_instant_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id=user_id, amount=1.99,
                description="Detailed Analytics Report"
            ) as usage:
                
                print("📈 Generating detailed analytics...")
                time.sleep(1.0)  # Simulate processing time
                
                usage["metadata"] = {
                    "analytics_type": "detailed",
                    "report_sections": ["usage", "costs", "trends", "recommendations"]
                }
                
                return {
                    "analytics_type": "detailed",
                    "total_api_calls": 150,
                    "total_tokens": 25000,
                    "total_cost": 15.75,
                    "cost_breakdown": {
                        "api_requests": 7.50,
                        "token_usage": 6.25,
                        "instant_payments": 2.00
                    },
                    "trends": {
                        "daily_usage": [10, 15, 12, 20, 18],
                        "peak_hours": "2-4 PM"
                    },
                    "recommendations": [
                        "Consider batch processing to reduce API costs",
                        "Monitor token usage during peak hours"
                    ],
                    "charged_as": "instant_pay",
                    "cost": 1.99
                }
        else:
            # Basic analytics (free)
            print("📊 Generating basic analytics...")
            return {
                "analytics_type": "basic",
                "total_operations": 150,
                "current_month_cost": 15.75,
                "charged_as": "free",
                "note": "Upgrade to detailed analytics for trends and recommendations"
            }


def demonstrate_user_meter_management(client: AgentMeterClient, user_id: str):
    """
    Demonstrate user meter/subscription management
    Shows how to set limits, track usage, and manage billing
    """
    print("\n" + "="*60)
    print("💳 USER METER & SUBSCRIPTION MANAGEMENT")
    print("="*60)
    
    try:
        # Set monthly usage limit
        print("1. Setting up user subscription...")
        user_meter = client.set_user_meter(
            threshold_amount=25.0,  # $25 monthly limit
            user_id=user_id
        )
        print(f"   ✅ Monthly limit set: ${user_meter.threshold_amount}")
        
        # Check current usage
        print("\n2. Checking current usage...")
        current_meter = client.get_user_meter(user_id=user_id)
        print(f"   💰 Current usage: ${current_meter.current_usage:.2f}/${current_meter.threshold_amount}")
        print(f"   📊 Usage: {current_meter.usage_percentage:.1f}%")
        print(f"   💵 Remaining: ${current_meter.remaining_budget:.2f}")
        
        # Simulate some usage
        print("\n3. Simulating usage...")
        client.increment_user_meter(amount=5.50, user_id=user_id)
        updated_meter = client.get_user_meter(user_id=user_id)
        print(f"   📈 After usage: ${updated_meter.current_usage:.2f}/${updated_meter.threshold_amount}")
        
        # Get usage statistics
        print("\n4. Getting usage statistics...")
        stats = client.get_meter_stats(timeframe="30 days")
        print(f"   📊 Total API calls: {stats.total_api_calls}")
        print(f"   🪙 Total tokens: {stats.total_tokens_in + stats.total_tokens_out}")
        print(f"   💰 Total cost: ${stats.total_cost:.2f}")
        
    except Exception as e:
        print(f"   ❌ Meter management error: {e}")


def demonstrate_quick_helpers(client: AgentMeterClient, user_id: str):
    """
    Demonstrate quick helper functions for simple usage tracking
    These are convenient for simple scenarios
    """
    print("\n" + "="*60)
    print("⚡ QUICK HELPER FUNCTIONS")
    print("="*60)
    
    print("1. Quick API request tracking...")
    response1 = quick_api_request_pay(
        client, PROJECT_ID, AGENT_ID,
        user_id=user_id, api_calls=3, unit_price=0.08
    )
    print(f"   ✅ Tracked 3 API calls: ${response1.total_cost:.2f}")
    
    print("\n2. Quick token usage tracking...")  
    response2 = quick_token_based_pay(
        client, PROJECT_ID, AGENT_ID,
        user_id=user_id,
        tokens_in=500, tokens_out=200,
        input_token_price=0.000020,
        output_token_price=0.000030
    )
    print(f"   ✅ Tracked 700 tokens: ${response2.total_cost:.4f}")
    
    print("\n3. Quick instant payment...")
    response3 = quick_instant_pay(
        client, PROJECT_ID, AGENT_ID,
        user_id=user_id, amount=0.99,
        description="Quick Premium Feature"
    )
    print(f"   ✅ Instant payment: ${response3.total_cost:.2f}")


def main():
    """
    Main demonstration function showing all AgentMeter SDK features
    """
    print("🤖 AgentMeter SDK - Basic Usage Demonstration")
    print("=" * 60)
    print("Scenario: Simple AI Assistant with three pricing models")
    print("1. API Request Pay: Basic operations ($0.05 per call)")
    print("2. Token-based Pay: AI processing ($0.000015-$0.000025 per token)")
    print("3. Instant Pay: Premium features ($1.99-$2.99)")
    print("=" * 60)
    
    if API_KEY == "your_api_key_here":
        print("⚠️  Please set AGENTMETER_API_KEY environment variable")
        return
    
    # Create AgentMeter client
    client = create_client(
        api_key=API_KEY,
        project_id=PROJECT_ID,
        agent_id=AGENT_ID,
        user_id="basic_demo_user"
    )
    
    # Test connection
    try:
        health = client.health_check()
        print(f"✅ Connected to AgentMeter: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Create AI assistant
    assistant = SimpleAIAssistant(client)
    demo_user = "demo_user_001"
    
    print(f"\n🎯 Testing with user: {demo_user}")
    
    # =================================================================
    # Demonstrate API Request Pay
    # =================================================================
    print("\n" + "="*60)
    print("1️⃣ API REQUEST PAY - Charge per operation")
    print("="*60)
    
    # Search operation
    search_result = assistant.search_knowledge("python programming", demo_user)
    print(f"   🔍 Search completed: Found {search_result['total_found']} results")
    
    # Math calculation
    calc_result = assistant.calculate_math("2 + 3 * 4", demo_user)
    print(f"   🧮 Calculation: {calc_result['expression']} = {calc_result.get('result', 'Error')}")
    
    # =================================================================
    # Demonstrate Token-based Pay
    # =================================================================
    print("\n" + "="*60)
    print("2️⃣ TOKEN-BASED PAY - Charge by token usage")
    print("="*60)
    
    # Text generation
    text_result = assistant.generate_text("Write a short story about AI", demo_user)
    print(f"   🤖 Generated {text_result['token_usage']['total_tokens']} tokens")
    print(f"   💰 Estimated cost: ${text_result['pricing']['estimated_cost']:.4f}")
    
    # Translation
    translate_result = assistant.translate_text("Hello, how are you?", "spanish", demo_user)
    print(f"   🌍 Translation: {translate_result['token_usage']['total_tokens']} tokens")
    
    # =================================================================
    # Demonstrate Instant Pay
    # =================================================================
    print("\n" + "="*60)
    print("3️⃣ INSTANT PAY - One-time payments")
    print("="*60)
    
    # Basic export (free)
    sample_data = [{"name": "John", "score": 95}, {"name": "Jane", "score": 87}]
    basic_export = assistant.export_data(sample_data, "json", demo_user, premium_export=False)
    print(f"   📊 Basic export: {basic_export['charged_as']}")
    
    # Premium export (paid)
    premium_export = assistant.export_data(sample_data, "csv", demo_user, premium_export=True)
    print(f"   💎 Premium export: ${premium_export['cost']}")
    
    # Analytics
    basic_analytics = assistant.get_analytics(demo_user, detailed=False)
    print(f"   📈 Basic analytics: {basic_analytics['charged_as']}")
    
    detailed_analytics = assistant.get_analytics(demo_user, detailed=True)
    print(f"   📊 Detailed analytics: ${detailed_analytics['cost']}")
    
    # =================================================================
    # Additional Demonstrations
    # =================================================================
    demonstrate_user_meter_management(client, demo_user)
    demonstrate_quick_helpers(client, demo_user)
    
    print("\n" + "="*60)
    print("✅ BASIC USAGE DEMONSTRATION COMPLETED")
    print("="*60)
    print("\nThis example demonstrated:")
    print("• Three payment types with real-world scenarios")
    print("• Multiple integration patterns (decorators, context managers, helpers)")
    print("• User subscription and meter management")  
    print("• Usage monitoring and analytics")
    print("• Error handling and edge cases")
    print("\nNext steps:")
    print("• See langchain_integration_meter.py for LangChain integration")
    print("• See search_agent_meter.py for advanced agent patterns")
    print("• Check the documentation for production best practices")


if __name__ == "__main__":
    main() 