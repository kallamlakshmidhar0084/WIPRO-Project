from typing import Literal

from pydantic import BaseModel, Field


class AnalysisOutput(BaseModel):
    summary: str
    identified_patterns: list[str]
    complexity_score: float = Field(ge=0.0, le=10.0)
    language: str


class RiskReport(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    risk_factors: list[str]
    estimated_effort_days: int
    breaking_change_likelihood: float = Field(ge=0.0, le=1.0)


class ModernCodeOutput(BaseModel):
    modern_code: str
    changes_made: list[str]
    frameworks_suggested: list[str]


class ChecklistOutput(BaseModel):
    checklist: list[str]


class MigrationReportOutput(BaseModel):
    migration_report: str
