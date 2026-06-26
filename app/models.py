from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class Language(str, Enum):
    en = "en"
    bn = "bn"
    mixed = "mixed"

class Channel(str, Enum):
    in_app_chat = "in_app_chat"
    call_center = "call_center"
    email = "email"
    merchant_portal = "merchant_portal"
    field_agent = "field_agent"

class UserType(str, Enum):
    customer = "customer"
    merchant = "merchant"
    agent = "agent"
    unknown = "unknown"

class TransactionType(str, Enum):
    transfer = "transfer"
    payment = "payment"
    cash_in = "cash_in"
    cash_out = "cash_out"
    settlement = "settlement"
    refund = "refund"

class TransactionStatus(str, Enum):
    completed = "completed"
    failed = "failed"
    pending = "pending"
    reversed = "reversed"

class EvidenceVerdict(str, Enum):
    consistent = "consistent"
    inconsistent = "inconsistent"
    insufficient_data = "insufficient_data"

class CaseType(str, Enum):
    wrong_transfer = "wrong_transfer"
    payment_failed = "payment_failed"
    refund_request = "refund_request"
    duplicate_payment = "duplicate_payment"
    merchant_settlement_delay = "merchant_settlement_delay"
    agent_cash_in_issue = "agent_cash_in_issue"
    phishing_or_social_engineering = "phishing_or_social_engineering"
    other = "other"

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Department(str, Enum):
    customer_support = "customer_support"
    dispute_resolution = "dispute_resolution"
    payments_ops = "payments_ops"
    merchant_operations = "merchant_operations"
    agent_operations = "agent_operations"
    fraud_risk = "fraud_risk"


# -------------------------------------------------------------------
# REQUEST MODELS
# -------------------------------------------------------------------

class TransactionHistoryEntry(BaseModel):
    transaction_id: str = Field(..., example="TXN-9101")
    timestamp: str = Field(..., description="ISO 8601 format", example="2026-04-14T14:08:22Z")
    type: TransactionType = Field(..., example="transfer")
    amount: float = Field(..., description="Amount in BDT", example=5000.0)
    counterparty: str = Field(..., description="Recipient phone, merchant ID, or agent ID", example="+8801719876543")
    status: TransactionStatus = Field(..., example="completed")

class AnalyzeTicketRequest(BaseModel):
    ticket_id: str = Field(..., example="TKT-001")
    complaint: str = Field(..., example="I sent 5000 taka to a wrong number around 2pm today...")
    language: Optional[Language] = Field(None, example="en")
    channel: Optional[Channel] = Field(None, example="in_app_chat")
    user_type: Optional[UserType] = Field(None, example="customer")
    campaign_context: Optional[str] = Field(None, example="boishakh_bonanza_day_1")
    transaction_history: Optional[List[TransactionHistoryEntry]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional simulated context provided by the harness")


# -------------------------------------------------------------------
# RESPONSE MODEL
# -------------------------------------------------------------------
class AnalyzeTicketResponse(BaseModel):
    ticket_id: str = Field(
        ...,
        description="Echo the input ticket ID exactly as received.",
        example="TKT-001",
    )

    relevant_transaction_id: Optional[str] = Field(
        ...,
        description=(
            "Transaction ID that best matches the customer's complaint. "
            "Choose the single strongest match using amount, transaction type, "
            "timestamp, counterparty, status, and complaint details. "
            "Return null if no reasonable match exists or if multiple transactions "
            "are equally plausible. Never guess."
        ),
        example="TXN-9101",
    )

    evidence_verdict: EvidenceVerdict = Field(
        ...,
        description=(
            "if the  transaction history is provided, check the complaint against the transaction  history and try to understand then decide the relationship then decide the verdict. "
            "Relationship between the complaint and transaction history. "
            "'consistent' when history supports the complaint, "
            "'inconsistent' when history contradicts it, "
            "and 'insufficient_data' when there is not enough information "
            "or no unique matching transaction."
        ),
        example="consistent",
    )

    case_type: CaseType = Field(
        ...,
        description=(
            "Primary classification of the customer's issue. "
            "Choose the single most appropriate category based on the complaint "
            "and supporting transaction evidence."
        ),
        example="wrong_transfer",
    )

    severity: Severity = Field(
        ...,
        description=(
            "Operational priority of the case. "
            "Use 'low' for informational or vague issues, "
            "'medium' for operational issues with limited financial risk, "
            "'high' for financial disputes such as wrong transfers, duplicate "
            "payments or failed payments, and "
            "'critical' for phishing, fraud, unauthorized activity or major "
            "security risks."
        ),
        example="high",
    )

    department: Department = Field(
        ...,
        description=(
            "Internal team responsible for handling the case. "
            "Select the department that best matches the identified case type "
            "and operational workflow."
        ),
        example="dispute_resolution",
    )

    agent_summary: str = Field(
        ...,
        description=(
            "A concise factual summary for internal agents. "
            "Summarize the complaint, relevant transaction (if any), "
            "key evidence, and important observations. "
            "Do not speculate or include unsupported assumptions."
        ),
        example=(
            "Customer reports sending 5000 BDT to the wrong recipient. "
            "Transaction TXN-9101 matches the complaint."
        ),
    )

    recommended_next_action: str = Field(
        ...,
        description=(
            "Recommended operational action for the internal support team. "
            "Suggest the next investigation or workflow step without approving "
            "refunds, reversals, or other unauthorized actions."
        ),
        example="Verify TXN-9101 and initiate the wrong-transfer dispute workflow.",
    )

    customer_reply: str = Field(
        ...,
        description=(
            "Safe, customer-facing response. "
            "Acknowledge the complaint, explain that the issue will be reviewed, "
            "avoid promising refunds or guaranteed outcomes, "
            "never request PIN, OTP, passwords or sensitive credentials, "
            "and direct the customer to official support channels."
        ),
        example=(
            "We have received your request regarding transaction TXN-9101. "
            "Our team will review the matter and contact you through official "
            "support channels. Please never share your PIN or OTP with anyone."
        ),
    )

    human_review_required: bool = Field(
        ...,
        description=(
            "Whether manual investigation by a human agent is required. "
            "Set to true for fraud, phishing, disputes, inconsistent evidence, "
            "wrong transfers, duplicate payments, pending cash-in issues, "
            "high/critical severity, or any case requiring manual validation. "
            "Otherwise return false."
        ),
        example=True,
    )

    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description=(
            "Overall confidence in the analysis from 0.0 to 1.0. "
            "Use higher values when transaction matching and evidence are clear. "
            "Reduce confidence when evidence is conflicting, ambiguous, "
            "or insufficient."
        ),
        example=0.92,
    )

    reason_codes: Optional[List[str]] = Field(
        None,
        description=(
            "Short machine-readable labels explaining why the decision was made. "
            "Include only the most relevant reasons, such as "
            "'transaction_match', 'duplicate_payment', "
            "'established_recipient_pattern', 'ambiguous_match', "
            "'payment_failed', 'fraud_risk', or 'needs_clarification'."
        ),
        example=[
            "wrong_transfer",
            "transaction_match",
            "dispute_initiated",
        ],
    )

