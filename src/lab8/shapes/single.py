"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.

Design notes (nhóm):
- decide() là "model" của vòng ReAct: mỗi bước gọi MockLLM một lần (tính cost),
  nhưng việc chọn tool đi theo một kế hoạch cố định chỉ gồm tool đọc:
  get_claim_view -> lookup_order -> lookup_refund_history -> compute_compensation -> final.
- Số ngày trễ, trạng thái đơn, số tiền đều lấy từ kết quả tool (order row đã qua
  allowlist), không bao giờ lấy từ chữ trong ticket.
- Sau vòng lặp, code của shape (không phải model) gọi durability.issue_refund với
  quote đầy đủ. Host kiểm approval, trần theo đơn, idempotency.
- Trace chỉ ghi tên tool, status/reason, order view đã allowlist và quote.
  Không ghi ticket, principal_id, claim row thô, parent_secret hay header.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    try:
        loop = run_react(
            conn,
            budget,
            observation={"claim": {"claim_id": claim_id}},
            decide=_make_decider(budget, seed, claim_id, trace),
            max_steps=MAX_STEPS,
        )
    except InjectedCrash:
        raise
    except Exception as exc:  # run_claim must not raise; record and fail closed.
        trace.add("error", {"reason": type(exc).__name__})
        return done("failed", 0, f"react_error:{type(exc).__name__}")

    proposal = 0
    try:
        trace.add("react_stop", {"stopped": loop["stopped"]})
        final = loop["final"]
        status = final.get("status", "failed")
        reason = final.get("error_reason")

        if status != "quote":
            # needs_info / escalated / failed decided inside the loop. No ledger write.
            complete(budget, seed=seed, purpose="draft", prompt=status)
            return done(status, 0, reason)

        proposal = int(final["amount_vnd"])
        complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
        if proposal <= 0:
            # Quote 0 -> denied, do not call issue_refund (no policy_denied expected).
            return done("denied", 0, reason)

        # Host is the only writer. Full quote; host subtracts earlier refunds on the order.
        try:
            outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        except InjectedCrash:
            trace.add("crash", {"at": crash_at})
            trace.write()
            raise

        trace.add("issue_refund", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})
        if not outcome["ok"]:
            return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
        return done("resolved", proposal, None)
    except InjectedCrash:
        raise
    except Exception as exc:  # run_claim must not raise; record the type only, no payload.
        trace.add("error", {"reason": type(exc).__name__})
        return done("failed", proposal, f"exception:{type(exc).__name__}")


def _make_decider(budget: Budget, seed: int, claim_id: str, trace: Trace):
    """Build decide() for run_react.

    run_react only hands back the last tool result, so the agent keeps its own
    scratchpad (`memory`) across steps. Every step is one MockLLM call.
    """
    memory: dict[str, Any] = {}

    def think(step: str) -> None:
        # Prompt never contains the ticket's numbers as facts; the model only "reasons" about the next step.
        complete(budget, seed=seed, purpose="react", prompt=f"claim={claim_id} step={step}")

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        last_tool = seen.get("last_tool")
        result = seen.get("last_result") or {}

        if last_tool is None:
            think("start")
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}

        if last_tool == "get_claim_view":
            trace.add("tool", {"name": "get_claim_view", "found": bool(result.get("found")), "has_order_id": bool(result.get("order_id"))})
            think("claim_view")
            if not result.get("found"):
                return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
            if not result.get("order_id"):
                # Do not mine an order id out of the ticket text.
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
            memory["order_id"] = result["order_id"]
            memory["principal_id"] = result["principal_id"]
            return {
                "tool": "lookup_order",
                "args": {"order_id": memory["order_id"], "principal_id": memory["principal_id"]},
            }

        if last_tool == "lookup_order":
            visible = bool(result.get("visible"))
            trace.add(
                "tool",
                {
                    "name": "lookup_order",
                    "visible": visible,
                    "reason": result.get("reason"),
                    # lookup_order already returns only allowlisted ORDER_FIELDS.
                    "order": result.get("order") if visible else None,
                },
            )
            think("order")
            if not visible:
                return {"final": {"status": "escalated", "error_reason": result.get("reason")}}
            memory["order"] = dict(result["order"])
            return {
                "tool": "lookup_refund_history",
                "args": {"order_id": memory["order_id"], "principal_id": memory["principal_id"]},
            }

        if last_tool == "lookup_refund_history":
            trace.add(
                "tool",
                {
                    "name": "lookup_refund_history",
                    "refund_count": result.get("refund_count"),
                    "refunded_vnd": result.get("refunded_vnd"),
                },
            )
            think("history")
            # Informational only: the host enforces the per-order cap. Quote from the order row.
            return {"tool": "compute_compensation", "args": {"order": memory["order"]}}

        if last_tool == "compute_compensation":
            trace.add("quote", {k: result.get(k) for k in ("amount_vnd", "reason", "clause_ids", "parts")})
            think("quote")
            return {
                "final": {
                    "status": "quote",
                    "amount_vnd": int(result.get("amount_vnd") or 0),
                    "error_reason": result.get("reason"),
                }
            }

        think("unexpected")
        return {"final": {"status": "failed", "error_reason": f"unexpected_tool:{last_tool}"}}

    return decide
