# Export Format Examples

This document shows examples of how envyro exports configurations to different formats.

## Input `.envyro` File

```ini
[envs]
environments = prod, dev, stage, local
default = dev

[app]
name = "MyApp"
version = [prod]:1.0.0 [dev]:0.1.0 [stage]:0.2.0 [local]:0.3.0
description = "Unified app config"
author = "John Doe"

[db]
host = [prod]:prod-db.example.com [*]:localhost
port = 5432
user = [prod]:prod_user [*]:local_user
password = [prod]:prod_pass [*]:dev_pass

[aws.s3]
bucket = [prod]:prod-bucket [dev]:dev-bucket [stage]:stage-bucket [local]:local-bucket
region = [*]:us-east-1
```

## Export Formats

### 1. ENV Format (Default)
```bash
envyro export --env dev
```

**Output (.env.dev):**
```env
APP_NAME=MyApp
APP_VERSION=0.1.0
APP_DESCRIPTION=Unified app config
APP_AUTHOR=John Doe
DB_HOST=localhost
DB_PORT=5432
DB_USER=local_user
DB_PASSWORD=dev_pass
AWS_S3_BUCKET=dev-bucket
AWS_S3_REGION=us-east-1
```

### 2. JSON Format
```bash
envyro export --env dev --format json
```

**Output (config.dev.json):**
```json
{
  "app": {
    "name": "MyApp",
    "version": "0.1.0",
    "description": "Unified app config",
    "author": "John Doe"
  },
  "db": {
    "host": "localhost",
    "port": "5432",
    "user": "local_user",
    "password": "dev_pass"
  },
  "aws": {
    "s3": {
      "bucket": "dev-bucket",
      "region": "us-east-1"
    }
  }
}
```

### 3. YAML Format
```bash
envyro export --env dev --format yaml
```

**Output (config.dev.yaml):**
```yaml
app:
  name: MyApp
  version: "0.1.0"
  description: Unified app config
  author: John Doe
db:
  host: localhost
  port: "5432"
  user: local_user
  password: dev_pass
aws:
  s3:
    bucket: dev-bucket
    region: us-east-1
```

### 4. TOML Format
```bash
envyro export --env dev --format toml
```

**Output (config.dev.toml):**
```toml
[app]
name = "MyApp"
version = "0.1.0"
description = "Unified app config"
author = "John Doe"

[db]
host = "localhost"
port = "5432"
user = "local_user"
password = "dev_pass"

[aws.s3]
bucket = "dev-bucket"
region = "us-east-1"
```

## Production Environment Examples

### JSON for Production
```bash
envyro export --env prod --format json
```

**Output (config.prod.json):**
```json
{
  "app": {
    "name": "MyApp",
    "version": "1.0.0",
    "description": "Unified app config",
    "author": "John Doe"
  },
  "db": {
    "host": "prod-db.example.com",
    "port": "5432",
    "user": "prod_user",
    "password": "prod_pass"
  },
  "aws": {
    "s3": {
      "bucket": "prod-bucket",
      "region": "us-east-1"
    }
  }
}
```

## Use Cases

### 1. Docker Compose
```bash
envyro export --env dev --format env --output .env
docker-compose up
```

### 2. Kubernetes ConfigMap
```bash
envyro export --env prod --format yaml --output k8s-config.yaml
kubectl apply -f k8s-config.yaml
```

### 3. Application Configuration
```bash
envyro export --env dev --format json --output app-config.json
# Use in your application
```

### 4. CI/CD Pipeline
```bash
envyro export --env $CI_ENVIRONMENT --format env --output .env
# Deploy with environment-specific config
``` 