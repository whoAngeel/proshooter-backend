from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, UUID4


class ReportType(str, Enum):
    INDIVIDUAL_SESSION = "session_individual"
    MONTHLY_SUMMARY = "monthly_summary"
    ANNUAL_SUMMARY = "annual_summary"
    SHOOTER_PROFILE = "shooter_profile"


class ReportRequest(BaseModel):
    shooter_id: UUID4
    report_type: ReportType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_images: bool = True
    include_analysis: bool = True


class ReportData(BaseModel):
    shooter_info: dict
    sessions: List[dict]
    statistics: dict
    evaluations: List[dict]
    exercises: List[dict]
    analysis_images: List[str] = []
