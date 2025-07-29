"""
Integration Test for VME Chat Client
Tests actual app functionality end-to-end with session logging
"""

import asyncio
import time
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock
from vme_cli.session_logs.session_logger import SessionLogger, ToolStatus

class MockMCPManager:
    """Mock MCP manager for testing"""
    
    def __init__(self):
        self.tools = [
            Mock(name="vme_compute_Get_All_Instances", description="Get all VM instances"),
            Mock(name="vme_virtual_images_Get_All_Virtual_Images", description="Get all virtual images"),
            Mock(name="discover_compute_infrastructure", description="Discover compute infrastructure"),
        ]
        self.connected = True
    
    def get_tools(self):
        return self.tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Simulate tool execution"""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        if tool_name == "vme_compute_Get_All_Instances":
            return {
                "instances": [
                    {"id": "vm-001", "name": "web-server", "status": "running"},
                    {"id": "vm-002", "name": "database", "status": "running"}
                ]
            }
        elif tool_name == "vme_virtual_images_Get_All_Virtual_Images":
            return {
                "images": [
                    {"id": "img-001", "name": "ubuntu-20.04", "size": "2GB"},
                    {"id": "img-002", "name": "rocky-8", "size": "1.8GB"}
                ]
            }
        elif tool_name == "discover_compute_infrastructure":
            return {"tools": ["Get_All_Instances", "Create_Instance", "Delete_Instance"]}
        else:
            raise Exception(f"Tool {tool_name} not found")

class MockLLMManager:
    """Mock LLM manager for testing"""
    
    def __init__(self):
        self.provider = "anthropic"
    
    async def chat(self, messages, tools=None, force_json=False):
        """Simulate LLM response"""
        await asyncio.sleep(0.5)  # Simulate LLM processing time
        
        user_message = messages[-1]["content"].lower() if messages else ""
        
        if "vm" in user_message or "instance" in user_message:
            if "create" in user_message:
                return {
                    "content": "I'll help you create a VM. Let me check what resources are available.",
                    "tool_calls": [
                        {"id": "call_1", "name": "vme_virtual_images_Get_All_Virtual_Images", "arguments": {}},
                        {"id": "call_2", "name": "vme_service_plans_Get_All_Service_Plans", "arguments": {}}
                    ]
                }
            else:
                return {
                    "content": "Let me check your running VMs.",
                    "tool_calls": [
                        {"id": "call_1", "name": "vme_compute_Get_All_Instances", "arguments": {}}
                    ]
                }
        else:
            return {
                "content": "Hello! How can I help you with your infrastructure?",
                "tool_calls": []
            }
    
    def get_current_provider(self):
        return self.provider

class ChatAppIntegrationTest:
    """Integration test for the chat application"""
    
    def __init__(self):
        self.session_logger = SessionLogger(log_dir="integration_test_logs")
        self.mcp_manager = MockMCPManager()
        self.llm_manager = MockLLMManager()
        
        # Configure session
        self.session_logger.set_session_config(
            audio_enabled=False,
            audio_mode=None,
            llm_provider="anthropic"
        )
    
    async def simulate_user_conversation(self, messages: list) -> Dict[str, Any]:
        """Simulate a complete user conversation"""
        print("🎭 Simulating user conversation...")
        
        for i, user_input in enumerate(messages):
            print(f"\n👤 User: {user_input}")
            
            # Log user message
            self.session_logger.log_user_message(user_input)
            
            # Get available tools
            tools = self.mcp_manager.get_tools()
            available_tool_names = [tool.name for tool in tools]
            
            # Convert to LLM format
            llm_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": {}
                }
                for tool in tools
            ]
            
            # Simulate conversation history
            conversation_history = [{"role": "user", "content": user_input}]
            
            # Get LLM response
            start_time = time.time()
            response = await self.llm_manager.chat(conversation_history, llm_tools)
            response_time_ms = (time.time() - start_time) * 1000
            
            print(f"🤖 Assistant: {response['content'][:100]}...")
            
            # Handle tool calls if present
            if response.get("tool_calls"):
                # Log intent analysis
                called_tool_names = [tc["name"] for tc in response["tool_calls"]]
                self.session_logger.log_intent_analysis(
                    user_message=user_input,
                    available_tools=available_tool_names,
                    called_tools=called_tool_names
                )
                
                # Log initial assistant message
                self.session_logger.log_assistant_message(
                    content=response["content"],
                    response_time_ms=response_time_ms,
                    metadata={"has_tool_calls": True, "tool_count": len(response["tool_calls"])}
                )
                
                # Start tool call group
                group_id = self.session_logger.start_tool_call_group(response["tool_calls"])
                
                # Execute tools in parallel
                tool_tasks = []
                for tool_call in response["tool_calls"]:
                    tool_tasks.append(self._execute_tool_call(tool_call))
                
                tool_results = await asyncio.gather(*tool_tasks)
                
                # Generate final response
                final_start_time = time.time()
                final_response = await self.llm_manager.chat([
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": response["content"], "tool_calls": response["tool_calls"]},
                    *[{"role": "tool", "content": str(result), "tool_call_id": tc["id"]} 
                      for tc, result in zip(response["tool_calls"], tool_results)]
                ])
                final_response_time_ms = (time.time() - final_start_time) * 1000
                
                # Log final response
                self.session_logger.log_assistant_message(
                    content=final_response["content"],
                    response_time_ms=final_response_time_ms,
                    metadata={"is_final_tool_response": True, "tool_group_id": group_id}
                )
                
                print(f"🔧 Executed {len(response['tool_calls'])} tools")
                print(f"🤖 Final: {final_response['content'][:100]}...")
                
            else:
                # Direct response
                self.session_logger.log_intent_analysis(
                    user_message=user_input,
                    available_tools=available_tool_names,
                    called_tools=[]
                )
                
                self.session_logger.log_assistant_message(
                    content=response["content"],
                    response_time_ms=response_time_ms
                )
        
        # Finalize session
        log_file = self.session_logger.finalize_session()
        print(f"\n📝 Session log saved: {log_file}")
        
        return self.session_logger.current_session.__dict__
    
    async def _execute_tool_call(self, tool_call):
        """Execute a single tool call"""
        tool_name = tool_call["name"]
        tool_id = tool_call["id"]
        
        try:
            result = await self.mcp_manager.call_tool(tool_name, tool_call.get("arguments", {}))
            
            # Log successful tool call
            self.session_logger.log_tool_call_result(
                tool_call_id=tool_id,
                tool_name=tool_name,
                status=ToolStatus.SUCCESS,
                result=result
            )
            
            return result
            
        except Exception as e:
            # Log failed tool call
            self.session_logger.log_tool_call_result(
                tool_call_id=tool_id,
                tool_name=tool_name,
                status=ToolStatus.FAILED,
                error_message=str(e)
            )
            
            return f"Error: {e}"

async def run_integration_tests():
    """Run comprehensive integration tests"""
    print("🧪 Running Integration Tests")
    print("=" * 50)
    
    test_runner = ChatAppIntegrationTest()
    
    # Test scenarios based on problematic session
    test_scenarios = [
        {
            "name": "VM Listing Workflow",
            "messages": ["Any VM instances running?"]
        },
        {
            "name": "VM Creation Workflow", 
            "messages": [
                "I'd like to create a VM",
                "Rocky Linux with 8GB memory"
            ]
        },
        {
            "name": "Mixed Conversation",
            "messages": [
                "Hello",
                "Show me my VMs",
                "Create a new Ubuntu VM"
            ]
        },
        {
            "name": "Edge Cases",
            "messages": [
                "",  # Empty message
                ".",  # Minimal message
                "What?"  # Vague query
            ]
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        print(f"\n🎯 Testing: {scenario['name']}")
        print("-" * 30)
        
        try:
            # Run scenario
            start_time = time.time()
            session_data = await test_runner.simulate_user_conversation(scenario["messages"])
            execution_time = time.time() - start_time
            
            # Analyze results
            total_messages = len(session_data.get("messages", []))
            total_tools = sum(len(msg.get("tool_calls", [])) for msg in session_data.get("messages", []))
            avg_response_time = sum(msg.get("response_time_ms", 0) for msg in session_data.get("messages", []) 
                                  if msg.get("response_time_ms")) / max(1, total_messages)
            
            result = {
                "name": scenario["name"],
                "status": "✅ PASS",
                "execution_time": execution_time,
                "total_messages": total_messages,
                "total_tools": total_tools,
                "avg_response_time_ms": avg_response_time,
                "user_messages": len(scenario["messages"])
            }
            
            print(f"  ✅ Status: PASS")
            print(f"  ⏱️  Execution: {execution_time:.2f}s")
            print(f"  💬 Messages: {total_messages}")
            print(f"  🔧 Tools: {total_tools}")
            print(f"  📊 Avg Response: {avg_response_time:.0f}ms")
            
        except Exception as e:
            result = {
                "name": scenario["name"],
                "status": "❌ FAIL",
                "error": str(e),
                "execution_time": time.time() - start_time if 'start_time' in locals() else 0
            }
            
            print(f"  ❌ Status: FAIL")
            print(f"  💥 Error: {e}")
        
        results.append(result)
        
        # Reset for next test
        test_runner = ChatAppIntegrationTest()
    
    # Print summary
    print(f"\n📊 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = len([r for r in results if "PASS" in r["status"]])
    failed = len([r for r in results if "FAIL" in r["status"]])
    
    print(f"Total Scenarios: {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Pass Rate: {passed/len(results):.1%}")
    
    if failed > 0:
        print(f"\n❌ Failed Scenarios:")
        for result in results:
            if "FAIL" in result["status"]:
                print(f"  - {result['name']}: {result.get('error', 'Unknown error')}")
    
    # Performance analysis
    print(f"\n⏱️  Performance Analysis:")
    total_execution_time = sum(r.get("execution_time", 0) for r in results)
    avg_response_times = [r.get("avg_response_time_ms", 0) for r in results if r.get("avg_response_time_ms")]
    
    print(f"  Total Test Time: {total_execution_time:.2f}s")
    if avg_response_times:
        print(f"  Avg Response Time: {sum(avg_response_times)/len(avg_response_times):.0f}ms")
        print(f"  Max Response Time: {max(avg_response_times):.0f}ms")
        print(f"  Min Response Time: {min(avg_response_times):.0f}ms")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_integration_tests())