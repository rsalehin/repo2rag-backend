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