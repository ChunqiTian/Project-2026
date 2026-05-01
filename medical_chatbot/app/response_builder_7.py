from app.schemas_1 import AnswerResponse, BotResponse

def build_bot_response_from_answer(
        answer_response: AnswerResponse,
        intent: str,
        risk_level: str, 
        action: str, 
        needs_human: bool,
        safe_to_answer: bool,
        detected_flags: list[str] | None=None,
        disclaimer: str | None=None, 
        follow_up: str | None=None,
        refusal_reason: str | None=None,
        escalation_type: str = "none",
        safety_note: str | None=None,
) -> BotResponse:
    # Convvert the smalled AnswerRsponse into the fuller BotResponse

    if detected_flags is None: detected_flags = []

    return BotResponse(
        intent=intent, 
        risk_level=risk_level, 
        action=action, 
        answer=answer_response.answer,
        citations=answer_response.citations, 
        needs_human=needs_human,
        safe_to_answer=safe_to_answer,
        confidence=answer_response.confidence, 
        reason=answer_response.reason, 
        disclaimer=disclaimer, 
        follow_up=follow_up,
        detected_flags=detected_flags,
        allowed_to_answer=safe_to_answer,
        refusal_reason=refusal_reason,
        escalation_type=escalation_type,
        safety_note=safety_note,
    )





