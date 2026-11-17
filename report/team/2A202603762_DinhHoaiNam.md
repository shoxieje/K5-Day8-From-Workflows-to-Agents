# Báo cáo cá nhân — MSSV_HoTen

## 1. Thông tin thành viên

- Họ tên: Đinh Hoài Nam
- MSSV: 2A202603762
- Email: hoainam.dnu@gmail.com
- GitHub: hoainamdnu-arch

## 2. Phần việc phụ trách

- **Shape C — orchestrator** (`src/lab8/shapes/orchestrator.py`): hiện thực hoàn chỉnh shape "orchestrator + read-only investigators".
- Ranh giới code / model trong shape: model (MockLLM) chỉ sinh văn bản phản hồi (`draft`), không ra quyết định trả tiền; mọi quyết định về số tiền đều do code tính từ order row và do host (`durability.issue_refund`) ghi.

## 3. Đóng góp cụ thể

- **Commit chính:** `3d9f899` — *feat(lab8): implement Shape C orchestrator with read-only investigators* (1 file, +193 / −6).
- **Quyết định kỹ thuật:**
  - **Handoff theo allowlist, không dùng tóm tắt của LLM làm bộ lọc.** Gọi `make_handoff` với `facts={}` và chỉ các tool read-only (`lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`). Không đưa `parent_secret`, raw headers hay full claim row vào facts; orchestrator tự đọc claim row rồi **không** forward thô.
  - **Trust order row, không trust số trong ticket.** Quote lấy từ `compute_compensation` trên order view của investigator → tránh đúng điểm yếu `REFERENCE_WEAKNESS` của swarm (seed % 5 tin delay trong ticket).
  - **Host là writer duy nhất, truyền full quote.** Gọi `issue_refund` với nguyên quote; host tự trừ refund cũ cùng order và cưỡng chế approval/ownership/idempotency.
  - **CP3 — crash safety.** Truyền thẳng `crash_at` vào `issue_refund` và **không** bắt `InjectedCrash` để resume replay an toàn.
  - **Trace contract v1.** Ghi handoff đã sanitize + các mốc quyết định, trả `trace_path` trên **mọi** return path (unknown_claim / needs_info / escalated / denied / resolved).
- **Test:** thêm `src/tests/test_orchestrator_shape.py` (6 test / 10 case: bỏ qua số ngày khai sai ở 5 seed, không lấy mã đơn từ ticket, handoff sanitize theo allowlist, quét leak trong trace khi escalate, claim không tồn tại fail-closed, crash `before_effect` rồi resume chỉ một refund); đồng thời kiểm chứng bằng bộ test chính thức `src/tests/test_public_matrix.py` (marker `student`).

## 4. Bằng chứng

- **Commit:** https://github.com/shoxieje/K5-Day8-From-Workflows-to-Agents/commit/3d9f899
- **Test chạy qua (62/62):** `src/tests/test_public_matrix.py` — `test_public_single_run_cases[*-orchestrator]` (T01–T10, T13, T14 × seed 11/22/33/44/55), `test_t11_retry_keeps_one_refund[orchestrator]`, `test_t12_crash_before_checkpoint_does_not_double_pay[orchestrator]`.
- **Lệnh đã chạy:**
  ```bash
  cd src
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. python -m pytest -q -m student -o addopts= \
    tests/test_public_matrix.py -k orchestrator
  # => 62 passed, 186 deselected
  ```
- **Run id mẫu:** `R-orchestrator-C-001-s11` → status `resolved`, proposal 35000 VND, `committed_audit_count = 1`. Sau crash `after_effect_before_checkpoint` rồi resume: vẫn `resolved`, đúng 1 refund (không trả trùng).

## 5. Công cụ AI đã dùng

- **Công cụ:** Claude Code (Opus 4.8).
- **Dùng vào việc:** đọc các module liên quan (`handoff`, `runtime`, `durability`, `tools`, `trace`, `common`) và `swarm_reference` để hiểu contract, rồi hiện thực `orchestrator.py`;.
- **Cách tự kiểm tra kết quả:**
  - Chạy bộ test chính thức `test_public_matrix.py -k orchestrator` → 62/62 pass (không sửa `metrics.py`, `durability.py`, `policy.py`, config hay data theo RULES).
  - Chạy tay qua `python -m lab8.run` để xác nhận trạng thái, số tiền và `committed_audit_count`.
  - Diễn lại kịch bản crash → resume để tự xác nhận idempotency (ledger chỉ 1 dòng, không trả trùng).
  - Tự đối chiếu handoff không chứa `parent_secret` / header / full claim row (trial_pass quét chuỗi cấm trong trace đều pass).

## 6. Tự đánh giá
Em phụ trách shape c và đã hoàn thành orchetrator, chạy pass 62 case test public, kịch bản retry, cash --> resume. đã nắm được cách truyền full quôt cho issue_refund, hiểu được vì sao trace bỏ parent_secret, khó khăn phần môi trường test, và đã xử lý ằng cách cài pytest, trỏ basetemp. Tự đánh giá đã hoàn thành tốt phần được giao
...
