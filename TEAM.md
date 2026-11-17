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
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Vũ Tuấn Đạt | Workflow (shape A) | `1a607d2` — Implement workflow shape (A) and add workflow tests | `src/tests/test_workflow_shape.py` (6 test, 10 case) |
| Trần Tuấn Anh (Tanh0406) | Single agent (shape B) | `94bc560` feat(single): implement shape B ReAct agent with read-only tools | `src/tests/test_single_shape.py` (thêm mới, 36 test) |

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

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
