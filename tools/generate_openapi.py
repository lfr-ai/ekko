#!/usr/bin/env python3
"""
OpenAPI specification generator for Ekko.

This script generates OpenAPI 3.1.0 specification files from the FastAPI app
in multiple formats: JSON, YAML, and HTML documentation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Final

import yaml
from fastapi.openapi.utils import get_openapi

# Ensure backend/src is importable when this script is run from repository root.
BACKEND_SRC: Final[Path] = Path(__file__).parent.parent / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

# Constants
OUTPUT_DIR: Final[Path] = Path(__file__).parent.parent / "docs" / "api"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OPENAPI_JSON: Final[Path] = OUTPUT_DIR / "openapi.json"
OPENAPI_YAML: Final[Path] = OUTPUT_DIR / "openapi.yaml"
OPENAPI_HTML: Final[Path] = OUTPUT_DIR / "index.html"


def generate_openapi_spec() -> dict:
    """
    Generate OpenAPI specification from FastAPI app.

    Returns:
        OpenAPI specification dictionary.
    """
    from ekko.composition.app_factory import create_app
    from ekko.config.openapi_config import (
        OPENAPI_CONTACT,
        OPENAPI_DESCRIPTION,
        OPENAPI_EXTERNAL_DOCS,
        OPENAPI_LICENSE,
        OPENAPI_SERVERS,
        OPENAPI_TAGS,
        OPENAPI_TITLE,
        OPENAPI_VERSION,
    )

    # Create FastAPI app from composition root
    app = create_app()

    # Generate OpenAPI schema
    openapi_schema = get_openapi(
        title=OPENAPI_TITLE,
        version=OPENAPI_VERSION,
        description=OPENAPI_DESCRIPTION,
        routes=app.routes,
        servers=OPENAPI_SERVERS,
        tags=OPENAPI_TAGS,
        contact=OPENAPI_CONTACT,
        license_info=OPENAPI_LICENSE,
    )

    # Add external docs
    openapi_schema["externalDocs"] = OPENAPI_EXTERNAL_DOCS

    return openapi_schema


def write_json_spec(spec: dict) -> None:
    """
    Write OpenAPI spec to JSON file.

    Args:
        spec: OpenAPI specification dictionary.
    """
    with OPENAPI_JSON.open("w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"✓ Generated OpenAPI JSON: {OPENAPI_JSON}")


def write_yaml_spec(spec: dict) -> None:
    """
    Write OpenAPI spec to YAML file.

    Args:
        spec: OpenAPI specification dictionary.
    """
    with OPENAPI_YAML.open("w", encoding="utf-8") as f:
        yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"✓ Generated OpenAPI YAML: {OPENAPI_YAML}")


def write_html_docs(spec: dict) -> None:
    """
    Write standalone HTML documentation using Swagger UI.

    Args:
        spec: OpenAPI specification dictionary.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{spec["info"]["title"]} - API Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                spec: {json.dumps(spec)},
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                docExpansion: "list",
                filter: true,
                showExtensions: true,
                showCommonExtensions: true
            }});
            window.ui = ui;
        }};
    </script>
</body>
</html>"""

    with OPENAPI_HTML.open("w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Generated HTML docs: {OPENAPI_HTML}")


def main() -> None:
    """Generate OpenAPI specification in multiple formats."""
    print("Generating OpenAPI specification...")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print()

    try:
        # Generate spec
        spec = generate_openapi_spec()

        # Write in multiple formats
        write_json_spec(spec)
        write_yaml_spec(spec)
        write_html_docs(spec)

        print()
        print("✅ OpenAPI specification generated successfully!")
        print()
        print("View documentation:")
        print(f"  - JSON: {OPENAPI_JSON.absolute()}")
        print(f"  - YAML: {OPENAPI_YAML.absolute()}")
        print(f"  - HTML: {OPENAPI_HTML.absolute()}")
        print()
        print("To view HTML docs, open index.html in your browser:")
        print(f"  file://{OPENAPI_HTML.absolute()}")

    except Exception as e:
        print(f"❌ Error generating OpenAPI spec: {e}")
        raise


if __name__ == "__main__":
    main()
