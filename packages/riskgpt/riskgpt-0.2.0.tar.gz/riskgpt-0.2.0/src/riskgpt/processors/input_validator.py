from models.chains.assessment import AssessmentRequest
from models.chains.categorization import CategoryRequest
from models.chains.mitigation import MitigationRequest
from models.chains.risk import RiskRequest
from pydantic import ValidationError


def validate_category_request(data: dict) -> CategoryRequest:
    try:
        return CategoryRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")


def validate_risk_request(data: dict) -> RiskRequest:
    """Validate dict input and return a :class:`RiskRequest` instance."""
    try:
        return RiskRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")


def validate_mitigation_request(data: dict) -> MitigationRequest:
    """Validate dict input and return a :class:`MitigationRequest` instance."""
    try:
        return MitigationRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")


def validate_assessment_request(data: dict) -> AssessmentRequest:
    """Validate dict input and return a :class:`AssessmentRequest` instance."""
    try:
        return AssessmentRequest(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid input data: {e}")
