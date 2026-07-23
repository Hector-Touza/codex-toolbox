#!/usr/bin/env python3
"""Dependency-free stdio MCP server for Excalidraw Studio."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Callable


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from excalidraw_studio import (  # noqa: E402
    StudioError,
    create_diagram,
    doctor,
    inspect_diagram,
    render_diagram,
    validate_diagram,
)


SERVER_NAME = "Excalidraw Studio"
SERVER_VERSION = "0.1.0"


def send(message: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def result(message_id: Any, payload: dict[str, Any], *, is_error: bool = False) -> None:
    summary = payload.get("error") or payload.get("status") or "ok"
    send(
        {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "content": [{"type": "text", "text": f"{summary}\n{json.dumps(payload, ensure_ascii=False, indent=2)}"}],
                "structuredContent": payload,
                "isError": is_error,
            },
        }
    )


def error(message_id: Any, code: int, message: str) -> None:
    send({"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}})


WORKSPACE_PROPERTY = {
    "type": "string",
    "description": "Absolute path inside the active Git repository. The repository root is resolved with git.",
}
FILE_PROPERTY = {
    "type": "string",
    "description": "Repository-relative path to an existing .excalidraw file.",
}


TOOLS = [
    {
        "name": "excalidraw_doctor",
        "title": "Check Local Excalidraw Workflow",
        "description": "Verify that the workspace is a writable Git repository and that local PNG rendering is available. No network, account, API key, or paid tier is used.",
        "inputSchema": {
            "type": "object",
            "properties": {"workspacePath": WORKSPACE_PROPERTY},
            "required": ["workspacePath"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "create_excalidraw_diagram",
        "title": "Create Repo-local Excalidraw Diagram",
        "description": "Compile a compact diagram spec into an editable .excalidraw file inside the Git repository and optionally render local SVG/PNG previews.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspacePath": WORKSPACE_PROPERTY,
                "outputPath": {
                    "type": "string",
                    "description": "Repository-relative .excalidraw destination, normally docs/diagrams/<slug>.excalidraw.",
                },
                "spec": {
                    "type": "object",
                    "description": "Compact scene specification with title, nodes, and edges.",
                    "properties": {
                        "title": {"type": "string"},
                        "roughness": {"type": "number", "minimum": 0, "maximum": 2},
                        "backgroundColor": {"type": "string"},
                        "nodes": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "type": {"type": "string", "enum": ["rectangle", "ellipse", "diamond", "text"]},
                                    "x": {"type": "number"},
                                    "y": {"type": "number"},
                                    "width": {"type": "number", "minimum": 40},
                                    "height": {"type": "number", "minimum": 32},
                                    "label": {"type": "string"},
                                    "semantic": {"type": "string", "enum": ["primary", "success", "warning", "error", "external", "process", "trigger", "neutral"]},
                                    "fontSize": {"type": "number", "minimum": 10},
                                    "roughness": {"type": "number", "minimum": 0, "maximum": 2},
                                },
                                "required": ["id", "x", "y", "label"],
                                "additionalProperties": True,
                            },
                        },
                        "edges": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "from": {"type": "string"},
                                    "to": {"type": "string"},
                                    "label": {"type": "string"},
                                    "style": {"type": "string", "enum": ["solid", "dashed", "dotted"]},
                                    "route": {"type": "string", "enum": ["straight", "elbow"]},
                                },
                                "required": ["from", "to"],
                                "additionalProperties": True,
                            },
                        },
                    },
                    "required": ["nodes"],
                    "additionalProperties": True,
                },
                "overwrite": {"type": "boolean", "default": False},
                "renderPreview": {"type": "boolean", "default": True},
            },
            "required": ["workspacePath", "outputPath", "spec"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
    },
    {
        "name": "validate_excalidraw_diagram",
        "title": "Validate Excalidraw Diagram",
        "description": "Validate JSON structure, element IDs, numeric geometry, and arrow bindings for a repo-local .excalidraw file.",
        "inputSchema": {
            "type": "object",
            "properties": {"workspacePath": WORKSPACE_PROPERTY, "filePath": FILE_PROPERTY},
            "required": ["workspacePath", "filePath"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "inspect_excalidraw_diagram",
        "title": "Inspect Excalidraw Layout",
        "description": "Inspect a repo-local scene for overlapping nodes, cramped labels, missing hierarchy, and container-heavy composition.",
        "inputSchema": {
            "type": "object",
            "properties": {"workspacePath": WORKSPACE_PROPERTY, "filePath": FILE_PROPERTY},
            "required": ["workspacePath", "filePath"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
    {
        "name": "render_excalidraw_preview",
        "title": "Render Local Excalidraw Preview",
        "description": "Render an SVG preview and, when Microsoft Edge is available, a PNG preview next to the repo-local .excalidraw source without uploading anything.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspacePath": WORKSPACE_PROPERTY,
                "filePath": FILE_PROPERTY,
                "svgPath": {"type": "string", "description": "Optional repository-relative .svg output path."},
                "pngPath": {"type": "string", "description": "Optional repository-relative .png output path."},
            },
            "required": ["workspacePath", "filePath"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    },
]


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    handlers: dict[str, Callable[[], dict[str, Any]]] = {
        "excalidraw_doctor": lambda: doctor(args["workspacePath"]),
        "create_excalidraw_diagram": lambda: create_diagram(
            args["workspacePath"],
            args["outputPath"],
            args["spec"],
            overwrite=bool(args.get("overwrite", False)),
            render_preview=bool(args.get("renderPreview", True)),
        ),
        "validate_excalidraw_diagram": lambda: validate_diagram(args["workspacePath"], args["filePath"]),
        "inspect_excalidraw_diagram": lambda: inspect_diagram(args["workspacePath"], args["filePath"]),
        "render_excalidraw_preview": lambda: render_diagram(
            args["workspacePath"], args["filePath"], args.get("svgPath"), args.get("pngPath")
        ),
    }
    if name not in handlers:
        raise StudioError(f"Unknown tool: {name}")
    return handlers[name]()


def handle(message: dict[str, Any]) -> None:
    message_id = message.get("id")
    method = message.get("method")
    if method == "initialize":
        params = message.get("params") or {}
        send(
            {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "protocolVersion": params.get("protocolVersion", "2025-11-25"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    "instructions": "Keep .excalidraw sources and previews inside the active Git repository. Use local render/inspection tools, never upload scenes or create share links unless explicitly requested.",
                },
            }
        )
    elif method == "ping":
        send({"jsonrpc": "2.0", "id": message_id, "result": {}})
    elif method == "tools/list":
        send({"jsonrpc": "2.0", "id": message_id, "result": {"tools": TOOLS}})
    elif method == "tools/call":
        params = message.get("params") or {}
        try:
            payload = call_tool(str(params.get("name", "")), params.get("arguments") or {})
            result(message_id, payload)
        except (KeyError, StudioError, OSError, ValueError) as exc:
            result(message_id, {"status": "error", "error": str(exc)}, is_error=True)
    elif message_id is not None:
        error(message_id, -32601, f"Method not found: {method}")


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(message, dict):
            handle(message)


if __name__ == "__main__":
    main()
