# 🛠️ Envyro: Environment Configuration Simplified

`Envyro` is a modern configuration format and CLI tool for managing environment variables across multiple environments like `dev`, `prod`, `stage`, and `local`. It uses a custom `.envyro` format that supports **nesting**, **multi-env inline values**, and **structured scoping**.

---

## 🔍 Features

### 1. 🔄 Convert `.envyro` to `.env`
Generate traditional `.env` files for a specific environment by parsing a structured `.envyro` file.

**Command:**
```bash
envyro export --env dev
```

### 2. 📤 Export Environment Variables to Shell
Directly export variables to your current shell environment for a given environment.

**Command:**
```bash
source <(envyro export --env dev --shell)
```

### 3. 📦 Split `.envyro` into Multiple `.env` Files
Break a single `.envyro` file into multiple `.env` files like `.env.dev`, `.env.prod`, etc.

**Command:**
```bash
envyro split
```

---

## 🧪 Example `.envyro` Format

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

[aws.sns]
topic = [prod]:arn:aws:sns:us-west-1:123456789012:prod-topic [dev]:arn:aws:sns:us-west-2:123456789012:dev-topic
```

---

## 🧠 Advantages of `.envyro`

- ✅ Supports **nesting** like `[aws.s3]`, `[db.connection]`
- ✅ **Single-file config** for all environments
- ✅ Allows **default (`[*]`) and environment-specific values**
- ✅ Cleaner and more maintainable than multiple `.env` files
- ✅ Easy to convert into `.env`, `.yaml`, or Python dict

---

## 🧰 Installation

You can install `envyro` as a local tool (coming soon as a CLI tool). For now, clone and run manually.

```bash
git clone https://github.com/your-org/envyro
cd envyro
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 👨‍💻 Author

Made with ❤️ by Manmeet Kohli, was there a need ? Don't know....

---

## 📜 License

MIT License