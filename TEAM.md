# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Trần Tuấn Anh | 2A202603909 | 275679340+Tanh0406@users.noreply.github.com | Tanh0406 | Single agent (shape B) |
|   2 | Vũ Tuấn Đạt | 2A202603744 | 26ai.datvt@vinuni.edu.vn | datkunal | Workflow (shape A) |
|   3 | Vũ Văn Chu | 2A202603873 | 26ai.chuvv@vinuni.edu.vn | chur04 | Ledger + evaluation (CP3–CP5) |
|   4 | Đinh Hoài Nam | 2A202603762 | hoainam.dnu@gmai.com | hoainamdnu-arch | Orchestrator + handoff |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Vũ Tuấn Đạt | Workflow (shape A) | `1a607d2` — Implement workflow shape (A) and add workflow tests | `src/tests/test_workflow_shape.py` (6 test, 10 case) |
| Trần Tuấn Anh (Tanh0406) | Single agent (shape B) | `94bc560` feat(single): implement shape B ReAct agent with read-only tools | `src/tests/test_single_shape.py` (thêm mới, 36 test) |
| Vũ Văn Chu (chuvv) | Ledger + evaluation | `132507f` — test(ledger-eval): verify refund durability and publish public evaluation evidence | `src/tests/test_ledger_evaluation.py` (35 trường hợp), `src/tests/test_evaluation.py` (11 trường hợp) |
| Đinh Hoài Nam (hoainamdnu-arch) | Orchestrator + handoff (shape C) | `3d9f899` feat(lab8): implement Shape C orchestrator with read-only investigators | `src/tests/test_orchestrator_shape.py` (thêm mới, 6 test / 10 case) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## Trần Tuấn Anh (Tanh0406)

### Phần việc phụ trách

- Shape B `single`: `src/lab8/shapes/single.py` (vòng ReAct một agent, tối đa 8 bước).

### Đóng góp cụ thể

- Viết `decide()` chỉ chọn tool đọc theo thứ tự `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation`; mỗi bước tính một lần gọi MockLLM vào Budget.
- Số ngày trễ và số tiền lấy từ order row đã allowlist, không lấy từ ticket (T02 đúng ở cả seed 55).
- Code của shape gọi `durability.issue_refund` với quote đầy đủ, truyền `crash_at`, không nuốt `InjectedCrash` (T11, T12, T13, T14 xanh).
- Trace chỉ ghi tên tool, order view đã allowlist, quote và kết quả host; không ghi ticket, `principal_id`, `parent_secret`, header.
- Thêm `src/tests/test_single_shape.py`: quét leak trong trace, contract + trần bước, bỏ qua số ngày trong ticket ở 5 seed, claim không tồn tại fail-closed, crash `before_effect` rồi resume chỉ một refund, quote đầy đủ ở T14.

### Bằng chứng

- Commit `94bc560` trên branch `Tanh0406`.
- `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` → 62 passed.
- `python -m pytest -q` (cổng host, gồm test mới) → 90 passed.

## Vũ Tuấn Đạt

### Phần việc phụ trách

- Cài đặt và tự kiểm môi trường (CP1).
- Shape A `workflow`: `src/lab8/shapes/workflow.py` (các bước Python cố định, model chỉ soạn câu trả lời).

### Đóng góp cụ thể

- Viết workflow theo thứ tự `get_claim_view` → kiểm `order_id` (`needs_info`) → `lookup_order` theo principal (`escalated`) → `compute_compensation` → `durability.issue_refund`; MockLLM chỉ gọi một lần để soạn câu trả lời, prompt chỉ chứa status.
- Số ngày trễ và số tiền lấy từ order row đã allowlist, không parse ticket (T02 đúng ở cả seed 55).
- Truyền quote đầy đủ vào `durability.issue_refund` để host tự trừ phần đã hoàn theo đơn (T13, T14); quote > 0 luôn đi qua host để có audit `policy_denied` khi bị từ chối.
- Truyền `crash_at`, không bắt `InjectedCrash` (T11, T12 xanh); exception khác trả `failed` thay vì ném ra.
- Trace chỉ ghi `claim` (`found`, `has_order_id`), order view đã allowlist, quote, kết quả host, decision; không ghi ticket, `principal_id`, `parent_secret`, header.
- Thêm `src/tests/test_workflow_shape.py`: ticket khai sai số ngày ở 5 seed, không lấy mã đơn từ ticket, approval mượn của claim khác (`approval_claim_mismatch`), quét leak trong trace khi escalate, claim không tồn tại fail-closed, quyết định không phụ thuộc seed.

### Bằng chứng

- Commit `1a607d2` trên branch `datvu_CP1+workflow` (merge vào `main` qua PR #1).
- `python -m pytest -q -m student -o addopts= -k workflow` → 62 passed.
- `python -m pytest -q tests/test_workflow_shape.py` → 10 passed.
- Crash C-012 `after_effect_before_checkpoint` rồi resume (`R-workflow-C-012-s11`) → 1 dòng ledger 35.000, 1 audit `refund_committed`.
- Báo cáo cá nhân: `report/team/2A202603744_VuTuanDat.md`.

## Vũ Văn Chu (chuvv)

### Phần việc phụ trách

- Ledger + evaluation (CP3–CP5): kiểm chứng transaction, idempotency, crash/resume và approval trên ba shape đã merge; chạy benchmark bốn shape và tổng hợp bằng chứng.
- Báo cáo cá nhân: `report/team/2A202603873-VuVanChu.md`; số liệu evaluation trong báo cáo nhóm, ADR và research card.

### Đóng góp cụ thể

- Tạo môi trường `src/.venv` bằng Python 3.12.9, cài dependencies, kiểm smoke và `pip check`.
- Thêm 35 trường hợp ledger: ba điểm crash × ba shape × hai loại refund (cap theo approval, hoàn phần chênh); đóng/mở lại DB rồi retry hai lần; kiểm số tiền, một effect, một audit và checkpoint.
- Kiểm rollback toàn bộ refund khi insert audit lỗi, checkpoint không có effect không được thay ledger, quote thay đổi khi retry phải conflict và giữ nguyên tiền cũ; retry với approval thiếu/hết hạn/thu hồi/mượn phải bị từ chối.
- Thêm 11 trường hợp evaluation: metric năm seed với đáp án tính tay, cost của trial fail, p95, không có success; DB mới cho từng trial, nhãn ngoài ghi đè nhãn inline, kết quả tự khai phải khớp SQLite; kiểm ablation và scanner phát hiện secret/PII trên stdout.
- Thêm hai runner `src/tests/evaluate_safety.py` và `src/tests/evaluation_ablation.py`. Sinh `benchmark.json`, `crash.json`, `safety.json`, `evaluation_ablation.json` bằng công cụ; không sửa tay JSON.
- Giữ nguyên host/thước đo (`durability.py`, `metrics.py`, `policy.py`, config/data) và code ba shape của các thành viên trước.

### Bằng chứng

- Commit kỹ thuật `132507f` trên branch `2A202603873-VuVanChu`.
- Trong `src/`, dùng Python của `.venv`: `python -m pytest -q` → **147 passed, 248 deselected**; `python -m pytest -q -m student -o addopts=` → **248 passed**; hai file test mới → **46 passed**.
- `src/reports/benchmark.json`: workflow/single/orchestrator đều 70/70; swarm 69/70 (sai `R-swarm-C-002-s55`). Workflow có cost/success thấp nhất: 28,77 VND mô phỏng.
- `src/reports/crash.json`: **20/20** (suite host + swarm); test bổ sung kiểm ba shape tại cả ba điểm crash.
- `src/reports/safety.json`: 280 trial public, 0 secret leak, 0 PII leak, 0 approval bypass, 0 invalid trace, 0 unexpected ledger, 0 exception.
- `src/reports/evaluation_ablation.json`: bỏ riêng draft call của workflow vẫn 70/70; cost/success từ 28,77 xuống 27,857143 VND mô phỏng.
- Chưa có `student_drop/`; chưa báo pass rate hidden hay kết quả chấm chính thức.

## Đinh Hoài Nam 

### Phần việc phụ trách

- Shape C `orchestrator`: `src/lab8/shapes/orchestrator.py` (orchestrator điều phối + các investigator chỉ-đọc) và handoff đã sanitize.

### Đóng góp cụ thể

- Dựng handoff bằng `make_handoff` theo allowlist: `facts={}`, chỉ các tool đọc (`lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`); không đưa `parent_secret`, header hay full claim row vào facts — orchestrator tự đọc claim row rồi không forward thô (tóm tắt của LLM không thay được allowlist).
- Số ngày trễ và số tiền lấy từ order view đã allowlist của investigator (`compute_compensation`), không tin số trong ticket — tránh đúng điểm yếu `REFERENCE_WEAKNESS` của swarm (T02 đúng ở cả seed 55).
- Host là writer duy nhất: truyền quote đầy đủ vào `durability.issue_refund` để host tự trừ phần đã hoàn theo đơn và cưỡng chế approval/ownership/idempotency (T13, T14).
- Truyền `crash_at`, không bắt `InjectedCrash` để resume replay an toàn (T11, T12 xanh).
- Trace chỉ ghi handoff đã sanitize, order view đã allowlist, refund_history, quote và kết quả host; trả `trace_path` trên mọi return path (unknown_claim / needs_info / escalated / denied / resolved); không ghi ticket, `principal_id`, `parent_secret`, header.
- Thêm `src/tests/test_orchestrator_shape.py`: bỏ qua số ngày khai sai trong ticket ở 5 seed, không lấy mã đơn từ ticket, handoff sanitize theo allowlist (chỉ tool đọc, facts rỗng, không rò secret/header/ticket), quét leak trong trace khi escalate, claim không tồn tại fail-closed, crash `before_effect` rồi resume chỉ một refund.
- Kiểm chứng thêm bằng bộ test chuẩn `src/tests/test_public_matrix.py` (marker `student`) cho orchestrator → 62/62 case xanh (T01–T14).

### Bằng chứng

- Commit `3d9f899` (Shape C) và `8273dbf` (báo cáo cá nhân) trên branch `dinhhoainam`, merge vào `main` qua PR #3.
- `python -m pytest -q -m student -o addopts= tests/test_public_matrix.py -k orchestrator` → 62 passed.
- Crash C-012 `after_effect_before_checkpoint` rồi resume (`R-orchestrator-C-012-s11`) → 1 dòng ledger, 1 audit `refund_committed` (không trả trùng).
- Báo cáo cá nhân: `report/team/2A202603762_DinhHoaiNam.md`.
