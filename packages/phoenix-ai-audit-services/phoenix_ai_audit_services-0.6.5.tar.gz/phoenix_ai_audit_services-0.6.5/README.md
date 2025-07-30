# phoenix‑ai‑audit‑services 🛡️🪄

FastAPI micro‑service for auditing and governing Phoenix‑AI agents & tools.

## 🚀 Quick start

```bash
# 1. Install Poetry if you haven't
curl -sSL https://install.python-poetry.org | python -

# 2. Clone & install deps
git clone https://github.com/Praveengovianalytics/phoenix-ai-audit-services.git

cd phoenix-ai-audit-services
cp .env.example .env               # adjust POSTGRES_DSN if desired
poetry install --sync

# 3. Run (SQLite fallback)
poetry run phoenix-ai-audit-services --reload

# or
poetry run python scripts/run_api.py --reload


phoenix-ai-audit-services/
│
├─ pyproject.toml
├─ README.md
├─ .env.example
│
├─ phoenix_ai_audit_services/          # ← import package
│  ├─ __init__.py
│  ├─ config.py
│  ├─ models.py
│  ├─ crud.py
│  ├─ storage/
│  │   ├─ __init__.py
│  │   ├─ base.py
│  │   ├─ postgres.py
│  │   └─ file.py
│  ├─ api.py
│  └─ main.py
│
├─ phoenix_ai_audit_api.py             # compatibility shim
│
├─ scripts/
│  ├─ run_api.py
│  └─ smoke_test.py
│
└─ tests/
   ├─ conftest.py
   ├─ test_health.py
   └─ test_crud_roundtrip.py
