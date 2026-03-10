# Easy eCoC Community Edition

## Project Overview
Python desktop GUI application that automates vehicle data submission to the Norwegian Statens Vegvesen eCoC (Electronic Certificate of Conformity) service.

## Tech Stack
- **Language**: Python 3.11+
- **GUI**: ttkbootstrap (tkinter)
- **Database**: SQLite (`vegvesen_data.db`)
- **Auth**: OAuth2 via JWT (Samarbeidsportalen)
- **Libraries**: requests, pyperclip, cryptography, python-jose, jwt

## Key Files
- `ecoc-gui.py` — Main entry point & GUI (3 tabs: Vegvesen eCoC, Settings, JWT Keygen)
- `samarbeidsportalen.py` — OAuth2 JWT token generation for Vegvesen API auth
- `pubkeygen.py` — RSA key pair / JWK generation utility
- `pyproject.toml` — Project config & dependencies (managed by uv)
- `xml_templates/Example.xml` — IVI XML template

## How to Run
```bash
uv sync
uv run python ecoc-gui.py
```

## Architecture
- **GUI**: Multi-tab interface (eCoC workflow, Settings, JWT Keygen)
- **Auth**: JWT-based OAuth2 tokens via Samarbeidsportalen
- **Data**: SQLite with two tables: `responses` (API responses) and `samarbeidsportalen` (auth config)
- **API**: Vegvesen vehicle pre-registration endpoint (test + production environments)

## Security Files (not in repo)
- `virksomhet.cer` — Company certificate (full chain, no BEGIN/END lines)
- `private_key.pem` — Company private key
- These are in `.gitignore` and must be provided by the user

## Conventions
- Single-file GUI application pattern
- SQLite for local persistence
- XML-based vehicle data format (IVI)
