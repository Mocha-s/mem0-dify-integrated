from collections.abc import Generator
from typing import Any, Dict, List
import json
import httpx
import time
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class UpdateMem0Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get API key from credentials
        api_key = self.runtime.credentials["mem0_api_key"]
        
        # Get API URL from credentials or use default
        api_url = self.runtime.credentials.get("mem0_api_url", "https://api.mem0.ai").rstrip("/")
        
        # Prepare payload
        payload = {
            "memory_id": tool_parameters["memory_id"],
            "memory": tool_parameters["memory"]
        }
        
        # Add optional fields if provided
        if "categories" in tool_parameters:
            # Parse categories from comma-separated string to list
            categories_str = tool_parameters["categories"]
            if categories_str:
                payload["categories"] = [cat.strip() for cat in categories_str.split(",")]
        if "metadata" in tool_parameters:
            # Parse metadata from JSON string to dict
            import json
            metadata_str = tool_parameters["metadata"]
            if metadata_str:
                try:
                    payload["metadata"] = json.loads(metadata_str)
                except json.JSONDecodeError:
                    # If JSON parsing fails, treat as a simple string
                    payload["metadata"] = metadata_str
        
        # 记录请求信息
        print(f"[Mem0 Plugin] 正在更新记忆:")
        print(f"[Mem0 Plugin] - 内存ID: {payload['memory_id']}")
        print(f"[Mem0 Plugin] - 新内容: {payload['memory'][:50]}{'...' if len(payload['memory']) > 50 else ''}")
        
        # 计时开始
        start_time = time.time()
        
        # Make direct HTTP request to mem0 API
        try:
            # Update specific memory
            endpoint = f"{api_url}/v1/memories/{tool_parameters['memory_id']}"
            print(f"[Mem0 Plugin] 请求API: PUT {endpoint}")
            
            response = httpx.put(
                endpoint,
                json=payload,
                headers={"Authorization": f"Token {api_key}"},
                timeout=30
            )
            
            # 计算请求耗时
            request_time = time.time() - start_time
            print(f"[Mem0 Plugin] API请求耗时: {request_time:.3f}秒")
            
            # 检查响应状态
            print(f"[Mem0 Plugin] 响应状态码: {response.status_code}")
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
                "message": "Memory updated successfully",
                "payload": payload,
                "response": result
            })
            
            # Return text format
            text_response = "Memory updated successfully\n\n"
            text_response += f"Updated memory ID: {payload['memory_id']}\n"
            text_response += f"New content: {payload['memory'][:100]}{'...' if len(payload['memory']) > 100 else ''}\n"
            
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
            
            yield self.create_text_message(f"Failed to update memory: {error_message}")
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            
            print(f"[Mem0 Plugin] 异常: {error_message}")
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to update memory: {error_message}")