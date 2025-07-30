# 🧑‍🍳 Structured Output Cookbook

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![uv](https://img.shields.io/badge/dependency--manager-uv-orange.svg)

A powerful Python library and CLI tool for extracting structured data from unstructured text using Large Language Models (LLMs). Transform raw text into clean, validated JSON with predefined templates or custom YAML schemas.

## ✨ Features

- **🎯 Predefined Templates**: Built-in schemas for common use cases (job descriptions, recipes, etc.)
- **📝 Custom YAML Schemas**: Define your own extraction schemas with simple YAML files
- **🔧 CLI Interface**: Easy-to-use command-line tool for batch processing
- **🐍 Python API**: Programmatic access for integration into your applications
- **📊 Token Tracking**: Monitor API usage and costs
- **🧪 Schema Validation**: Ensure your custom schemas are properly structured
- **📁 Auto-organized Output**: Automatic timestamped file organization

## 🚀 Quick Start

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/mazzasaverio/structured-output-cookbook.git
cd structured-output-cookbook
uv sync

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run your first extraction
uv run structured-output extract recipe --text "Pasta with tomato sauce: boil pasta, add sauce, serve hot"
```

### Using pip

```bash
pip install structured-output-cookbook
export OPENAI_API_KEY="your-api-key-here"
structured-output extract recipe --text "Your recipe text here"
```

### Using Docker

```bash
# Build the image
docker build -t structured-output-cookbook .

# Run with your API key
docker run --rm \
  -e OPENAI_API_KEY="your-api-key-here" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  structured-output-cookbook \
  extract recipe --text "Pasta with tomato sauce: boil pasta, add sauce, serve hot"
```

## 📖 Usage

### CLI Commands

```bash
# List available predefined templates
structured-output list-templates

# List custom YAML schemas
structured-output list-schemas

# Extract using predefined templates
structured-output extract recipe --input-file examples/recipe.txt
structured-output extract job --text "Software Engineer position at Tech Corp..."

# Extract using custom YAML schemas
structured-output extract-custom news_article --input-file examples/news_article.txt

# Options
structured-output extract recipe \
  --input-file examples/recipe.txt \
  --output my_recipe.json \
  --pretty \
  --no-save
```

### Python API

```python
from structured_output_cookbook import StructuredExtractor, RecipeSchema
from structured_output_cookbook.config import Config

# Initialize
config = Config.from_env()
extractor = StructuredExtractor(config)

# Extract with predefined template
text = "Spaghetti Carbonara: Cook pasta, fry pancetta, mix with eggs..."
result = extractor.extract(text, RecipeSchema)

if result.success:
    print(f"Recipe: {result.data['name']}")
    print(f"Servings: {result.data['servings']}")
else:
    print(f"Error: {result.error}")

# Extract with custom YAML schema
from structured_output_cookbook.utils import SchemaLoader

loader = SchemaLoader("config/schemas")
news_schema = loader.load_schema("news_article")
result = extractor.extract_with_yaml_schema(news_text, news_schema)
```

## 🎨 Creating Custom Schemas

Create YAML files in the `config/schemas/` directory:

```yaml
# config/schemas/product_review.yaml
name: "Product Review"
description: "Extract structured information from product reviews"

system_prompt: |
  Extract structured information from the following product review.
  Focus on identifying the product name, rating, pros, cons, and overall sentiment.

schema:
  type: object
  properties:
    product_name:
      type: string
      description: "Name of the product being reviewed"
    rating:
      type: number
      minimum: 1
      maximum: 5
      description: "Rating from 1 to 5 stars"
    pros:
      type: array
      items:
        type: string
      description: "Positive aspects mentioned"
    cons:
      type: array
      items:
        type: string
      description: "Negative aspects mentioned"
    sentiment:
      type: string
      enum: ["positive", "negative", "neutral"]
      description: "Overall sentiment"
  required: ["product_name", "rating", "sentiment"]
```

## 🐳 Docker Usage

### Development with Docker

```bash
# Build development image
docker build -t structured-output-cookbook:dev .

# Run interactive shell
docker run -it --rm \
  -e OPENAI_API_KEY="your-api-key" \
  -v $(pwd):/app \
  structured-output-cookbook:dev \
  /bin/bash

# Run specific command
docker run --rm \
  -e OPENAI_API_KEY="your-api-key" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  structured-output-cookbook:dev \
  list-templates
```

### Production Deployment

```bash
# For production, mount only necessary volumes
docker run -d \
  --name structured-output-service \
  -e OPENAI_API_KEY="your-api-key" \
  -v /path/to/data:/app/data \
  -v /path/to/schemas:/app/config/schemas \
  structured-output-cookbook:latest
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional
export OPENAI_MODEL="gpt-4o-mini"  # Default model
export LOG_LEVEL="INFO"            # Logging level
export MAX_TOKENS=4000            # Response token limit
export TEMPERATURE=0.1            # Model temperature
```

### Configuration File

Create a `.env` file in your project root:

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
MAX_TOKENS=4000
TEMPERATURE=0.1
```

## 📊 Examples

Check out the `examples/` directory for sample inputs and usage patterns:

- `examples/recipe.txt` - Recipe extraction example
- `examples/job_description.txt` - Job posting extraction
- `examples/news_article.txt` - News article analysis
- `examples/example_usage.py` - Python API examples
- `examples/usage_examples.ipynb` - Jupyter notebook with detailed examples

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/structured_output_cookbook

# Run specific test file
uv run pytest tests/unit/test_extractor.py

# Run integration tests
uv run pytest tests/integration/
```

## 🛠️ Development

```bash
# Install development dependencies
uv sync --all-extras

# Run linting
uv run ruff check .
uv run black --check .
uv run mypy src/

# Format code
uv run black .
uv run ruff --fix .

# Install pre-commit hooks
uv run pre-commit install
```

## 📈 Performance Tips

1. **Batch Processing**: Process multiple files in sequence for better efficiency
2. **Model Selection**: Use `gpt-4o-mini` for cost-effective extraction
3. **Schema Optimization**: Keep schemas focused and avoid unnecessary fields
4. **Caching**: Results are automatically saved with timestamps for reference

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [uv](https://docs.astral.sh/uv/) for fast dependency management
- Powered by OpenAI's language models
- Inspired by the need for reliable structured data extraction

## 📚 Related Projects

- [Instructor](https://github.com/jxnl/instructor) - Structured outputs with function calling
- [Marvin](https://github.com/prefecthq/marvin) - AI toolkit for building reliable AI-powered software
- [Outlines](https://github.com/outlines-dev/outlines) - Structured generation for LLMs

---

<div align="center">
  <strong>Made with ❤️ by <a href="https://github.com/mazzasaverio">Saverio Mazza</a></strong>
</div>
