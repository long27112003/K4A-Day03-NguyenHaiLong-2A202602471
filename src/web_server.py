"""
🌐 WEB SERVER CHO REACT QC AGENT (ZERO-DEPENDENCY HTTP SERVER)
Phục vụ giao diện Web UI và cung cấp REST API cho ReAct QC Agent.
"""

import os
import sys
import json
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Đảm bảo import được các module trong src/
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
sys.path.append(SRC_DIR)

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from mcp_server import MCPAcademicServer
from providers import get_llm_provider
from app import run_react_agent, save_waterfall_trace, load_test_cases
from tools import MOCK_DATABASE

# Khởi tạo singleton Provider và MCP Server
provider = get_llm_provider()
mcp_server = MCPAcademicServer(server_name="vinuni-qc-mcp-server")
UI_DIR = os.path.join(BASE_DIR, "ui")


class QCReActHandler(SimpleHTTPRequestHandler):
    """Handler xử lý phục vụ static files và các REST API endpoints"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        
        # API: Lấy trạng thái hệ thống
        if parsed.path == "/api/status":
            self.send_json_response({
                "status": "ONLINE",
                "provider": provider.__class__.__name__,
                "model": getattr(provider, "model_name", "Default"),
                "server": mcp_server.server_name,
                "version": mcp_server.version
            })
            return

        # API: Lấy danh sách 5 Test Cases
        elif parsed.path == "/api/test-cases":
            try:
                test_cases = load_test_cases()
                self.send_json_response(test_cases)
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=500)
            return

        # API: Lấy dữ liệu Mock Database QC
        elif parsed.path == "/api/database":
            self.send_json_response(MOCK_DATABASE)
            return

        # API: Lấy log Waterfall Trace
        elif parsed.path == "/api/waterfall":
            trace_file = os.path.join(BASE_DIR, "docs", "trace_waterfall.json")
            if os.path.exists(trace_file):
                try:
                    with open(trace_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.send_json_response(data)
                except Exception as e:
                    self.send_json_response([], status=200)
            else:
                self.send_json_response([])
            return

        # Mặc định: Phục vụ các file tĩnh trong thư mục ui/ (index.html, style.css, app.js)
        if parsed.path == "/" or parsed.path == "":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        # API: Gửi câu hỏi đến ReAct Agent
        if parsed.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length).decode("utf-8")

            try:
                req_data = json.loads(post_body)
                user_query = req_data.get("query", "").strip()

                if not user_query:
                    self.send_json_response({"status": "ERROR", "message": "Câu hỏi không được để trống."}, status=400)
                    return

                # Thực thi ReAct Loop
                trace_logs = run_react_agent(user_query, provider, mcp_server)
                save_waterfall_trace(trace_logs)

                # Tìm Final Answer từ trace logs
                final_answer = ""
                for log in reversed(trace_logs):
                    if log.get("action_type") == "FINAL_ANSWER":
                        final_answer = log.get("output", "")
                        break

                self.send_json_response({
                    "status": "SUCCESS",
                    "query": user_query,
                    "final_answer": final_answer,
                    "trace_logs": trace_logs
                })
            except Exception as e:
                self.send_json_response({
                    "status": "ERROR",
                    "message": f"Lỗi thực thi Agent: {str(e)}"
                }, status=500)
            return

        self.send_response(404)
        self.end_headers()

    def send_json_response(self, data, status=200):
        """Tiện ích trả về JSON response chuẩn UTF-8"""
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)


def start_server(port=7860, open_browser=True):
    """Khởi động Web Server tại cổng chỉ định"""
    host = "127.0.0.1"
    server_address = (host, port)

    try:
        httpd = HTTPServer(server_address, QCReActHandler)
    except OSError:
        # Nếu cổng 7860 đang bận, thử cổng kế tiếp
        port += 1
        server_address = (host, port)
        httpd = HTTPServer(server_address, QCReActHandler)

    url = f"http://localhost:{port}"
    print("==========================================================")
    print("🌐 VINUNI QC REACT AGENT - WEB UI SERVER")
    print("==========================================================")
    print(f"🔌 LLM Provider: {provider.__class__.__name__}")
    print(f"🌐 MCP Server: {mcp_server.server_name}")
    print(f"🚀 Giao diện Web đang chạy tại: {url}")
    print("💡 Nhấn Ctrl+C trong Terminal để dừng server.\n")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Đã tắt Web Server.")
        httpd.server_close()


if __name__ == "__main__":
    port_arg = 7860
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_arg = int(sys.argv[1])
    start_server(port=port_arg, open_browser=True)
