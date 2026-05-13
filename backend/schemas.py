from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


MAX_CODE_LENGTH = 50_000


class AnalysisRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=MAX_CODE_LENGTH)
    query: Optional[str] = Field(default=None, max_length=2_000)

    @field_validator("code")
    @classmethod
    def code_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("code must not be empty")
        return value

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank_when_present(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            return None
        return value


class AnalysisResponse(BaseModel):
    snippet_id: str
    analysis: str


class ChecklistStatus(str, Enum):
    changed = "changed"
    review_required = "review_required"
    not_applicable = "not_applicable"


class RiskSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ChecklistItem(BaseModel):
    item: str
    status: ChecklistStatus
    notes: str


class RiskItem(BaseModel):
    risk: str
    severity: RiskSeverity
    mitigation: str


class MigrationResponse(BaseModel):
    snippet_id: str
    modernized_code: str
    language: str
    summary: str
    checklist: list[ChecklistItem]
    risks: list[RiskItem]


class PatternItem(BaseModel):
    name: str
    description: str
    example: Optional[str] = None
    modern_alternative: Optional[str] = None


class PatternsResponse(BaseModel):
    patterns: list[PatternItem]
