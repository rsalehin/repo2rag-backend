# Repository Content
**Total files:** 24
**Total tokens:** 11786

---

## File: .env.example (9 tokens)

```
DATABASE_PATH=data/bauamt_permits.db
```

## File: .gitattributes (81 tokens)

```
* text=auto

*.py text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
*.json text eol=lf
*.toml text eol=lf
*.sql text eol=lf

*.bat text eol=crlf
*.ps1 text eol=crlf
```

## File: .github/workflows/ci.yml (132 tokens)

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest tests/test_tools.py
```

## File: .gitignore (98 tokens)

```
# Python bytecode/cache
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
env/

# Test/cache artifacts
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Environment files
.env

# Generated local database files
data/*.db
data/*.sqlite
data/*.sqlite3

# OS/editor noise
.DS_Store
Thumbs.db
.vscode/
.idea/
```

## File: architecture.md (634 tokens)

```markdown
# Architecture — Bauamt MCP Permit Agent

## Purpose

This project demonstrates how a legacy-style municipal permit system can be exposed to an AI assistant through a narrow MCP layer.

The goal is not to build a full Bauamt web application. The goal is to show the integration pattern:

Claude Desktop
→ MCP server
→ domain tools
→ permit database
→ structured answer

## System overview

Claude Desktop acts as the MCP host.

The Python MCP server exposes four domain-specific tools:

- search_permits
- get_permit_details
- get_kpi_summary
- prepare_data_entry

The tools query a local SQLite database seeded with 50 fake German building-permit records.

## Runtime flow

1. A clerk asks Claude a German natural-language question.
2. Claude decides whether one of the MCP tools is useful.
3. Claude calls the MCP tool with structured arguments.
4. The Python server validates the tool call through typed function signatures.
5. The tool queries the SQLite permit database.
6. The tool returns structured data.
7. Claude explains the result in natural language.

## Data layer

The demo uses SQLite for portability.

In a production system, this layer could be replaced by:

- PostgreSQL
- Oracle
- Microsoft SQL Server
- an existing Fachverfahren database
- an internal HTTP API

The important design point is that the MCP tool layer hides raw database access from Claude.

## Tool boundary

Claude does not receive arbitrary SQL access.

Instead, Claude only gets narrow domain operations:

### search_permits

Read-only search over permits.

### get_permit_details

Read-only detail retrieval for one permit.

### get_kpi_summary

Read-only reporting/KPI calculation.

### prepare_data_entry

Draft-only write preparation.

This tool does not write to the database. It returns a structured draft that a human clerk must review.

## Safety model

The server follows three safety rules:

1. No arbitrary SQL tool.
2. No direct write operation from Claude.
3. Write-like actions return draft payloads only.

The response from prepare_data_entry always includes:

- database_updated: false
- requires_human_confirmation: true

## Why MCP here?

An ordinary API is still mainly a developer-facing integration surface.

An MCP server makes selected system capabilities directly usable by an MCP-capable AI client. Claude can discover and call the exposed tools during a conversation.

This is useful for legacy business systems because the first modernization step does not need to be a full UI rewrite. A thin MCP adapter can make selected workflows agent-accessible.

## Current limitations

This is a portfolio demo, not a production system.

Production hardening would require:

- authentication
- authorization
- audit logging
- structured observability
- deployment configuration
- real database integration
- stricter input validation
- approval workflow UI
- rate limiting
- permission-aware tool exposure

## Interview takeaway

The architectural pattern is:

Existing Fachverfahren
→ narrow safe tool layer
→ MCP server
→ AI assistant
→ faster clerk workflow

The system becomes agent-accessible without giving the AI unrestricted access to the underlying database.
```

## File: demo-script.md (1018 tokens)

```markdown
# Demo Script — Bauamt MCP Permit Agent

## One-sentence pitch

This demo shows how a legacy-style German Bauamt permit system can be exposed as an MCP server so Claude can search permits, inspect missing documents, calculate office KPIs, and prepare draft-only data entries from natural German instructions.

## Core interview thesis

Das Fachsystem war bisher nur über seine eigene Oberfläche nutzbar. Als MCP-Server kann Claude die relevanten Fachfunktionen direkt verwenden: Bauanträge suchen, fehlende Unterlagen anzeigen, KPIs berechnen und Dateneingaben vorbereiten. Der Sachbearbeiter muss dafür nicht mehr manuell durch das System navigieren, und kritische Änderungen bleiben trotzdem prüfpflichtig.

## What the demo proves

- MCP tool integration over a domain system
- German natural-language workflow
- Structured permit search
- Detail retrieval
- KPI calculation
- Safe draft-only write preparation
- No arbitrary SQL exposure
- Human approval boundary for risky actions

## Pre-demo checks

Run before the interview:

pytest tests/test_tools.py

Expected:

6 passed

## Demo prompt 1 — Search permits

Ask Claude:

Finde alle Bauanträge für Hauptstraße 12 aus dem Jahr 2024.

Expected MCP tool:

search_permits

Expected visible result:

- Permit ID: BG-2024-0847
- Applicant: Müller Bau GmbH
- Address: Hauptstraße 12, Leipzig
- Status: unterlagen_fehlen
- Assigned clerk: Frau Schneider

Suggested explanation:

Hier sieht man den ersten Nutzen: Der Sachbearbeiter muss nicht manuell im Fachsystem suchen. Claude ruft gezielt das MCP-Tool search_permits auf und bekommt strukturierte Fachdaten zurück.

## Demo prompt 2 — Missing documents

Ask Claude:

Welche Unterlagen fehlen noch für BG-2024-0847?

Expected MCP tool:

get_permit_details

Expected visible result:

- Brandschutznachweis
- Statiknachweis

Suggested explanation:

Claude beantwortet die Frage nicht aus freiem Text oder Halluzination, sondern über ein eng definiertes Fach-Tool. Das ist wichtig, weil die Antwort aus dem Systemzustand kommt.

## Demo prompt 3 — KPI reporting

Ask Claude:

Wie viele Anträge im BAUAMT-LE-01 sind zwischen 2024-01-01 und 2026-12-31 mehr als 30 Tage überfällig?

Expected MCP tool:

get_kpi_summary

Expected visible result includes:

- total_permits
- pending_permits
- overdue_more_than_30_days
- missing_documents_cases
- average_nominal_processing_days

Suggested explanation:

Das ist der Reporting-Teil. Statt manuell Daten aus dem System zu kopieren, kann Claude eine KPI-Abfrage ausführen und die Zahlen direkt strukturiert zurückgeben.

## Demo prompt 4 — Safe draft-only data entry

Ask Claude:

Bereite eine Dateneingabe vor, um BG-2024-0847 als genehmigungsbereit zu markieren. Setze das Freigabedatum auf 2026-04-26 und füge die Notiz hinzu: Alle erforderlichen Unterlagen liegen vor. Nicht speichern.

Expected MCP tool:

prepare_data_entry

Expected safety result:

- database_updated: false
- requires_human_confirmation: true

Suggested explanation:

Das ist bewusst kein echter Schreibzugriff. Claude darf eine Dateneingabe vorbereiten, aber nicht direkt speichern. Damit bleibt der Sachbearbeiter in der Verantwortung, und kritische Änderungen bleiben prüfpflichtig.

## Why MCP instead of only an API?

Eine API wäre weiterhin primär eine Entwickler-Schnittstelle. Ein MCP-Server macht die Fachfunktionen direkt für einen LLM-Client nutzbar. Claude kann die verfügbaren Tools erkennen, gezielt aufrufen und strukturierte Ergebnisse in der Unterhaltung verwenden.

## Safety boundary

Claude bekommt keine freie SQL-Schnittstelle. Es gibt nur fachlich definierte Operationen:

- search_permits
- get_permit_details
- get_kpi_summary
- prepare_data_entry

prepare_data_entry ist absichtlich draft-only. Es schreibt nicht in die Datenbank.

## Closing line for the interview

Das eigentliche Muster ist: Ein bestehendes Fachsystem muss nicht sofort komplett neu gebaut werden. Man kann zuerst eine sichere MCP-Schicht über die wichtigsten Fachfunktionen legen und dadurch das System agentenfähig machen.
```

## File: docker-compose.yml (0 tokens)

```yaml

```

## File: docs/claude_desktop_config.example.json (152 tokens)

```json
{
  "mcpServers": {
    "bauamt-permit-agent": {
      "command": "C:\\Users\\rsalehin\\OneDrive\\Desktop\\Projects\\bauamt-mcp-permit-agent\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "src.bauamt_mcp.server"
      ],
      "env": {
        "DATABASE_PATH": "C:\\Users\\rsalehin\\OneDrive\\Desktop\\Projects\\bauamt-mcp-permit-agent\\data\\bauamt_permits.db",
        "PYTHONPATH": "C:\\Users\\rsalehin\\OneDrive\\Desktop\\Projects\\bauamt-mcp-permit-agent"
      }
    }
  }
}
```

## File: docs/mcp-inspector-test-guide.md (608 tokens)

```markdown
# MCP Inspector Test Guide

## Purpose

Use MCP Inspector to verify that the Bauamt MCP server exposes the expected tools and that each tool can be called independently of Claude Desktop.

MCP Inspector is useful as a fallback/debugging tool before an interview demo.

## Prerequisites

- Node.js installed
- Python virtual environment created
- Python dependencies installed
- Demo database seeded

## Pre-check

From the project root, run:

python -m src.bauamt_mcp.seed
pytest tests/test_tools.py

Expected:

6 passed

## Start MCP Inspector

From the project root, run:

npx @modelcontextprotocol/inspector .\.venv\Scripts\python.exe -m src.bauamt_mcp.server

MCP Inspector should open a local browser UI.

## Expected tools

The Inspector should show these tools:

- search_permits
- get_permit_details
- get_kpi_summary
- prepare_data_entry

## Test call 1 — search_permits

Tool:

search_permits

Arguments:

{
  "address": "Hauptstraße 12",
  "submitted_year": 2024
}

Expected result includes:

- BG-2024-0847
- Müller Bau GmbH
- Hauptstraße 12, Leipzig
- unterlagen_fehlen

## Test call 2 — get_permit_details

Tool:

get_permit_details

Arguments:

{
  "permit_id": "BG-2024-0847"
}

Expected result includes:

- Brandschutznachweis
- Statiknachweis
- Frau Schneider

## Test call 3 — get_kpi_summary

Tool:

get_kpi_summary

Arguments:

{
  "office_id": "BAUAMT-LE-01",
  "start_date": "2024-01-01",
  "end_date": "2026-12-31"
}

Expected result includes:

- total_permits
- pending_permits
- overdue_more_than_30_days
- missing_documents_cases
- average_nominal_processing_days

## Test call 4 — prepare_data_entry

Tool:

prepare_data_entry

Arguments:

{
  "permit_id": "BG-2024-0847",
  "field_updates": {
    "status": "genehmigungsbereit",
    "approval_date": "2026-04-26",
    "clerk_note": "Alle erforderlichen Unterlagen liegen vor.",
    "dangerous_sql": "DROP TABLE permits"
  }
}

Expected safety result:

- prepared: true
- database_updated: false
- requires_human_confirmation: true
- rejected_fields contains dangerous_sql

## Interview use

If Claude Desktop integration fails, open MCP Inspector and show that the server exposes the tools correctly.

Then run the smoke demo:

python -m src.bauamt_mcp.smoke_demo

This proves the backend/tool layer works even if the Claude Desktop client setup is not available.
```

## File: docs/security-notes.md (398 tokens)

```markdown
# Security Notes — Bauamt MCP Permit Agent

## Security posture

This project is a local portfolio demo. It is not a production-ready government software system.

The goal is to demonstrate a safe MCP integration pattern over a domain workflow.

## Main risks

MCP servers expose tools to AI clients. That creates an action surface.

Important risks include:

- excessive tool permissions
- unsafe write operations
- arbitrary SQL access
- prompt/tool injection
- misleading tool descriptions
- accidental exposure of sensitive data
- missing audit logging
- unclear human approval boundaries

## Design decisions in this demo

### No arbitrary SQL

Claude does not receive a generic SQL tool.

Instead, the server exposes only domain-specific tools:

- search_permits
- get_permit_details
- get_kpi_summary
- prepare_data_entry

### Draft-only write preparation

The prepare_data_entry tool intentionally does not write to the database.

It only returns a proposed update.

Expected safety fields:

- database_updated: false
- requires_human_confirmation: true

### Synthetic data only

The database contains fake permit records generated for the demo.

No real citizen, company, or government data is used.

### Narrow tool surface

Each tool maps to one business operation.

The tools do not expose:

- shell execution
- raw file access
- arbitrary database mutation
- unrestricted external API calls

## Production hardening checklist

Before a real deployment, this system would need:

- authentication
- role-based authorization
- permission-aware tool exposure
- audit logging
- approval workflow UI
- input validation
- output validation
- secret management
- monitoring and alerting
- deployment isolation
- rate limiting
- security review of tool descriptions
- tests for prompt injection and tool misuse

## Interview takeaway

The important principle is not "let Claude access everything."

The principle is:

Expose only narrow, auditable, domain-specific operations through MCP, and keep risky actions behind human review.
```

## File: pyproject.toml (149 tokens)

```
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "bauamt-mcp-permit-agent"
version = "0.1.0"
description = "Local MCP server exposing a synthetic German Bauamt permit workflow to Claude."
readme = "README.md"
requires-python = ">=3.11"
authors = [
    { name = "Rafiqus Salehin" }
]
dependencies = [
    "mcp",
    "faker",
    "pytest",
    "python-dotenv"
]

[project.optional-dependencies]
dev = [
    "pytest"
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

## File: pytest.ini (11 tokens)

```
[pytest]
pythonpath = .
testpaths = tests
```

## File: README.md (649 tokens)

```markdown
# Bauamt MCP Permit Agent

A local MCP server that exposes a synthetic German municipal building-permit system to Claude.

## Demo thesis

A Bauamt clerk normally has to open a permit-management system, search for a permit, inspect missing documents, copy KPI values into reports, and prepare form entries manually.

This project shows how the same workflow can be exposed through MCP tools so Claude can interact with the domain system directly from German natural language.

## What Claude can do

- Search building permits
- Retrieve permit details
- Show missing documents
- Calculate office-level KPIs
- Prepare draft-only data entries
- Keep write-like actions behind human approval

## MCP tools

### search_permits

Search permits by applicant name, address, status, or submitted year.

Example:

Finde alle Bauanträge für Hauptstraße 12 aus dem Jahr 2024.

### get_permit_details

Retrieve full details for one permit.

Example:

Welche Unterlagen fehlen noch für BG-2024-0847?

### get_kpi_summary

Calculate KPI summaries for an office and date range.

Example:

Wie viele Anträge im BAUAMT-LE-01 sind zwischen 2024-01-01 und 2026-12-31 mehr als 30 Tage überfällig?

### prepare_data_entry

Prepare a draft data-entry update without writing to the database.

Example:

Bereite eine Dateneingabe vor, um BG-2024-0847 als genehmigungsbereit zu markieren. Nicht speichern.

## Safety model

Claude does not receive arbitrary SQL access.

The MCP server exposes only narrow domain tools. The write-like tool, prepare_data_entry, is intentionally draft-only:

- database_updated: false
- requires_human_confirmation: true

## Tech stack

- Python
- MCP Python SDK / FastMCP
- SQLite
- Faker
- pytest

## Setup

Create and activate a virtual environment:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r requirements.txt

Seed demo data:

python -m src.bauamt_mcp.seed

Run tests:

pytest tests/test_tools.py

## Run MCP server manually

python -m src.bauamt_mcp.server

The process waits for an MCP client over stdio. If started manually, stop it with Ctrl+C.

## Claude Desktop config

See:

docs/claude_desktop_config.example.json

Use that as a template for your local Claude Desktop MCP configuration.

## Demo record

The seed data always includes this known record:

- Permit ID: BG-2024-0847
- Applicant: Müller Bau GmbH
- Address: Hauptstraße 12, Leipzig
- Status: unterlagen_fehlen
- Missing documents:
  - Brandschutznachweis
  - Statiknachweis

## Interview positioning

This is not just a chatbot. It is a thin MCP layer over a domain system.

The point is that an existing Fachverfahren can become agent-accessible without rebuilding the whole UI first.
```

## File: requirements.txt (1497 tokens)

```text
��a n n o t a t e d - t y p e s = = 0 . 7 . 0  
 a n y i o = = 4 . 1 3 . 0  
 a t t r s = = 2 6 . 1 . 0  
 c e r t i f i = = 2 0 2 6 . 4 . 2 2  
 c f f i = = 2 . 0 . 0  
 c l i c k = = 8 . 3 . 3  
 c o l o r a m a = = 0 . 4 . 6  
 c r y p t o g r a p h y = = 4 7 . 0 . 0  
 F a k e r = = 4 0 . 1 5 . 0  
 h 1 1 = = 0 . 1 6 . 0  
 h t t p c o r e = = 1 . 0 . 9  
 h t t p x = = 0 . 2 8 . 1  
 h t t p x - s s e = = 0 . 4 . 3  
 i d n a = = 3 . 1 3  
 i n i c o n f i g = = 2 . 3 . 0  
 j s o n s c h e m a = = 4 . 2 6 . 0  
 j s o n s c h e m a - s p e c i f i c a t i o n s = = 2 0 2 5 . 9 . 1  
 m c p = = 1 . 2 7 . 0  
 p a c k a g i n g = = 2 6 . 2  
 p l u g g y = = 1 . 6 . 0  
 p s y c o p g = = 3 . 3 . 3  
 p s y c o p g - b i n a r y = = 3 . 3 . 3  
 p y c p a r s e r = = 3 . 0  
 p y d a n t i c = = 2 . 1 3 . 3  
 p y d a n t i c - s e t t i n g s = = 2 . 1 4 . 0  
 p y d a n t i c _ c o r e = = 2 . 4 6 . 3  
 P y g m e n t s = = 2 . 2 0 . 0  
 P y J W T = = 2 . 1 2 . 1  
 p y t e s t = = 9 . 0 . 3  
 p y t h o n - d o t e n v = = 1 . 2 . 2  
 p y t h o n - m u l t i p a r t = = 0 . 0 . 2 6  
 p y w i n 3 2 = = 3 1 1  
 r e f e r e n c i n g = = 0 . 3 7 . 0  
 r p d s - p y = = 0 . 3 0 . 0  
 s s e - s t a r l e t t e = = 3 . 3 . 4  
 s t a r l e t t e = = 1 . 0 . 0  
 t y p i n g - i n s p e c t i o n = = 0 . 4 . 2  
 t y p i n g _ e x t e n s i o n s = = 4 . 1 5 . 0  
 t z d a t a = = 2 0 2 6 . 2  
 u v i c o r n = = 0 . 4 6 . 0  
 
```

## File: spec.md (1150 tokens)

```markdown
# Specification — Bauamt MCP Permit Agent

## 1. Problem

A German municipal building office clerk often needs to perform repetitive work inside a permit-management system:

- search for a building permit
- inspect the current permit status
- check missing documents
- extract KPI values for reports
- prepare form updates

In many legacy or domain-specific systems, this requires opening the application UI, navigating menus, filtering records, copying values, and preparing data entries manually.

## 2. Goal

Expose selected permit-management workflows through an MCP server so Claude can use them from German natural-language instructions.

The system should demonstrate that an existing Fachverfahren can become agent-accessible without first rebuilding the whole UI.

## 3. Primary user

Bauamt clerk / Sachbearbeiter/in.

## 4. Demo user stories

### US-001 — Search permits

As a clerk, I want to ask Claude for permits matching an address, applicant, status, or year so that I do not have to manually search the system UI.

Example:

Finde alle Bauanträge für Hauptstraße 12 aus dem Jahr 2024.

### US-002 — Inspect missing documents

As a clerk, I want to ask what documents are missing for a permit so that I can answer applicants faster.

Example:

Welche Unterlagen fehlen noch für BG-2024-0847?

### US-003 — Calculate KPIs

As an office lead, I want to ask for permit-processing KPIs so that I can prepare operational reports faster.

Example:

Wie viele Anträge im BAUAMT-LE-01 sind zwischen 2024-01-01 und 2026-12-31 mehr als 30 Tage überfällig?

### US-004 — Prepare draft data entry

As a clerk, I want Claude to prepare a form update, but not save it, so that I can review the proposed change before committing anything.

Example:

Bereite eine Dateneingabe vor, um BG-2024-0847 als genehmigungsbereit zu markieren. Nicht speichern.

## 5. Functional requirements

### FR-001 — Permit search

The system must expose a search_permits tool.

It must support:

- applicant_name
- address
- status_filter
- submitted_year

### FR-002 — Permit details

The system must expose a get_permit_details tool.

It must return:

- permit ID
- applicant name
- address
- permit type
- status
- submitted date
- deadline
- missing documents
- assigned clerk
- office ID
- estimated cost
- overdue information

### FR-003 — KPI summary

The system must expose a get_kpi_summary tool.

It must return:

- total permits
- pending permits
- permits overdue by more than 30 days
- cases with missing documents
- average nominal processing days

### FR-004 — Draft-only data entry

The system must expose a prepare_data_entry tool.

It must:

- accept a permit ID
- accept proposed field updates
- reject unknown fields
- return a structured draft
- not write to the database
- mark the result as requiring human confirmation

## 6. Non-functional requirements

### NFR-001 — Local demo

The project must run locally on Windows with Python.

### NFR-002 — No external service dependency

The core demo must not require Docker, Postgres, cloud services, or real client data.

### NFR-003 — Reproducible seed data

The project must generate deterministic fake permit data.

### NFR-004 — Testability

The core tool functions must be covered by pytest tests.

### NFR-005 — Safe tool boundary

Claude must not receive arbitrary SQL access.

## 7. Non-goals

This demo does not implement:

- real HHV-Bau integration
- real citizen data
- production authentication
- production authorization
- deployment infrastructure
- a web frontend
- actual database writes
- real approval workflow UI

## 8. Safety constraints

The MCP server exposes only narrow domain tools.

The system must not expose:

- arbitrary SQL execution
- shell command execution
- direct database mutation
- real personal data
- unrestricted file access

The prepare_data_entry tool must always return:

- database_updated: false
- requires_human_confirmation: true

## 9. Seed data

The demo database contains 50 fake building permits.

A known demo record must always exist:

- Permit ID: BG-2024-0847
- Applicant: Müller Bau GmbH
- Address: Hauptstraße 12, Leipzig
- Status: unterlagen_fehlen
- Missing documents:
  - Brandschutznachweis
  - Statiknachweis

## 10. Acceptance criteria

The demo is successful if:

1. pytest tests pass.
2. The MCP server starts without import errors.
3. Claude can call search_permits.
4. Claude can call get_permit_details.
5. Claude can call get_kpi_summary.
6. Claude can call prepare_data_entry.
7. prepare_data_entry does not mutate the database.
8. The GitHub README explains the project clearly.
9. The demo script gives a clean interview walkthrough.

## 11. Interview takeaway

This project demonstrates a practical modernization pattern:

Existing domain system
→ narrow safe MCP tool layer
→ AI assistant
→ faster operational workflow

The key engineering idea is not "chatbot over data." The key idea is safe tool exposure over a domain workflow.
```

## File: sql/schema.sql (306 tokens)

```
CREATE TABLE IF NOT EXISTS permits (
    id TEXT PRIMARY KEY,
    applicant_name TEXT NOT NULL,
    address TEXT NOT NULL,
    permit_type TEXT NOT NULL CHECK (
        permit_type IN (
            'Neubau',
            'Umbau',
            'Abriss',
            'Nutzungsänderung',
            'Dachausbau',
            'Anbau'
        )
    ),
    status TEXT NOT NULL CHECK (
        status IN (
            'eingereicht',
            'in_prüfung',
            'unterlagen_fehlen',
            'genehmigungsbereit',
            'genehmigt',
            'abgelehnt',
            'überfällig'
        )
    ),
    submitted_date TEXT NOT NULL,
    deadline TEXT NOT NULL,
    missing_documents TEXT NOT NULL DEFAULT '[]',
    assigned_clerk TEXT NOT NULL,
    office_id TEXT NOT NULL,
    estimated_cost_eur REAL,
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_permits_applicant_name
    ON permits (applicant_name);

CREATE INDEX IF NOT EXISTS idx_permits_address
    ON permits (address);

CREATE INDEX IF NOT EXISTS idx_permits_status
    ON permits (status);

CREATE INDEX IF NOT EXISTS idx_permits_submitted_date
    ON permits (submitted_date);

CREATE INDEX IF NOT EXISTS idx_permits_deadline
    ON permits (deadline);

CREATE INDEX IF NOT EXISTS idx_permits_office_id
    ON permits (office_id);
```

## File: src/__init__.py (0 tokens)

```python

```

## File: src/bauamt_mcp/__init__.py (0 tokens)

```python

```

## File: src/bauamt_mcp/db.py (170 tokens)

```python
from __future__ import annotations

import os
import sqlite3
from pathlib import Path


DEFAULT_DATABASE_PATH = "data/bauamt_permits.db"


def get_database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH))


def get_connection() -> sqlite3.Connection:
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    schema_path = Path("sql/schema.sql")

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with get_connection() as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()
```

## File: src/bauamt_mcp/seed.py (1255 tokens)

```python
from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta

from faker import Faker

from src.bauamt_mcp.db import get_connection, initialize_database


fake = Faker("de_DE")
Faker.seed(42)
random.seed(42)


PERMIT_TYPES = [
    "Neubau",
    "Umbau",
    "Abriss",
    "Nutzungsänderung",
    "Dachausbau",
    "Anbau",
]

STATUSES = [
    "eingereicht",
    "in_prüfung",
    "unterlagen_fehlen",
    "genehmigungsbereit",
    "genehmigt",
    "abgelehnt",
    "überfällig",
]

DOCUMENTS = [
    "Lageplan",
    "Bauantragsformular",
    "Baubeschreibung",
    "Brandschutznachweis",
    "Statiknachweis",
    "Entwässerungsplan",
    "Energieausweis",
    "Nachweis Stellplätze",
    "Eigentumsnachweis",
    "Schallschutznachweis",
]

CLERKS = [
    "Frau Schneider",
    "Herr Müller",
    "Frau Wagner",
    "Herr Becker",
    "Frau Hoffmann",
]

OFFICES = [
    "BAUAMT-LE-01",
    "BAUAMT-LE-02",
    "BAUAMT-LE-03",
]

STREETS = [
    "Hauptstraße",
    "Bahnhofstraße",
    "Leipziger Straße",
    "Schillerstraße",
    "Goethestraße",
    "Gartenstraße",
    "Dorfstraße",
    "Karl-Liebknecht-Straße",
    "August-Bebel-Straße",
    "Markt",
]


def random_address() -> str:
    street = random.choice(STREETS)
    house_number = random.randint(1, 120)
    city = random.choice(["Leipzig", "Markranstädt", "Borna", "Grimma", "Taucha"])
    return f"{street} {house_number}, {city}"


def random_missing_documents(status: str) -> list[str]:
    if status == "unterlagen_fehlen":
        return random.sample(DOCUMENTS, random.randint(1, 4))

    if status in {"eingereicht", "in_prüfung"} and random.random() < 0.3:
        return random.sample(DOCUMENTS, random.randint(1, 2))

    return []


def derive_status(submitted_date: date, deadline: date) -> str:
    today = date.today()

    if deadline < today - timedelta(days=30):
        return "überfällig"

    if deadline < today:
        return random.choice(["überfällig", "in_prüfung", "unterlagen_fehlen"])

    return random.choice(STATUSES[:-1])


def build_permit(index: int) -> tuple:
    year = random.choice([2024, 2025, 2026])
    submitted = date(year, random.randint(1, 12), random.randint(1, 28))
    deadline = submitted + timedelta(days=random.choice([45, 60, 90, 120]))

    status = derive_status(submitted, deadline)
    missing_docs = random_missing_documents(status)

    # Ensure a known demo record exists.
    if index == 1:
        permit_id = "BG-2024-0847"
        applicant_name = "Müller Bau GmbH"
        address = "Hauptstraße 12, Leipzig"
        permit_type = "Umbau"
        status = "unterlagen_fehlen"
        submitted = date(2024, 8, 12)
        deadline = date(2024, 11, 12)
        missing_docs = ["Brandschutznachweis", "Statiknachweis"]
        assigned_clerk = "Frau Schneider"
        office_id = "BAUAMT-LE-01"
        estimated_cost = 248000.00
    else:
        permit_id = f"BG-{year}-{index:04d}"
        applicant_name = random.choice(
            [
                fake.name(),
                f"{fake.last_name()} Bau GmbH",
                f"{fake.last_name()} Immobilien GmbH",
                f"{fake.last_name()} Projektentwicklung",
            ]
        )
        address = random_address()
        permit_type = random.choice(PERMIT_TYPES)
        assigned_clerk = random.choice(CLERKS)
        office_id = random.choice(OFFICES)
        estimated_cost = round(random.uniform(15000, 950000), 2)

    return (
        permit_id,
        applicant_name,
        address,
        permit_type,
        status,
        submitted.isoformat(),
        deadline.isoformat(),
        json.dumps(missing_docs, ensure_ascii=False),
        assigned_clerk,
        office_id,
        estimated_cost,
        datetime.now().isoformat(timespec="seconds"),
    )


def seed_database(count: int = 50) -> None:
    initialize_database()

    permits = [build_permit(index) for index in range(1, count + 1)]

    with get_connection() as conn:
        conn.execute("DELETE FROM permits")
        conn.executemany(
            """
            INSERT INTO permits (
                id,
                applicant_name,
                address,
                permit_type,
                status,
                submitted_date,
                deadline,
                missing_documents,
                assigned_clerk,
                office_id,
                estimated_cost_eur,
                last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            permits,
        )
        conn.commit()

    print(f"Seeded {len(permits)} fake Bauamt permits.")


if __name__ == "__main__":
    seed_database()
```

## File: src/bauamt_mcp/server.py (682 tokens)

```python
from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.bauamt_mcp.db import initialize_database
from src.bauamt_mcp.tools import (
    get_kpi_summary as domain_get_kpi_summary,
    get_permit_details as domain_get_permit_details,
    prepare_data_entry as domain_prepare_data_entry,
    search_permits as domain_search_permits,
)

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("bauamt-permit-agent")


@mcp.tool()
def search_permits(
    applicant_name: str | None = None,
    address: str | None = None,
    status_filter: str | None = None,
    submitted_year: int | None = None,
) -> list[dict[str, Any]]:
    """
    Search German municipal building permits by applicant, address, status, or submitted year.

    Example German clerk requests:
    - Finde alle offenen Bauanträge für Hauptstraße 12 aus dem Jahr 2024.
    - Suche alle Anträge von Müller Bau GmbH.
    - Zeige alle überfälligen Bauanträge.
    """
    return domain_search_permits(
        applicant_name=applicant_name,
        address=address,
        status_filter=status_filter,
        submitted_year=submitted_year,
    )


@mcp.tool()
def get_permit_details(permit_id: str) -> dict[str, Any]:
    """
    Get full details for one German building permit.

    Use this when the clerk asks about missing documents, permit status,
    assigned clerk, deadline, applicant, address, or estimated project cost.

    Example:
    - Welche Unterlagen fehlen noch für BG-2024-0847?
    """
    return domain_get_permit_details(permit_id)


@mcp.tool()
def get_kpi_summary(
    office_id: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """
    Calculate permit-processing KPIs for a Bauamt office in a date range.

    Dates must use ISO format: YYYY-MM-DD.

    Example:
    - Wie viele Anträge im BAUAMT-LE-01 sind zwischen 2024-01-01 und 2026-12-31 mehr als 30 Tage überfällig?
    """
    return domain_get_kpi_summary(
        office_id=office_id,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
def prepare_data_entry(
    permit_id: str,
    field_updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepare a draft data-entry update for a building permit.

    Safety rule:
    This tool never writes to the database. It only returns a structured draft
    that a human clerk must review and approve.

    Example:
    - Bereite eine Dateneingabe vor, um BG-2024-0847 als genehmigungsbereit zu markieren. Nicht speichern.
    """
    return domain_prepare_data_entry(
        permit_id=permit_id,
        field_updates=field_updates,
    )


def main() -> None:
    initialize_database()
    mcp.run()


if __name__ == "__main__":
    main()
```

## File: src/bauamt_mcp/smoke_demo.py (395 tokens)

```python
from __future__ import annotations

import json

from src.bauamt_mcp.seed import seed_database
from src.bauamt_mcp.tools import (
    get_kpi_summary,
    get_permit_details,
    prepare_data_entry,
    search_permits,
)


def print_section(title: str, payload: object) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    seed_database(count=50)

    print_section(
        "1. Search permits: Hauptstraße 12, submitted in 2024",
        search_permits(address="Hauptstraße 12", submitted_year=2024),
    )

    print_section(
        "2. Permit details: missing documents for BG-2024-0847",
        get_permit_details("BG-2024-0847"),
    )

    print_section(
        "3. KPI summary: BAUAMT-LE-01 from 2024-01-01 to 2026-12-31",
        get_kpi_summary(
            office_id="BAUAMT-LE-01",
            start_date="2024-01-01",
            end_date="2026-12-31",
        ),
    )

    print_section(
        "4. Draft-only data entry: mark BG-2024-0847 as ready for approval",
        prepare_data_entry(
            "BG-2024-0847",
            {
                "status": "genehmigungsbereit",
                "approval_date": "2026-04-26",
                "clerk_note": "Alle erforderlichen Unterlagen liegen vor.",
                "dangerous_sql": "DROP TABLE permits",
            },
        ),
    )


if __name__ == "__main__":
    main()
```

## File: src/bauamt_mcp/tools.py (1501 tokens)

```python
from __future__ import annotations

import json
from datetime import date
from typing import Any

from src.bauamt_mcp.db import get_connection


def _row_to_dict(row: Any) -> dict[str, Any]:
    data = dict(row)

    if "missing_documents" in data:
        try:
            data["missing_documents"] = json.loads(data["missing_documents"])
        except json.JSONDecodeError:
            data["missing_documents"] = []

    return data


def search_permits(
    applicant_name: str | None = None,
    address: str | None = None,
    status_filter: str | None = None,
    submitted_year: int | None = None,
) -> list[dict[str, Any]]:
    """
    Search German municipal building permits by applicant, address, status, and submitted year.
    Use this when a clerk asks to find permits matching a person, company, address, status, or year.
    """
    query = """
        SELECT
            id,
            applicant_name,
            address,
            permit_type,
            status,
            submitted_date,
            deadline,
            assigned_clerk,
            office_id
        FROM permits
        WHERE 1 = 1
    """
    params: list[Any] = []

    if applicant_name:
        query += " AND lower(applicant_name) LIKE lower(?)"
        params.append(f"%{applicant_name}%")

    if address:
        query += " AND lower(address) LIKE lower(?)"
        params.append(f"%{address}%")

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if submitted_year:
        query += " AND substr(submitted_date, 1, 4) = ?"
        params.append(str(submitted_year))

    query += " ORDER BY submitted_date DESC LIMIT 20"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_permit_details(permit_id: str) -> dict[str, Any]:
    """
    Get full details for one German building permit, including missing documents and deadline status.
    Use this when a clerk asks what is missing, who is assigned, or what the current status is.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                id,
                applicant_name,
                address,
                permit_type,
                status,
                submitted_date,
                deadline,
                missing_documents,
                assigned_clerk,
                office_id,
                estimated_cost_eur,
                last_updated
            FROM permits
            WHERE id = ?
            """,
            (permit_id,),
        ).fetchone()

    if row is None:
        return {
            "found": False,
            "permit_id": permit_id,
            "message": "No permit found with this ID.",
        }

    data = _row_to_dict(row)
    deadline = date.fromisoformat(data["deadline"])
    today = date.today()
    data["found"] = True
    data["days_until_deadline"] = (deadline - today).days
    data["is_overdue"] = deadline < today
    data["overdue_by_days"] = max((today - deadline).days, 0)

    return data


def get_kpi_summary(
    office_id: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """
    Calculate KPI summary for a Bauamt office in a date range.
    Use this for reporting questions like overdue permits, pending cases, missing documents, and average processing time.
    Dates must be ISO format: YYYY-MM-DD.
    """
    with get_connection() as conn:
        total = conn.execute(
            """
            SELECT COUNT(*)
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

        pending = conn.execute(
            """
            SELECT COUNT(*)
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
              AND status IN ('eingereicht', 'in_prüfung', 'unterlagen_fehlen', 'genehmigungsbereit', 'überfällig')
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

        overdue_more_than_30_days = conn.execute(
            """
            SELECT COUNT(*)
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
              AND julianday('now') - julianday(deadline) > 30
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

        missing_documents_cases = conn.execute(
            """
            SELECT COUNT(*)
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
              AND missing_documents != '[]'
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

        avg_processing_days = conn.execute(
            """
            SELECT AVG(julianday(deadline) - julianday(submitted_date))
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

    return {
        "office_id": office_id,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "total_permits": total,
        "pending_permits": pending,
        "overdue_more_than_30_days": overdue_more_than_30_days,
        "missing_documents_cases": missing_documents_cases,
        "average_nominal_processing_days": round(avg_processing_days or 0, 1),
    }


def prepare_data_entry(
    permit_id: str,
    field_updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepare a draft data-entry update for a building permit.
    This tool must not write to the database. It only returns a reviewable draft for a human clerk.
    """
    allowed_fields = {
        "status",
        "approval_date",
        "clerk_note",
        "assigned_clerk",
        "missing_documents",
    }

    rejected_fields = sorted(set(field_updates) - allowed_fields)
    accepted_updates = {
        key: value for key, value in field_updates.items() if key in allowed_fields
    }

    permit = get_permit_details(permit_id)

    if not permit.get("found"):
        return {
            "prepared": False,
            "permit_id": permit_id,
            "message": "Cannot prepare data entry because the permit was not found.",
            "database_updated": False,
        }

    return {
        "prepared": True,
        "permit_id": permit_id,
        "current_status": permit["status"],
        "draft_entry": accepted_updates,
        "rejected_fields": rejected_fields,
        "safety": {
            "database_updated": False,
            "requires_human_confirmation": True,
            "reason": "MCP tool is intentionally draft-only for write-like operations.",
        },
    }
```

## File: tests/test_tools.py (891 tokens)

```python
from __future__ import annotations

from pathlib import Path

import pytest

from src.bauamt_mcp.seed import seed_database
from src.bauamt_mcp.tools import (
    get_kpi_summary,
    get_permit_details,
    prepare_data_entry,
    search_permits,
)


@pytest.fixture()
def seeded_temp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "bauamt_permits_test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    seed_database(count=50)
    return db_path


def test_search_permits_finds_known_demo_record(seeded_temp_db: Path) -> None:
    results = search_permits(address="Hauptstraße 12", submitted_year=2024)

    assert len(results) >= 1
    assert results[0]["id"] == "BG-2024-0847"
    assert results[0]["applicant_name"] == "Müller Bau GmbH"
    assert results[0]["status"] == "unterlagen_fehlen"


def test_get_permit_details_returns_missing_documents(seeded_temp_db: Path) -> None:
    permit = get_permit_details("BG-2024-0847")

    assert permit["found"] is True
    assert permit["id"] == "BG-2024-0847"
    assert permit["permit_type"] == "Umbau"
    assert permit["missing_documents"] == [
        "Brandschutznachweis",
        "Statiknachweis",
    ]
    assert permit["assigned_clerk"] == "Frau Schneider"
    assert "days_until_deadline" in permit
    assert "is_overdue" in permit
    assert "overdue_by_days" in permit


def test_get_permit_details_handles_unknown_id(seeded_temp_db: Path) -> None:
    permit = get_permit_details("BG-DOES-NOT-EXIST")

    assert permit["found"] is False
    assert permit["permit_id"] == "BG-DOES-NOT-EXIST"


def test_get_kpi_summary_returns_expected_contract(seeded_temp_db: Path) -> None:
    summary = get_kpi_summary(
        office_id="BAUAMT-LE-01",
        start_date="2024-01-01",
        end_date="2026-12-31",
    )

    assert summary["office_id"] == "BAUAMT-LE-01"
    assert summary["date_range"]["start_date"] == "2024-01-01"
    assert summary["date_range"]["end_date"] == "2026-12-31"
    assert summary["total_permits"] >= 1
    assert "pending_permits" in summary
    assert "overdue_more_than_30_days" in summary
    assert "missing_documents_cases" in summary
    assert "average_nominal_processing_days" in summary


def test_prepare_data_entry_is_draft_only_and_rejects_unknown_fields(
    seeded_temp_db: Path,
) -> None:
    draft = prepare_data_entry(
        "BG-2024-0847",
        {
            "status": "genehmigungsbereit",
            "approval_date": "2026-04-26",
            "clerk_note": "Alle erforderlichen Unterlagen liegen vor.",
            "dangerous_sql": "DROP TABLE permits",
        },
    )

    assert draft["prepared"] is True
    assert draft["permit_id"] == "BG-2024-0847"
    assert draft["draft_entry"]["status"] == "genehmigungsbereit"
    assert draft["draft_entry"]["approval_date"] == "2026-04-26"
    assert draft["rejected_fields"] == ["dangerous_sql"]
    assert draft["safety"]["database_updated"] is False
    assert draft["safety"]["requires_human_confirmation"] is True


def test_prepare_data_entry_handles_unknown_permit(seeded_temp_db: Path) -> None:
    draft = prepare_data_entry(
        "BG-DOES-NOT-EXIST",
        {
            "status": "genehmigungsbereit",
        },
    )

    assert draft["prepared"] is False
    assert draft["database_updated"] is False
```
