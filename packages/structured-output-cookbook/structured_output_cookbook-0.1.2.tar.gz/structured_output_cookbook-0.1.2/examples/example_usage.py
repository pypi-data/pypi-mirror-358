#!/usr/bin/env python3
"""
Example usage of the Structured Output Cookbook with YAML schemas.

This script demonstrates how to use the library programmatically with both
predefined templates and custom YAML schemas.
"""

import os
from structured_output_cookbook import StructuredExtractor, SchemaLoader, JobDescriptionSchema, RecipeSchema
from structured_output_cookbook.config import Config

def main():
    """Main example function."""
    
    # Initialize the configuration
    config = Config.from_env()
    extractor = StructuredExtractor(config)
    
    print("🚀 Structured Output Cookbook - Example Usage\n")
    
    # Example 1: Using predefined templates
    print("📝 Example 1: Using Predefined Templates")
    print("-" * 50)
    
    recipe_text = """
    Spaghetti Carbonara
    
    Ingredients:
    - 400g spaghetti
    - 200g guanciale or pancetta
    - 4 large eggs
    - 100g Pecorino Romano cheese
    - Black pepper
    - Salt
    
    Instructions:
    1. Cook spaghetti in salted water until al dente
    2. Fry guanciale until crispy
    3. Beat eggs with grated cheese
    4. Combine hot pasta with guanciale
    5. Add egg mixture off heat, stirring quickly
    6. Season with black pepper
    
    Serves 4 people. Total time: 20 minutes.
    """
    
    result = extractor.extract(recipe_text, RecipeSchema)
    if result.success and result.data:
        print("✅ Recipe extraction successful!")
        print(f"   Recipe: {result.data.get('name', 'N/A')}")
        print(f"   Servings: {result.data.get('servings', 'N/A')}")
        print(f"   Total time: {result.data.get('total_time', 'N/A')}")
        ingredients = result.data.get('ingredients', [])
        print(f"   Ingredients: {len(ingredients)} items")
    else:
        print(f"❌ Recipe extraction failed: {result.error}")
    
    print()
    
    # Example 2: Using custom YAML schemas
    print("🎯 Example 2: Using Custom YAML Schemas")
    print("-" * 50)
    
    # Load available schemas
    loader = SchemaLoader("config/schemas")
    available_schemas = loader.get_available_schemas()
    print(f"Available custom schemas: {', '.join(available_schemas)}")
    
    # Use a custom schema
    news_text = """
    Breaking: Apple Unveils Revolutionary iPhone 15 Pro
    
    CUPERTINO, Calif. - Apple Inc. today announced the highly anticipated iPhone 15 Pro,
    featuring groundbreaking titanium design and advanced AI capabilities. CEO Tim Cook
    presented the device at Apple Park, highlighting its improved camera system and
    extended battery life.
    
    The new device, starting at $999, will be available for pre-order this Friday.
    Industry analysts predict strong sales, with some calling it "the most significant
    iPhone upgrade in years."
    """
    
    try:
        news_schema = loader.load_schema("news_article")
        result = extractor.extract_with_yaml_schema(news_text, news_schema)
        
        if result.success and result.data:
            print("✅ News extraction successful!")
            print(f"   Headline: {result.data.get('headline', 'N/A')}")
            print(f"   Location: {result.data.get('location', 'N/A')}")
            print(f"   Key people: {result.data.get('key_people', [])}")
            print(f"   Organizations: {result.data.get('organizations', [])}")
            print(f"   Sentiment: {result.data.get('sentiment', 'N/A')}")
        else:
            print(f"❌ News extraction failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
    
    print()
    
    # Example 3: Schema validation
    print("🔍 Example 3: Schema Validation")
    print("-" * 50)
    
    for schema_name in available_schemas:
        is_valid, error = loader.validate_schema_structure(schema_name)
        status = "✅ Valid" if is_valid else f"❌ Invalid: {error}"
        print(f"   {schema_name}: {status}")
    
    print("\n🎉 All examples completed!")

if __name__ == "__main__":
    main() 