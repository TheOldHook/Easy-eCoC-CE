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
- `ecoc-gui.py` — Main entry point & GUI (4 tabs: Vegvesen eCoC, Settings, JWT Keygen, Certificate Import)
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
- **GUI**: Multi-tab interface (eCoC workflow, Settings, JWT Keygen, Certificate Import)
- **Auth**: JWT-based OAuth2 tokens via Samarbeidsportalen
- **Data**: SQLite with two tables: `responses` (API responses) and `samarbeidsportalen` (auth config, keyed by environment)
- **API**: Vegvesen vehicle pre-registration endpoint (test + production environments, switchable at runtime via Settings tab)
- **Environments**: Test and Production URLs are managed in `ecoc_service.py` via `_ENVIRONMENTS` dict; settings (issuer, audience, scope, resource) are stored per environment in the DB

## Security Files (not in repo)
- `virksomhet.cer` — Company certificate (full chain, no BEGIN/END lines)
- `private_key.pem` — Company private key
- `public_key.pem` — Company public key
- These are in `.gitignore` and can be imported from a .p12 certificate via the Certificate Import tab

## Conventions
- Single-file GUI application pattern
- SQLite for local persistence
- XML-based vehicle data format (IVI)
