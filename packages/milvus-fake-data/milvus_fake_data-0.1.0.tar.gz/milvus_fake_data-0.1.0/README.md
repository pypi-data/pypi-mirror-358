# Milvus Fake Data Generator

A powerful Python tool for generating realistic mock data for Milvus vector databases. Create test data quickly and efficiently using schema definitions, with support for all Milvus field types and built-in schemas for common use cases.

## ✨ Key Features

- 🎯 **Ready-to-use schemas** - Pre-built schemas for e-commerce, documents, images, users, news, and videos
- 📚 **Schema management** - Add, organize, and reuse custom schemas with metadata
- 🚀 **Flexible generation** - Support for JSON/YAML schema files with comprehensive field types
- 🔧 **Complete Milvus support** - All field types including vectors, arrays, JSON, and primitive types
- ✅ **Smart validation** - Pydantic-based validation with detailed error messages and suggestions
- 📊 **Multiple formats** - Output as Parquet, CSV, JSON, or NumPy arrays
- 🌱 **Reproducible results** - Seed support for consistent data generation
- 🎨 **Rich customization** - Field constraints, nullable fields, auto-generated IDs
- 🔍 **Schema exploration** - Validation, help commands, and schema details
- 🏠 **Unified interface** - Use custom and built-in schemas interchangeably

## Installation

```bash
# Install from PyPI (when published)
pip install milvus-fake-data

# Or install from source
git clone https://github.com/your-org/milvus-fake-data.git
cd milvus-fake-data
pdm install
```

## 🚀 Quick Start

### 1. Use Built-in Schemas (Recommended)

Get started instantly with pre-built schemas for common use cases:

```bash
# List all available built-in schemas
milvus-fake-data schema list

# Generate data using a built-in schema (backward compatible)
milvus-fake-data --builtin simple --rows 1000 --preview

# Generate data using explicit generate command
milvus-fake-data generate --builtin simple --rows 1000 --preview

# Generate e-commerce product data with output file
milvus-fake-data --builtin ecommerce --rows 5000 --out products.parquet
```

**Available Built-in Schemas:**
| Schema | Description | Use Cases |
|--------|-------------|-----------|
| `simple` | Basic example with common field types | Learning, testing |
| `ecommerce` | Product catalog with search embeddings | Online stores, recommendations |
| `documents` | Document search with semantic embeddings | Knowledge bases, document search |
| `images` | Image gallery with visual similarity | Media platforms, image search |
| `users` | User profiles with behavioral embeddings | User analytics, personalization |
| `videos` | Video library with multimodal embeddings | Video platforms, content discovery |
| `news` | News articles with sentiment analysis | News aggregation, content analysis |

### 2. Create Custom Schemas

Define your own collection structure with JSON or YAML:

```json
{
  "collection_name": "my_collection",
  "fields": [
    {
      "name": "id",
      "type": "Int64",
      "is_primary": true
    },
    {
      "name": "title",
      "type": "VarChar",
      "max_length": 256
    },
    {
      "name": "embedding",
      "type": "FloatVector",
      "dim": 128
    }
  ]
}
```

```bash
# Generate mock data from custom schema
milvus-fake-data --schema my_schema.json --rows 1000 --format csv --preview
```

### 3. Schema Management

Store and organize your schemas for reuse:

```bash
# Add a custom schema to your library
milvus-fake-data schema add my_products product_schema.json

# List all schemas (built-in + custom)
milvus-fake-data schema list

# Use your custom schema like a built-in one
milvus-fake-data --builtin my_products --rows 1000

# Show detailed schema information
milvus-fake-data schema show my_products
```

### 4. Python API

```python
from milvus_fake_data.generator import generate_mock_data
from milvus_fake_data.schema_manager import get_schema_manager
from milvus_fake_data.builtin_schemas import load_builtin_schema
from tempfile import NamedTemporaryFile
import json

# Use the schema manager to work with schemas
manager = get_schema_manager()

# List all available schemas
all_schemas = manager.list_all_schemas()
print("Available schemas:", list(all_schemas.keys()))

# Load any schema (built-in or custom)
schema = manager.load_schema("ecommerce")  # Built-in
# schema = manager.load_schema("my_products")  # Custom

# Generate data from schema
with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(schema, f)
    df = generate_mock_data(f.name, rows=1000, seed=42)

print(df.head())

# Add a custom schema programmatically
custom_schema = {
    "collection_name": "my_collection",
    "fields": [
        {"name": "id", "type": "Int64", "is_primary": True},
        {"name": "text", "type": "VarChar", "max_length": 100},
        {"name": "vector", "type": "FloatVector", "dim": 256}
    ]
}

manager.add_schema("my_custom", custom_schema, "Custom schema", ["testing"])
print("Added custom schema!")
```

## 📋 Schema Reference

### Supported Field Types

| Type | Description | Required Parameters | Optional Parameters |
|------|-------------|-------------------|-------------------|
| **Numeric Types** | | | |
| `Int8`, `Int16`, `Int32`, `Int64` | Integer types | - | `min`, `max` |
| `Float`, `Double` | Floating point | - | `min`, `max` |
| `Bool` | Boolean values | - | - |
| **Text Types** | | | |
| `VarChar`, `String` | Variable length string | `max_length` | - |
| `JSON` | JSON objects | - | - |
| **Vector Types** | | | |
| `FloatVector` | 32-bit float vectors | `dim` | - |
| `BinaryVector` | Binary vectors | `dim` | - |
| `Float16Vector` | 16-bit float vectors | `dim` | - |
| `BFloat16Vector` | Brain float vectors | `dim` | - |
| `Int8Vector` | 8-bit integer vectors | `dim` | - |
| `SparseFloatVector` | Sparse float vectors | `dim` | - |
| **Complex Types** | | | |
| `Array` | Array of elements | `element_type`, `max_capacity` | `max_length` (for string elements) |

### Field Properties

| Property | Description | Applicable Types |
|----------|-------------|------------------|
| `is_primary` | Mark field as primary key (exactly one required) | All types |
| `auto_id` | Auto-generate ID values | Int64 primary keys only |
| `nullable` | Allow null values (10% probability) | All types |
| `min`, `max` | Value constraints | Numeric types |
| `max_length` | String/element length limit | String and Array types |
| `dim` | Vector dimension (1-32768) | Vector types |
| `element_type` | Array element type | Array type |
| `max_capacity` | Array capacity (1-4096) | Array type |

### Complete Example

```yaml
collection_name: "advanced_catalog"
fields:
  # Primary key with auto-generated IDs
  - name: "id"
    type: "Int64"
    is_primary: true
    auto_id: true
  
  # Text fields with constraints
  - name: "title"
    type: "VarChar"
    max_length: 200
  
  - name: "description"
    type: "VarChar"
    max_length: 1000
    nullable: true
  
  # Numeric fields with ranges
  - name: "price"
    type: "Float"
    min: 0.01
    max: 9999.99
  
  - name: "rating"
    type: "Int8"
    min: 1
    max: 5
  
  # Vector for semantic search
  - name: "embedding"
    type: "FloatVector"
    dim: 768
  
  # Array of tags
  - name: "tags"
    type: "Array"
    element_type: "VarChar"
    max_capacity: 10
    max_length: 50
  
  # Structured metadata
  - name: "metadata"
    type: "JSON"
    nullable: true
  
  # Boolean flags
  - name: "in_stock"
    type: "Bool"
```

## 📚 CLI Reference

### Grouped Command Structure

The CLI now supports a cleaner grouped structure while maintaining backward compatibility:

```bash
# Main command groups
milvus-fake-data [generate options]  # Default: data generation (backward compatible)
milvus-fake-data generate [options]  # Explicit data generation
milvus-fake-data schema [command]    # Schema management
milvus-fake-data clean [options]     # Utility commands
```

### Migration Guide

**Old Commands → New Commands (both work!)**

| Old Command | New Command | Status |
|-------------|-------------|--------|
| `--list-schemas` | `schema list` | ✅ Both work |
| `--show-schema ID` | `schema show ID` | ✅ Both work |
| `--add-schema ID:FILE` | `schema add ID FILE` | ✅ New syntax preferred |
| `--remove-schema ID` | `schema remove ID` | ✅ Both work |
| `--schema-help` | `schema help` | ✅ Both work |
| `--clean` | `clean` | ✅ Both work |

### Data Generation Commands

| Command | Description | Example |
|---------|-------------|---------|
| `--schema PATH` | Generate from custom schema file | `--schema my_schema.json` |
| `--builtin SCHEMA_ID` | Use built-in or managed schema | `--builtin ecommerce` |
| `--rows INTEGER` | Number of rows to generate | `--rows 5000` |
| `--format FORMAT` | Output format (parquet, csv, json, npy) | `--format csv` |
| `--out PATH` | Output file path | `--out data.parquet` |
| `--preview` | Show first 5 rows | `--preview` |
| `--seed INTEGER` | Random seed for reproducibility | `--seed 42` |
| `--validate-only` | Validate schema without generating | `--validate-only` |

### Schema Management Commands

| Command | Description | Example |
|---------|-------------|---------|
| `schema list` | List all schemas (built-in + custom) | `milvus-fake-data schema list` |
| `schema show SCHEMA_ID` | Show schema details | `milvus-fake-data schema show ecommerce` |
| `schema add SCHEMA_ID FILE` | Add custom schema | `milvus-fake-data schema add products schema.json` |
| `schema remove SCHEMA_ID` | Remove custom schema | `milvus-fake-data schema remove products` |
| `schema help` | Show schema format help | `milvus-fake-data schema help` |

### Utility Commands

| Command | Description | Example |
|---------|-------------|---------|
| `clean` | Clean up generated output files | `milvus-fake-data clean --yes` |
| `--help` | Show help message | `milvus-fake-data --help` |

### Common Usage Patterns

```bash
# Quick start with built-in schema (backward compatible)
milvus-fake-data --builtin simple --rows 1000 --preview

# Using explicit generate command
milvus-fake-data generate --builtin simple --rows 1000 --preview

# Generate large dataset with custom format
milvus-fake-data --builtin ecommerce --rows 100000 --format csv --out products.csv

# Test custom schema
milvus-fake-data --schema my_schema.json --validate-only

# Reproducible data generation
milvus-fake-data --builtin users --rows 5000 --seed 42 --out users.parquet

# Schema management workflow
milvus-fake-data schema list
milvus-fake-data schema show ecommerce
# Add custom schema
milvus-fake-data schema add my_ecommerce ecommerce_base.json

# Clean up generated output files
milvus-fake-data clean --yes
```

## 🛠️ Development

This project uses PDM for dependency management and follows modern Python development practices.

### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/your-org/milvus-fake-data.git
cd milvus-fake-data
pdm install  # Install development dependencies
```

### Development Workflow

```bash
# Code formatting and linting
pdm run ruff format src tests    # Format code
pdm run ruff check src tests     # Check linting
pdm run mypy src                 # Type checking

# Testing
pdm run pytest                           # Run all tests
pdm run pytest --cov=src --cov-report=html  # With coverage
pdm run pytest tests/test_generator.py   # Specific test file

# Combined quality checks
make lint test                   # Run linting and tests together
```

### Project Structure

```
src/milvus_fake_data/
├── cli.py              # Command-line interface
├── generator.py        # Core data generation logic
├── models.py           # Pydantic validation models
├── schema_manager.py   # Schema management system
├── builtin_schemas.py  # Built-in schema definitions
├── rich_display.py     # Terminal formatting
├── logging_config.py   # Structured logging
└── schemas/            # Built-in schema files
    ├── simple.json
    ├── ecommerce.json
    └── ...
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes with tests
4. **Ensure** quality checks pass: `make lint test`
5. **Commit** changes: `git commit -m 'Add amazing feature'`
6. **Push** to branch: `git push origin feature/amazing-feature`
7. **Open** a Pull Request

### Contribution Guidelines

- Add tests for new functionality
- Update documentation for API changes
- Follow existing code style (ruff + mypy)
- Include helpful error messages for user-facing features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the [Milvus](https://milvus.io/) vector database
- Uses [Faker](https://faker.readthedocs.io/) for realistic data generation
- Powered by [Pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/)
