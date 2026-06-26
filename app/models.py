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
    ticket_id: str = Field(..., example="TKT-001")
    relevant_transaction_id: Optional[str] = Field(
        ..., 
        description="Transaction ID the complaint refers to, or null if none matches.", 
        example="TXN-9101"
    )
    evidence_verdict: EvidenceVerdict = Field(..., example="consistent")
    case_type: CaseType = Field(..., example="wrong_transfer")
    severity: Severity = Field(..., example="high")
    department: Department = Field(..., example="dispute_resolution")
    agent_summary: str = Field(..., description="Concise agent ready summary", example="Customer reports sending 5000 BDT to the wrong number...")
    recommended_next_action: str = Field(..., example="Verify TXN-9101 details with the customer...")
    customer_reply: str = Field(..., description="Safe official reply respecting safety rules", example="We have noted your concern about transaction TXN-9101...")
    human_review_required: bool = Field(..., example=True)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, example=0.95)
    reason_codes: Optional[List[str]] = Field(None, example=["wrong_transfer", "transaction_match"])