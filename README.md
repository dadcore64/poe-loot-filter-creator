# PoE Loot Filter Creator

A lightweight web application that bridges the gap between Path of Building (PoB) and Path of Exile (PoE) loot filters. It extracts your build's specific item bases and socket requirements from a PoB export code, generates custom highlight rules, and injects them seamlessly at the top of the latest NeverSink economy filter.

## Features

- **PoB Ingestion**: Decodes Base64/zlib PoB export strings and parses the underlying XML.
- **Smart Extraction**: Identifies required gear bases (e.g., "Amethyst Ring") and socket links (e.g., "B-B-R-B") from your build.
- **Live Editor**: Review and edit the generated rules in the browser using a PoE-themed CodeMirror editor.
- **Syntax Validation**: Built-in linter prevents you from accidentally breaking your filter with typos.
- **Always Up-to-Date**: Automatically fetches the latest `1_Regular.filter` release directly from NeverSink's GitHub repository.

## Local Setup

This application is built with Python and Flask.

### Prerequisites
- Python 3.8+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dadcore64/poe-loot-filter-creator.git
   cd poe-loot-filter-creator
   ```

2. Create and activate a virtual environment:
   
   **On macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   **On Windows:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   **On macOS/Linux:**
   ```bash
   # Development mode
   python run.py
   
   # Or using Gunicorn (Production/WSGI)
   gunicorn -b 127.0.0.1:5000 run:app
   ```
   
   **On Windows:**
   ```powershell
   # Use the built-in Flask development server (Gunicorn is not supported on Windows)
   python run.py
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000`.

## Usage

1. Go to Path of Building, click **Import/Export Build**, and click **Generate** to get your build code.
2. Paste the code into the web interface and click **Extract & Generate Rules**.
3. Review the custom `Show` blocks generated in the editor. You can tweak border colors, sounds, or bases as needed.
4. Click **Validate Syntax**. If everything is correct, the download button will activate.
5. Click **Download .filter** and save it to your `Documents/My Games/Path of Exile` folder!
