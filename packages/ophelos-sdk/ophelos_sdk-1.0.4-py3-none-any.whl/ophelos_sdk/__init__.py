"""
Ophelos Python SDK

Python SDK for the Ophelos API - a comprehensive debt management platform.
"""

from .client import OphelosClient
from .exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    OphelosAPIError,
    OphelosError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import (
    BaseOphelosModel,
    Communication,
    ContactDetailType,
    Currency,
    Customer,
    Debt,
    DebtStatus,
    Invoice,
    LineItem,
    Organisation,
    PaginatedResponse,
    Payment,
    PaymentPlan,
    PaymentStatus,
    Payout,
    Tenant,
    Webhook,
    WebhookEvent,
)
from .webhooks import WebhookHandler, construct_event

__version__ = "1.0.4"
__author__ = "Ophelos"
__email__ = "support@ophelos.com"

__all__ = [
    "OphelosClient",
    # Exceptions
    "OphelosError",
    "OphelosAPIError",
    "AuthenticationError",
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ConflictError",
    "ForbiddenError",
    "ServerError",
    # Webhook handling
    "WebhookHandler",
    "construct_event",
    # Models
    "BaseOphelosModel",
    "Debt",
    "Customer",
    "Organisation",
    "Payment",
    "PaymentPlan",
    "Invoice",
    "LineItem",
    "Communication",
    "Webhook",
    "WebhookEvent",
    "Tenant",
    "Payout",
    "PaginatedResponse",
    # Enums
    "DebtStatus",
    "PaymentStatus",
    "ContactDetailType",
    "Currency",
]
