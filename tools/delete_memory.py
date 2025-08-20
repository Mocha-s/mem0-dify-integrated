from collections.abc import Generator
from typing import Any, Dict, List
import json
import httpx
import time
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class DeleteMem0Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get API key from credentials
        api_key = self.runtime.credentials["mem0_api_key"]
        
        # Get API URL from credentials or use default
        api_url = self.runtime.credentials.get("mem0_api_url", "https://api.mem0.ai").rstrip("/")
        
        # Prepare payload
        payload = {
            "user_id": tool_parameters["user_id"]
        }
        
        # Add memory_id if provided
        if "memory_id" in tool_parameters:
            payload["memory_id"] = tool_parameters["memory_id"]
        
        # 记录请求信息
        print(f"[Mem0 Plugin] 正在删除记忆:")
        if "memory_id" in payload:
            print(f"[Mem0 Plugin] - 内存ID: {payload['memory_id']}")
        print(f"[Mem0 Plugin] - 用户ID: {payload['user_id']}")
        
        # 计时开始
        start_time = time.time()
        
        # Make direct HTTP request to mem0 API
        try:
            # Determine the correct endpoint based on whether memory_id is provided
            if "memory_id" in tool_parameters:
                # Delete specific memory
                endpoint = f"{api_url}/v1/memories/{tool_parameters['memory_id']}"
                print(f"[Mem0 Plugin] 请求API: DELETE {endpoint}")
                response = httpx.delete(
                    endpoint,
                    headers={"Authorization": f"Token {api_key}"},
                    timeout=30,
                    follow_redirects=True  # Follow redirects to handle 307 properly
                )
            else:
                # Delete all memories for user
                endpoint = f"{api_url}/v1/memories"
                print(f"[Mem0 Plugin] 请求API: DELETE {endpoint}")
                response = httpx.delete(
                    endpoint,
                    json=payload,
                    headers={"Authorization": f"Token {api_key}"},
                    timeout=30,
                    follow_redirects=True  # Follow redirects to handle 307 properly
                )
            
            # 计算请求耗时
            request_time = time.time() - start_time
            print(f"[Mem0 Plugin] API请求耗时: {request_time:.3f}秒")
            
            # 检查响应状态
            print(f"[Mem0 Plugin] 响应状态码: {response.status_code}")
            
            # Handle redirect responses (301, 302, 307, 308)
            if response.status_code in [301, 302, 307, 308]:
                print(f"[Mem0 Plugin] 收到重定向响应，跳转到: {response.url}")
                # If it's a redirect, we should follow it
                response.raise_for_status()
            else:
                response.raise_for_status()
            
            # 解析响应
            result = response.json()
            print(f"[Mem0 Plugin] 收到响应: {result}")
            
            # 计算总耗时
            total_time = time.time() - start_time
            print(f"[Mem0 Plugin] 总耗时: {total_time:.3f}秒")
            
            # Return JSON format
            yield self.create_json_message({
                "status": "success",
                "message": "Memory deleted successfully",
                "payload": payload,
                "response": result
            })
            
            # Return text format
            text_response = "Memory deleted successfully\n\n"
            text_response += f"Deleted for user: {payload['user_id']}\n"
            if "memory_id" in payload:
                text_response += f"Memory ID: {payload['memory_id']}\n"
            
            yield self.create_text_message(text_response)
            
        except httpx.HTTPStatusError as e:
            error_message = f"HTTP error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "detail" in error_data:
                    error_message = f"Error: {error_data['detail']}"
            except:
                pass
            
            print(f"[Mem0 Plugin] 错误: {error_message}")
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to delete memory: {error_message}")
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            
            print(f"[Mem0 Plugin] 异常: {error_message}")
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to delete memory: {error_message}")