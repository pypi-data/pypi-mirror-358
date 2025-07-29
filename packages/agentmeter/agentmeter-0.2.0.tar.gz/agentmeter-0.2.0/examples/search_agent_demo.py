#!/usr/bin/env python3
"""
AgentMeter SDK Search Agent Demo
Search agent demonstration

A comprehensive demo showing how to build a search agent with AgentMeter integration
using all three payment types: API requests, token-based, and instant payments.
"""

import os
import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    meter_agent, PaymentType
)

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
PROJECT_ID = "search_agent_proj"
AGENT_ID = "smart_search_agent"

@dataclass
class SearchResult:
    """Search result data structure"""
    id: str
    title: str
    content: str
    relevance_score: float
    source: str
    metadata: Dict[str, Any]

@dataclass
class SearchConfig:
    """Search configuration"""
    max_results: int = 10
    enable_ai_enhancement: bool = True
    enable_semantic_search: bool = False
    premium_features: bool = False
    user_tier: str = "basic"  # basic, premium, enterprise


class SearchDatabase:
    """Simulated search database"""
    
    def __init__(self):
        self.documents = [
            {"id": "1", "title": "Python Programming Guide", "content": "Learn Python programming with examples", "tags": ["python", "programming"]},
            {"id": "2", "title": "Machine Learning Basics", "content": "Introduction to ML algorithms and concepts", "tags": ["ml", "ai"]},
            {"id": "3", "title": "Web Development Tutorial", "content": "Build modern web applications", "tags": ["web", "javascript"]},
            {"id": "4", "title": "Data Science Handbook", "content": "Complete guide to data science", "tags": ["data", "science"]},
            {"id": "5", "title": "AI Ethics Guidelines", "content": "Responsible AI development practices", "tags": ["ai", "ethics"]},
            {"id": "6", "title": "Cloud Computing Fundamentals", "content": "AWS, Azure, and GCP essentials", "tags": ["cloud", "devops"]},
            {"id": "7", "title": "Cybersecurity Best Practices", "content": "Protect your applications and data", "tags": ["security", "cyber"]},
            {"id": "8", "title": "Mobile App Development", "content": "iOS and Android development guide", "tags": ["mobile", "apps"]},
        ]
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Basic keyword search"""
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            relevance = 0
            
            # Check title match
            if query_lower in doc["title"].lower():
                relevance += 0.8
            
            # Check content match
            if query_lower in doc["content"].lower():
                relevance += 0.6
            
            # Check tags match
            for tag in doc["tags"]:
                if query_lower in tag:
                    relevance += 0.4
            
            if relevance > 0:
                results.append({
                    **doc,
                    "relevance_score": relevance + random.uniform(0, 0.2)  # Add some randomness
                })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:max_results]


@meter_agent(
    client=None,  # Will be injected dynamically
    payment_type=PaymentType.API_REQUEST_PAY,
    unit_price=0.05,  # $0.05 per search operation
    methods_to_meter=['basic_search', 'advanced_search']
)
class SmartSearchAgent:
    """Intelligent search agent with AgentMeter integration"""
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
        self.database = SearchDatabase()
        
        # Inject client into class decorator
        SmartSearchAgent.__dict__['client'] = client
        
        # Usage tracking
        self.search_count = 0
        self.total_cost = 0.0
    
    def basic_search(self, query: str, user_id: str, config: SearchConfig = None) -> List[SearchResult]:
        """
        Basic search functionality - Charged per API request count
        """
        if config is None:
            config = SearchConfig()
        
        print(f"🔍 Performing basic search for: '{query}'")
        
        # Search the database
        raw_results = self.database.search(query, config.max_results)
        
        # Convert to SearchResult objects
        results = []
        for raw in raw_results:
            result = SearchResult(
                id=raw["id"],
                title=raw["title"],
                content=raw["content"],
                relevance_score=raw["relevance_score"],
                source="database",
                metadata={
                    "tags": raw["tags"],
                    "search_type": "basic",
                    "query": query
                }
            )
            results.append(result)
        
        self.search_count += 1
        return results
    
    def extract_enhancement_tokens(self, *args, result=None, **kwargs):
        """Extract token counts from AI enhancement"""
        query = args[0] if args else ""
        results = result or []
        
        # Estimate tokens for AI enhancement
        input_tokens = len(query.split()) * 2 + len(results) * 10  # Query + result processing
        output_tokens = len(results) * 15  # Enhanced descriptions
        
        return int(input_tokens), int(output_tokens)
    
    @meter_token_based_pay(
        client=None,  # Will be injected
        input_token_price=0.00002,   # $0.00002 per input token
        output_token_price=0.00004,  # $0.00004 per output token
        tokens_extractor=lambda self, *args, **kwargs: self.extract_enhancement_tokens(*args, **kwargs)
    )
    def ai_enhance_results(self, query: str, results: List[SearchResult], user_id: str) -> List[SearchResult]:
        """
        AI-enhanced result processing - Charged based on token usage
        """
        # Inject client for decorator
        SmartSearchAgent.ai_enhance_results.__wrapped__.__globals__['client'] = self.client
        
        print(f"🤖 AI enhancing {len(results)} search results...")
        
        # Simulate AI processing
        time.sleep(0.5)  # Simulate processing time
        
        enhanced_results = []
        for result in results:
            # Simulate AI enhancement
            enhanced_content = f"{result.content} [AI-Enhanced: This result is highly relevant to '{query}' with confidence {result.relevance_score:.2f}]"
            
            enhanced_result = SearchResult(
                id=result.id,
                title=f"✨ {result.title}",
                content=enhanced_content,
                relevance_score=min(result.relevance_score * 1.2, 1.0),  # Boost relevance
                source="ai_enhanced",
                metadata={
                    **result.metadata,
                    "ai_enhanced": True,
                    "enhancement_type": "content_augmentation"
                }
            )
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def should_charge_premium(self, *args, **kwargs):
        """Determine if premium features should be charged"""
        config = kwargs.get('config')
        return config and config.premium_features
    
    @meter_instant_pay(
        client=None,  # Will be injected
        amount=2.99,
        description="Advanced semantic search",
        condition_func=lambda self, *args, **kwargs: self.should_charge_premium(*args, **kwargs)
    )
    def semantic_search(self, query: str, user_id: str, config: SearchConfig) -> List[SearchResult]:
        """
        Advanced semantic search feature - Instant payment
        """
        # Inject client for decorator
        SmartSearchAgent.semantic_search.__wrapped__.__globals__['client'] = self.client
        
        if not config.premium_features:
            print("ℹ️  Basic semantic search (limited)")
            # Return basic results
            return self.basic_search(query, user_id, config)[:3]
        
        print(f"⭐ Premium semantic search for: '{query}'")
        
        # Simulate advanced semantic search
        time.sleep(1.0)  # Simulate processing time
        
        # Get basic results first
        basic_results = self.database.search(query, config.max_results * 2)
        
        # Simulate semantic reranking
        semantic_results = []
        for raw in basic_results:
            # Simulate semantic similarity scoring
            semantic_score = random.uniform(0.7, 1.0)
            
            result = SearchResult(
                id=raw["id"],
                title=f"🎯 {raw['title']}",
                content=f"{raw['content']} [Semantic Match: {semantic_score:.2f}]",
                relevance_score=semantic_score,
                source="semantic_engine",
                metadata={
                    "tags": raw["tags"],
                    "search_type": "semantic",
                    "semantic_score": semantic_score,
                    "premium_feature": True
                }
            )
            semantic_results.append(result)
        
        # Sort by semantic score
        semantic_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return semantic_results[:config.max_results]
    
    def advanced_search(self, query: str, user_id: str, config: SearchConfig = None) -> Dict[str, Any]:
        """
        Advanced search combining multiple techniques
        """
        if config is None:
            config = SearchConfig()
        
        print(f"🚀 Advanced search pipeline for: '{query}'")
        
        search_results = {
            "query": query,
            "user_id": user_id,
            "config": config.__dict__,
            "results": [],
            "metadata": {
                "search_techniques": [],
                "total_cost": 0.0,
                "processing_time": 0.0
            }
        }
        
        start_time = time.time()
        
        # Step 1: Basic search (already metered by decorator)
        basic_results = self.basic_search(query, user_id, config)
        search_results["results"] = basic_results
        search_results["metadata"]["search_techniques"].append("basic_search")
        
        # Step 2: AI enhancement if enabled
        if config.enable_ai_enhancement:
            try:
                enhanced_results = self.ai_enhance_results(query, basic_results, user_id)
                search_results["results"] = enhanced_results
                search_results["metadata"]["search_techniques"].append("ai_enhancement")
            except Exception as e:
                print(f"⚠️  AI enhancement failed: {e}")
        
        # Step 3: Semantic search if enabled and premium
        if config.enable_semantic_search:
            try:
                semantic_results = self.semantic_search(query, user_id, config)
                # Merge semantic results with existing results
                search_results["results"] = semantic_results
                search_results["metadata"]["search_techniques"].append("semantic_search")
            except Exception as e:
                print(f"⚠️  Semantic search failed: {e}")
        
        # Calculate processing time
        end_time = time.time()
        search_results["metadata"]["processing_time"] = end_time - start_time
        
        return search_results
    
    def batch_search(self, queries: List[str], user_id: str, config: SearchConfig = None) -> Dict[str, Any]:
        """
        Batch search processing with aggregated billing
        """
        if config is None:
            config = SearchConfig()
        
        print(f"📦 Batch processing {len(queries)} search queries...")
        
        batch_results = {
            "queries": queries,
            "user_id": user_id,
            "results": {},
            "summary": {
                "total_queries": len(queries),
                "successful_queries": 0,
                "failed_queries": 0,
                "total_results": 0
            }
        }
        
        # API Request Pay: Batch search operations
        with track_api_request_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id, unit_price=0.03  # Discount for batch
        ) as api_usage:
            
            api_usage["api_calls"] = len(queries)
            api_usage["metadata"] = {
                "operation": "batch_search",
                "batch_size": len(queries),
                "discount_applied": True
            }
            
            # Process each query
            for i, query in enumerate(queries):
                try:
                    results = self.basic_search(query, user_id, config)
                    batch_results["results"][query] = [
                        {
                            "title": r.title,
                            "content": r.content,
                            "relevance_score": r.relevance_score
                        } for r in results
                    ]
                    batch_results["summary"]["successful_queries"] += 1
                    batch_results["summary"]["total_results"] += len(results)
                    
                except Exception as e:
                    batch_results["results"][query] = {"error": str(e)}
                    batch_results["summary"]["failed_queries"] += 1
        
        # Token-based Pay: AI enhancement for all results if enabled
        if config.enable_ai_enhancement and batch_results["summary"]["total_results"] > 0:
            with track_token_based_pay(
                self.client, PROJECT_ID, AGENT_ID,
                user_id=user_id,
                input_token_price=0.000015,  # Batch discount
                output_token_price=0.000025
            ) as token_usage:
                
                print("🤖 Applying AI enhancement to batch results...")
                
                # Estimate tokens for batch processing
                total_input_tokens = len(" ".join(queries)) // 4  # Rough estimation
                total_output_tokens = batch_results["summary"]["total_results"] * 20
                
                token_usage["tokens_in"] = total_input_tokens
                token_usage["tokens_out"] = total_output_tokens
                token_usage["metadata"] = {
                    "operation": "batch_ai_enhancement",
                    "queries_processed": batch_results["summary"]["successful_queries"],
                    "results_enhanced": batch_results["summary"]["total_results"]
                }
        
        return batch_results
    
    def get_search_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get search analytics and usage statistics"""
        try:
            # Get user meter status
            user_meter = self.client.get_user_meter(user_id=user_id)
            
            # Get recent search events
            events = self.client.get_events(
                user_id=user_id,
                limit=20,
                event_type="api_call"
            )
            
            # Get usage statistics
            stats = self.client.get_meter_stats(timeframe="7 days")
            
            analytics = {
                "user_id": user_id,
                "usage_summary": {
                    "current_usage": user_meter.current_usage,
                    "monthly_limit": user_meter.threshold_amount,
                    "usage_percentage": (user_meter.current_usage / user_meter.threshold_amount) * 100,
                    "remaining_budget": user_meter.threshold_amount - user_meter.current_usage
                },
                "search_stats": {
                    "total_searches": len(events),
                    "total_cost": stats.total_cost,
                    "average_cost_per_search": stats.total_cost / max(len(events), 1),
                    "api_calls": stats.total_api_calls,
                    "tokens_used": stats.total_tokens_in + stats.total_tokens_out
                },
                "recommendations": []
            }
            
            # Add recommendations based on usage
            if analytics["usage_summary"]["usage_percentage"] > 80:
                analytics["recommendations"].append("Consider upgrading to a higher tier plan")
            
            if analytics["search_stats"]["average_cost_per_search"] > 0.1:
                analytics["recommendations"].append("Enable batch processing for cost savings")
            
            return analytics
            
        except Exception as e:
            return {"error": f"Failed to get analytics: {e}"}


def main():
    """Main demonstration function"""
    print("🔍 AgentMeter Search Agent Demo")
    print("=" * 50)
    
    if API_KEY == "your_api_key_here":
        print("⚠️  Please configure AGENTMETER_API_KEY environment variable")
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
        print(f"✅ AgentMeter API connected: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ AgentMeter connection failed: {e}")
        return
    
    # Create search agent
    search_agent = SmartSearchAgent(client)
    user_id = "demo_user_123"
    
    print(f"\n🎯 Search Agent Demo - User: {user_id}")
    print("=" * 50)
    
    # Set up user subscription
    try:
        user_meter = client.set_user_meter(threshold_amount=25.0, user_id=user_id)
        print(f"📊 Set monthly search budget: ${user_meter.threshold_amount}")
    except Exception as e:
        print(f"⚠️  Failed to set user meter: {e}")
    
    # Example 1: Basic Search (API Request Pay)
    print("\n1️⃣ Basic Search Examples")
    print("-" * 30)
    
    try:
        config = SearchConfig(max_results=5)
        results = search_agent.basic_search("machine learning", user_id, config)
        print(f"✅ Found {len(results)} results for 'machine learning'")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result.title} (score: {result.relevance_score:.2f})")
    except Exception as e:
        print(f"❌ Basic search failed: {e}")
    
    # Example 2: AI-Enhanced Search (Token-based Pay)
    print("\n2️⃣ AI-Enhanced Search Examples")
    print("-" * 30)
    
    try:
        config = SearchConfig(max_results=3, enable_ai_enhancement=True)
        advanced_results = search_agent.advanced_search("python programming", user_id, config)
        print(f"✅ Advanced search completed with {len(advanced_results['results'])} enhanced results")
        print(f"   Techniques used: {', '.join(advanced_results['metadata']['search_techniques'])}")
        print(f"   Processing time: {advanced_results['metadata']['processing_time']:.2f}s")
    except Exception as e:
        print(f"❌ AI-enhanced search failed: {e}")
    
    # Example 3: Premium Semantic Search (Instant Pay)
    print("\n3️⃣ Premium Semantic Search Examples")
    print("-" * 30)
    
    try:
        # Free semantic search (limited)
        config_free = SearchConfig(enable_semantic_search=True, premium_features=False)
        free_results = search_agent.semantic_search("web development", user_id, config_free)
        print(f"✅ Free semantic search: {len(free_results)} results (limited)")
        
        # Premium semantic search (charged)
        config_premium = SearchConfig(enable_semantic_search=True, premium_features=True)
        premium_results = search_agent.semantic_search("data science", user_id, config_premium)
        print(f"✅ Premium semantic search: {len(premium_results)} results (full features)")
        
    except Exception as e:
        print(f"❌ Semantic search failed: {e}")
    
    # Example 4: Batch Processing
    print("\n4️⃣ Batch Search Processing")
    print("-" * 30)
    
    try:
        queries = [
            "artificial intelligence",
            "cloud computing", 
            "cybersecurity",
            "mobile development"
        ]
        
        config = SearchConfig(max_results=3, enable_ai_enhancement=True)
        batch_results = search_agent.batch_search(queries, user_id, config)
        
        print(f"✅ Batch search completed:")
        print(f"   Queries processed: {batch_results['summary']['successful_queries']}/{batch_results['summary']['total_queries']}")
        print(f"   Total results: {batch_results['summary']['total_results']}")
        
    except Exception as e:
        print(f"❌ Batch search failed: {e}")
    
    # Example 5: Usage Analytics
    print("\n5️⃣ Search Analytics & Monitoring")
    print("-" * 30)
    
    try:
        analytics = search_agent.get_search_analytics(user_id)
        
        if "error" not in analytics:
            print(f"📊 Usage Analytics:")
            usage = analytics["usage_summary"]
            print(f"   Budget: ${usage['current_usage']:.2f}/${usage['monthly_limit']:.2f} ({usage['usage_percentage']:.1f}%)")
            print(f"   Remaining: ${usage['remaining_budget']:.2f}")
            
            stats = analytics["search_stats"]
            print(f"   Total searches: {stats['total_searches']}")
            print(f"   Average cost per search: ${stats['average_cost_per_search']:.3f}")
            
            if analytics["recommendations"]:
                print("💡 Recommendations:")
                for rec in analytics["recommendations"]:
                    print(f"   • {rec}")
        else:
            print(f"❌ Analytics error: {analytics['error']}")
            
    except Exception as e:
        print(f"❌ Analytics failed: {e}")
    
    print("\n✅ Search Agent Demo completed!")
    print("\nThis demo showcases:")
    print("• API Request Pay: Basic search operations")
    print("• Token-based Pay: AI enhancement and processing") 
    print("• Instant Pay: Premium semantic search features")
    print("• Batch Processing: Cost-efficient bulk operations")
    print("• Usage Monitoring: Analytics and budget management")
    print("\nIntegration patterns demonstrated:")
    print("• Class-level decorators for automatic metering")
    print("• Method-specific decorators with custom pricing")
    print("• Context managers for complex operations")
    print("• Conditional charging based on feature usage")


if __name__ == "__main__":
    main() 