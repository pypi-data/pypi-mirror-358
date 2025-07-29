from typing import List, Optional

from models.base import BaseResponse
from models.chains.risk import Risk
from models.common import BusinessContext
from models.enums import AudienceEnum
from pydantic import BaseModel, Field


class ChallengeQuestionsRequest(BaseModel):
    """Request model for generating challenging questions from business context."""

    business_context: BusinessContext
    audience: AudienceEnum = Field(
        description="The target audience for the questions",
        default=AudienceEnum.risk_internal,
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on when generating questions",
    )
    num_questions: int = Field(
        default=5,
        description="Number of challenging questions to generate",
        ge=1,
        le=10,
    )

    class Config:
        schema_extra = {
            "example": {
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "domain_knowledge": "The company operates in the B2B sector",
                    "business_area": "Sales",
                    "industry_sector": "Technology",
                },
                "audience": "risk_internal",
                "focus_areas": ["data security", "user adoption", "integration"],
                "num_questions": 5,
            }
        }


class ChallengeQuestionsResponse(BaseResponse):
    """Output model containing challenging questions derived from business context."""

    questions: List[str]

    class Config:
        schema_extra = {
            "example": {
                "questions": [
                    "What are the potential data security risks when migrating customer data to the new CRM system?",
                    "How might the implementation of the new CRM system affect existing sales processes?",
                    "What integration challenges might arise with existing systems?",
                    "What user adoption barriers might impact the success of the CRM implementation?",
                    "How might the new CRM system affect compliance with industry regulations?",
                ],
                "response_info": {"token_usage": 100, "cost": 0.01},
            }
        }


class ChallengeRiskRequest(BaseModel):
    """Request model for generating challenging questions for a specific risk."""

    risk: Risk
    business_context: BusinessContext
    audience: AudienceEnum = Field(
        description="The target audience for the questions",
        default=AudienceEnum.risk_internal,
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on when generating questions",
    )
    num_questions: int = Field(
        default=5,
        description="Number of challenging questions to generate",
        ge=1,
        le=10,
    )

    class Config:
        schema_extra = {
            "example": {
                "risk": {
                    "title": "Data Migration Failure",
                    "description": "Risk of losing critical customer data during migration to the new CRM system",
                    "category": "Technical",
                },
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "domain_knowledge": "The company operates in the B2B sector",
                    "business_area": "Sales",
                    "industry_sector": "Technology",
                },
                "audience": "risk_internal",
                "focus_areas": ["data security", "contingency planning", "testing"],
                "num_questions": 5,
            }
        }


class ChallengeRisksRequest(BaseModel):
    """Request model for generating challenging questions for multiple risks."""

    risks: List[Risk]
    business_context: BusinessContext
    audience: AudienceEnum = Field(
        description="The target audience for the questions",
        default=AudienceEnum.risk_internal,
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on when generating questions",
    )
    questions_per_risk: int = Field(
        default=3,
        description="Number of challenging questions to generate per risk",
        ge=1,
        le=5,
    )

    class Config:
        schema_extra = {
            "example": {
                "risks": [
                    {
                        "title": "Data Migration Failure",
                        "description": "Risk of losing critical customer data during migration to the new CRM system",
                        "category": "Technical",
                    },
                    {
                        "title": "User Adoption Issues",
                        "description": "Risk of low user adoption due to resistance to change",
                        "category": "Organizational",
                    },
                ],
                "business_context": {
                    "project_id": "CRM-2023",
                    "project_description": "Implementation of a new CRM system",
                    "domain_knowledge": "The company operates in the B2B sector",
                    "business_area": "Sales",
                    "industry_sector": "Technology",
                },
                "audience": "risk_internal",
                "focus_areas": ["implementation strategy", "change management"],
                "questions_per_risk": 3,
            }
        }


class RiskQuestions(BaseModel):
    """Model for questions related to a specific risk."""

    risk_title: str
    questions: List[str]


class ChallengeRiskResponse(BaseResponse):
    """Output model containing challenging questions for a specific risk."""

    questions: List[str]

    class Config:
        schema_extra = {
            "example": {
                "questions": [
                    "What data validation procedures will be in place during the migration process?",
                    "How will you ensure data integrity if the migration process is interrupted?",
                    "What is the rollback strategy if critical data is corrupted during migration?",
                    "How will you test the migration process without risking production data?",
                    "What monitoring systems will be in place during the migration to detect data issues?",
                ],
                "response_info": {"token_usage": 120, "cost": 0.012},
            }
        }


class ChallengeRisksResponse(BaseResponse):
    """Output model containing challenging questions for multiple risks."""

    risk_questions: List[RiskQuestions]

    class Config:
        schema_extra = {
            "example": {
                "risk_questions": [
                    {
                        "risk_title": "Data Migration Failure",
                        "questions": [
                            "What data validation procedures will be in place during the migration process?",
                            "How will you ensure data integrity if the migration process is interrupted?",
                            "What is the rollback strategy if critical data is corrupted during migration?",
                        ],
                    },
                    {
                        "risk_title": "User Adoption Issues",
                        "questions": [
                            "What change management strategies will be implemented to address resistance?",
                            "How will you measure and track user adoption rates?",
                            "What training programs will be provided to ensure smooth transition?",
                        ],
                    },
                ],
                "response_info": {"token_usage": 180, "cost": 0.018},
            }
        }
