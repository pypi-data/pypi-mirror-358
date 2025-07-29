"""
AgentMeter SDK - LangChain Integration Demonstration
==================================================

PURPOSE:
This example showcases how to integrate AgentMeter SDK with LangChain agents
and function calls, demonstrating automatic usage tracking for LLM-based
applications with complex agent workflows.

SCENARIO:
We're building a LangChain-powered customer support agent that:
1. Uses LLM calls for understanding and generating responses (token-based billing)
2. Has access to various tools/functions (API request billing)
3. Offers premium analysis features (instant payments)

APPLICATION STRUCTURE:
- LangChain agents with custom tools
- Automatic token tracking via callbacks
- Function call metering for tool usage
- Premium feature gating with instant payments

PRICING MODEL:
1. LLM Token Usage: $0.000015 per input token, $0.000025 per output token
2. Tool Function Calls: $0.10 per function execution
3. Premium Analysis: $4.99 per detailed report

This demonstrates how AgentMeter seamlessly integrates with LangChain's
callback system and tool framework for comprehensive usage tracking.
"""

import os
import time
import json
from typing import Dict, List, Any, Optional, Type
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    PaymentType
)

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
PROJECT_ID = "langchain_support_agent"
AGENT_ID = "customer_support_ai"

# LangChain imports with graceful fallback
try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.agents import Tool, AgentExecutor, create_react_agent
    from langchain.prompts import PromptTemplate
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import LLMResult, AgentAction, AgentFinish
    from langchain.tools import BaseTool
    from langchain import hub
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  LangChain not installed. Install with: pip install langchain openai")


class AgentMeterLangChainCallback(BaseCallbackHandler):
    """
    Enhanced AgentMeter callback for LangChain integration
    Automatically tracks token usage and costs for all LLM interactions
    """
    
    def __init__(
        self,
        client: AgentMeterClient,
        project_id: str,
        agent_id: str,
        user_id: str,
        input_token_price: float = 0.000015,
        output_token_price: float = 0.000025,
        enable_detailed_logging: bool = True
    ):
        super().__init__()
        self.client = client
        self.project_id = project_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.input_token_price = input_token_price
        self.output_token_price = output_token_price
        self.enable_detailed_logging = enable_detailed_logging
        
        # Track current operation
        self.current_operation = {}
        self.operation_count = 0
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Called when LLM starts - track input tokens"""
        self.operation_count += 1
        
        if prompts:
            prompt_text = prompts[0]
            # Estimate input tokens (rough: 4 chars = 1 token)
            estimated_input_tokens = len(prompt_text) // 4
            
            self.current_operation = {
                "operation_id": self.operation_count,
                "model_name": serialized.get("name", "unknown"),
                "prompt_length": len(prompt_text),
                "estimated_input_tokens": estimated_input_tokens,
                "start_time": time.time(),
                "kwargs": kwargs
            }
            
            if self.enable_detailed_logging:
                print(f"🤖 LLM Start #{self.operation_count}: {estimated_input_tokens} input tokens estimated")
    
    def on_llm_end(self, response: LLMResult, **kwargs):
        """Called when LLM ends - track output tokens and record usage"""
        if not self.current_operation:
            return
        
        # Extract output text and estimate tokens
        output_text = ""
        if response.generations:
            for generation_list in response.generations:
                for generation in generation_list:
                    output_text += generation.text
        
        estimated_output_tokens = len(output_text) // 4
        
        # Get actual token usage if available (OpenAI provides this)
        actual_input_tokens = self.current_operation["estimated_input_tokens"]
        actual_output_tokens = estimated_output_tokens
        
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            if token_usage:
                actual_input_tokens = token_usage.get('prompt_tokens', actual_input_tokens)
                actual_output_tokens = token_usage.get('completion_tokens', actual_output_tokens)
        
        # Calculate processing time
        processing_time = time.time() - self.current_operation["start_time"]
        
        # Record the usage
        try:
            response_obj = self.client.record_token_based_pay(
                tokens_in=actual_input_tokens,
                tokens_out=actual_output_tokens,
                input_token_price=self.input_token_price,
                output_token_price=self.output_token_price,
                project_id=self.project_id,
                agent_id=self.agent_id,
                user_id=self.user_id,
                metadata={
                    "operation_id": self.current_operation["operation_id"],
                    "model_name": self.current_operation["model_name"],
                    "processing_time": processing_time,
                    "prompt_length": self.current_operation["prompt_length"],
                    "response_length": len(output_text),
                    "langchain_callback": True
                }
            )
            
            cost = response_obj.total_cost
            if self.enable_detailed_logging:
                print(f"💰 LLM End #{self.current_operation['operation_id']}: "
                      f"${cost:.4f} ({actual_input_tokens}+{actual_output_tokens} tokens)")
                
        except Exception as e:
            print(f"❌ Failed to record LLM usage: {e}")
        
        # Clear current operation
        self.current_operation = {}
    
    def on_llm_error(self, error: Exception, **kwargs):
        """Called when LLM encounters an error"""
        if self.current_operation:
            print(f"❌ LLM Error #{self.current_operation['operation_id']}: {error}")
            
            # Still record input tokens for failed calls
            try:
                self.client.record_token_based_pay(
                    tokens_in=self.current_operation["estimated_input_tokens"],
                    tokens_out=0,
                    input_token_price=self.input_token_price,
                    output_token_price=self.output_token_price,
                    project_id=self.project_id,
                    agent_id=self.agent_id,
                    user_id=self.user_id,
                    metadata={
                        "operation_id": self.current_operation["operation_id"],
                        "error": str(error),
                        "failed_call": True
                    }
                )
            except Exception as track_error:
                print(f"❌ Failed to track error usage: {track_error}")
        
        self.current_operation = {}
    
    def on_agent_action(self, action: AgentAction, **kwargs):
        """Called when agent takes an action (tool usage)"""
        if self.enable_detailed_logging:
            print(f"🔧 Agent Action: {action.tool} - {action.tool_input}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        """Called when agent finishes"""
        if self.enable_detailed_logging:
            print(f"✅ Agent Finished: {finish.return_values}")


class CustomerSupportTools:
    """
    Collection of tools for the customer support agent
    Each tool is metered using AgentMeter for usage tracking
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
        self.knowledge_base = {
            "pricing": {
                "basic_plan": "$9.99/month",
                "pro_plan": "$29.99/month", 
                "enterprise": "Contact sales"
            },
            "features": {
                "basic_plan": ["API access", "5GB storage", "Email support"],
                "pro_plan": ["Everything in Basic", "50GB storage", "Priority support", "Analytics"],
                "enterprise": ["Everything in Pro", "Unlimited storage", "Custom integrations", "Dedicated support"]
            },
            "common_issues": {
                "login_problems": "Try clearing browser cache and cookies, then attempt login again",
                "api_errors": "Check your API key format and ensure it hasn't expired",
                "billing_questions": "Contact billing@example.com for account-specific billing questions"
            }
        }
    
    @meter_api_request_pay(client=None, unit_price=0.10)
    def search_knowledge_base(self, query: str) -> str:
        """
        Search the customer support knowledge base
        Charged per search operation ($0.10)
        """
        # Inject client (in real implementation, handle this more elegantly)
        CustomerSupportTools.search_knowledge_base.__wrapped__.__globals__['client'] = self.client
        
        query_lower = query.lower()
        results = []
        
        # Search through different knowledge base sections
        for section, data in self.knowledge_base.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    if query_lower in key.lower() or query_lower in str(value).lower():
                        results.append(f"{section.title()}: {key} - {value}")
        
        if results:
            return f"Found {len(results)} relevant articles:\n" + "\n".join(results[:3])
        else:
            return "No relevant articles found in the knowledge base."
    
    @meter_api_request_pay(client=None, unit_price=0.15)
    def check_user_account(self, user_email: str) -> str:
        """
        Check user account status and details
        Charged per account lookup ($0.15)
        """
        CustomerSupportTools.check_user_account.__wrapped__.__globals__['client'] = self.client
        
        # Simulate account lookup
        time.sleep(0.5)
        
        # Mock account data
        mock_accounts = {
            "user@example.com": {
                "status": "active",
                "plan": "pro_plan",
                "last_login": "2024-01-15",
                "api_usage": "2,450 calls this month"
            },
            "premium@example.com": {
                "status": "active", 
                "plan": "enterprise",
                "last_login": "2024-01-16",
                "api_usage": "15,230 calls this month"
            }
        }
        
        account = mock_accounts.get(user_email.lower())
        if account:
            return f"Account Status: {account['status']}\nPlan: {account['plan']}\nLast Login: {account['last_login']}\nAPI Usage: {account['api_usage']}"
        else:
            return "Account not found. Please verify the email address."
    
    @meter_api_request_pay(client=None, unit_price=0.05)
    def create_support_ticket(self, issue_description: str, priority: str = "normal") -> str:
        """
        Create a support ticket
        Charged per ticket creation ($0.05)
        """
        CustomerSupportTools.create_support_ticket.__wrapped__.__globals__['client'] = self.client
        
        ticket_id = f"TICK-{int(time.time())}"
        
        return f"Support ticket created successfully!\nTicket ID: {ticket_id}\nPriority: {priority}\nDescription: {issue_description[:100]}...\nEstimated response time: 24 hours"
    
    def get_tools_list(self) -> List[Tool]:
        """Get the list of LangChain tools with AgentMeter integration"""
        return [
            Tool(
                name="search_knowledge_base",
                func=self.search_knowledge_base,
                description="Search the customer support knowledge base for information about pricing, features, and common issues. Input should be a search query."
            ),
            Tool(
                name="check_user_account", 
                func=self.check_user_account,
                description="Check user account status, plan details, and usage information. Input should be a user email address."
            ),
            Tool(
                name="create_support_ticket",
                func=self.create_support_ticket,
                description="Create a support ticket for issues that need human attention. Input should be the issue description."
            )
        ]


class PremiumAnalysisService:
    """
    Premium analysis service with instant payment features
    Provides detailed analytics and insights for an additional cost
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
    
    def should_charge_for_analysis(self, *args, **kwargs):
        """Determine if premium analysis should be charged"""
        return kwargs.get('detailed_analysis', False)
    
    @meter_instant_pay(
        client=None,
        amount=4.99,
        description="Premium Support Analytics",
        condition_func=lambda self, *args, **kwargs: self.should_charge_for_analysis(*args, **kwargs)
    )
    def analyze_support_interaction(self, conversation_history: List[str], user_id: str, detailed_analysis: bool = False) -> Dict[str, Any]:
        """
        Analyze support interaction with optional premium features
        Basic analysis is free, detailed analysis costs $4.99
        """
        # Inject client
        PremiumAnalysisService.analyze_support_interaction.__wrapped__.__globals__['client'] = self.client
        
        if detailed_analysis:
            print("🔍 Generating premium support analysis...")
            time.sleep(2.0)  # Simulate complex analysis
            
            return {
                "analysis_type": "premium",
                "conversation_length": len(conversation_history),
                "sentiment_analysis": {
                    "overall_sentiment": "neutral",
                    "sentiment_trend": "improving",
                    "key_emotions": ["frustration", "relief"]
                },
                "issue_classification": {
                    "category": "billing_inquiry",
                    "urgency": "medium",
                    "complexity": "low"
                },
                "resolution_insights": {
                    "likely_resolution_time": "< 1 hour",
                    "suggested_actions": [
                        "Provide billing documentation",
                        "Escalate to billing specialist",
                        "Follow up in 24 hours"
                    ],
                    "similar_cases": 5
                },
                "customer_profile": {
                    "interaction_history": "3 previous tickets",
                    "satisfaction_score": 4.2,
                    "retention_risk": "low"
                },
                "cost": 4.99,
                "charged_as": "instant_pay"
            }
        else:
            # Basic analysis (free)
            return {
                "analysis_type": "basic",
                "conversation_length": len(conversation_history),
                "basic_sentiment": "neutral",
                "suggested_category": "general_inquiry",
                "charged_as": "free",
                "upgrade_note": "Upgrade to premium analysis for detailed insights"
            }


class LangChainAgentMeterDemo:
    """
    Main demonstration class showing LangChain + AgentMeter integration
    """
    
    def __init__(self, agentmeter_client: AgentMeterClient, openai_api_key: str):
        self.client = agentmeter_client
        self.openai_api_key = openai_api_key
        
        # Initialize services
        self.support_tools = CustomerSupportTools(agentmeter_client)
        self.premium_service = PremiumAnalysisService(agentmeter_client)
        
        # Create AgentMeter callback
        self.callback = AgentMeterLangChainCallback(
            client=agentmeter_client,
            project_id=PROJECT_ID,
            agent_id=AGENT_ID,
            user_id="langchain_demo_user",
            input_token_price=0.000015,
            output_token_price=0.000025
        )
    
    def create_customer_support_agent(self):
        """Create a LangChain agent with AgentMeter integration"""
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not available")
        
        # Create LLM with callback
        llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.7,
            callbacks=[self.callback]
        )
        
        # Get tools from support service
        tools = self.support_tools.get_tools_list()
        
        # Create agent prompt
        prompt = PromptTemplate.from_template("""
You are a helpful customer support agent. You have access to tools that can help you assist customers.

Use the available tools to:
1. Search the knowledge base for relevant information
2. Check user account details when needed
3. Create support tickets for complex issues

Be friendly, helpful, and thorough in your responses.

Tools available:
{tools}

Tool names: {tool_names}

Question: {input}
Thought: {agent_scratchpad}
""")
        
        # Create the agent
        agent = create_react_agent(llm, tools, prompt)
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            callbacks=[self.callback]
        )
        
        return agent_executor
    
    def demonstrate_basic_interaction(self, agent_executor, user_query: str, user_id: str):
        """Demonstrate basic customer support interaction"""
        print(f"\n🎧 Customer Query: '{user_query}'")
        print("-" * 50)
        
        try:
            # Run the agent
            response = agent_executor.invoke({
                "input": user_query,
                "user_id": user_id
            })
            
            print(f"\n🤖 Agent Response: {response['output']}")
            return response
            
        except Exception as e:
            print(f"❌ Agent error: {e}")
            return None
    
    def demonstrate_premium_analysis(self, conversation_history: List[str], user_id: str):
        """Demonstrate premium analysis features"""
        print("\n" + "="*60)
        print("💎 PREMIUM ANALYSIS DEMONSTRATION")
        print("="*60)
        
        # Basic analysis (free)
        print("1. Basic Analysis (Free):")
        basic_analysis = self.premium_service.analyze_support_interaction(
            conversation_history, user_id, detailed_analysis=False
        )
        print(f"   📊 Type: {basic_analysis['analysis_type']}")
        print(f"   💬 Conversation length: {basic_analysis['conversation_length']}")
        print(f"   🎭 Sentiment: {basic_analysis['basic_sentiment']}")
        
        # Premium analysis (paid)
        print("\n2. Premium Analysis ($4.99):")
        premium_analysis = self.premium_service.analyze_support_interaction(
            conversation_history, user_id, detailed_analysis=True
        )
        print(f"   📈 Detailed insights: {len(premium_analysis['resolution_insights']['suggested_actions'])} recommendations")
        print(f"   🎯 Classification: {premium_analysis['issue_classification']['category']}")
        print(f"   👤 Customer profile: {premium_analysis['customer_profile']['satisfaction_score']} satisfaction")
        print(f"   💰 Cost: ${premium_analysis['cost']}")
    
    def demonstrate_usage_monitoring(self, user_id: str):
        """Demonstrate usage monitoring and cost tracking"""
        print("\n" + "="*60)
        print("📊 USAGE MONITORING & COST TRACKING")
        print("="*60)
        
        try:
            # Set up user meter for LangChain usage
            print("1. Setting up usage limits...")
            user_meter = self.client.set_user_meter(
                threshold_amount=50.0,  # $50 monthly limit
                user_id=user_id
            )
            print(f"   ✅ Monthly limit: ${user_meter.threshold_amount}")
            
            # Check current usage
            print("\n2. Current usage status...")
            current_meter = self.client.get_user_meter(user_id=user_id)
            print(f"   💰 Usage: ${current_meter.current_usage:.2f}/${current_meter.threshold_amount}")
            print(f"   📊 Percentage: {current_meter.usage_percentage:.1f}%")
            
            # Get detailed statistics
            print("\n3. Detailed usage statistics...")
            stats = self.client.get_meter_stats(timeframe="7 days")
            print(f"   🔧 Total function calls: {stats.total_api_calls}")
            print(f"   🪙 Total tokens: {stats.total_tokens_in + stats.total_tokens_out}")
            print(f"   💰 Total cost: ${stats.total_cost:.2f}")
            
            if stats.total_api_calls > 0:
                avg_cost_per_call = stats.total_cost / stats.total_api_calls
                print(f"   📈 Average cost per operation: ${avg_cost_per_call:.3f}")
            
        except Exception as e:
            print(f"   ❌ Monitoring error: {e}")
    
    def run_comprehensive_demo(self):
        """Run comprehensive LangChain + AgentMeter demonstration"""
        print("🦜 LangChain + AgentMeter Integration Demo")
        print("=" * 60)
        print("Scenario: AI-powered customer support with usage tracking")
        print("Features: LLM token tracking, tool usage billing, premium analytics")
        print("=" * 60)
        
        if not LANGCHAIN_AVAILABLE:
            print("❌ LangChain not available - install with: pip install langchain openai")
            return
        
        if self.openai_api_key == "your_openai_api_key":
            print("❌ Please set OPENAI_API_KEY environment variable")
            return
        
        demo_user = "langchain_customer_001"
        
        # Create the agent
        print("\n🔧 Creating customer support agent...")
        try:
            agent_executor = self.create_customer_support_agent()
            print("✅ Agent created with AgentMeter integration")
        except Exception as e:
            print(f"❌ Failed to create agent: {e}")
            return
        
        # Test scenarios
        test_queries = [
            "What are the differences between your pricing plans?",
            "I'm having trouble with API authentication errors",
            "Can you check the status of my account? My email is user@example.com",
            "I need help with a billing issue, can you create a ticket?"
        ]
        
        conversation_history = []
        
        print("\n" + "="*60)
        print("🎧 CUSTOMER SUPPORT INTERACTIONS")
        print("="*60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Interaction {i} ---")
            response = self.demonstrate_basic_interaction(agent_executor, query, demo_user)
            
            if response:
                conversation_history.append(f"Customer: {query}")
                conversation_history.append(f"Agent: {response['output']}")
        
        # Demonstrate premium features
        if conversation_history:
            self.demonstrate_premium_analysis(conversation_history, demo_user)
        
        # Show usage monitoring
        self.demonstrate_usage_monitoring(demo_user)
        
        print("\n" + "="*60)
        print("✅ LANGCHAIN INTEGRATION DEMO COMPLETED")
        print("="*60)
        print("\nKey features demonstrated:")
        print("• Automatic LLM token tracking via callbacks")
        print("• Function/tool usage billing with decorators")
        print("• Premium feature gating with instant payments")
        print("• Comprehensive usage monitoring and analytics")
        print("• Error handling and failed call tracking")
        print("\nIntegration benefits:")
        print("• Zero-code LLM usage tracking")
        print("• Flexible tool billing strategies")
        print("• Real-time cost monitoring")
        print("• User limit management")


def main():
    """Main demonstration function"""
    if API_KEY == "your_api_key_here":
        print("⚠️  Please configure AGENTMETER_API_KEY environment variable")
        return
    
    if OPENAI_API_KEY == "your_openai_api_key":
        print("⚠️  Please configure OPENAI_API_KEY environment variable")
        return
    
    # Create AgentMeter client
    client = create_client(
        api_key=API_KEY,
        project_id=PROJECT_ID,
        agent_id=AGENT_ID,
        user_id="langchain_integration_demo"
    )
    
    # Test connection
    try:
        health = client.health_check()
        print(f"✅ AgentMeter connected: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ AgentMeter connection failed: {e}")
        return
    
    # Run the demonstration
    demo = LangChainAgentMeterDemo(client, OPENAI_API_KEY)
    demo.run_comprehensive_demo()


if __name__ == "__main__":
    main() 