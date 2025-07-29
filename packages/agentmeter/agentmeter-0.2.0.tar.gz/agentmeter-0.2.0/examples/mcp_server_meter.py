"""
AgentMeter SDK - MCP Server Metering Demonstration
=================================================

PURPOSE:
This example demonstrates how to meter an MCP (Model Context Protocol) server
you build/deploy according to the demands of your business model. It shows
different approaches to track usage for MCP servers and tools.

SCENARIO:
We're building an MCP server that provides various AI-powered tools to clients.
The server offers different types of tools:
1. Basic utilities (file operations, calculations) - API request billing
2. AI processing tools (text analysis, generation) - Token-based billing
3. Premium services (advanced analytics, reports) - Instant payments

APPLICATION STRUCTURE:
- MCPServer: Main MCP server with tool registration
- MeteredTools: Collection of tools with different billing models
- UsageTracker: Tracks tool usage across all client sessions
- BillingManager: Manages different billing strategies per tool

PRICING MODEL:
1. Basic Tools: $0.02 per operation (file ops, calculations)
2. AI Tools: $0.000020 per input token, $0.000030 per output token
3. Premium Tools: $1.99-$9.99 per advanced operation
4. Bulk Operations: Discounted rates for batch processing

This demonstrates how to implement comprehensive usage tracking for
MCP servers while maintaining clean separation between tool logic
and billing concerns.
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from agentmeter import (
    AgentMeterClient, create_client,
    meter_api_request_pay, meter_token_based_pay, meter_instant_pay,
    track_api_request_pay, track_token_based_pay, track_instant_pay,
    PaymentType
)

# Configuration
API_KEY = os.getenv("AGENTMETER_API_KEY", "your_api_key_here")
PROJECT_ID = "mcp_server_tools"
AGENT_ID = "ai_tools_server"

# MCP Protocol simulation (in real implementation, use official MCP library)
class MCPMessageType(Enum):
    INITIALIZE = "initialize"
    CALL_TOOL = "call_tool"
    LIST_TOOLS = "list_tools"
    GET_TOOL_INFO = "get_tool_info"


@dataclass
class MCPTool:
    """MCP Tool definition with billing configuration"""
    name: str
    description: str
    parameters: Dict[str, Any]
    billing_type: PaymentType
    billing_config: Dict[str, Any]
    category: str = "utility"
    requires_premium: bool = False


@dataclass
class MCPRequest:
    """MCP Request message"""
    message_type: MCPMessageType
    tool_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    client_id: str = "default_client"
    session_id: str = "default_session"


@dataclass
class MCPResponse:
    """MCP Response message"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    usage_info: Optional[Dict[str, Any]] = None
    billing_info: Optional[Dict[str, Any]] = None


class MeteredMCPTools:
    """
    Collection of MCP tools with integrated AgentMeter billing
    Each tool demonstrates different billing approaches
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
        self.tools_registry = {}
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Register all available tools with their billing configurations"""
        
        # Basic utility tools - API request billing
        self.tools_registry.update({
            "file_read": MCPTool(
                name="file_read",
                description="Read contents of a file",
                parameters={"filename": {"type": "string", "required": True}},
                billing_type=PaymentType.API_REQUEST_PAY,
                billing_config={"unit_price": 0.02},
                category="file_operations"
            ),
            "file_write": MCPTool(
                name="file_write", 
                description="Write content to a file",
                parameters={"filename": {"type": "string", "required": True}, "content": {"type": "string", "required": True}},
                billing_type=PaymentType.API_REQUEST_PAY,
                billing_config={"unit_price": 0.03},
                category="file_operations"
            ),
            "calculator": MCPTool(
                name="calculator",
                description="Perform mathematical calculations",
                parameters={"expression": {"type": "string", "required": True}},
                billing_type=PaymentType.API_REQUEST_PAY,
                billing_config={"unit_price": 0.01},
                category="utility"
            ),
            "url_fetch": MCPTool(
                name="url_fetch",
                description="Fetch content from a URL",
                parameters={"url": {"type": "string", "required": True}},
                billing_type=PaymentType.API_REQUEST_PAY,
                billing_config={"unit_price": 0.05},
                category="network"
            )
        })
        
        # AI processing tools - Token-based billing
        self.tools_registry.update({
            "text_analyze": MCPTool(
                name="text_analyze",
                description="Analyze text for sentiment, topics, and insights",
                parameters={"text": {"type": "string", "required": True}, "analysis_type": {"type": "string", "default": "basic"}},
                billing_type=PaymentType.TOKEN_BASED_PAY,
                billing_config={"input_token_price": 0.000020, "output_token_price": 0.000030},
                category="ai_processing"
            ),
            "text_generate": MCPTool(
                name="text_generate",
                description="Generate text based on prompts",
                parameters={"prompt": {"type": "string", "required": True}, "max_length": {"type": "integer", "default": 500}},
                billing_type=PaymentType.TOKEN_BASED_PAY,
                billing_config={"input_token_price": 0.000025, "output_token_price": 0.000040},
                category="ai_processing"
            ),
            "text_translate": MCPTool(
                name="text_translate",
                description="Translate text between languages",
                parameters={"text": {"type": "string", "required": True}, "target_language": {"type": "string", "required": True}},
                billing_type=PaymentType.TOKEN_BASED_PAY,
                billing_config={"input_token_price": 0.000015, "output_token_price": 0.000020},
                category="ai_processing"
            ),
            "code_analyze": MCPTool(
                name="code_analyze",
                description="Analyze code for quality, security, and best practices",
                parameters={"code": {"type": "string", "required": True}, "language": {"type": "string", "required": True}},
                billing_type=PaymentType.TOKEN_BASED_PAY,
                billing_config={"input_token_price": 0.000030, "output_token_price": 0.000050},
                category="ai_processing"
            )
        })
        
        # Premium tools - Instant payment billing
        self.tools_registry.update({
            "advanced_analytics": MCPTool(
                name="advanced_analytics",
                description="Generate comprehensive analytics reports",
                parameters={"data": {"type": "array", "required": True}, "report_type": {"type": "string", "default": "standard"}},
                billing_type=PaymentType.INSTANT_PAY,
                billing_config={"amount": 1.99, "description": "Advanced Analytics Report"},
                category="premium",
                requires_premium=True
            ),
            "ai_consultation": MCPTool(
                name="ai_consultation",
                description="Get expert AI consultation and recommendations",
                parameters={"topic": {"type": "string", "required": True}, "detail_level": {"type": "string", "default": "standard"}},
                billing_type=PaymentType.INSTANT_PAY,
                billing_config={"amount": 4.99, "description": "AI Expert Consultation"},
                category="premium",
                requires_premium=True
            ),
            "custom_model_training": MCPTool(
                name="custom_model_training",
                description="Train a custom AI model for specific use case",
                parameters={"training_data": {"type": "array", "required": True}, "model_type": {"type": "string", "required": True}},
                billing_type=PaymentType.INSTANT_PAY,
                billing_config={"amount": 9.99, "description": "Custom Model Training"},
                category="premium",
                requires_premium=True
            )
        })
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        return max(1, len(text) // 4)
    
    async def execute_file_read(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute file read operation with API request billing"""
        filename = parameters.get("filename", "")
        
        with track_api_request_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id, unit_price=0.02
        ) as usage:
            
            print(f"📁 Reading file: {filename}")
            await asyncio.sleep(0.1)  # Simulate file I/O
            
            # Simulate file content (in real implementation, read actual file)
            mock_content = f"Contents of {filename}:\nThis is sample file content for demonstration purposes.\nFile operations are billed per API call."
            
            usage["api_calls"] = 1
            usage["metadata"] = {
                "operation": "file_read",
                "filename": filename,
                "content_length": len(mock_content)
            }
            
            return {
                "filename": filename,
                "content": mock_content,
                "size_bytes": len(mock_content),
                "billing_info": {"type": "api_request_pay", "cost": 0.02}
            }
    
    async def execute_file_write(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute file write operation with API request billing"""
        filename = parameters.get("filename", "")
        content = parameters.get("content", "")
        
        with track_api_request_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id, unit_price=0.03
        ) as usage:
            
            print(f"📝 Writing file: {filename}")
            await asyncio.sleep(0.2)  # Simulate file I/O
            
            usage["api_calls"] = 1
            usage["metadata"] = {
                "operation": "file_write",
                "filename": filename,
                "content_length": len(content)
            }
            
            return {
                "filename": filename,
                "bytes_written": len(content),
                "success": True,
                "billing_info": {"type": "api_request_pay", "cost": 0.03}
            }
    
    async def execute_calculator(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute calculation with API request billing"""
        expression = parameters.get("expression", "")
        
        with track_api_request_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id, unit_price=0.01
        ) as usage:
            
            print(f"🧮 Calculating: {expression}")
            await asyncio.sleep(0.05)
            
            try:
                # Simple expression evaluation (be careful in production!)
                result = eval(expression)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
            
            usage["api_calls"] = 1
            usage["metadata"] = {
                "operation": "calculation",
                "expression": expression,
                "success": success
            }
            
            return {
                "expression": expression,
                "result": result,
                "success": success,
                "error": error,
                "billing_info": {"type": "api_request_pay", "cost": 0.01}
            }
    
    async def execute_text_analyze(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute text analysis with token-based billing"""
        text = parameters.get("text", "")
        analysis_type = parameters.get("analysis_type", "basic")
        
        with track_token_based_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id,
            input_token_price=0.000020,
            output_token_price=0.000030
        ) as usage:
            
            print(f"🔍 Analyzing text ({analysis_type}): {text[:50]}...")
            await asyncio.sleep(0.5)  # Simulate AI processing
            
            input_tokens = self.estimate_tokens(text)
            
            # Generate analysis result
            analysis_result = {
                "sentiment": "positive",
                "confidence": 0.85,
                "topics": ["technology", "ai", "business"],
                "key_phrases": ["artificial intelligence", "machine learning", "automation"],
                "word_count": len(text.split()),
                "reading_level": "college"
            }
            
            if analysis_type == "detailed":
                analysis_result.update({
                    "emotion_analysis": {"joy": 0.6, "trust": 0.7, "anticipation": 0.5},
                    "entity_extraction": ["OpenAI", "Python", "API"],
                    "intent_classification": "informational"
                })
            
            output_tokens = self.estimate_tokens(json.dumps(analysis_result))
            
            usage["tokens_in"] = input_tokens
            usage["tokens_out"] = output_tokens
            usage["metadata"] = {
                "operation": "text_analysis",
                "analysis_type": analysis_type,
                "text_length": len(text)
            }
            
            cost = (input_tokens * 0.000020) + (output_tokens * 0.000030)
            
            return {
                "analysis": analysis_result,
                "tokens_used": {"input": input_tokens, "output": output_tokens},
                "billing_info": {"type": "token_based_pay", "cost": cost}
            }
    
    async def execute_text_generate(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute text generation with token-based billing"""
        prompt = parameters.get("prompt", "")
        max_length = parameters.get("max_length", 500)
        
        with track_token_based_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id,
            input_token_price=0.000025,
            output_token_price=0.000040
        ) as usage:
            
            print(f"✍️ Generating text for: {prompt[:50]}...")
            await asyncio.sleep(1.0)  # Simulate AI processing
            
            input_tokens = self.estimate_tokens(prompt)
            
            # Generate response (simulated)
            generated_text = f"This is generated content based on the prompt: '{prompt}'. " * (max_length // 100)
            generated_text = generated_text[:max_length]
            
            output_tokens = self.estimate_tokens(generated_text)
            
            usage["tokens_in"] = input_tokens
            usage["tokens_out"] = output_tokens
            usage["metadata"] = {
                "operation": "text_generation",
                "prompt_length": len(prompt),
                "max_length": max_length,
                "actual_length": len(generated_text)
            }
            
            cost = (input_tokens * 0.000025) + (output_tokens * 0.000040)
            
            return {
                "generated_text": generated_text,
                "prompt": prompt,
                "tokens_used": {"input": input_tokens, "output": output_tokens},
                "billing_info": {"type": "token_based_pay", "cost": cost}
            }
    
    async def execute_advanced_analytics(self, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute advanced analytics with instant payment billing"""
        data = parameters.get("data", [])
        report_type = parameters.get("report_type", "standard")
        
        with track_instant_pay(
            self.client, PROJECT_ID, AGENT_ID,
            user_id=user_id, amount=1.99,
            description="Advanced Analytics Report"
        ) as usage:
            
            print(f"📊 Generating advanced analytics report ({report_type})...")
            await asyncio.sleep(2.0)  # Simulate complex analysis
            
            # Generate comprehensive analytics
            analytics_report = {
                "report_type": report_type,
                "data_points_analyzed": len(data),
                "insights": [
                    "Key trend identified in data pattern A",
                    "Significant correlation found between variables X and Y",
                    "Anomaly detected in time series data"
                ],
                "recommendations": [
                    "Consider implementing strategy A for 15% improvement",
                    "Monitor metric B for early warning indicators",
                    "Optimize process C for cost reduction"
                ],
                "statistical_summary": {
                    "mean": 45.7,
                    "median": 42.3,
                    "std_dev": 12.8,
                    "confidence_interval": [38.2, 53.2]
                },
                "visualizations": [
                    "trend_chart.png",
                    "correlation_matrix.png", 
                    "distribution_histogram.png"
                ],
                "generated_at": time.time()
            }
            
            usage["metadata"] = {
                "operation": "advanced_analytics",
                "report_type": report_type,
                "data_points": len(data),
                "analysis_complexity": "high"
            }
            
            return {
                "report": analytics_report,
                "billing_info": {"type": "instant_pay", "cost": 1.99}
            }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute a tool with appropriate billing"""
        if tool_name not in self.tools_registry:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool = self.tools_registry[tool_name]
        
        # Route to appropriate execution method
        execution_map = {
            "file_read": self.execute_file_read,
            "file_write": self.execute_file_write,
            "calculator": self.execute_calculator,
            "text_analyze": self.execute_text_analyze,
            "text_generate": self.execute_text_generate,
            "advanced_analytics": self.execute_advanced_analytics,
        }
        
        if tool_name in execution_map:
            try:
                return await execution_map[tool_name](parameters, user_id)
            except Exception as e:
                return {"error": f"Tool execution failed: {str(e)}"}
        else:
            return {"error": f"Tool '{tool_name}' not implemented yet"}


class MCPServerUsageTracker:
    """
    Tracks usage across all MCP server sessions and clients
    Provides aggregated billing and analytics
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
        self.session_data = {}
        self.client_usage = {}
    
    def start_session(self, client_id: str, session_id: str, user_id: str):
        """Start tracking a new session"""
        session_key = f"{client_id}:{session_id}"
        self.session_data[session_key] = {
            "client_id": client_id,
            "session_id": session_id,
            "user_id": user_id,
            "start_time": time.time(),
            "tool_calls": [],
            "total_cost": 0.0
        }
        
        if client_id not in self.client_usage:
            self.client_usage[client_id] = {
                "total_sessions": 0,
                "total_tools_called": 0,
                "total_cost": 0.0,
                "first_seen": time.time()
            }
        
        self.client_usage[client_id]["total_sessions"] += 1
        print(f"📡 Started session {session_id} for client {client_id}")
    
    def record_tool_usage(self, client_id: str, session_id: str, tool_name: str, result: Dict[str, Any]):
        """Record tool usage for billing tracking"""
        session_key = f"{client_id}:{session_id}"
        
        if session_key in self.session_data:
            billing_info = result.get("billing_info", {})
            cost = billing_info.get("cost", 0.0)
            
            tool_record = {
                "tool_name": tool_name,
                "timestamp": time.time(),
                "cost": cost,
                "billing_type": billing_info.get("type"),
                "success": "error" not in result
            }
            
            self.session_data[session_key]["tool_calls"].append(tool_record)
            self.session_data[session_key]["total_cost"] += cost
            
            # Update client aggregates
            self.client_usage[client_id]["total_tools_called"] += 1
            self.client_usage[client_id]["total_cost"] += cost
    
    def end_session(self, client_id: str, session_id: str):
        """End session and generate summary"""
        session_key = f"{client_id}:{session_id}"
        
        if session_key in self.session_data:
            session = self.session_data[session_key]
            duration = time.time() - session["start_time"]
            
            print(f"📡 Ended session {session_id}")
            print(f"   Duration: {duration:.1f}s")
            print(f"   Tools called: {len(session['tool_calls'])}")
            print(f"   Total cost: ${session['total_cost']:.4f}")
            
            # Could implement session billing here
            return session
        
        return None
    
    def get_client_analytics(self, client_id: str) -> Dict[str, Any]:
        """Get analytics for a specific client"""
        if client_id not in self.client_usage:
            return {"error": "Client not found"}
        
        usage = self.client_usage[client_id]
        active_sessions = sum(1 for key in self.session_data.keys() if key.startswith(f"{client_id}:"))
        
        return {
            "client_id": client_id,
            "total_sessions": usage["total_sessions"],
            "active_sessions": active_sessions,
            "total_tools_called": usage["total_tools_called"],
            "total_cost": usage["total_cost"],
            "avg_cost_per_session": usage["total_cost"] / max(1, usage["total_sessions"]),
            "avg_cost_per_tool": usage["total_cost"] / max(1, usage["total_tools_called"]),
            "first_seen": usage["first_seen"],
            "client_lifetime": time.time() - usage["first_seen"]
        }


class AgentMeterMCPServer:
    """
    MCP Server with integrated AgentMeter billing
    Handles MCP protocol messages and tracks usage
    """
    
    def __init__(self, client: AgentMeterClient):
        self.client = client
        self.tools = MeteredMCPTools(client)
        self.usage_tracker = MCPServerUsageTracker(client)
        self.server_stats = {
            "start_time": time.time(),
            "total_requests": 0,
            "total_tool_calls": 0,
            "total_revenue": 0.0
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP request with usage tracking"""
        self.server_stats["total_requests"] += 1
        
        try:
            if request.message_type == MCPMessageType.LIST_TOOLS:
                return await self._handle_list_tools(request)
            
            elif request.message_type == MCPMessageType.GET_TOOL_INFO:
                return await self._handle_get_tool_info(request)
            
            elif request.message_type == MCPMessageType.CALL_TOOL:
                return await self._handle_call_tool(request)
            
            elif request.message_type == MCPMessageType.INITIALIZE:
                return await self._handle_initialize(request)
            
            else:
                return MCPResponse(
                    success=False,
                    error=f"Unknown message type: {request.message_type}"
                )
                
        except Exception as e:
            return MCPResponse(
                success=False,
                error=f"Server error: {str(e)}"
            )
    
    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle client initialization"""
        self.usage_tracker.start_session(
            request.client_id,
            request.session_id,
            request.client_id  # Using client_id as user_id for simplicity
        )
        
        return MCPResponse(
            success=True,
            result={
                "server_name": "AgentMeter MCP Server",
                "server_version": "1.0.0",
                "capabilities": ["tools", "billing", "analytics"],
                "billing_enabled": True
            }
        )
    
    async def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """Handle list tools request"""
        tools_list = []
        
        for tool_name, tool in self.tools.tools_registry.items():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "billing_type": tool.billing_type.value,
                "requires_premium": tool.requires_premium,
                "parameters": tool.parameters
            })
        
        return MCPResponse(
            success=True,
            result={
                "tools": tools_list,
                "total_tools": len(tools_list),
                "categories": list(set(tool.category for tool in self.tools.tools_registry.values()))
            }
        )
    
    async def _handle_get_tool_info(self, request: MCPRequest) -> MCPResponse:
        """Handle get tool info request"""
        tool_name = request.tool_name
        
        if tool_name not in self.tools.tools_registry:
            return MCPResponse(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        tool = self.tools.tools_registry[tool_name]
        
        return MCPResponse(
            success=True,
            result={
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "category": tool.category,
                "billing": {
                    "type": tool.billing_type.value,
                    "config": tool.billing_config,
                    "requires_premium": tool.requires_premium
                }
            }
        )
    
    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """Handle tool call request with billing"""
        tool_name = request.tool_name
        parameters = request.parameters or {}
        user_id = request.client_id  # Using client_id as user_id
        
        if tool_name not in self.tools.tools_registry:
            return MCPResponse(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        # Execute the tool
        result = await self.tools.execute_tool(tool_name, parameters, user_id)
        
        # Track usage
        self.usage_tracker.record_tool_usage(
            request.client_id,
            request.session_id,
            tool_name,
            result
        )
        
        # Update server stats
        self.server_stats["total_tool_calls"] += 1
        if "billing_info" in result:
            self.server_stats["total_revenue"] += result["billing_info"].get("cost", 0)
        
        if "error" in result:
            return MCPResponse(
                success=False,
                error=result["error"]
            )
        else:
            return MCPResponse(
                success=True,
                result=result.get("result", result),
                billing_info=result.get("billing_info")
            )
    
    def get_server_analytics(self) -> Dict[str, Any]:
        """Get server-wide analytics"""
        uptime = time.time() - self.server_stats["start_time"]
        
        return {
            "server_uptime": uptime,
            "total_requests": self.server_stats["total_requests"],
            "total_tool_calls": self.server_stats["total_tool_calls"],
            "total_revenue": self.server_stats["total_revenue"],
            "avg_revenue_per_request": self.server_stats["total_revenue"] / max(1, self.server_stats["total_requests"]),
            "requests_per_minute": (self.server_stats["total_requests"] / uptime) * 60,
            "available_tools": len(self.tools.tools_registry),
            "tool_categories": list(set(tool.category for tool in self.tools.tools_registry.values()))
        }


async def demonstrate_mcp_server_usage():
    """
    Demonstrate MCP server with AgentMeter integration
    Shows different billing models in action
    """
    print("\n" + "="*80)
    print("🖥️ MCP SERVER WITH AGENTMETER BILLING DEMONSTRATION")
    print("="*80)
    
    # Create AgentMeter client
    client = create_client(
        api_key=API_KEY,
        project_id=PROJECT_ID,
        agent_id=AGENT_ID,
        user_id="mcp_server_demo"
    )
    
    # Create MCP server
    mcp_server = AgentMeterMCPServer(client)
    
    # Simulate multiple clients connecting
    clients = ["client_001", "client_002", "client_003"]
    
    for client_id in clients:
        print(f"\n--- Client {client_id} Session ---")
        
        # Initialize client
        init_request = MCPRequest(
            message_type=MCPMessageType.INITIALIZE,
            client_id=client_id,
            session_id=f"session_{int(time.time())}"
        )
        
        init_response = await mcp_server.handle_request(init_request)
        print(f"✅ Client {client_id} initialized")
        
        # List available tools
        list_request = MCPRequest(
            message_type=MCPMessageType.LIST_TOOLS,
            client_id=client_id,
            session_id=init_request.session_id
        )
        
        list_response = await mcp_server.handle_request(list_request)
        if list_response.success:
            tools = list_response.result["tools"]
            print(f"📋 Available tools: {len(tools)}")
        
        # Demonstrate different tool types
        test_tools = [
            # Basic utility tools (API request billing)
            ("calculator", {"expression": "15 * 8 + 42"}),
            ("file_read", {"filename": "config.json"}),
            
            # AI processing tools (token billing)
            ("text_analyze", {"text": "This is a sample text for sentiment analysis and topic extraction using AI.", "analysis_type": "detailed"}),
            ("text_generate", {"prompt": "Write a brief summary about artificial intelligence", "max_length": 200}),
            
            # Premium tools (instant payment) - only for first client
            *([("advanced_analytics", {"data": [1, 2, 3, 4, 5], "report_type": "comprehensive"})] if client_id == "client_001" else [])
        ]
        
        for tool_name, params in test_tools:
            print(f"\n🔧 Calling tool: {tool_name}")
            
            call_request = MCPRequest(
                message_type=MCPMessageType.CALL_TOOL,
                tool_name=tool_name,
                parameters=params,
                client_id=client_id,
                session_id=init_request.session_id
            )
            
            call_response = await mcp_server.handle_request(call_request)
            
            if call_response.success:
                billing = call_response.billing_info or {}
                print(f"   ✅ Success - {billing.get('type', 'unknown')} billing: ${billing.get('cost', 0):.4f}")
            else:
                print(f"   ❌ Failed: {call_response.error}")
        
        # End session
        session_summary = mcp_server.usage_tracker.end_session(client_id, init_request.session_id)
        
        # Get client analytics
        client_analytics = mcp_server.usage_tracker.get_client_analytics(client_id)
        print(f"📊 Client analytics: {client_analytics['total_tools_called']} tools, ${client_analytics['total_cost']:.4f}")
    
    # Show server-wide analytics
    print(f"\n--- Server Analytics ---")
    server_analytics = mcp_server.get_server_analytics()
    print(f"📈 Server performance:")
    print(f"   • Total requests: {server_analytics['total_requests']}")
    print(f"   • Total tool calls: {server_analytics['total_tool_calls']}")
    print(f"   • Total revenue: ${server_analytics['total_revenue']:.4f}")
    print(f"   • Avg revenue per request: ${server_analytics['avg_revenue_per_request']:.4f}")
    print(f"   • Available tools: {server_analytics['available_tools']}")
    print(f"   • Tool categories: {', '.join(server_analytics['tool_categories'])}")


async def main():
    """Main demonstration function"""
    print("🖥️ AgentMeter SDK - MCP Server Billing Demo")
    print("=" * 80)
    print("Scenario: MCP server with multiple tool types and billing models")
    print("Tools: Utilities (API billing), AI processing (token billing), Premium (instant pay)")
    print("Features: Multi-client support, usage tracking, comprehensive analytics")
    print("=" * 80)
    
    if API_KEY == "your_api_key_here":
        print("⚠️  Please set AGENTMETER_API_KEY environment variable")
        return
    
    # Test AgentMeter connection
    client = create_client(
        api_key=API_KEY,
        project_id=PROJECT_ID,
        agent_id=AGENT_ID
    )
    
    try:
        health = client.health_check()
        print(f"✅ AgentMeter connected: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Run the demonstration
    await demonstrate_mcp_server_usage()
    
    print("\n" + "="*80)
    print("✅ MCP SERVER BILLING DEMONSTRATION COMPLETED")
    print("="*80)
    print("\nKey features demonstrated:")
    print("• Multi-tool MCP server with different billing models")
    print("• API request billing for utility operations")
    print("• Token-based billing for AI processing")
    print("• Instant payment billing for premium features")
    print("• Multi-client session management")
    print("• Comprehensive usage tracking and analytics")
    print("• Server-wide performance metrics")
    print("\nBilling models showcased:")
    print("• Basic tools: $0.01-$0.05 per operation")
    print("• AI tools: $0.000015-$0.000050 per token")
    print("• Premium tools: $1.99-$9.99 per advanced operation")
    print("• Real-time cost tracking across all clients")


if __name__ == "__main__":
    asyncio.run(main()) 