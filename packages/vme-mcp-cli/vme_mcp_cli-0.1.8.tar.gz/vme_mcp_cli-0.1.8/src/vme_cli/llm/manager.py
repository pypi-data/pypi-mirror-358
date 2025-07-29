"""
Simplified LLM Manager for VME Chat Client
Supports Anthropic and OpenAI with tool calling
"""

import logging
from typing import List, Dict, Any, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None

from vme_cli.config.settings import LLMConfig

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages LLM providers and chat functionality"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.anthropic_client = None
        self.openai_client = None
        self.current_provider = None
    
    async def initialize(self):
        """Initialize available LLM providers"""
        if self.config.anthropic_key and anthropic:
            try:
                self.anthropic_client = anthropic.AsyncAnthropic(
                    api_key=self.config.anthropic_key
                )
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
        
        if self.config.openai_key and openai:
            try:
                self.openai_client = openai.AsyncOpenAI(
                    api_key=self.config.openai_key
                )
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Set current provider
        if self.config.default_provider == "anthropic" and self.anthropic_client:
            self.current_provider = "anthropic"
        elif self.config.default_provider == "openai" and self.openai_client:
            self.current_provider = "openai"
        elif self.anthropic_client:
            self.current_provider = "anthropic"
        elif self.openai_client:
            self.current_provider = "openai"
        else:
            raise Exception("No LLM providers available")
        
        logger.info(f"Active LLM provider: {self.current_provider}")
    
    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, force_json: bool = False) -> Dict[str, Any]:
        """Send chat request to current LLM provider"""
        if self.current_provider == "anthropic":
            return await self._chat_anthropic(messages, tools, force_json)
        elif self.current_provider == "openai":
            return await self._chat_openai(messages, tools, force_json)
        else:
            raise Exception("No active LLM provider")
    
    async def _chat_anthropic(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, force_json: bool = False) -> Dict[str, Any]:
        """Chat using Anthropic Claude"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not available")
        
        try:
            # Convert messages to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                elif msg["role"] in ["user", "assistant"]:
                    # CRITICAL FIX: Ensure content is not empty for Anthropic API
                    content = msg.get("content", "")
                    if not content.strip():
                        logger.warning(f"Empty content in message, role: {msg['role']}")
                        # For assistant messages, provide a fallback. For user messages, skip.
                        if msg["role"] == "assistant":
                            content = "I understand."
                            logger.debug(f"Using fallback content for empty assistant message")
                        else:
                            logger.debug(f"Skipping empty user message")
                            continue
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": content
                    })
                elif msg["role"] == "tool":
                    # Add tool result as user message
                    anthropic_messages.append({
                        "role": "user",
                        "content": f"Tool result: {msg['content']}"
                    })
            
            # Simple JSON prefill for force_json mode (only when no tools to avoid conflicts)
            if force_json and anthropic_messages and not tools:
                # Add assistant prefill to force JSON format
                anthropic_messages.append({
                    "role": "assistant",
                    "content": "{\n  \"content\": \""
                })
            
            # Prepare request
            request_params = {
                "model": self.config.default_model,
                "max_tokens": 8000,  # Increased for JSON responses
                "messages": anthropic_messages
            }
            
            if system_message:
                # If force_json is enabled, enhance the system message
                if force_json:
                    enhanced_system = system_message + "\n\nCRITICAL: You MUST respond with complete, valid JSON only. No text before or after. Always close all quotes and braces. If you run out of space, make the content shorter but keep valid JSON structure."
                    request_params["system"] = enhanced_system
                else:
                    request_params["system"] = system_message
            
            # Add tools if provided
            anthropic_tools = []
            if tools:
                for tool in tools:
                    anthropic_tools.append({
                        "name": tool["name"],
                        "description": tool["description"],
                        "input_schema": tool["input_schema"]
                    })
            
            if anthropic_tools:
                request_params["tools"] = anthropic_tools
            
            # Make request
            response = await self.anthropic_client.messages.create(**request_params)
            
            # Convert response
            result = {
                "content": "",
                "tool_calls": []
            }
            
            for content_block in response.content:
                if content_block.type == "text":
                    result["content"] += content_block.text
                elif content_block.type == "tool_use":
                    result["tool_calls"].append({
                        "id": content_block.id,
                        "name": content_block.name,
                        "arguments": content_block.input
                    })
            
            # If we used JSON prefill, prepend the opening
            if force_json and not tools and result["content"] and not result["content"].strip().startswith("{"):
                result["content"] = "{\n  \"content\": \"" + result["content"]
            
            return result
            
        except Exception as e:
            logger.error(f"Anthropic chat failed: {e}")
            raise Exception(f"Anthropic error: {e}")
    
    async def _chat_openai(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, force_json: bool = False) -> Dict[str, Any]:
        """Chat using OpenAI GPT"""
        if not self.openai_client:
            raise Exception("OpenAI client not available")
        
        try:
            # Convert messages to OpenAI format
            openai_messages = []
            
            for msg in messages:
                if msg["role"] in ["system", "user", "assistant"]:
                    openai_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                elif msg["role"] == "tool":
                    openai_messages.append({
                        "role": "tool",
                        "content": msg["content"],
                        "tool_call_id": msg.get("tool_call_id", "unknown")
                    })
            
            # Prepare request
            request_params = {
                "model": "gpt-4-turbo",
                "messages": openai_messages,
                "max_tokens": 4000
            }
            
            # Add JSON mode if requested
            if force_json:
                request_params["response_format"] = {"type": "json_object"}
            
            # Add tools if provided
            if tools:
                openai_tools = []
                for tool in tools:
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["input_schema"]
                        }
                    })
                request_params["tools"] = openai_tools
            
            # Make request
            response = await self.openai_client.chat.completions.create(**request_params)
            
            # Convert response
            message = response.choices[0].message
            result = {
                "content": message.content or "",
                "tool_calls": []
            }
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": eval(tool_call.function.arguments)  # JSON string to dict
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI chat failed: {e}")
            raise Exception(f"OpenAI error: {e}")
    
    def get_current_provider(self) -> str:
        """Get the current active provider"""
        return self.current_provider or "none"
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        providers = []
        if self.anthropic_client:
            providers.append("anthropic")
        if self.openai_client:
            providers.append("openai")
        return providers