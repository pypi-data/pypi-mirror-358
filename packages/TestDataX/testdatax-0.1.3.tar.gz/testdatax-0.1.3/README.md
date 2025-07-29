# TestDataX

# TestDataX

![Build Status](https://github.com/JamesPBrett/testdatax/actions/workflows/publish.yml/badge.svg)
[![codecov](https://codecov.io/gh/JamesPBrett/testdatax/branch/main/graph/badge.svg?token=6VX62CI6U9)](https://codecov.io/gh/JamesPBrett/testdatax)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

This command-line interface application enables quick and customizable test data generation across various formats. It supports multiple data providers (Mimesis and Faker) for realistic data generation, offers flexible schema configurations, and simplifies output to multiple database dialects or file types. Users can define precise parameters for data volume, types, and constraints for each target data set.

## Requirements
- Python 3.11+

## Quick Start

```bash
# Install from PyPI
pip install testdatax

# Generate sample data
testdatax --rows 1000 --format json --output data.json


## Features

- Generate realistic test data using multiple data providers (Mimesis, Faker)
- Support for multiple output formats (CSV, JSON, SQL, etc.)
- Customizable schema definitions
- Configurable data generation parameters
- CLI tool for easy test data generation

## Supported Formats

- JSON
- CSV
- ORC
- Parquet
- MySQL
- MSSQL
- Oracle

## CLI Usage
```bash
testdatax -o <output_file> -f <format> -s <schema_file> -r <num_rows> -p <provider> [-d]
```

Options:
- `-o, --output`: Output file path (table_name for sql exports)
- `-f, --format`: Output format (csv, json, orc, parquet, mysql, mssql, oracle)
- `-r, --rows`: Number of rows to generate (default: 10)
- `-s, --schema`: Path to schema file
- `-p, --provider`: Data provider (mimesis, faker) - default: mimesis
- `-d, --debug`: Enable debug output

## Usage Examples

Generate 10 rows of CSV data:
```bash
testdatax -o users.csv -f csv -s schema.json -r 10
```

Generate 10 rows of CSV data using Faker provider:
```bash
testdatax -o users.csv -f csv -s schema.json -r 10 -p faker
```

Generate 1000 rows of Parquet data with debug output:
```bash
testdatax -o large_dataset.parquet -f parquet -s users_schema.json -r 1000 -d
```

Generate 1000 rows of Parquet data using Mimesis provider:
```bash
testdatax -o large_dataset.parquet -f parquet -s users_schema.json -r 1000 -p mimesis
```
Generate JSON data with default row count (10):
```bash
testdatax -o data.json -f json -s schema.json
```

Generate ORC file with specific schema:
```bash
testdatax -o analytics.orc -f orc -s analytics_schema.json -r 100
```

Generate MySQL with default row count (1000), table_name as 'default':
```bash
testdatax -o default.sql -f mysql -r 1000
```

Generate MSSQL with default row count (1000), table_name as 'mstest':
```bash
testdatax -o mstest.sql -f mssql -r 1000
```

Generate Oracle with default row count (1000), table_name as 'oracle':
```bash
datagen -o oracle.sql -f oracle -r 1000
```

Each command consists of:
- `-o, --output`: Specify the output file path and name
- `-f, --format`: Output format (csv, json, orc, parquet, mysql, mssql, oracle)
- `-s, --schema`: Path to your schema definition file
- `-r, --rows`: Number of rows to generate (optional, defaults to 10)
- `-p, --provider`: Data provider (mimesis, faker) - default: mimesis
- `-d, --debug`: Enable debug logging (optional)

## Schema Example

```json
{
  "username": {
    "type": "string",
    "provider_field": "name"
  },
  "date_joined": {
    "type": "datetime"
  },
  "date": {
    "type": "date"
  },
  "age": {
    "type": "integer",
    "min": 18,
    "max": 99
  },
  "is_active": {
    "type": "boolean"
  },
  "float": {
    "type": "float"
  },
  "uuid": {
    "type": "uuid"
  },
  "status": {
    "type": "enum",
    "values": ["active", "inactive", "pending"]
  }
}
```

## Schema Configuration

The schema file defines the structure and constraints of your generated data. Each field in the schema can have the following properties:

### Basic Field Properties
- `type`: (required) The data type of the field
- `nullable`: (optional) Boolean to allow null values (default: false)
- `unique`: (optional) Boolean to ensure unique values (default: false)

### Type-Specific Properties

#### String Fields
```json
{
  "username": {
    "type": "string",
    "min_length": 5,
    "max_length": 20,
    "provider_field": "user_name"  // Use provider-specific field to generate realistic data
  },
  "description": {
    "type": "text",
    "min_length": 100,
    "max_length": 500
  }
}
```

#### Numeric Fields
```json
{
  "age": {
    "type": "integer",
    "min": 18,
    "max": 99
  },
  "score": {
    "type": "float",
    "min": 0.0,
    "max": 100.0,
    "precision": 2
  }
}
```

#### Date and Time Fields
```json
{
  "created_at": {
    "type": "datetime",
    "start_date": "2020-01-01",
    "end_date": "2023-12-31"
  },
  "birth_date": {
    "type": "date",
    "format": "%Y-%m-%d"
  }
}
```

#### Enum Fields
```json
{
  "status": {
    "type": "enum",
    "values": ["pending", "active", "suspended"],
    "weights": [0.2, 0.7, 0.1]  // Optional probability weights
  }
}
```

#### Using Data Providers
Both Mimesis and Faker providers support the same schema format. You can specify provider-specific generators using the `provider_field` field (works with both providers):
```json
{
  "name": {
    "type": "string",
    "provider_field": "name"
  },
  "email": {
    "type": "string",
    "provider_field": "email"
  },
  "address": {
    "type": "string",
    "provider_field": "address"
  },
  "company": {
    "type": "string",
    "provider_field": "company"
  }
}
```

### Complete Example
```json
{
  "user_id": {
    "type": "uuid",
    "unique": true
  },
  "username": {
    "type": "string",
    "provider_field": "user_name",
    "unique": true
  },
  "email": {
    "type": "string",
    "provider_field": "email",
    "unique": true
  },
  "age": {
    "type": "integer",
    "min": 18,
    "max": 99
  },
  "status": {
    "type": "enum",
    "values": ["active", "inactive"],
    "weights": [0.8, 0.2]
  },
  "created_at": {
    "type": "datetime",
    "start_date": "2020-01-01",
    "end_date": "2023-12-31"
  },
  "is_verified": {
    "type": "boolean",
    "nullable": true
  }
}
```

## Data Providers

TestDataX supports two powerful data providers for generating realistic test data:

### Mimesis (Default)
Mimesis is a high-performance Python library for generating synthetic data. It provides:
- Fast data generation with excellent performance
- Support for multiple locales and languages
- Wide variety of data providers for different domains
- Lightweight and efficient implementation

### Faker
Faker is a popular Python library for generating fake data. It offers:
- Extensive provider ecosystem with community contributions
- Rich set of localized providers
- Well-established and widely used in the Python community
- Comprehensive documentation and examples

You can specify the provider using the `-p` or `--provider` option:
```bash
# Use Mimesis (default)
testdatax -o data.csv -f csv -p mimesis

# Use Faker
testdatax -o data.csv -f csv -p faker
```

Both providers support the same schema format and generate compatible data types.

**Note:** For backward compatibility, the legacy `faker` field name is still supported, but `provider_field` is recommended for new schemas.

## Supported Data Types

- string
- text
- integer
- bigint
- float
- decimal
- boolean
- date
- datetime
- blob
- uuid
- enum

## Database Type Mappings

| Generic Type | MySQL         | MSSQL             | Oracle        |
|--------------|---------------|-------------------|---------------|
| string       | VARCHAR(255)  | NVARCHAR(255)     | VARCHAR2(255) |
| text         | TEXT          | NVARCHAR(MAX)     | CLOB          |
| integer      | INT           | INT               | NUMBER(10)    |
| bigint       | BIGINT        | BIGINT            | NUMBER(19)    |
| float        | FLOAT         | FLOAT             | FLOAT         |
| decimal      | DECIMAL(18,2) | DECIMAL(18,2)     | NUMBER(18,2)  |
| boolean      | TINYINT(1)    | BIT               | NUMBER(1)     |
| date         | DATE          | DATE              | DATE          |
| datetime     | DATETIME      | DATETIME2         | TIMESTAMP     |
| blob         | LONGBLOB      | VARBINARY(MAX)    | BLOB          |
| uuid         | VARCHAR(36)   | UNIQUEIDENTIFIER  | VARCHAR2(36)  |
| enum         | ENUM          | NVARCHAR(255)     | VARCHAR2(255) |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
