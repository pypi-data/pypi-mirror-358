"""Recipe extraction schema."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..schemas.base import BaseSchema


class Ingredient(BaseModel):
    """Single ingredient with quantity and unit."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Ingredient name")
    quantity: str | None = Field(description="Amount needed")
    unit: str | None = Field(description="Unit of measurement")
    notes: str | None = Field(description="Additional notes")


class RecipeSchema(BaseSchema):
    """Extract structured information from recipes."""

    name: str = Field(description="Recipe name or title")
    description: str | None = Field(description="Brief description of the dish")
    cuisine: str | None = Field(description="Cuisine type (Italian, Asian, etc.)")
    difficulty: str | None = Field(
        description="Difficulty level (easy, medium, hard)",
    )
    prep_time: str | None = Field(description="Preparation time")
    cook_time: str | None = Field(description="Cooking time")
    total_time: str | None = Field(description="Total time required")
    servings: int | None = Field(description="Number of servings")
    ingredients: list[Ingredient] = Field(
        description="List of ingredients with quantities",
    )
    instructions: list[str] = Field(description="Step-by-step cooking instructions")
    tags: list[str] = Field(description="Recipe tags (vegetarian, gluten-free, etc.)")
    nutrition: dict[str, Any] | None = Field(
        description="Nutritional information if available",
    )

    @classmethod
    def get_extraction_prompt(cls) -> str:
        return """
        Extract structured information from the following recipe text.
        Focus on identifying:
        - Recipe name and description
        - Timing information (prep, cook, total time)
        - Complete ingredients list with quantities and units
        - Step-by-step instructions
        - Difficulty level and serving information
        - Any dietary tags or restrictions
        
        For ingredients, try to separate quantity, unit, and ingredient name.
        If information is not available, leave fields empty.
        """.strip()
