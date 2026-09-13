"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MCPAcademicServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    """
    def __init__(self, server_name: str = "vinuni-academic-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA
        
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [TASK 2.1] HỌC VIÊN HOÀN THIỆN HÀM THỰC THI TOOL TRÊN MCP SERVER
        Thực thi request gọi Tool theo chuẩn MCP JSON-RPC
        """
        # Gọi hàm dispatch_tool_call để lấy chuỗi JSON kết quả từ Tool Router.
        result_json = dispatch_tool_call(tool_name, arguments)

        # Chuyển đổi chuỗi JSON kết quả thành Python Dictionary (dùng json.loads).
        result_dict = json.loads(result_json)

        # Đóng gói phản hồi và trả về Dict theo đúng chuẩn giao thức MCP JSON-RPC 2.0:
        # - Các trường bắt buộc: "jsonrpc": "2.0", "server": self.server_name, "tool": tool_name, "result": content
        response = {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": result_dict
        }
        return response


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (vinuni-qc-mcp-server)")
    print("==========================================================")
    
    server = MCPAcademicServer(server_name="vinuni-qc-mcp-server")
    tools = server.list_tools()
    print(f"✅ [MCP SERVER] Đã khởi tạo thành công {server.server_name} (Version: {server.version})")
    print(f"📦 Số lượng Tools công bố qua MCP: {len(tools)}")
    
    # Kiểm tra trạng thái TODO 1.2 (Tool Schema)
    rework_tool = next((t for t in tools if t.get("name") in ["create_rework_ticket", "schedule_appointment"]), None)
    if rework_tool and not rework_tool.get("parameters", {}).get("properties"):
        print(f"⏳ [TODO 1.2]: Tool '{rework_tool.get('name')}' chưa được định nghĩa properties trong 'src/tools.py'.")
    else:
        tool_name_found = rework_tool.get("name") if rework_tool else "create_rework_ticket"
        print(f"✅ [TODO 1.2]: Tool '{tool_name_found}' đã có schema đầy đủ.")

    # Kiểm tra trạng thái TODO 2.1 (call_tool)
    test_tool_name = "qc_query" if any(t.get("name") == "qc_query" for t in tools) else "academic_query"
    test_args = {"qc_id": "QC-2D-001"} if test_tool_name == "qc_query" else {"student_id": "SV2026001"}
    
    test_result = server.call_tool(test_tool_name, test_args)
    if not test_result or not test_result.get("result"):
        print("⏳ [TODO 2.1]: Hàm call_tool() đang trả về rỗng. Học viên hãy hoàn thiện TODO 2.1 trong 'src/mcp_server.py'!")
    else:
        print(f"✅ [TODO 2.1]: Test dispatch tool '{test_tool_name}' thành công:")
        print(f"   Phản hồi JSON-RPC: {json.dumps(test_result, ensure_ascii=False)}")
