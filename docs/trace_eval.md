# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** [Nguyễn Hải Long]  
> **Mã Sinh Viên / Mã Học viên:** [2A202602471]  
> **Chủ đề Lựa chọn:** [Trợ lý Kiểm định Chất lượng (QC Assistant):* Tra cứu ca lỗi gán nhãn 2D/3D và tạo phiếu Rework kiểm định.]  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Cần xâu chuỗi nhiều bước logic (như ở TC04: Tra cứu thông tin ca kiểm định `QC-2D-001` $\rightarrow$ Đọc kết quả quan sát phân tích trạng thái có bị lỗi không $\rightarrow$ Nếu có lỗi, trích xuất dữ liệu để tự động kích hoạt tạo phiếu Rework). Chatbot đơn thuần không thể tự phân nhánh suy luận đa bước như vậy. |
| **2. Tool Interaction** | 5 / 5 | Hệ thống bắt buộc phải tương tác với MCP Server để kết nối CSDL kiểm định chất lượng gán nhãn: tra cứu thông tin ca lỗi 2D/3D và ghi nhận tạo phiếu Rework vào hệ thống. LLM không thể tự có dữ liệu nội bộ và không được phép bịa đặt (Hallucination). |
| **3. Dynamic Decision** | 5 / 5 | Hành động của Agent thay đổi linh hoạt theo kết quả Observation ở bước trước: Nếu tra cứu không tìm thấy ca lỗi (TC05 - NOT_FOUND) thì dừng và phản hồi ngoại lệ; nếu ca lỗi hợp lệ và có trạng thái cần sửa (TC04) thì mới tiếp tục gọi Tool tạo phiếu Rework; nếu người dùng chỉ hỏi nghiệp vụ chung (TC01) thì trả lời trực tiếp không gọi Tool. |
| **4. Long Horizon Goal** | 4 / 5 | Agent phải ghi nhớ và duy trì mục tiêu nghiệp vụ xuyên suốt vòng lặp ReAct: từ tiếp nhận yêu cầu, kiểm tra thông tin, xử lý ngoại lệ, đến khi xác nhận tạo phiếu Rework thành công cho kiểm định viên (QC Inspector). |
| **TỔNG ĐIỂM AGENTIC FIT** | **18 / 20** | *Đạt 18/20 điểm (> 12/20): Bài toán Trợ lý Kiểm định Chất lượng QC rất phù hợp và cần thiết để triển khai ReAct Agent System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "action_type": "TOOL_EXECUTION",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026001"
    },
    "observation": {
      "status": "SUCCESS",
      "student_id": "SV2026001",
      "data": {
        "full_name": "Nguyễn Văn An",
        "gpa": 3.85
      }
    },
    "latency_ms": 120.5
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [ ] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** ___ / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** ___ lượt.
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
