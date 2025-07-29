"""
AgentMeter SDK LangChain Integration Example
LangChain集成示例

This example demonstrates how to integrate AgentMeter with LangChain applications
for automatic token-based billing and usage tracking.
"""

import os
from typing import Dict, Any, List
from agentmeter import (
    AgentMeterClient, create_client,
    meter_token_based_pay, track_token_based_pay,
    PaymentType
)

# LangChain imports
try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import LLMChain, ConversationChain
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.agents import initialize_agent, AgentType, Tool
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import LLMResult
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️  LangChain not installed. Install with: pip install langchain openai")

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
PROJECT_ID = "langchain_proj_123"
AGENT_ID = "langchain_agent"


class AgentMeterLangChainCallback(BaseCallbackHandler):
    """
    Enhanced LangChain callback for AgentMeter integration
    支持自动Token计费的LangChain回调处理器
    """
    
    def __init__(
        self,
        client: AgentMeterClient,
        project_id: str,
        agent_id: str,
        user_id: str = "anonymous",
        input_token_price: float = 0.000015,  # $0.000015 per input token
        output_token_price: float = 0.00002,  # $0.00002 per output token
        track_all_calls: bool = True
    ):
        super().__init__()
        self.client = client
        self.project_id = project_id
        self.agent_id = agent_id
        self.user_id = user_id
        self.input_token_price = input_token_price
        self.output_token_price = output_token_price
        self.track_all_calls = track_all_calls
        
        # Track current operation
        self.current_prompt = ""
        self.current_tokens_in = 0
        self.current_tokens_out = 0
        self.operation_metadata = {}
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts running"""
        if prompts:
            self.current_prompt = prompts[0]
            # Estimate input tokens (rough approximation)
            self.current_tokens_in = len(self.current_prompt.split()) * 1.3
            
        self.operation_metadata = {
            "model_name": serialized.get("name", "unknown"),
            "model_type": serialized.get("_type", "llm"),
            "prompt_length": len(self.current_prompt),
            "llm_kwargs": kwargs
        }
        
        print(f"🤖 LLM started: {self.operation_metadata['model_name']}")
    
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLM ends running"""
        if not self.track_all_calls:
            return
            
        # Extract tokens from response
        if response.generations:
            output_text = ""
            for generation_list in response.generations:
                for generation in generation_list:
                    output_text += generation.text
            
            # Estimate output tokens
            self.current_tokens_out = len(output_text.split()) * 1.3
        
        # Get token usage from response if available
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            if token_usage:
                self.current_tokens_in = token_usage.get('prompt_tokens', self.current_tokens_in)
                self.current_tokens_out = token_usage.get('completion_tokens', self.current_tokens_out)
                self.operation_metadata['actual_token_usage'] = token_usage
        
        # Record the event
        try:
            self.operation_metadata.update({
                "estimated_tokens_in": int(self.current_tokens_in),
                "estimated_tokens_out": int(self.current_tokens_out),
                "total_tokens": int(self.current_tokens_in + self.current_tokens_out)
            })
            
            response = self.client.record_token_based_pay(
                tokens_in=int(self.current_tokens_in),
                tokens_out=int(self.current_tokens_out),
                input_token_price=self.input_token_price,
                output_token_price=self.output_token_price,
                project_id=self.project_id,
                agent_id=self.agent_id,
                user_id=self.user_id,
                metadata=self.operation_metadata
            )
            
            cost = response.total_cost
            print(f"💰 LLM call tracked: ${cost:.4f} ({int(self.current_tokens_in)} in + {int(self.current_tokens_out)} out tokens)")
            
        except Exception as e:
            print(f"❌ Failed to track LLM usage: {e}")
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM encounters an error"""
        print(f"❌ LLM error: {error}")
        
        # Still track the input tokens even on error
        if self.current_tokens_in > 0:
            try:
                self.operation_metadata.update({
                    "error": str(error),
                    "status": "error",
                    "tokens_in": int(self.current_tokens_in),
                    "tokens_out": 0
                })
                
                self.client.record_token_based_pay(
                    tokens_in=int(self.current_tokens_in),
                    tokens_out=0,
                    input_token_price=self.input_token_price,
                    output_token_price=self.output_token_price,
                    project_id=self.project_id,
                    agent_id=self.agent_id,
                    user_id=self.user_id,
                    metadata=self.operation_metadata
                )
                
                print(f"💰 Error call tracked: input tokens {int(self.current_tokens_in)}")
                
            except Exception as track_error:
                print(f"❌ Failed to track error usage: {track_error}")


def extract_chain_tokens(*args, result=None, **kwargs):
    """Extract token counts from chain execution"""
    # This is a simplified extraction - in practice you'd get this from the callback
    prompt = args[0] if args else ""
    input_tokens = len(str(prompt).split()) * 1.3
    output_tokens = len(str(result).split()) * 1.3 if result else 0
    return int(input_tokens), int(output_tokens)


class LangChainAgentMeterDemo:
    """Demonstration class for LangChain + AgentMeter integration"""
    
    def __init__(self, agentmeter_client: AgentMeterClient, openai_api_key: str):
        self.client = agentmeter_client
        self.openai_api_key = openai_api_key
        
        # Create callback
        self.callback = AgentMeterLangChainCallback(
            client=agentmeter_client,
            project_id=PROJECT_ID,
            agent_id=AGENT_ID,
            user_id="langchain_user",
            input_token_price=0.000015,
            output_token_price=0.00002
        )
    
    def basic_llm_example(self):
        """Basic LLM usage with automatic tracking"""
        print("\n1️⃣ Basic LLM Example")
        print("-" * 30)
        
        if not LANGCHAIN_AVAILABLE:
            print("❌ LangChain not available")
            return
        
        try:
            # Create LLM with callback
            llm = OpenAI(
                openai_api_key=self.openai_api_key,
                temperature=0.7,
                callbacks=[self.callback]
            )
            
            # Make a call
            response = llm("What are the benefits of using AI in e-commerce?")
            print(f"✅ LLM Response: {response[:100]}...")
            
        except Exception as e:
            print(f"❌ Basic LLM example failed: {e}")
    
    def chain_example(self):
        """Chain usage with manual tracking using decorators"""
        print("\n2️⃣ Chain Example with Decorators")
        print("-" * 30)
        
        if not LANGCHAIN_AVAILABLE:
            print("❌ LangChain not available")
            return
        
        try:
            # Create a chain
            llm = OpenAI(openai_api_key=self.openai_api_key, temperature=0.7)
            
            prompt = PromptTemplate(
                input_variables=["topic"],
                template="Write a short summary about {topic} in e-commerce:"
            )
            
            chain = LLMChain(llm=llm, prompt=prompt)
            
            # Wrap chain execution with decorator
            @meter_token_based_pay(
                self.client,
                input_token_price=0.000015,
                output_token_price=0.00002,
                tokens_extractor=extract_chain_tokens
            )
            def run_chain(topic):
                return chain.run(topic=topic)
            
            # Execute chain
            result = run_chain("artificial intelligence")
            print(f"✅ Chain Result: {result[:100]}...")
            
        except Exception as e:
            print(f"❌ Chain example failed: {e}")
    
    def conversation_example(self):
        """Conversation chain with context tracking"""
        print("\n3️⃣ Conversation Example")
        print("-" * 30)
        
        if not LANGCHAIN_AVAILABLE:
            print("❌ LangChain not available")
            return
        
        try:
            # Create conversation chain with memory
            llm = ChatOpenAI(
                openai_api_key=self.openai_api_key,
                temperature=0.7,
                callbacks=[self.callback]
            )
            
            memory = ConversationBufferMemory()
            conversation = ConversationChain(
                llm=llm,
                memory=memory,
                verbose=False
            )
            
            # Have a conversation
            questions = [
                "What is machine learning?",
                "How can it be applied to e-commerce?",
                "What are some specific examples?"
            ]
            
            for i, question in enumerate(questions, 1):
                print(f"   Q{i}: {question}")
                response = conversation.predict(input=question)
                print(f"   A{i}: {response[:80]}...")
                print()
            
        except Exception as e:
            print(f"❌ Conversation example failed: {e}")
    
    def agent_example(self):
        """Agent example with tool usage tracking"""
        print("\n4️⃣ Agent Example with Tools")
        print("-" * 30)
        
        if not LANGCHAIN_AVAILABLE:
            print("❌ LangChain not available")
            return
        
        try:
            # Define tools with AgentMeter tracking
            @meter_token_based_pay(
                self.client,
                input_token_price=0.000010,  # Cheaper for tool usage
                output_token_price=0.000015,
                tokens_extractor=extract_chain_tokens
            )
            def product_search_tool(query: str) -> str:
                """Search for products in the database"""
                # Simulate product search
                products = [
                    f"Laptop Pro - ${999.99}",
                    f"Smart Watch - ${299.99}",
                    f"Wireless Headphones - ${199.99}"
                ]
                return f"Found products for '{query}': {', '.join(products)}"
            
            @meter_token_based_pay(
                self.client,
                input_token_price=0.000010,
                output_token_price=0.000015,
                tokens_extractor=extract_chain_tokens
            )
            def price_calculator_tool(product: str) -> str:
                """Calculate pricing for a product"""
                # Simulate price calculation
                base_price = 299.99
                discount = 0.1
                final_price = base_price * (1 - discount)
                return f"Price for {product}: ${final_price:.2f} (10% discount applied)"
            
            # Create tools
            tools = [
                Tool(
                    name="Product Search",
                    func=product_search_tool,
                    description="Search for products by name or category"
                ),
                Tool(
                    name="Price Calculator", 
                    func=price_calculator_tool,
                    description="Calculate final price with discounts"
                )
            ]
            
            # Create agent
            llm = OpenAI(
                openai_api_key=self.openai_api_key,
                temperature=0.7,
                callbacks=[self.callback]
            )
            
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False
            )
            
            # Run agent
            query = "Find me a laptop and calculate its price with discounts"
            response = agent.run(query)
            print(f"✅ Agent Response: {response[:150]}...")
            
        except Exception as e:
            print(f"❌ Agent example failed: {e}")
    
    def batch_processing_example(self):
        """Batch processing multiple LLM calls"""
        print("\n5️⃣ Batch Processing Example")
        print("-" * 30)
        
        if not LANGCHAIN_AVAILABLE:
            print("❌ LangChain not available")
            return
        
        try:
            # Create LLM
            llm = OpenAI(
                openai_api_key=self.openai_api_key,
                temperature=0.7
            )
            
            # Batch of questions to process
            questions = [
                "What is AI?",
                "How does machine learning work?", 
                "What are neural networks?",
                "Explain deep learning",
                "What is natural language processing?"
            ]
            
            # Process with context tracking
            with track_token_based_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id="batch_user",
                input_token_price=0.000012,  # Batch discount
                output_token_price=0.000018
            ) as usage:
                
                print("🔄 Processing batch of questions...")
                total_input_tokens = 0
                total_output_tokens = 0
                
                for i, question in enumerate(questions, 1):
                    try:
                        response = llm(question)
                        
                        # Estimate tokens
                        input_tokens = len(question.split()) * 1.3
                        output_tokens = len(response.split()) * 1.3
                        
                        total_input_tokens += input_tokens
                        total_output_tokens += output_tokens
                        
                        print(f"   Q{i}: {question} -> {len(response)} chars")
                        
                    except Exception as e:
                        print(f"   Q{i}: Error - {e}")
                
                # Update usage tracking
                usage["tokens_in"] = int(total_input_tokens)
                usage["tokens_out"] = int(total_output_tokens)
                usage["metadata"] = {
                    "batch_size": len(questions),
                    "total_questions": len(questions),
                    "processing_type": "batch"
                }
                
                print(f"✅ Batch completed: {int(total_input_tokens)} + {int(total_output_tokens)} tokens")
            
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
    
    def usage_monitoring_example(self):
        """Monitor and manage usage limits"""
        print("\n6️⃣ Usage Monitoring Example")
        print("-" * 30)
        
        try:
            # Set up user limits for LangChain usage
            user_id = "langchain_user"
            monthly_limit = 50.0  # $50 monthly limit
            
            # Set user meter
            user_meter = self.client.set_user_meter(
                threshold_amount=monthly_limit,
                user_id=user_id
            )
            print(f"📊 Set monthly limit: ${user_meter.threshold_amount}")
            
            # Check current usage
            current_meter = self.client.get_user_meter(user_id=user_id)
            usage_percentage = (current_meter.current_usage / current_meter.threshold_amount) * 100
            
            print(f"💰 Current usage: ${current_meter.current_usage:.2f}/${current_meter.threshold_amount}")
            print(f"📈 Usage percentage: {usage_percentage:.1f}%")
            
            # Get recent LangChain events
            events = self.client.get_events(
                user_id=user_id,
                limit=5,
                event_type="token_usage"
            )
            print(f"📋 Recent events: {len(events)} found")
            
            # Get usage statistics
            stats = self.client.get_meter_stats(timeframe="7 days")
            print(f"📈 7-day LangChain stats:")
            print(f"   Total cost: ${stats.total_cost:.2f}")
            print(f"   Total tokens: {stats.total_tokens_in + stats.total_tokens_out:,}")
            print(f"   Average cost per token: ${stats.total_cost / max(stats.total_tokens_in + stats.total_tokens_out, 1):.6f}")
            
        except Exception as e:
            print(f"❌ Usage monitoring failed: {e}")


def main():
    """Main demonstration function"""
    print("🦜 AgentMeter + LangChain Integration Example")
    print("=" * 60)
    
    if API_KEY == "your_api_key_here":
        print("⚠️  Please configure AGENTMETER_API_KEY environment variable")
        return
    
    if OPENAI_API_KEY == "your_openai_api_key":
        print("⚠️  Please configure OPENAI_API_KEY environment variable")
        return
    
    if not LANGCHAIN_AVAILABLE:
        print("⚠️  Please install LangChain: pip install langchain openai")
        return
    
    # Create AgentMeter client
    client = create_client(
        api_key=API_KEY,
        project_id=PROJECT_ID,
        agent_id=AGENT_ID,
        user_id="langchain_demo_user"
    )
    
    # Test connection
    try:
        health = client.health_check()
        print(f"✅ AgentMeter API connected: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ AgentMeter connection failed: {e}")
        return
    
    # Create demo instance
    demo = LangChainAgentMeterDemo(client, OPENAI_API_KEY)
    
    print(f"\n🎯 Running LangChain integration examples...")
    print("=" * 60)
    
    # Run examples
    demo.basic_llm_example()
    demo.chain_example()
    demo.conversation_example()
    demo.agent_example()
    demo.batch_processing_example()
    demo.usage_monitoring_example()
    
    print("\n✅ LangChain integration examples completed!")
    print("\nThis example demonstrates:")
    print("• Automatic token tracking with LangChain callbacks")
    print("• Manual tracking using decorators and context managers")
    print("• Conversation and agent usage patterns")
    print("• Batch processing with usage aggregation")
    print("• Usage monitoring and limit management")
    print("\nFor production use:")
    print("• Configure appropriate token prices for your models")
    print("• Implement proper error handling and retries")
    print("• Set up usage alerts and limit enforcement")
    print("• Monitor costs and optimize usage patterns")


if __name__ == "__main__":
    main() 