from collections.abc import Generator
from typing import Any, Dict, List
import json
import httpx
import time
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class Mem0Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get API key from credentials
        api_key = self.runtime.credentials["mem0_api_key"]
        
        # Get API URL from credentials or use default
        api_url = self.runtime.credentials.get("mem0_api_url", "https://api.mem0.ai").rstrip("/")
        
        # Format messages
        user_content = tool_parameters["user"]
        assistant_content = tool_parameters["assistant"]
        messages = [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]
        
        # 记录请求信息
        user_preview = user_content[:30] + "..." if len(user_content) > 30 else user_content
        assistant_preview = assistant_content[:30] + "..." if len(assistant_content) > 30 else assistant_content
        print(f"[Mem0 Plugin] 正在添加记忆:")
        print(f"[Mem0 Plugin] - 用户消息: {user_preview}")
        print(f"[Mem0 Plugin] - 助手回复: {assistant_preview}")
        print(f"[Mem0 Plugin] - 用户ID: {tool_parameters['user_id']}")
        
        # Prepare payload
        payload = {
            "messages": messages,
            "user_id": tool_parameters["user_id"]
        }
        
        # 计时开始
        start_time = time.time()
        
        # Make direct HTTP request to mem0 API
        try:
            # 发送请求前记录
            print(f"[Mem0 Plugin] 请求API: POST {api_url}/v1/memories/")
            
            response = httpx.post(
                f"{api_url}/v1/memories/",
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
            
            # Handle different response formats
            memory_ids = []
            
            # 处理不同格式的响应
            if isinstance(result, dict):
                if "memory_id" in result:
                    # 标准格式: {"memory_id": "xxx"}
                    memory_ids.append(result["memory_id"])
                    print(f"[Mem0 Plugin] 已处理标准格式响应, 内存ID: {result['memory_id']}")
                elif "id" in result:
                    # 备用格式: {"id": "xxx"}
                    memory_ids.append(result["id"])
                    print(f"[Mem0 Plugin] 已处理备用格式响应, 内存ID: {result['id']}")
                elif "results" in result and isinstance(result["results"], list):
                    # 结果集合格式: {"results": [{...}, ...]}
                    for r in result["results"]:
                        if isinstance(r, dict):
                            if "event" in r and r["event"] == "ADD" and "id" in r:
                                memory_ids.append(r["id"])
                            elif "id" in r:
                                memory_ids.append(r["id"])
                    print(f"[Mem0 Plugin] 已处理结果集合格式, 找到 {len(memory_ids)} 个内存ID")
            elif isinstance(result, list):
                # 直接列表格式: [{...}, ...]
                for r in result:
                    if isinstance(r, dict):
                        if "event" in r and r["event"] == "ADD" and "id" in r:
                            memory_ids.append(r["id"])
                        elif "id" in r:
                            memory_ids.append(r["id"])
                print(f"[Mem0 Plugin] 已处理列表格式, 找到 {len(memory_ids)} 个内存ID")
            
            # 记录最终结果
            if memory_ids:
                print(f"[Mem0 Plugin] 成功添加记忆, 内存ID: {', '.join(memory_ids)}")
            else:
                print(f"[Mem0 Plugin] 警告: 无法从响应中提取内存ID")
                
            # 计算总耗时
            total_time = time.time() - start_time
            print(f"[Mem0 Plugin] 总耗时: {total_time:.3f}秒")
            
            # Return JSON format
            yield self.create_json_message({
                "status": "success",
                "messages": messages,
                "memory_ids": memory_ids
            })
            
            # Return text format
            text_response = "Memory added successfully\n\n"
            text_response += "Added messages:\n"
            for msg in messages:
                text_response += f"- {msg['role']}: {msg['content']}\n"
            
            if memory_ids:
                text_response += f"\nMemory IDs: {', '.join(memory_ids)}"
            else:
                text_response += "\nNo memory IDs returned. Memory may still have been added."
            
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
            
            yield self.create_text_message(f"Failed to add memory: {error_message}")
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            
            print(f"[Mem0 Plugin] 异常: {error_message}")
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to add memory: {error_message}")