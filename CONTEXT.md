# Project Context for AI Agents

**Project**: PoE Loot Filter Creator
**Stack**: Python, Flask, Pytest, Bootstrap 5, CodeMirror 5, Vanilla JS.
**Architecture**: Factory-pattern Flask app with Blueprints.

## Core Purpose
To generate custom Path of Exile loot filter override blocks based on a Path of Building (PoB) export code, and prepend them to the latest NeverSink base filter.

## Directory Structure
- `app/`
  - `__init__.py`: Flask app factory and logging setup.
  - `routes.py`: Flask blueprint containing the API endpoints and view rendering.
  - `pob_decoder.py`: Decodes the Base64/zlib PoB string and parses the XML to extract items and socket links.
  - `filter_generator.py`: Formats extracted data into PoE filter syntax (`Show` blocks) and fetches the NeverSink base filter from GitHub API.
  - `linter.py`: Custom syntax validator to ensure CodeMirror text uses valid PoE commands (`Show`, `Hide`, `BaseType`, etc.).
  - `templates/index.html`: The single-page frontend.
- `tests/`: Pytest suite (TDD heavily utilized).
- `run.py`: Application entry point.

## Important Technical Details & Constraints

1. **Test-Driven Development (TDD)**:
   - Always update or write tests in the `tests/` directory *before* or *alongside* modifying core logic in `pob_decoder.py`, `filter_generator.py`, or `linter.py`.
   - Run tests with `export PYTHONPATH=. && pytest`.

2. **PoB Decoding**:
   - PoB codes are URL-safe base64 strings compressing an XML payload via `zlib`.
   - The XML `<Items>` node contains raw text blocks for each item. Parsing relies on splitting these strings by newlines and doing lightweight prefix checks (e.g., `Rarity: RARE`, `Sockets: B-B-B-B`).

3. **Filter Syntax Injection**:
   - PoE filters read top-to-bottom. First match wins.
   - We *never* overwrite or fully replace the base economy filter. We always generate specific override blocks and append them at the very top of the NeverSink filter text.

4. **Frontend Architecture**:
   - No frontend frameworks (React/Vue/etc). Pure Vanilla JS with `fetch` API.
   - CodeMirror 5 is used for the code editor, utilizing the `material-darker` theme for a PoE-appropriate dark aesthetic.
   - Flow: `Generate (POST /api/generate_rules)` -> `Review in CodeMirror` -> `Validate (POST /api/validate)` -> `Download (POST /api/download)`.

## Future Expansion
- OAuth integration with the official Path of Exile API to allow direct cloud syncing of filters instead of local downloads.
- Deeper PoB XML parsing (e.g., extracting exact desired stats like "+Max Life" and linking them to base types).
