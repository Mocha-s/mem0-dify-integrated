from collections.abc import Generator
from typing import Any, Dict, List
import json
import httpx
import time
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RetrieveMem0Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get API key from credentials
        api_key = self.runtime.credentials["mem0_api_key"]
        
        # Get API URL from credentials or use default
        api_url = self.runtime.credentials.get("mem0_api_url", "https://api.mem0.ai").rstrip("/")
        
        # Prepare payload for search
        payload = {
            "query": tool_parameters["query"],
            "user_id": tool_parameters["user_id"]
        }

        # 记录请求信息
        query_preview = payload["query"][:50] + "..." if len(payload["query"]) > 50 else payload["query"]
        print(f"[Mem0 Plugin] 正在搜索记忆: '{query_preview}', user_id: {payload['user_id']}")
        
        # 计时开始
        start_time = time.time()
        
        # Make direct HTTP request to mem0 API
        try:
            response = httpx.post(
                f"{api_url}/v1/memories/search/",
                json=payload,
                headers={"Authorization": f"Token {api_key}"},
                timeout=30
            )
            
            # 计算请求耗时
            request_time = time.time() - start_time
            print(f"[Mem0 Plugin] API请求耗时: {request_time:.3f}秒")
            
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            
            # Process results based on response format
            # The Mem0 API returns {"results": [...]} format
            if isinstance(response_data, dict) and "results" in response_data:
                print(f"[Mem0 Plugin] 收到包装格式响应 {{'results': [...]}} (老格式)")
                results = response_data["results"]
            # Handle direct list format (for backward compatibility)
            elif isinstance(response_data, list):
                print(f"[Mem0 Plugin] 收到直接数组响应 [...] (新格式)")
                results = response_data
            else:
                # Fallback for unexpected format
                print(f"[Mem0 Plugin] 警告: 收到未预期的响应格式: {type(response_data)}")
                results = []
                yield self.create_json_message({
                    "query": tool_parameters["query"],
                    "results": []
                })
                yield self.create_text_message(f"Query: {tool_parameters['query']}\n\nUnexpected response format: {response_data}")
                return
            
            # Return JSON format with safe access to fields
            processed_results = []
            for r in results:
                if not isinstance(r, dict):
                    continue
                    
                item = {
                    "id": r.get("id", "unknown"),
                    "memory": r.get("memory", ""),
                    "score": r.get("score", 0.0),
                    "categories": r.get("categories", []),
                    "created_at": r.get("created_at", "")
                }
                processed_results.append(item)
            
            # 记录结果统计
            print(f"[Mem0 Plugin] 搜索完成, 获取到 {len(processed_results)} 条记忆")
            
            # 计算总耗时
            total_time = time.time() - start_time
            print(f"[Mem0 Plugin] 总耗时: {total_time:.3f}秒")
                
            yield self.create_json_message({
                "query": tool_parameters["query"],
                "results": processed_results
            })
            
            # Return text format
            text_response = f"Query: {tool_parameters['query']}\n\nResults:\n"
            if processed_results:
                for idx, r in enumerate(processed_results, 1):
                    text_response += f"\n{idx}. Memory: {r['memory']}"
                    text_response += f"\n   Score: {r['score']:.2f}"
                    text_response += f"\n   Categories: {', '.join(r.get('categories', []))}"
            else:
                text_response += "\nNo results found."
                
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
            
            yield self.create_text_message(f"Failed to retrieve memory: {error_message}")
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            
            print(f"[Mem0 Plugin] 异常: {error_message}")
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to retrieve memory: {error_message}")
