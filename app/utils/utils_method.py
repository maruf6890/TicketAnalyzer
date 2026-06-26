import json
from app.models import AnalyzeTicketRequest

def request_to_prompt(req: AnalyzeTicketRequest) -> str:
    lines = [
        f"Ticket ID: {req.ticket_id}",
        f"Complaint: {req.complaint}",
    ]

    if req.language:
        lines.append(f"Language: {req.language.value}")

    if req.channel:
        lines.append(f"Channel: {req.channel.value}")

    if req.user_type:
        lines.append(f"User Type: {req.user_type.value}")

    if req.campaign_context:
        lines.append(f"Campaign Context: {req.campaign_context}")

    if req.transaction_history:
        lines.append("\nTransaction History:")
        for i, tx in enumerate(req.transaction_history, 1):
            lines.append(
                f"""\
{i}.
  Transaction ID: {tx.transaction_id}
  Timestamp: {tx.timestamp}
  Type: {tx.type.value}
  Amount: {tx.amount}
  Counterparty: {tx.counterparty}
  Status: {tx.status.value}"""
            )

    if req.metadata:
        lines.append("\nMetadata:")
        lines.append(json.dumps(req.metadata, indent=2))

    return "\n".join(lines)