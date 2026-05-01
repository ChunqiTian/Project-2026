
import json
from pathlib import Path
from typing import Any

import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from eval.metrics_9 import compute_metrics, find_failures, normalize_action, has_citation
from app.router_8 import handle_message

TEST_CASES_PATH = Path("eval/test_cases_9.jsonl")
REPORTS_DIR = Path("eval/reports")
RESULTS_PATH = REPORTS_DIR / "baseline_results.json"
ERROR_ANALYSIS_PATH = REPORTS_DIR / "error_analysis.md"

def load_jsonl(path: Path) -> list[dict[str, Any]]:
    cases = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            cases.append(json.loads(line))
    return cases

def to_dict(obj: Any) -> dict[str, Any]:
    # Converts Pydantic models or normal objects into dicts
    # Supports: Pydantic v2: model_dump();  Pydantic v1:dict()
    if isinstance(obj, dict): return obj
    if hasattr(obj, "model_dump"): return obj.model_dump()
    if hasattr(obj, "dict"): return obj.dict()
    return {"raw_response": str(obj)}

def extract_predicted_action(result: dict[str, Any]) -> str:
    """
    Try to find the bot's decision/acion from common fields.
    Your proj may return fields like: action | route | safety_decision | needs_human | safe_to_answer | refusal_reason
    This function can be adjusted based on the BotResponse
    """
    if "action" in result: return normalize_action(result.get("action"))
    if result.get("needs_human") is True: return "escalate"
    if result.get("safe_to_answer") is False: return "refuse"
    if result.get("refusal_reason"): return "refuse"
    return "answer"

def run_one_case(test_case: dict[str, Any]) -> dict[str, Any]:
    query = test_case["query"]
    try:
        bot_response = handle_message(query)
        result = to_dict(bot_response)
        predicted_action = extract_predicted_action(result)
        citation_present = has_citation(result)
        return {
            "id": test_case["id"],
            "category": test_case["category"],
            "query": query,
            "expected_action": test_case["expected_action"],
            "predicted_action":  predicted_action,
            "must_have_citation": test_case["must_have_citation"],
            "has_citation": citation_present,
            "passed_action": normalize_action(test_case["expected_action"]) == predicted_action,
            "passed_citation": (True if test_case["must_have_citation"] is False else citation_present),
            "notes": test_case.get("notes", ""),
            "bot_response": result,
        }
    except Exception as e:
        return {
            "id": test_case["id"],
            "category": test_case["category"],
            "query": query,
            "expected_action": test_case["expected_action"],
            "predicted_action": "error",
            "must_have_citation": test_case["must_have_citation"],
            "has_citation": False,
            "passed_action": False,
            "passed_citation": False,
            "notes": test_case.get("notes", ""),
            "error": str(e),
        }

def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_error_analysis(failures: list[dict[str, Any]], metrics: dict[str, Any], path: Path) -> None:
    lines=[]
    lines.append("# Error Analysis")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total cases: {metrics['total_cases']}")
    lines.append(f"- Overall action accuracy: {metrics['overall_action_accuracy']:.2%}")
    lines.append(f"- Refusal correctness: {metrics['refusal_correctness']:.2%}")
    lines.append(f"- Escalation recall: {metrics['escalation_recall']:.2%}")
    lines.append(f"- Citation rate when required: {metrics['citation_rate_when_required']:.2%}")
    lines.append("")

    lines.append("## Category Accuracy")
    lines.append("")

    for category, accuracy in metrics["category_accuracy"].items():
        lines.append(f"- {category}: {accuracy:.2%}")

    lines.append("")
    lines.append("## Failed Cases")
    lines.append("")

    if not failures: 
        lines.append("No failed cases found.")
    else:
        for failure in failures:
            lines.append(f"### {failure['id']} - {failure['category']}")
            lines.append("")
            lines.append(f"**Query:** {failure['query']}")
            lines.append("")
            lines.append(f"**Expected:** {failure['expected_action']}")
            lines.append("")
            lines.append(f"**Predicted:** {failure['predicted_action']}")
            lines.append("")
            lines.append(f"**Must have citation:** {failure['must_have_citation']}")
            lines.append("")
            lines.append(f"**Has citation:** {failure['has_citation']}")
            lines.append("")
            lines.append(f"**Notes:** {failure.get('notes', '')}")
            lines.append("")
            lines.append("---")
            lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main() -> None:
    test_cases = load_jsonl(TEST_CASES_PATH)
    records=[]
    for test_case in test_cases:
        record = run_one_case(test_case)
        records.append(record)
        status = "PASS" if record["passed_action"] and record["passed_citation"] else "FAIL"
        print(
            f"{status} | {record['id']} | "
            f"expected={record['expected_action']} | "
            f"predicted={record['predicted_action']}"
        )
    metrics = compute_metrics(records)
    failures = find_failures(records)
    report = {
        "metrics": metrics, 
        "records": records,
    }
    save_json(report, RESULTS_PATH)
    save_error_analysis(failures, metrics, ERROR_ANALYSIS_PATH)

    print("")
    print("Evaluation complete.")
    print(f"Results saved to: {RESULTS_PATH}")
    print(f"Error analysis saved to: {ERROR_ANALYSIS_PATH}")
    print("")
    print("Metrics:")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()




