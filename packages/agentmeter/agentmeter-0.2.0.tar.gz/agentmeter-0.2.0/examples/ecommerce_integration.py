"""
AgentMeter SDK E-commerce Integration Example
电商应用集成示例

This example demonstrates how to integrate AgentMeter into an e-commerce platform
with different pricing models for various features and AI services.
"""

import os
import time
from typing import Dict, List, Any
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    PaymentType
)

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
PROJECT_ID = "ecommerce_proj_123"
AGENT_ID = "ecommerce_agent"

class EcommerceService:
    """Example e-commerce service with AgentMeter integration"""
    
    def __init__(self, api_key: str, project_id: str, agent_id: str):
        self.client = create_client(
            api_key=api_key,
            project_id=project_id,
            agent_id=agent_id,
            base_url="https://api.staging.agentmeter.money"
        )
        self.project_id = project_id
        self.agent_id = agent_id
    
    # API Request Pay Examples
    print("=== API Request Pay Examples ===")
    
    @meter_api_request_pay(client=None, unit_price=0.05)  # $0.05 per search
    def search_products(self, query: str, user_id: str) -> List[Dict]:
        """
        Product search API - charged per search request
        """
        # Inject client dynamically
        EcommerceService.search_products.__wrapped__.__globals__['client'] = self.client
        
        print(f"🔍 Searching products for: {query}")
        
        # Simulate product search
        products = [
            {"id": 1, "name": f"Product matching '{query}'", "price": 29.99},
            {"id": 2, "name": f"Another {query} item", "price": 49.99}
        ]
        
        return products
    
    @meter_api_request_pay(client=None, unit_price=0.10)  # $0.10 per recommendation request
    def get_recommendations(self, user_id: str, category: str = None) -> List[Dict]:
        """
        Product recommendation API - charged per recommendation request
        """
        EcommerceService.get_recommendations.__wrapped__.__globals__['client'] = self.client
        
        print(f"🎯 Getting recommendations for user {user_id}")
        
        # Simulate AI-powered recommendations
        recommendations = [
            {"id": 10, "name": "Recommended Item 1", "price": 39.99, "score": 0.95},
            {"id": 11, "name": "Recommended Item 2", "price": 59.99, "score": 0.89}
        ]
        
        return recommendations
    
    # Token-based Pay Examples
    print("\n=== Token-based Pay Examples ===")
    
    def extract_review_tokens(self, *args, result=None, **kwargs):
        """Extract token counts from review analysis"""
        review_text = args[0] if args else ""
        sentiment_result = result or ""
        
        # Estimate tokens (in real scenario, get from AI model response)
        input_tokens = len(review_text.split()) * 1.3
        output_tokens = len(str(sentiment_result).split()) * 1.3
        
        return int(input_tokens), int(output_tokens)
    
    @meter_token_based_pay(
        client=None,
        input_token_price=0.002,   # $0.002 per input token
        output_token_price=0.0005, # $0.0005 per output token
        tokens_extractor=lambda self, *args, **kwargs: self.extract_review_tokens(*args, **kwargs)
    )
    def analyze_product_reviews(self, review_text: str, user_id: str) -> Dict:
        """
        AI-powered review sentiment analysis - charged by token usage
        """
        EcommerceService.analyze_product_reviews.__wrapped__.__globals__['client'] = self.client
        
        print(f"🤖 Analyzing review sentiment...")
        
        # Simulate AI analysis
        time.sleep(0.5)  # Simulate processing time
        
        sentiment_analysis = {
            "sentiment": "positive",
            "confidence": 0.87,
            "keywords": ["great", "quality", "recommend"],
            "summary": "Customer is very satisfied with the product quality and recommends it."
        }
        
        return sentiment_analysis
    
    def extract_description_tokens(self, *args, result=None, **kwargs):
        """Extract token counts from product description generation"""
        product_data = args[0] if args else {}
        description = result or ""
        
        # Estimate tokens
        input_tokens = len(str(product_data).split()) * 1.2
        output_tokens = len(description.split()) * 1.3
        
        return int(input_tokens), int(output_tokens)
    
    @meter_token_based_pay(
        client=None,
        input_token_price=0.003,   # $0.003 per input token
        output_token_price=0.001,  # $0.001 per output token
        tokens_extractor=lambda self, *args, **kwargs: self.extract_description_tokens(*args, **kwargs)
    )
    def generate_product_description(self, product_data: Dict, user_id: str) -> str:
        """
        AI-generated product descriptions - charged by token usage
        """
        EcommerceService.generate_product_description.__wrapped__.__globals__['client'] = self.client
        
        print(f"✍️ Generating product description...")
        
        # Simulate AI description generation
        time.sleep(1.0)  # Simulate processing time
        
        description = f"""
        Discover the amazing {product_data.get('name', 'product')}! 
        This high-quality item offers exceptional value at ${product_data.get('price', 0)}.
        Perfect for customers looking for {product_data.get('category', 'quality products')}.
        Don't miss out on this incredible deal!
        """
        
        return description.strip()
    
    # Instant Pay Examples
    print("\n=== Instant Pay Examples ===")
    
    def should_charge_premium_support(self, *args, **kwargs):
        """Check if premium support should be charged"""
        support_type = kwargs.get('support_type', 'basic')
        return support_type in ['premium', 'priority']
    
    @meter_instant_pay(
        client=None,
        amount=9.99,
        description="Premium Customer Support",
        condition_func=lambda self, *args, **kwargs: self.should_charge_premium_support(*args, **kwargs)
    )
    def get_customer_support(self, user_id: str, issue: str, support_type: str = "basic") -> Dict:
        """
        Customer support service - premium support charged instantly
        """
        EcommerceService.get_customer_support.__wrapped__.__globals__['client'] = self.client
        
        if support_type == "premium":
            print(f"⭐ Providing premium support for: {issue}")
            response_time = "< 1 hour"
            agent_type = "Senior Support Specialist"
        else:
            print(f"📞 Providing basic support for: {issue}")
            response_time = "< 24 hours"
            agent_type = "Support Agent"
        
        return {
            "ticket_id": f"TICKET_{int(time.time())}",
            "issue": issue,
            "support_type": support_type,
            "estimated_response": response_time,
            "assigned_agent": agent_type,
            "status": "open"
        }
    
    @meter_instant_pay(client=None, amount=4.99, description="Express Shipping Upgrade")
    def upgrade_shipping(self, order_id: str, user_id: str) -> Dict:
        """
        Express shipping upgrade - charged instantly
        """
        EcommerceService.upgrade_shipping.__wrapped__.__globals__['client'] = self.client
        
        print(f"🚚 Upgrading shipping for order {order_id}")
        
        return {
            "order_id": order_id,
            "shipping_type": "express",
            "estimated_delivery": "1-2 business days",
            "tracking_priority": "high",
            "upgrade_fee": 4.99
        }
    
    # Context Manager Examples
    
    def process_bulk_order(self, user_id: str, items: List[Dict]) -> Dict:
        """
        Process bulk order with different payment types
        """
        print(f"📦 Processing bulk order for {len(items)} items")
        
        total_cost = 0
        processed_items = []
        
        # API Request Pay: Inventory check for each item
        with track_api_request_pay(
            self.client, self.project_id, self.agent_id, 
            user_id=user_id, unit_price=0.02
        ) as usage:
            print("🔍 Checking inventory...")
            usage["api_calls"] = len(items)
            usage["metadata"]["operation"] = "inventory_check"
            
            for item in items:
                # Simulate inventory check
                item["in_stock"] = True
                item["available_qty"] = 50
                processed_items.append(item)
                total_cost += item.get("price", 0)
        
        # Token-based Pay: Generate order summary
        with track_token_based_pay(
            self.client, self.project_id, self.agent_id,
            user_id=user_id,
            input_token_price=0.002,
            output_token_price=0.0008
        ) as usage:
            print("📝 Generating order summary...")
            
            # Simulate AI summary generation
            order_summary = f"Bulk order of {len(items)} items totaling ${total_cost:.2f}"
            
            # Estimate tokens
            usage["tokens_in"] = len(str(items)) // 4  # Rough estimation
            usage["tokens_out"] = len(order_summary) // 4
            usage["metadata"]["summary_length"] = len(order_summary)
        
        # Instant Pay: Premium packaging (if requested)
        if total_cost > 100:  # Auto-upgrade for large orders
            with track_instant_pay(
                self.client, self.project_id, self.agent_id,
                user_id=user_id, description="Premium packaging"
            ) as usage:
                print("🎁 Adding premium packaging...")
                usage["amount"] = 12.99
                usage["metadata"]["package_type"] = "premium"
                usage["metadata"]["order_value"] = total_cost
        
        return {
            "order_id": f"BULK_{int(time.time())}",
            "items": processed_items,
            "total_cost": total_cost,
            "summary": order_summary,
            "status": "processed"
        }
    
    # User Meter Management for Subscription Services
    
    def setup_user_subscription(self, user_id: str, plan: str) -> Dict:
        """
        Setup user subscription with meter limits
        """
        print(f"🎯 Setting up {plan} subscription for user {user_id}")
        
        # Define subscription limits
        limits = {
            "basic": 50.0,      # $50/month
            "premium": 150.0,   # $150/month
            "enterprise": 500.0 # $500/month
        }
        
        threshold = limits.get(plan, 50.0)
        
        # Set user meter
        user_meter = self.client.set_user_meter(
            threshold_amount=threshold,
            user_id=user_id
        )
        
        return {
            "user_id": user_id,
            "plan": plan,
            "monthly_limit": threshold,
            "current_usage": user_meter.current_usage,
            "status": "active"
        }
    
    def check_usage_status(self, user_id: str) -> Dict:
        """
        Check user's current usage status
        """
        user_meter = self.client.get_user_meter(user_id=user_id)
        
        usage_percentage = (user_meter.current_usage / user_meter.threshold_amount) * 100
        
        if usage_percentage >= 90:
            status = "critical"
            message = "Usage limit almost reached"
        elif usage_percentage >= 75:
            status = "warning"
            message = "Approaching usage limit"
        else:
            status = "normal"
            message = "Usage within limits"
        
        return {
            "user_id": user_id,
            "current_usage": user_meter.current_usage,
            "limit": user_meter.threshold_amount,
            "percentage": round(usage_percentage, 2),
            "status": status,
            "message": message
        }


def main():
    """Main demonstration function"""
    print("🛒 AgentMeter E-commerce Integration Example")
    print("=" * 60)
    
    if API_KEY == "your_api_key_here":
        print("⚠️  Please configure your API key before running examples")
        return
    
    # Initialize e-commerce service
    ecommerce = EcommerceService(API_KEY, PROJECT_ID, AGENT_ID)
    user_id = "customer_123"
    
    print(f"\n👤 Customer: {user_id}")
    print("=" * 60)
    
    # Example 1: API Request Pay scenarios
    print("\n1️⃣ API Request Pay Scenarios")
    print("-" * 30)
    
    try:
        # Product search
        products = ecommerce.search_products("laptop", user_id)
        print(f"Found {len(products)} products")
        
        # Get recommendations
        recommendations = ecommerce.get_recommendations(user_id, "electronics")
        print(f"Generated {len(recommendations)} recommendations")
        
    except Exception as e:
        print(f"❌ API request scenarios failed: {e}")
    
    # Example 2: Token-based Pay scenarios
    print("\n2️⃣ Token-based Pay Scenarios")
    print("-" * 30)
    
    try:
        # Review sentiment analysis
        review = "This laptop is absolutely amazing! Great performance and excellent build quality."
        sentiment = ecommerce.analyze_product_reviews(review, user_id)
        print(f"Sentiment analysis: {sentiment['sentiment']} ({sentiment['confidence']:.2f})")
        
        # Product description generation
        product_data = {"name": "Gaming Laptop Pro", "price": 1299.99, "category": "electronics"}
        description = ecommerce.generate_product_description(product_data, user_id)
        print(f"Generated description ({len(description)} chars)")
        
    except Exception as e:
        print(f"❌ Token-based scenarios failed: {e}")
    
    # Example 3: Instant Pay scenarios
    print("\n3️⃣ Instant Pay Scenarios")
    print("-" * 30)
    
    try:
        # Basic support (free)
        basic_support = ecommerce.get_customer_support(
            user_id, "Question about return policy", "basic"
        )
        print(f"Basic support ticket: {basic_support['ticket_id']}")
        
        # Premium support (charged)
        premium_support = ecommerce.get_customer_support(
            user_id, "Urgent order issue", "premium"
        )
        print(f"Premium support ticket: {premium_support['ticket_id']}")
        
        # Express shipping upgrade
        shipping_upgrade = ecommerce.upgrade_shipping("ORDER_123", user_id)
        print(f"Shipping upgraded: {shipping_upgrade['shipping_type']}")
        
    except Exception as e:
        print(f"❌ Instant pay scenarios failed: {e}")
    
    # Example 4: Bulk order processing (mixed payment types)
    print("\n4️⃣ Bulk Order Processing")
    print("-" * 30)
    
    try:
        bulk_items = [
            {"name": "Laptop", "price": 999.99},
            {"name": "Mouse", "price": 29.99},
            {"name": "Keyboard", "price": 79.99}
        ]
        
        order_result = ecommerce.process_bulk_order(user_id, bulk_items)
        print(f"Bulk order processed: {order_result['order_id']}")
        print(f"Total cost: ${order_result['total_cost']:.2f}")
        
    except Exception as e:
        print(f"❌ Bulk order processing failed: {e}")
    
    # Example 5: Subscription management
    print("\n5️⃣ Subscription Management")
    print("-" * 30)
    
    try:
        # Setup subscription
        subscription = ecommerce.setup_user_subscription(user_id, "premium")
        print(f"Subscription setup: {subscription['plan']} plan")
        print(f"Monthly limit: ${subscription['monthly_limit']}")
        
        # Check usage status
        usage_status = ecommerce.check_usage_status(user_id)
        print(f"Usage status: {usage_status['status']} ({usage_status['percentage']}%)")
        
    except Exception as e:
        print(f"❌ Subscription management failed: {e}")
    
    print("\n✅ E-commerce integration example completed!")
    print("\nThis example demonstrates how to integrate AgentMeter into")
    print("an e-commerce platform with multiple payment models:")
    print("• API Request Pay: Search, recommendations, inventory checks")
    print("• Token-based Pay: AI analysis, content generation")
    print("• Instant Pay: Premium services, upgrades")


if __name__ == "__main__":
    main() 