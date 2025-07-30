"""Structured Output Cookbook - Extract structured data from text using LLMs with ready-to-use templates."""

__version__ = "0.1.2"
__author__ = "Saverio Mazza"
__email__ = "saverio3107@gmail.com"
__description__ = (
    "Extract structured data from text using LLMs with ready-to-use templates"
)
__url__ = "https://github.com/mazzasaverio/structured-output-cookbook"

from .config import Config
from .extractor import StructuredExtractor
from .schemas.base import BaseSchema, ExtractionResult
from .templates.email import EmailSchema
from .templates.event import EventSchema
from .templates.job_description import JobDescriptionSchema
from .templates.product_review import ProductReviewSchema
from .templates.recipe import RecipeSchema
from .utils import SchemaLoader, YamlSchema, setup_minimal_logger

__all__ = [
    "BaseSchema",
    "Config",
    "EmailSchema",
    "EventSchema",
    "ExtractionResult",
    "JobDescriptionSchema",
    "ProductReviewSchema",
    "RecipeSchema",
    "SchemaLoader",
    "StructuredExtractor",
    "YamlSchema",
    "__version__",
    "setup_minimal_logger",
]
