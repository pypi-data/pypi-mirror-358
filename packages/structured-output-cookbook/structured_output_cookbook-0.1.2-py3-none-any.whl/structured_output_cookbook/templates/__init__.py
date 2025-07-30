"""Predefined templates for common extraction tasks."""

from .email import EmailSchema
from .event import EventSchema
from .job_description import JobDescriptionSchema
from .product_review import ProductReviewSchema
from .recipe import RecipeSchema

__all__ = [
    "EmailSchema",
    "EventSchema",
    "JobDescriptionSchema",
    "ProductReviewSchema",
    "RecipeSchema",
]
