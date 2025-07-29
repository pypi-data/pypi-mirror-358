"""
AgentMeter SDK - Search Agent Demonstration
==========================================

PURPOSE:
This example demonstrates a synthetic AI agent app with agent workflows and
function calls, showcasing how to meter different aspects of agent operations:
1. Token-based metering for agent input/output tokens (different prices for input vs output)
2. Function call metering for search operations (charge per function execution)

SCENARIO:
We're building an intelligent search agent that helps users find information
across multiple data sources. The agent:
- Uses LLM reasoning to understand queries and plan searches
- Executes various search functions (web, database, documents)
- Provides AI-enhanced responses with analysis and recommendations

APPLICATION STRUCTURE:
- SearchAgent: Main agent orchestrator with LLM reasoning
- SearchTools: Collection of search functions (each metered separately)
- ResponseEnhancer: AI post-processing with token-based billing
- UsageAnalytics: Premium analytics with instant payments

PRICING MODEL:
1. LLM Token Usage: 
   - Input tokens: $0.000015 per token (for query understanding)
   - Output tokens: $0.000025 per token (for response generation)
2. Search Function Calls:
   - Web search: $0.05 per search
   - Database search: $0.03 per query
   - Document search: $0.02 per search
3. Response Enhancement:
   - Basic summary: Free
   - AI analysis: $0.10 per enhancement
   - Premium insights: $0.99 per detailed report

This demonstrates how to build a comprehensive usage-based billing system
for complex AI agent applications with multiple service tiers.
"""

import os
import time
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    meter_function, meter_agent, PaymentType
)

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
PROJECT_ID = "intelligent_search_agent"
AGENT_ID = "multi_source_search_ai"

# Token pricing configuration
INPUT_TOKEN_PRICE = 0.000015   # $0.000015 per input token
OUTPUT_TOKEN_PRICE = 0.000025  # $0.000025 per output token


@dataclass
class SearchResult:
    """Structured search result"""
    source: str
    title: str
    content: str
    url: str
    relevance_score: float
    metadata: Dict[str, Any]


@dataclass
class AgentThought:
    """Agent reasoning step"""
    step: int
    thought: str
    action: str
    reasoning: str
    tokens_used: Tuple[int, int]  # (input, output)


class SearchTools:
    """
    Collection of search tools with individual metering
    Each search function is tracked separately with appropriate pricing
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
        
        # Mock data sources
        self.web_results = [
            {"title": "Python Programming Guide", "url": "example.com/python", "content": "Comprehensive guide to Python programming"},
            {"title": "AI Development Best Practices", "url": "example.com/ai", "content": "Best practices for AI application development"},
            {"title": "AgentMeter Usage Tutorial", "url": "agentmeter.com/tutorial", "content": "Learn how to implement usage-based billing"},
        ]
        
        self.database_records = [
            {"id": 1, "category": "technology", "title": "Machine Learning Trends", "content": "Latest trends in ML"},
            {"id": 2, "category": "business", "title": "SaaS Pricing Models", "content": "Different approaches to SaaS pricing"},
            {"id": 3, "category": "development", "title": "API Design Patterns", "content": "Common patterns for API design"},
        ]
        
        self.documents = [
            {"filename": "research_paper.pdf", "content": "Academic research on neural networks", "pages": 15},
            {"filename": "company_report.docx", "content": "Quarterly business performance report", "pages": 8},
            {"filename": "technical_spec.md", "content": "Technical specifications for API integration", "pages": 5},
        ]
    
    @meter_api_request_pay(client=None, unit_price=0.05)
    def search_web(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search web sources - $0.05 per search
        Most expensive due to external API costs
        """
        # Inject client
        SearchTools.search_web.__wrapped__.__globals__['client'] = self.client
        
        print(f"🌐 Searching web for: '{query}'")
        time.sleep(0.8)  # Simulate API call time
        
        results = []
        query_words = query.lower().split()
        
        for item in self.web_results:
            # Simple relevance calculation
            relevance = 0.0
            for word in query_words:
                if word in item["title"].lower() or word in item["content"].lower():
                    relevance += 0.3
            
            if relevance > 0:
                results.append(SearchResult(
                    source="web",
                    title=item["title"],
                    content=item["content"],
                    url=item["url"],
                    relevance_score=min(relevance, 1.0),
                    metadata={"search_time": 0.8, "api_cost": 0.05}
                ))
        
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)[:max_results]
    
    @meter_api_request_pay(client=None, unit_price=0.03)
    def search_database(self, query: str, category: Optional[str] = None) -> List[SearchResult]:
        """
        Search internal database - $0.03 per query
        Moderate cost for internal database operations
        """
        SearchTools.search_database.__wrapped__.__globals__['client'] = self.client
        
        print(f"🗄️ Searching database for: '{query}'" + (f" (category: {category})" if category else ""))
        time.sleep(0.3)  # Simulate database query time
        
        results = []
        query_words = query.lower().split()
        
        for record in self.database_records:
            # Filter by category if specified
            if category and record["category"] != category.lower():
                continue
            
            relevance = 0.0
            for word in query_words:
                if word in record["title"].lower() or word in record["content"].lower():
                    relevance += 0.4
            
            if relevance > 0:
                results.append(SearchResult(
                    source="database",
                    title=record["title"],
                    content=record["content"],
                    url=f"internal://db/{record['id']}",
                    relevance_score=min(relevance, 1.0),
                    metadata={
                        "record_id": record["id"],
                        "category": record["category"],
                        "query_time": 0.3
                    }
                ))
        
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
    
    @meter_api_request_pay(client=None, unit_price=0.02)
    def search_documents(self, query: str, file_types: Optional[List[str]] = None) -> List[SearchResult]:
        """
        Search document collection - $0.02 per search
        Lowest cost for document indexing
        """
        SearchTools.search_documents.__wrapped__.__globals__['client'] = self.client
        
        print(f"📄 Searching documents for: '{query}'" + (f" (types: {file_types})" if file_types else ""))
        time.sleep(0.2)  # Simulate document indexing
        
        results = []
        query_words = query.lower().split()
        
        for doc in self.documents:
            # Filter by file type if specified
            if file_types:
                file_ext = doc["filename"].split(".")[-1]
                if file_ext not in [ft.lower() for ft in file_types]:
                    continue
            
            relevance = 0.0
            for word in query_words:
                if word in doc["content"].lower():
                    relevance += 0.5
            
            if relevance > 0:
                results.append(SearchResult(
                    source="documents",
                    title=doc["filename"],
                    content=doc["content"],
                    url=f"file://{doc['filename']}",
                    relevance_score=min(relevance, 1.0),
                    metadata={
                        "filename": doc["filename"],
                        "pages": doc["pages"],
                        "search_time": 0.2
                    }
                ))
        
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)


class IntelligentSearchAgent:
    """
    Main search agent with LLM reasoning capabilities
    Demonstrates token-based billing for AI operations
    """
    
    def __init__(self, client: AgentMeterClient, search_tools: SearchTools):
        self.client = client
        self.search_tools = search_tools
        self.reasoning_history: List[AgentThought] = []
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (4 characters ≈ 1 token)"""
        return max(1, len(text) // 4)
    
    def llm_reasoning(self, prompt: str, context: str = "") -> Tuple[str, int, int]:
        """
        Simulate LLM reasoning with token tracking
        Returns: (response, input_tokens, output_tokens)
        """
        full_prompt = f"{context}\n\nQuery: {prompt}" if context else prompt
        input_tokens = self.estimate_tokens(full_prompt)
        
        # Simulate AI processing time
        time.sleep(0.5)
        
        # Generate reasoning response based on prompt
        if "plan" in prompt.lower():
            response = f"To answer this query, I need to: 1) Search web for recent information, 2) Check database for internal knowledge, 3) Review relevant documents, 4) Synthesize findings into a comprehensive response."
        elif "analyze" in prompt.lower():
            response = f"Based on the search results, I can identify key patterns and themes. The most relevant information comes from multiple sources and requires synthesis for a complete answer."
        elif "summarize" in prompt.lower():
            response = f"Here's a summary of the key findings: The search revealed {random.randint(3, 8)} relevant sources with varying relevance scores. The most important insights are..."
        else:
            response = f"Processing query about '{prompt[:50]}...'. I'll need to gather information from multiple sources to provide a comprehensive response."
        
        output_tokens = self.estimate_tokens(response)
        
        return response, input_tokens, output_tokens
    
    def plan_search_strategy(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Plan the search strategy using LLM reasoning
        Token-based billing for strategic planning
        """
        with track_token_based_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id,
            input_token_price=INPUT_TOKEN_PRICE,
            output_token_price=OUTPUT_TOKEN_PRICE
        ) as usage:
            
            print("🧠 Planning search strategy...")
            
            planning_prompt = f"Create a search plan for: {query}"
            reasoning, input_tokens, output_tokens = self.llm_reasoning(planning_prompt)
            
            # Determine search sources based on query
            search_plan = {
                "query": query,
                "reasoning": reasoning,
                "search_sources": [],
                "priority": "medium"
            }
            
            # Simple heuristics for search planning
            if any(word in query.lower() for word in ["latest", "recent", "current", "news"]):
                search_plan["search_sources"].append("web")
            
            if any(word in query.lower() for word in ["company", "internal", "policy", "database"]):
                search_plan["search_sources"].append("database")
            
            if any(word in query.lower() for word in ["document", "paper", "report", "spec"]):
                search_plan["search_sources"].append("documents")
            
            # Default to all sources if unclear
            if not search_plan["search_sources"]:
                search_plan["search_sources"] = ["web", "database", "documents"]
            
            # Record token usage
            usage["tokens_in"] = input_tokens
            usage["tokens_out"] = output_tokens
            usage["metadata"] = {
                "operation": "search_planning",
                "query_length": len(query),
                "sources_planned": len(search_plan["search_sources"])
            }
            
            # Track reasoning step
            self.reasoning_history.append(AgentThought(
                step=len(self.reasoning_history) + 1,
                thought="Planning search strategy",
                action="analyze_query",
                reasoning=reasoning,
                tokens_used=(input_tokens, output_tokens)
            ))
            
            return search_plan
    
    def execute_searches(self, search_plan: Dict[str, Any], user_id: str) -> List[SearchResult]:
        """
        Execute the planned searches
        Function calls are metered individually
        """
        print("🔍 Executing search plan...")
        
        all_results = []
        query = search_plan["query"]
        
        # Execute searches based on plan
        for source in search_plan["search_sources"]:
            try:
                if source == "web":
                    results = self.search_tools.search_web(query, max_results=3)
                elif source == "database":
                    results = self.search_tools.search_database(query)
                elif source == "documents":
                    results = self.search_tools.search_documents(query)
                else:
                    continue
                
                all_results.extend(results)
                print(f"   ✅ {source}: {len(results)} results")
                
            except Exception as e:
                print(f"   ❌ {source} search failed: {e}")
        
        return all_results
    
    def synthesize_response(self, query: str, search_results: List[SearchResult], user_id: str) -> Dict[str, Any]:
        """
        Synthesize final response using LLM
        Token-based billing for response generation
        """
        with track_token_based_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id,
            input_token_price=INPUT_TOKEN_PRICE,
            output_token_price=OUTPUT_TOKEN_PRICE
        ) as usage:
            
            print("🎯 Synthesizing final response...")
            
            # Create context from search results
            context = f"Found {len(search_results)} relevant results:\n"
            for i, result in enumerate(search_results[:5], 1):
                context += f"{i}. {result.title} ({result.source}): {result.content[:100]}...\n"
            
            synthesis_prompt = f"Synthesize a comprehensive answer for: {query}"
            response, input_tokens, output_tokens = self.llm_reasoning(synthesis_prompt, context)
            
            # Create structured response
            final_response = {
                "query": query,
                "answer": response,
                "sources_consulted": len(search_results),
                "search_breakdown": {},
                "confidence_score": min(0.9, len(search_results) * 0.15),
                "reasoning_steps": len(self.reasoning_history)
            }
            
            # Break down results by source
            for result in search_results:
                source = result.source
                if source not in final_response["search_breakdown"]:
                    final_response["search_breakdown"][source] = 0
                final_response["search_breakdown"][source] += 1
            
            # Record token usage
            usage["tokens_in"] = input_tokens
            usage["tokens_out"] = output_tokens
            usage["metadata"] = {
                "operation": "response_synthesis",
                "results_processed": len(search_results),
                "context_length": len(context)
            }
            
            # Track reasoning step
            self.reasoning_history.append(AgentThought(
                step=len(self.reasoning_history) + 1,
                thought="Synthesizing final response",
                action="generate_answer",
                reasoning=response,
                tokens_used=(input_tokens, output_tokens)
            ))
            
            return final_response
    
    def process_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Main query processing pipeline
        Orchestrates the entire search agent workflow
        """
        print(f"\n🚀 Processing query: '{query}'")
        print("-" * 60)
        
        start_time = time.time()
        self.reasoning_history.clear()
        
        try:
            # Step 1: Plan search strategy (token-based billing)
            search_plan = self.plan_search_strategy(query, user_id)
            
            # Step 2: Execute searches (function call billing)
            search_results = self.execute_searches(search_plan, user_id)
            
            # Step 3: Synthesize response (token-based billing)
            final_response = self.synthesize_response(query, search_results, user_id)
            
            # Add execution metadata
            processing_time = time.time() - start_time
            final_response.update({
                "processing_time": processing_time,
                "search_plan": search_plan,
                "raw_results": len(search_results),
                "agent_reasoning": [
                    {
                        "step": thought.step,
                        "thought": thought.thought,
                        "action": thought.action,
                        "tokens": thought.tokens_used
                    }
                    for thought in self.reasoning_history
                ]
            })
            
            return final_response
            
        except Exception as e:
            print(f"❌ Query processing failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "processing_time": time.time() - start_time
            }


class ResponseEnhancementService:
    """
    Post-processing service for enhanced responses
    Demonstrates different pricing tiers for value-added features
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
    
    def enhance_response_basic(self, response_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Basic response enhancement - Free
        Adds formatting and basic metadata
        """
        print("✨ Applying basic response enhancement...")
        time.sleep(0.1)
        
        enhanced = response_data.copy()
        enhanced.update({
            "enhanced": True,
            "enhancement_type": "basic",
            "formatting": {
                "answer_length": len(response_data.get("answer", "")),
                "readability_score": 7.5,
                "structure": "improved"
            },
            "cost": 0.0
        })
        
        return enhanced
    
    @meter_api_request_pay(client=None, unit_price=0.10)
    def enhance_response_ai(self, response_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        AI-powered response enhancement - $0.10
        Adds analysis, key points, and related suggestions
        """
        ResponseEnhancementService.enhance_response_ai.__wrapped__.__globals__['client'] = self.client
        
        print("🤖 Applying AI response enhancement...")
        time.sleep(1.0)  # Simulate AI processing
        
        enhanced = response_data.copy()
        enhanced.update({
            "enhanced": True,
            "enhancement_type": "ai_powered",
            "key_insights": [
                "Primary insight based on search results",
                "Secondary finding from analysis",
                "Recommendation for further action"
            ],
            "related_topics": [
                "Topic A - Related concept",
                "Topic B - Additional information", 
                "Topic C - Further reading"
            ],
            "confidence_analysis": {
                "overall_confidence": enhanced.get("confidence_score", 0.7),
                "source_reliability": 0.85,
                "completeness": 0.75
            },
            "cost": 0.10
        })
        
        return enhanced
    
    def should_charge_premium(self, *args, **kwargs):
        """Determine if premium enhancement should be charged"""
        return kwargs.get('premium_insights', False)
    
    @meter_instant_pay(
        client=None,
        amount=0.99,
        description="Premium Response Insights",
        condition_func=lambda self, *args, **kwargs: self.should_charge_premium(*args, **kwargs)
    )
    def enhance_response_premium(self, response_data: Dict[str, Any], user_id: str, premium_insights: bool = False) -> Dict[str, Any]:
        """
        Premium response enhancement - $0.99
        Adds deep analysis, trend insights, and actionable recommendations
        """
        ResponseEnhancementService.enhance_response_premium.__wrapped__.__globals__['client'] = self.client
        
        if premium_insights:
            print("💎 Applying premium response enhancement...")
            time.sleep(2.0)  # Simulate complex analysis
            
            enhanced = response_data.copy()
            enhanced.update({
                "enhanced": True,
                "enhancement_type": "premium",
                "deep_analysis": {
                    "trend_analysis": "Identified 3 key trends in the search results",
                    "gap_analysis": "Found 2 information gaps that may need additional research",
                    "impact_assessment": "High relevance for business decision making"
                },
                "actionable_recommendations": [
                    "Immediate action: Implement finding A within 1 week",
                    "Short-term: Further research on topic B within 1 month",
                    "Long-term: Consider strategic implications for Q2 planning"
                ],
                "competitive_insights": {
                    "market_position": "Strong position in 2 out of 3 key areas",
                    "opportunities": ["Opportunity 1", "Opportunity 2"],
                    "threats": ["Potential risk A", "Market shift B"]
                },
                "cost": 0.99
            })
            
            return enhanced
        else:
            # Return basic enhancement if premium not requested
            return self.enhance_response_basic(response_data, user_id)


class SearchAgentAnalytics:
    """
    Analytics service for search agent usage
    Provides insights into agent performance and costs
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
    
    def get_usage_analytics(self, user_id: str, timeframe: str = "7 days") -> Dict[str, Any]:
        """Get comprehensive usage analytics"""
        try:
            # Get meter statistics
            stats = self.client.get_meter_stats(timeframe=timeframe)
            
            # Get user meter information
            user_meter = self.client.get_user_meter(user_id=user_id)
            
            # Calculate derived metrics
            if stats.total_api_calls > 0:
                avg_cost_per_search = stats.total_cost / stats.total_api_calls
                token_efficiency = stats.total_tokens / stats.total_cost if stats.total_cost > 0 else 0
            else:
                avg_cost_per_search = 0
                token_efficiency = 0
            
            return {
                "timeframe": timeframe,
                "user_id": user_id,
                "usage_summary": {
                    "total_searches": stats.total_api_calls,
                    "total_tokens": stats.total_tokens,
                    "total_cost": stats.total_cost,
                    "avg_cost_per_search": avg_cost_per_search
                },
                "cost_breakdown": {
                    "function_calls": stats.total_api_calls * 0.035,  # Estimated average
                    "token_usage": stats.total_tokens * 0.00002,     # Estimated average
                    "premium_features": stats.total_cost - (stats.total_api_calls * 0.035) - (stats.total_tokens * 0.00002)
                },
                "user_limits": {
                    "monthly_limit": user_meter.threshold_amount,
                    "current_usage": user_meter.current_usage,
                    "remaining_budget": user_meter.remaining_budget,
                    "usage_percentage": user_meter.usage_percentage
                },
                "efficiency_metrics": {
                    "tokens_per_dollar": token_efficiency,
                    "searches_per_dollar": stats.total_api_calls / stats.total_cost if stats.total_cost > 0 else 0
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to get analytics: {e}"}


def demonstrate_comprehensive_search(client: AgentMeterClient):
    """
    Demonstrate comprehensive search agent workflow
    Shows all metering aspects in action
    """
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE SEARCH AGENT DEMONSTRATION")
    print("="*80)
    
    # Initialize services
    search_tools = SearchTools(client)
    agent = IntelligentSearchAgent(client, search_tools)
    enhancer = ResponseEnhancementService(client)
    analytics = SearchAgentAnalytics(client)
    
    demo_user = "search_agent_user_001"
    
    # Set up user subscription
    print("1. Setting up user subscription...")
    try:
        user_meter = client.set_user_meter(threshold_amount=30.0, user_id=demo_user)
        print(f"   ✅ Monthly limit: ${user_meter.threshold_amount}")
    except Exception as e:
        print(f"   ⚠️ Meter setup: {e}")
    
    # Test queries with different complexity
    test_queries = [
        "What are the latest AI development trends?",
        "Find company policies about remote work",
        "Show me technical specifications for API integration"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Search Session {i} ---")
        
        # Process the query (includes planning, searching, and synthesis)
        response = agent.process_query(query, demo_user)
        
        if "error" not in response:
            print(f"✅ Query processed successfully")
            print(f"   🔍 Sources: {response['sources_consulted']}")
            print(f"   🧠 Reasoning steps: {response['reasoning_steps']}")
            print(f"   ⏱️ Processing time: {response['processing_time']:.2f}s")
            
            # Demonstrate response enhancement
            print("\n   📈 Response Enhancement Options:")
            
            # Basic enhancement (free)
            basic_enhanced = enhancer.enhance_response_basic(response, demo_user)
            print(f"      • Basic: {basic_enhanced['enhancement_type']} (${basic_enhanced['cost']})")
            
            # AI enhancement (paid)
            ai_enhanced = enhancer.enhance_response_ai(response, demo_user)
            print(f"      • AI-powered: {ai_enhanced['enhancement_type']} (${ai_enhanced['cost']})")
            
            # Premium enhancement (premium)
            if i == 1:  # Only for first query to show premium features
                premium_enhanced = enhancer.enhance_response_premium(response, demo_user, premium_insights=True)
                print(f"      • Premium: {premium_enhanced['enhancement_type']} (${premium_enhanced['cost']})")
        else:
            print(f"❌ Query failed: {response['error']}")
    
    # Show usage analytics
    print(f"\n--- Usage Analytics ---")
    analytics_data = analytics.get_usage_analytics(demo_user, "1 day")
    
    if "error" not in analytics_data:
        print(f"📊 Usage Summary:")
        print(f"   • Total searches: {analytics_data['usage_summary']['total_searches']}")
        print(f"   • Total tokens: {analytics_data['usage_summary']['total_tokens']}")
        print(f"   • Total cost: ${analytics_data['usage_summary']['total_cost']:.2f}")
        print(f"   • Avg cost per search: ${analytics_data['usage_summary']['avg_cost_per_search']:.3f}")
        
        print(f"\n💰 Cost Breakdown:")
        breakdown = analytics_data['cost_breakdown']
        print(f"   • Function calls: ${breakdown['function_calls']:.2f}")
        print(f"   • Token usage: ${breakdown['token_usage']:.2f}")
        print(f"   • Premium features: ${breakdown['premium_features']:.2f}")
        
        print(f"\n📈 User Limits:")
        limits = analytics_data['user_limits']
        print(f"   • Usage: ${limits['current_usage']:.2f}/${limits['monthly_limit']}")
        print(f"   • Remaining: ${limits['remaining_budget']:.2f}")
        print(f"   • Percentage: {limits['usage_percentage']:.1f}%")
    else:
        print(f"❌ Analytics error: {analytics_data['error']}")


def main():
    """Main demonstration function"""
    print("🔍 AgentMeter SDK - Intelligent Search Agent Demo")
    print("=" * 80)
    print("Scenario: Multi-source search agent with AI reasoning")
    print("Metering: Token-based for AI + Function calls for searches")
    print("Features: Query planning, multi-source search, response synthesis")
    print("=" * 80)
    
    if API_KEY == "your_api_key_here":
        print("⚠️  Please set AGENTMETER_API_KEY environment variable")
        return
    
    # Create AgentMeter client
    client = create_client(
        api_key=API_KEY,
        project_id=PROJECT_ID,
        agent_id=AGENT_ID,
        user_id="search_demo_user"
    )
    
    # Test connection
    try:
        health = client.health_check()
        print(f"✅ AgentMeter connected: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Run comprehensive demonstration
    demonstrate_comprehensive_search(client)
    
    print("\n" + "="*80)
    print("✅ SEARCH AGENT DEMONSTRATION COMPLETED")
    print("="*80)
    print("\nKey features demonstrated:")
    print("• Token-based billing for LLM reasoning (input vs output pricing)")
    print("• Function call billing for search operations (different rates per function)")
    print("• Multi-tier enhancement services (free, paid, premium)")
    print("• Comprehensive usage analytics and cost tracking")
    print("• User subscription management with limits")
    print("\nPricing model showcased:")
    print("• Input tokens: $0.000015 each (query understanding)")
    print("• Output tokens: $0.000025 each (response generation)")
    print("• Web search: $0.05 per search (highest cost)")
    print("• Database search: $0.03 per query (medium cost)")
    print("• Document search: $0.02 per search (lowest cost)")
    print("• AI enhancement: $0.10 per enhancement")
    print("• Premium insights: $0.99 per detailed analysis")


if __name__ == "__main__":
    main() 