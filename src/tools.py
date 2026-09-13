"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Tra cứu ca lỗi QC cho dữ liệu gán nhãn 2D/3D
    {
        "name": "qc_query",
        "description": "Tra cứu hồ sơ và thông tin ca lỗi kiểm định chất lượng (QC) cho dữ liệu gán nhãn 2D/3D bằng mã ca lỗi.",
        "parameters": {
            "type": "object",
            "properties": {
                "qc_id": {
                    "type": "string",
                    "description": "Mã ca lỗi QC cần tra cứu (ví dụ: 'QC-2D-001' hoặc 'QC-3D-002')"
                }
            },
            "required": ["qc_id"]
        }
    },
    
    # --------------------------------------------------------------------------
    # TODO 1.2: HỌC VIÊN HOÀN THIỆN TOOL SCHEMA CHO 'create_rework_ticket'
    # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # 1. Tool dùng để tạo phiếu Rework gửi đội gán nhãn sửa lỗi kiểm định.
    # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    #    - qc_id (string): Mã ca lỗi QC cần tạo phiếu Rework (ví dụ: 'QC-2D-001', 'QC-3D-002')
    #    - reason (string): Lý do tạo phiếu hoặc mô tả lỗi cần sửa (ví dụ: 'sai nhãn đối tượng')
    #    - priority (string): Mức độ ưu tiên ('Cao', 'Trung bình', 'Thấp')
    # 3. Khai báo danh sách các trường bắt buộc: ["qc_id", "reason"].
    # --------------------------------------------------------------------------
    {
        "name": "create_rework_ticket",
        "description": "Tạo phiếu Rework kiểm định chất lượng gửi đội gán nhãn để chỉnh sửa các ca lỗi 2D/3D.",
        "parameters": {
            "type": "object",
            "properties": {
                "qc_id": {
                    "type": "string",
                    "description": "Mã ca lỗi QC cần tạo phiếu Rework (ví dụ: 'QC-2D-001' hoặc 'QC-3D-002')"
                },
                "reason": {
                    "type": "string",
                    "description": "Lý do tạo phiếu Rework hoặc chi tiết lỗi cần sửa (ví dụ: 'sai nhãn đối tượng')"
                },
                "priority": {
                    "type": "string",
                    "description": "Mức độ ưu tiên xử lý ('Cao', 'Trung bình', 'Thấp')",
                    "enum": ["Cao", "Trung bình", "Thấp"]
                }
            },
            "required": ["qc_id", "reason"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "QC-2D-001": {
        "qc_id": "QC-2D-001",
        "task_type": "2D Bounding Box",
        "dataset": "Autopilot-Front-Cam",
        "annotator": "nguyen_van_a",
        "status": "FAILED",
        "defect_type": "Sai nhãn đối tượng (Pedestrian nhầm thành Cyclist)",
        "severity": "Cao",
        "inspector": "QC_Lead_01"
    },
    "QC-3D-002": {
        "qc_id": "QC-3D-002",
        "task_type": "3D LiDAR Point Cloud",
        "dataset": "LiDAR-Velodyne-32C",
        "annotator": "tran_thi_b",
        "status": "FAILED",
        "defect_type": "Sai nhãn đối tượng (Lệch 3D Box kích thước xe tải)",
        "severity": "Cao",
        "inspector": "QC_Lead_02"
    },
    "QC-2D-003": {
        "qc_id": "QC-2D-003",
        "task_type": "2D Semantic Segmentation",
        "dataset": "Road-Surface-Lane",
        "annotator": "le_van_c",
        "status": "PASSED",
        "defect_type": "Không có lỗi",
        "severity": "None",
        "inspector": "QC_Lead_01"
    }
}


def execute_qc_query(qc_id: str) -> str:
    """Thực thi tra cứu ca lỗi QC theo mã ca kiểm định"""
    qc_key = qc_id.strip().upper()
    case = MOCK_DATABASE.get(qc_key)
    if case:
        return json.dumps({
            "status": "SUCCESS",
            "qc_id": qc_key,
            "data": case,
            "message": f"Ca kiểm định {qc_key} ({case['task_type']}): Trạng thái '{case['status']}', Lỗi: '{case['defect_type']}', Mức độ: '{case['severity']}'."
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "qc_id": qc_key,
            "message": f"Không tìm thấy dữ liệu ca kiểm định có mã '{qc_id}' trong hệ thống QC."
        }, ensure_ascii=False)


def execute_create_rework_ticket(qc_id: str, reason: str, priority: str = "Cao") -> str:
    """Thực thi tạo phiếu Rework cho ca lỗi kiểm định chất lượng"""
    ticket_id = f"RWK-{qc_id.strip().upper()}-01"
    return json.dumps({
        "status": "SUCCESS",
        "ticket_id": ticket_id,
        "qc_id": qc_id.strip().upper(),
        "reason": reason,
        "priority": priority,
        "message": f"Tạo phiếu Rework thành công: Mã phiếu '{ticket_id}' cho ca lỗi '{qc_id}' với lý do '{reason}', độ ưu tiên '{priority}'."
    }, ensure_ascii=False)


# Router gọi tool thực tế (hỗ trợ cả tên mới và fallback tên cũ)
TOOL_ROUTER = {
    "qc_query": execute_qc_query,
    "create_rework_ticket": execute_create_rework_ticket,
    # Fallback tương thích
    "academic_query": lambda student_id=None, qc_id=None, **kwargs: execute_qc_query(qc_id or student_id or "QC-2D-001"),
    "schedule_appointment": lambda qc_id=None, reason="Cần sửa lại", **kwargs: execute_create_rework_ticket(qc_id or "QC-3D-002", reason)
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("==========================================================")
    print("🛠️ KIỂM THỬ NATIVE TOOLS LAYER (src/tools.py)")
    print("==========================================================")
    print(f"✅ [TOOLS CHECK]: Đã đăng ký thành công {len(TOOLS_SCHEMA)} Native Tools trong TOOLS_SCHEMA!")
    for idx, t in enumerate(TOOLS_SCHEMA, 1):
        print(f"   {idx}. Tool '{t['name']}': {t['description']}")
    
    # Test thử Tool 1: Tra cứu ca lỗi QC
    res1_raw = dispatch_tool_call("qc_query", {"qc_id": "QC-2D-001"})
    res1 = json.loads(res1_raw)
    status1 = res1.get("status", "UNKNOWN")
    print(f"🧪 Kết quả gọi thử qc_query: Status {status1} ({res1.get('message', '')})")
    
    # Test thử Tool 2: Tạo phiếu Rework
    res2_raw = dispatch_tool_call("create_rework_ticket", {"qc_id": "QC-3D-002", "reason": "sai nhãn đối tượng", "priority": "Cao"})
    res2 = json.loads(res2_raw)
    status2 = res2.get("status", "UNKNOWN")
    print(f"🧪 Kết quả gọi thử create_rework_ticket: Status {status2} ({res2.get('message', '')})")

