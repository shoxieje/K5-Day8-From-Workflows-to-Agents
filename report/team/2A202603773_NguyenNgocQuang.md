# Báo cáo cá nhân — 2A202603773_NguyenNgocQuang

## 1. Thông tin thành viên

- Họ tên: Nguyễn Ngọc Quang
- MSSV: 2A202603773
- Email: 26ai.quangnn3@vinuni.edu.vn
- GitHub: shoxieje

## 2. Phần việc phụ trách

- Nhóm trưởng: tạo và quản lý repo nhóm `K5-L3B-DAY08-Nhom101-FromWorkflowsToAgents`, nhánh nộp `main`.
- Integration: review và merge toàn bộ PR của nhóm (#1–#6), giải quyết xung đột khi merge, giữ `main` luôn xanh.
- Sửa lỗi hợp đồng `run_claim` ở shape single và shape orchestrator sau khi review.
- Chốt bài nộp: thông tin nhóm trong `TEAM.md`, tên repo và lớp L3B, commit chốt, chạy `check_submission`.

## 3. Đóng góp cụ thể

**Commit chính** (trên `main`):

- `4375615` — fix(single): run_claim returns failed instead of raising on post-loop errors.
- `6aba155` — fix(orchestrator): never raise from run_claim, flush trace on crash, use claim view (PR #4).
- `09ac71c`, `b8511e1` — merge `main` vào branch thành viên, giải quyết xung đột `TEAM.md`.
- `fb67388` — docs: update commit hash (sửa hash sai trong báo cáo của Đinh Hoài Nam).
- `77c2fbe`, `f9b6280` — docs(team): thông tin nhóm, tên repo, lớp L3B, commit chốt.

**Review và merge PR:**

| PR | Người làm | Nội dung | Việc của nhóm trưởng |
| --- | --- | --- | --- |
| #1 | Vũ Tuấn Đạt | Shape A workflow + test | Review, merge |
| #2 | Trần Tuấn Anh | Shape B single + test | Review; thêm `4375615` sửa lỗi ném exception; giải quyết xung đột `TEAM.md`; merge |
| #3 | Đinh Hoài Nam | Shape C orchestrator | Review sau merge, tìm 5 vấn đề (xem dưới) |
| #4 | Nguyễn Ngọc Quang | Sửa orchestrator theo review PR #3 | Viết, test, merge |
| #5 | Đinh Hoài Nam | Test orchestrator + mục `TEAM.md` | Giải quyết xung đột `TEAM.md` với PR #6 (giữ cả hai thành viên), chạy lại test, merge |
| #6 | Vũ Văn Chu | Ledger + evaluation, report JSON | Kiểm file thay đổi, merge, chạy lại test |

**Quyết định kỹ thuật:**

- **`run_claim` không được ném exception** (`docs/contracts.md`). Ở shape single, các lệnh gọi MockLLM soạn câu trả lời và `issue_refund` sau vòng ReAct nằm ngoài `try`, nên lỗi DB (store bị khóa) thoát ra ngoài. Ở orchestrator, chỉ `InjectedCrash` được xử lý. Cả hai được sửa theo cùng cách với workflow: ném lại `InjectedCrash`, mọi lỗi khác trả `failed` với `exception:<tên lỗi>`, chỉ ghi tên loại lỗi, không ghi nội dung.
- **Ghi trace trước khi ném lại `InjectedCrash`** ở orchestrator, để vẫn còn bằng chứng khi crash giữa chừng; resume vẫn dựa vào ledger và idempotency của host.
- **Bỏ lớp `Trace` tự viết** ở orchestrator: lớp này chỉ gọi lại `lab8.trace.Trace` và ghi chú nói sai rằng nó lưu trace khi crash.
- **Đọc claim qua `get_claim_view`** thay vì câu `SELECT` viết tay. Phần đọc claim lần hai nằm trong `runtime.py` (code của host, không được sửa), nên orchestrator vẫn bị tính thêm một tool call; ghi rõ điều này trong PR #4 thay vì sửa file của host.
- **Không sửa file thước đo** (`metrics.py`, `durability.py`, `policy.py`, `config/`, `data/`) và không sửa code của thành viên khác ngoài các lỗi hợp đồng đã nêu.
- **Xung đột `TEAM.md`:** giữ dòng của mọi thành viên, chỉ đánh lại số thứ tự; không đổi nội dung người khác viết.

**Test đã thêm** (`src/tests/test_single_shape.py`, trong commit `4375615`):

| Test | Kiểm điều gì |
| --- | --- |
| `test_db_error_returns_failed_instead_of_raising` | Một kết nối khác giữ `BEGIN IMMEDIATE` làm store bị khóa → `run_claim` trả `failed`, `error_reason` bắt đầu bằng `exception:`, không ghi ledger |

## 4. Bằng chứng

Chạy trong `src/` trên commit chốt:

- `python -m pytest -q` → `157 passed, 248 deselected`.
- `python -m pytest -q -m student -o addopts= tests/test_public_matrix.py` → `248 passed` (cả 4 shape, T01–T14).
- `python -m pytest -q -m student -o addopts= tests/test_public_matrix.py -k orchestrator` → `62 passed` trước và sau PR #4.
- `python -m lab8.check_submission` → `0 FAIL, 0 WARN`; ba shape đều 12/12 claim public ở seed 11, `crash.json` 20/20, bảng đóng góp đủ thành viên.
- Kiểm tay PR #4: thay `issue_refund` bằng hàm ném `sqlite3.OperationalError("database is locked")` → `failed` / `exception:OperationalError`; `crash_at=before_effect` → ném `InjectedCrash` và sự kiện cuối trong trace là `crash`.
- PR #4: https://github.com/shoxieje/K5-L3B-DAY08-Nhom101-FromWorkflowsToAgents/pull/4

## 5. Công cụ AI đã dùng

- **Claude Code (Claude Opus):** review PR #3 theo `RULES.md` và `docs/contracts.md`; viết bản sửa orchestrator và single; giải quyết xung đột merge; soạn nháp mục `TEAM.md` và báo cáo này.
- **Cách tự kiểm tra:**
  - Đọc lại từng phát hiện của review, đối chiếu với code và tài liệu hợp đồng trước khi sửa; bỏ phần không sửa được trong phạm vi shape (`runtime.py`).
  - Chạy cổng host, ma trận student và `check_submission` sau mỗi lần merge.
  - Kiểm tay đường lỗi và đường crash của orchestrator.
  - Xem diff kết quả giải quyết xung đột trước khi commit, đảm bảo không mất dòng của thành viên nào.
  - Số liệu trong báo cáo lấy từ output lệnh đã chạy, không tự điền.

## 6. Tự đánh giá

- `main` có đủ ba shape, test của mọi thành viên, report JSON và tài liệu nhóm; `check_submission` sạch.
- Hiểu và giải thích được: vì sao `run_claim` không được ném exception nhưng phải để `InjectedCrash` đi qua; vì sao không sửa file của host dù orchestrator bị tính thêm tool call; vì sao giải quyết xung đột phải giữ nguyên nội dung của người khác.
- Hạn chế: review PR #3 thực hiện sau khi PR đã được merge nên phải sửa bằng PR tiếp theo; vài lỗi chữ trong báo cáo của thành viên khác (email, tiêu đề mẫu) chưa được sửa; chưa chạy tự kiểm trên bộ hidden.
