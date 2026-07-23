#!/usr/bin/env python3
"""Local-first Excalidraw compiler, validator, inspector, and preview renderer."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from typing import Any


PALETTE = {
    "primary": ("#dbeafe", "#1e40af"),
    "success": ("#dcfce7", "#166534"),
    "warning": ("#fef9c3", "#854d0e"),
    "error": ("#fee2e2", "#991b1b"),
    "external": ("#f3e8ff", "#6b21a8"),
    "process": ("#e0f2fe", "#0369a1"),
    "trigger": ("#fed7aa", "#c2410c"),
    "neutral": ("#f1f5f9", "#475569"),
}
NODE_TYPES = {"rectangle", "ellipse", "diamond", "text"}
EDGE_STYLES = {"solid", "dashed", "dotted"}
EDGE_ROUTES = {"straight", "elbow"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")


class StudioError(RuntimeError):
    pass


def _stable_int(value: str, salt: str = "") -> int:
    digest = hashlib.sha256(f"{salt}:{value}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF or 1


def _git_root(workspace_path: str | os.PathLike[str]) -> Path:
    workspace = Path(workspace_path).expanduser().resolve()
    if not workspace.exists() or not workspace.is_dir():
        raise StudioError(f"Workspace does not exist or is not a directory: {workspace}")
    try:
        result = subprocess.run(
            ["git", "-C", str(workspace), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise StudioError("workspacePath must be inside a Git repository") from exc
    return Path(result.stdout.strip()).resolve()


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _repo_path(root: Path, value: str, *, must_exist: bool = False) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise StudioError("Path must be a non-empty string")
    supplied = Path(value.strip()).expanduser()
    target = supplied.resolve() if supplied.is_absolute() else (root / supplied).resolve()
    if not _inside(root, target):
        raise StudioError(f"Path must stay inside the Git repository: {value}")
    if must_exist and not target.is_file():
        raise StudioError(f"File does not exist: {target}")
    return target


def _common(element_id: str, element_type: str, x: float, y: float, width: float, height: float) -> dict[str, Any]:
    return {
        "id": element_id,
        "type": element_type,
        "x": round(float(x), 2),
        "y": round(float(y), 2),
        "width": round(float(width), 2),
        "height": round(float(height), 2),
        "angle": 0,
        "strokeColor": "#334155",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": _stable_int(element_id, "seed"),
        "version": 1,
        "versionNonce": _stable_int(element_id, "nonce"),
        "isDeleted": False,
        "boundElements": None,
        "updated": 1,
        "link": None,
        "locked": False,
    }


def _validate_id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise StudioError(f"{field} must match {ID_RE.pattern}")
    return value


def _number(value: Any, field: str, *, minimum: float | None = None) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise StudioError(f"{field} must be a finite number")
    result = float(value)
    if minimum is not None and result < minimum:
        raise StudioError(f"{field} must be at least {minimum}")
    return result


def _wrapped_label(text: str, width: float, font_size: float) -> str:
    max_chars = max(8, int((width - 24) / max(1, font_size * 0.56)))
    lines: list[str] = []
    for raw_line in str(text).splitlines() or [""]:
        lines.extend(
            textwrap.wrap(
                raw_line,
                width=max_chars,
                break_long_words=True,
                break_on_hyphens=True,
            )
            or [""]
        )
    return "\n".join(lines)


def _text_size(text: str, font_size: float) -> tuple[float, float]:
    lines = str(text).splitlines() or [""]
    width = max(1.0, max(len(line) for line in lines) * font_size * 0.57)
    height = max(1.0, len(lines) * font_size * 1.25)
    return round(width, 2), round(height, 2)


def _text_element(
    element_id: str,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    font_size: float = 20,
    container_id: str | None = None,
    align: str = "center",
    color: str = "#1e293b",
) -> dict[str, Any]:
    element = _common(element_id, "text", x, y, width, height)
    element.update(
        {
            "strokeColor": color,
            "strokeWidth": 1,
            "roughness": 0,
            "fontSize": font_size,
            "fontFamily": 1,
            "text": text,
            "rawText": text,
            "originalText": text,
            "textAlign": align,
            "verticalAlign": "middle",
            "containerId": container_id,
            "autoResize": True,
            "lineHeight": 1.25,
        }
    )
    return element


def _edge_point(source: dict[str, Any], target: dict[str, Any]) -> tuple[float, float]:
    sx = source["x"] + source["width"] / 2
    sy = source["y"] + source["height"] / 2
    tx = target["x"] + target["width"] / 2
    ty = target["y"] + target["height"] / 2
    dx, dy = tx - sx, ty - sy
    if abs(dx) * source["height"] >= abs(dy) * source["width"]:
        return (source["x"] + source["width"] if dx >= 0 else source["x"], sy)
    return (sx, source["y"] + source["height"] if dy >= 0 else source["y"])


def _polyline_midpoint(points: list[tuple[float, float]]) -> tuple[float, float]:
    lengths = [math.dist(left, right) for left, right in zip(points, points[1:])]
    total = sum(lengths)
    if total <= 0:
        return points[0]
    remaining = total / 2
    for (x1, y1), (x2, y2), length in zip(points, points[1:], lengths):
        if remaining <= length:
            ratio = remaining / length if length else 0
            return x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio
        remaining -= length
    return points[-1]


def compile_spec(spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise StudioError("spec must be an object")
    nodes = spec.get("nodes")
    edges = spec.get("edges", [])
    if not isinstance(nodes, list) or not nodes:
        raise StudioError("spec.nodes must be a non-empty array")
    if not isinstance(edges, list):
        raise StudioError("spec.edges must be an array")

    default_roughness = _number(spec.get("roughness", 1), "roughness", minimum=0)
    records: dict[str, dict[str, Any]] = {}
    node_elements: list[dict[str, Any]] = []
    label_elements: list[dict[str, Any]] = []
    all_ids: set[str] = set()

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise StudioError(f"nodes[{index}] must be an object")
        node_id = _validate_id(node.get("id"), f"nodes[{index}].id")
        if node_id in all_ids:
            raise StudioError(f"Duplicate element id: {node_id}")
        all_ids.add(node_id)
        node_type = str(node.get("type", "rectangle"))
        if node_type not in NODE_TYPES:
            raise StudioError(f"Unsupported node type: {node_type}")
        x = _number(node.get("x"), f"nodes[{index}].x")
        y = _number(node.get("y"), f"nodes[{index}].y")
        width = _number(node.get("width", 220), f"nodes[{index}].width", minimum=40)
        height = _number(node.get("height", 88), f"nodes[{index}].height", minimum=32)
        label = str(node.get("label", "")).strip()
        if not label:
            raise StudioError(f"nodes[{index}].label must be non-empty")
        font_size = _number(node.get("fontSize", 20), f"nodes[{index}].fontSize", minimum=10)
        semantic = str(node.get("semantic", "process"))
        if semantic not in PALETTE:
            raise StudioError(f"Unsupported semantic value: {semantic}")

        if node_type == "text":
            wrapped = _wrapped_label(label, width, font_size)
            text_width, text_height = _text_size(wrapped, font_size)
            text_element = _text_element(
                node_id,
                wrapped,
                x,
                y,
                max(width, text_width),
                max(height, text_height),
                font_size=font_size,
                align=str(node.get("align", "left")),
                color=str(node.get("color", "#334155")),
            )
            node_elements.append(text_element)
            records[node_id] = text_element
            continue

        fill, stroke = PALETTE[semantic]
        shape = _common(node_id, node_type, x, y, width, height)
        shape.update(
            {
                "strokeColor": str(node.get("strokeColor", stroke)),
                "backgroundColor": str(node.get("backgroundColor", fill)),
                "roughness": _number(node.get("roughness", default_roughness), f"nodes[{index}].roughness", minimum=0),
                "roundness": {"type": 3} if node_type == "rectangle" else ({"type": 2} if node_type == "diamond" else None),
                "boundElements": [],
            }
        )
        label_id = f"{node_id}-label"
        if label_id in all_ids:
            raise StudioError(f"Generated label id collides with another id: {label_id}")
        all_ids.add(label_id)
        wrapped = _wrapped_label(label, width, font_size)
        label_width, label_height = _text_size(wrapped, font_size)
        label_width = min(label_width, max(20, width - 24))
        label_height = min(label_height, max(16, height - 16))
        label_element = _text_element(
            label_id,
            wrapped,
            x + (width - label_width) / 2,
            y + (height - label_height) / 2,
            label_width,
            label_height,
            font_size=font_size,
            container_id=node_id,
        )
        shape["boundElements"].append({"type": "text", "id": label_id})
        node_elements.append(shape)
        label_elements.append(label_element)
        records[node_id] = shape

    arrow_elements: list[dict[str, Any]] = []
    arrow_labels: list[dict[str, Any]] = []
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise StudioError(f"edges[{index}] must be an object")
        edge_id = _validate_id(edge.get("id", f"edge-{index + 1}"), f"edges[{index}].id")
        if edge_id in all_ids:
            raise StudioError(f"Duplicate element id: {edge_id}")
        all_ids.add(edge_id)
        source_id = _validate_id(edge.get("from"), f"edges[{index}].from")
        target_id = _validate_id(edge.get("to"), f"edges[{index}].to")
        if source_id not in records or target_id not in records:
            raise StudioError(f"Edge {edge_id} references an unknown node")
        if records[source_id]["type"] == "text" or records[target_id]["type"] == "text":
            raise StudioError(f"Edge {edge_id} cannot bind to a free-standing text node")
        style = str(edge.get("style", "solid"))
        route = str(edge.get("route", "straight"))
        if style not in EDGE_STYLES:
            raise StudioError(f"Unsupported edge style: {style}")
        if route not in EDGE_ROUTES:
            raise StudioError(f"Unsupported edge route: {route}")
        source, target = records[source_id], records[target_id]
        start = _edge_point(source, target)
        end = _edge_point(target, source)
        absolute_points = [start, end]
        if route == "elbow":
            mid_x = (start[0] + end[0]) / 2
            absolute_points = [start, (mid_x, start[1]), (mid_x, end[1]), end]
        rel_points = [[round(px - start[0], 2), round(py - start[1], 2)] for px, py in absolute_points]
        arrow = _common(edge_id, "arrow", start[0], start[1], end[0] - start[0], end[1] - start[1])
        arrow.update(
            {
                "strokeColor": str(edge.get("color", "#334155")),
                "strokeStyle": style,
                "roughness": _number(edge.get("roughness", default_roughness), f"edges[{index}].roughness", minimum=0),
                "roundness": {"type": 2},
                "points": rel_points,
                "lastCommittedPoint": None,
                "startBinding": {"elementId": source_id, "focus": 0, "gap": 1},
                "endBinding": {"elementId": target_id, "focus": 0, "gap": 1},
                "startArrowhead": str(edge.get("startArrowhead")) if edge.get("startArrowhead") else None,
                "endArrowhead": str(edge.get("endArrowhead", "arrow")),
                "elbowed": route == "elbow",
            }
        )
        source["boundElements"].append({"type": "arrow", "id": edge_id})
        target["boundElements"].append({"type": "arrow", "id": edge_id})
        label = str(edge.get("label", "")).strip()
        if label:
            label_id = f"{edge_id}-label"
            if label_id in all_ids:
                raise StudioError(f"Generated edge label id collides: {label_id}")
            all_ids.add(label_id)
            font_size = _number(edge.get("fontSize", 16), f"edges[{index}].fontSize", minimum=10)
            label_width, label_height = _text_size(label, font_size)
            middle = _polyline_midpoint(absolute_points)
            arrow_label = _text_element(
                label_id,
                label,
                middle[0] - label_width / 2,
                middle[1] - label_height / 2 - 12,
                label_width,
                label_height,
                font_size=font_size,
                container_id=edge_id,
            )
            arrow["boundElements"] = [{"type": "text", "id": label_id}]
            arrow_labels.append(arrow_label)
        arrow_elements.append(arrow)

    title_elements: list[dict[str, Any]] = []
    title = str(spec.get("title", "")).strip()
    if title:
        min_x = min(float(item["x"]) for item in records.values())
        min_y = min(float(item["y"]) for item in records.values())
        title_width, title_height = _text_size(title, 28)
        title_elements.append(
            _text_element("diagram-title", title, min_x, min_y - 78, max(320, title_width), title_height, font_size=28, align="left")
        )

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "excalidraw-studio",
        "elements": title_elements + arrow_elements + node_elements + label_elements + arrow_labels,
        "appState": {"gridSize": None, "viewBackgroundColor": str(spec.get("backgroundColor", "#ffffff"))},
        "files": {},
    }


def _load_scene(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StudioError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise StudioError("Excalidraw scene must be a JSON object")
    return data


def _scene_validation(scene: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if scene.get("type") != "excalidraw":
        errors.append("root.type must be 'excalidraw'")
    if scene.get("version") != 2:
        warnings.append("root.version is expected to be 2")
    elements = scene.get("elements")
    if not isinstance(elements, list):
        errors.append("root.elements must be an array")
        elements = []
    ids: set[str] = set()
    for index, element in enumerate(elements):
        if not isinstance(element, dict):
            errors.append(f"elements[{index}] must be an object")
            continue
        element_id = element.get("id")
        if not isinstance(element_id, str) or not element_id:
            errors.append(f"elements[{index}].id must be a non-empty string")
        elif element_id in ids:
            errors.append(f"duplicate element id: {element_id}")
        else:
            ids.add(element_id)
        for key in ("x", "y", "width", "height"):
            value = element.get(key)
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                errors.append(f"element {element_id or index} has invalid {key}")
        if element.get("type") == "arrow":
            for binding_name in ("startBinding", "endBinding"):
                binding = element.get(binding_name)
                if not isinstance(binding, dict) or not binding.get("elementId"):
                    warnings.append(f"arrow {element_id or index} has no {binding_name}")
    for element in elements:
        if isinstance(element, dict) and element.get("type") == "arrow":
            for binding_name in ("startBinding", "endBinding"):
                binding = element.get(binding_name)
                if isinstance(binding, dict) and binding.get("elementId") not in ids:
                    errors.append(f"arrow {element.get('id')} references missing element {binding.get('elementId')}")
    return {"valid": not errors, "errors": errors, "warnings": warnings, "elementCount": len(elements)}


def create_diagram(
    workspace_path: str,
    output_path: str,
    spec: dict[str, Any],
    *,
    overwrite: bool = False,
    render_preview: bool = True,
) -> dict[str, Any]:
    root = _git_root(workspace_path)
    target = _repo_path(root, output_path)
    if target.suffix.lower() != ".excalidraw":
        raise StudioError("outputPath must end in .excalidraw")
    if target.exists() and not overwrite:
        raise StudioError(f"Refusing to overwrite existing diagram: {target.relative_to(root)}")
    scene = compile_spec(spec)
    validation = _scene_validation(scene)
    if not validation["valid"]:
        raise StudioError("Generated scene failed validation: " + "; ".join(validation["errors"]))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result: dict[str, Any] = {
        "status": "created",
        "repoRoot": str(root),
        "diagramPath": str(target),
        "repoRelativePath": target.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "validation": validation,
    }
    if render_preview:
        result["preview"] = render_diagram(workspace_path, output_path)
    return result


def validate_diagram(workspace_path: str, file_path: str) -> dict[str, Any]:
    root = _git_root(workspace_path)
    target = _repo_path(root, file_path, must_exist=True)
    scene = _load_scene(target)
    result = _scene_validation(scene)
    result.update(
        {
            "repoRoot": str(root),
            "diagramPath": str(target),
            "repoRelativePath": target.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }
    )
    return result


def _rect(element: dict[str, Any]) -> tuple[float, float, float, float]:
    x, y = float(element["x"]), float(element["y"])
    return x, y, x + float(element["width"]), y + float(element["height"])


def _overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def inspect_diagram(workspace_path: str, file_path: str) -> dict[str, Any]:
    root = _git_root(workspace_path)
    target = _repo_path(root, file_path, must_exist=True)
    scene = _load_scene(target)
    validation = _scene_validation(scene)
    elements = [e for e in scene.get("elements", []) if isinstance(e, dict) and not e.get("isDeleted", False)]
    shapes = [e for e in elements if e.get("type") in {"rectangle", "ellipse", "diamond"}]
    texts = [e for e in elements if e.get("type") == "text"]
    issues: list[dict[str, str]] = []

    for index, left in enumerate(shapes):
        for right in shapes[index + 1 :]:
            if _overlap(_rect(left), _rect(right)) > 1:
                issues.append({"severity": "error", "code": "node-overlap", "message": f"{left.get('id')} overlaps {right.get('id')}"})

    by_id = {e.get("id"): e for e in elements if e.get("id")}
    for text in texts:
        container_id = text.get("containerId")
        container = by_id.get(container_id)
        if container and container.get("type") in {"rectangle", "ellipse", "diamond"}:
            if float(text.get("width", 0)) > float(container.get("width", 0)) - 12 or float(text.get("height", 0)) > float(container.get("height", 0)) - 8:
                issues.append({"severity": "warning", "code": "label-fit", "message": f"Label {text.get('id')} is cramped inside {container_id}"})

    title_present = any(not text.get("containerId") and float(text.get("fontSize", 0)) >= 24 for text in texts)
    if not title_present:
        issues.append({"severity": "warning", "code": "missing-title", "message": "No free-standing title at 24 px or larger"})
    if shapes and len(shapes) >= max(6, len(texts) * 0.75):
        issues.append({"severity": "info", "code": "container-heavy", "message": "The scene may rely on too many containers; consider free-standing text and whitespace"})

    severity_order = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda item: severity_order[item["severity"]])
    return {
        "repoRoot": str(root),
        "diagramPath": str(target),
        "repoRelativePath": target.relative_to(root).as_posix(),
        "validation": validation,
        "summary": {
            "elements": len(elements),
            "shapes": len(shapes),
            "texts": len(texts),
            "arrows": sum(1 for e in elements if e.get("type") == "arrow"),
        },
        "issues": issues,
        "clean": validation["valid"] and not any(item["severity"] == "error" for item in issues),
    }


def _dash(style: str) -> str:
    return {"dashed": "10 8", "dotted": "3 7"}.get(style, "")


def _scene_bounds(elements: list[dict[str, Any]]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for element in elements:
        if element.get("type") in {"arrow", "line"} and isinstance(element.get("points"), list):
            for point in element["points"]:
                if isinstance(point, list) and len(point) >= 2:
                    xs.append(float(element.get("x", 0)) + float(point[0]))
                    ys.append(float(element.get("y", 0)) + float(point[1]))
        else:
            x, y, x2, y2 = _rect(element)
            xs.extend([x, x2])
            ys.extend([y, y2])
    return (min(xs or [0]), min(ys or [0]), max(xs or [800]), max(ys or [600]))


def _arrow_head(points: list[tuple[float, float]], color: str) -> str:
    if len(points) < 2:
        return ""
    x2, y2 = points[-1]
    x1, y1 = points[-2]
    angle = math.atan2(y2 - y1, x2 - x1)
    length, spread = 14, 0.55
    p1 = (x2 - length * math.cos(angle - spread), y2 - length * math.sin(angle - spread))
    p2 = (x2 - length * math.cos(angle + spread), y2 - length * math.sin(angle + spread))
    return f'<polygon points="{x2:.2f},{y2:.2f} {p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" fill="{html.escape(color)}" />'


def scene_to_svg(scene: dict[str, Any]) -> tuple[str, int, int]:
    elements = [e for e in scene.get("elements", []) if isinstance(e, dict) and not e.get("isDeleted", False)]
    min_x, min_y, max_x, max_y = _scene_bounds(elements)
    padding = 64
    view_x, view_y = min_x - padding, min_y - padding
    natural_width = max(320.0, max_x - min_x + 2 * padding)
    natural_height = max(240.0, max_y - min_y + 2 * padding)
    scale = min(1.0, 2200 / natural_width, 1500 / natural_height)
    width, height = max(320, round(natural_width * scale)), max(240, round(natural_height * scale))
    background = html.escape(str(scene.get("appState", {}).get("viewBackgroundColor", "#ffffff")))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{view_x:.2f} {view_y:.2f} {natural_width:.2f} {natural_height:.2f}">',
        f'<rect x="{view_x:.2f}" y="{view_y:.2f}" width="{natural_width:.2f}" height="{natural_height:.2f}" fill="{background}"/>',
    ]

    for element in elements:
        if element.get("type") not in {"arrow", "line"}:
            continue
        points = [
            (float(element.get("x", 0)) + float(point[0]), float(element.get("y", 0)) + float(point[1]))
            for point in element.get("points", [])
            if isinstance(point, list) and len(point) >= 2
        ]
        if len(points) < 2:
            continue
        color = str(element.get("strokeColor", "#334155"))
        point_text = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        dash = _dash(str(element.get("strokeStyle", "solid")))
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(f'<polyline points="{point_text}" fill="none" stroke="{html.escape(color)}" stroke-width="{float(element.get("strokeWidth", 2))}" stroke-linecap="round" stroke-linejoin="round"{dash_attr}/>' )
        if element.get("type") == "arrow" and element.get("endArrowhead"):
            parts.append(_arrow_head(points, color))

    for element in elements:
        kind = element.get("type")
        if kind not in {"rectangle", "ellipse", "diamond"}:
            continue
        x, y = float(element["x"]), float(element["y"])
        w, h = float(element["width"]), float(element["height"])
        stroke = html.escape(str(element.get("strokeColor", "#334155")))
        fill_value = str(element.get("backgroundColor", "transparent"))
        fill = "none" if fill_value == "transparent" else html.escape(fill_value)
        opacity = max(0, min(100, float(element.get("opacity", 100)))) / 100
        dash = _dash(str(element.get("strokeStyle", "solid")))
        common = f'fill="{fill}" stroke="{stroke}" stroke-width="{float(element.get("strokeWidth", 2))}" opacity="{opacity:.3f}"' + (f' stroke-dasharray="{dash}"' if dash else "")
        if kind == "rectangle":
            radius = min(20, w / 8, h / 8) if element.get("roundness") else 0
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius:.2f}" {common}/>' )
        elif kind == "ellipse":
            parts.append(f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2}" ry="{h / 2}" {common}/>' )
        else:
            points = f"{x + w / 2},{y} {x + w},{y + h / 2} {x + w / 2},{y + h} {x},{y + h / 2}"
            parts.append(f'<polygon points="{points}" {common}/>' )

    for element in elements:
        if element.get("type") != "text":
            continue
        text = str(element.get("text", ""))
        lines = text.splitlines() or [""]
        font_size = float(element.get("fontSize", 20))
        x, y = float(element["x"]), float(element["y"])
        w, h = float(element["width"]), float(element["height"])
        align = str(element.get("textAlign", "left"))
        anchor = "middle" if align == "center" else ("end" if align == "right" else "start")
        tx = x + w / 2 if align == "center" else (x + w if align == "right" else x)
        line_height = font_size * float(element.get("lineHeight", 1.25))
        start_y = y + h / 2 - ((len(lines) - 1) * line_height) / 2 + font_size * 0.35
        family = "Segoe Print, Comic Sans MS, cursive" if int(element.get("fontFamily", 1)) == 1 else "Segoe UI, sans-serif"
        parts.append(f'<text x="{tx:.2f}" y="{start_y:.2f}" text-anchor="{anchor}" font-family="{family}" font-size="{font_size}" fill="{html.escape(str(element.get("strokeColor", "#1e293b")))}">')
        for line_index, line in enumerate(lines):
            dy = 0 if line_index == 0 else line_height
            parts.append(f'<tspan x="{tx:.2f}" dy="{dy:.2f}">{html.escape(line)}</tspan>')
        parts.append("</text>")
    parts.append("</svg>")
    return "\n".join(parts), width, height


def _find_edge() -> Path | None:
    candidates = [
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate).resolve()
    return None


def render_diagram(
    workspace_path: str,
    file_path: str,
    svg_path: str | None = None,
    png_path: str | None = None,
) -> dict[str, Any]:
    root = _git_root(workspace_path)
    source = _repo_path(root, file_path, must_exist=True)
    scene = _load_scene(source)
    validation = _scene_validation(scene)
    if not validation["valid"]:
        raise StudioError("Cannot render invalid scene: " + "; ".join(validation["errors"]))
    default_svg = source.with_name(source.stem + ".preview.svg")
    default_png = source.with_name(source.stem + ".preview.png")
    svg_target = _repo_path(root, svg_path) if svg_path else default_svg
    png_target = _repo_path(root, png_path) if png_path else default_png
    if svg_target.suffix.lower() != ".svg" or png_target.suffix.lower() != ".png":
        raise StudioError("Preview paths must end in .svg and .png")
    svg, width, height = scene_to_svg(scene)
    svg_target.parent.mkdir(parents=True, exist_ok=True)
    svg_target.write_text(svg, encoding="utf-8")
    edge = _find_edge()
    png_created = False
    warning = None
    if edge:
        png_target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="excalidraw-studio-edge-") as profile:
            command = [
                str(edge),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-first-run",
                "--allow-file-access-from-files",
                f"--user-data-dir={profile}",
                f"--window-size={width},{height}",
                f"--screenshot={png_target}",
                svg_target.as_uri(),
            ]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=45)
            png_created = completed.returncode == 0 and png_target.is_file() and png_target.stat().st_size > 0
            if not png_created:
                warning = (completed.stderr or completed.stdout or "Edge did not create a PNG preview").strip()
    else:
        warning = "Microsoft Edge was not found; SVG preview was created but PNG was skipped"
    return {
        "status": "rendered",
        "repoRoot": str(root),
        "sourcePath": str(source),
        "svgPath": str(svg_target),
        "svgRepoRelativePath": svg_target.relative_to(root).as_posix(),
        "pngPath": str(png_target) if png_created else None,
        "pngRepoRelativePath": png_target.relative_to(root).as_posix() if png_created else None,
        "width": width,
        "height": height,
        "warning": warning,
        "renderer": "local-svg+system-edge" if png_created else "local-svg",
    }


def doctor(workspace_path: str) -> dict[str, Any]:
    root = _git_root(workspace_path)
    edge = _find_edge()
    return {
        "status": "ok" if edge and os.access(root, os.W_OK) else "degraded",
        "repoRoot": str(root),
        "repoWritable": os.access(root, os.W_OK),
        "python": sys.version.split()[0],
        "edgePath": str(edge) if edge else None,
        "pngRenderingAvailable": bool(edge),
        "networkRequired": False,
        "apiKeyRequired": False,
        "paidTierRequired": False,
        "storage": "git-repository-local-files",
    }


def _print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor_parser = sub.add_parser("doctor")
    doctor_parser.add_argument("--workspace", required=True)
    create_parser = sub.add_parser("create")
    create_parser.add_argument("--workspace", required=True)
    create_parser.add_argument("--output", required=True)
    create_parser.add_argument("--spec", required=True)
    create_parser.add_argument("--overwrite", action="store_true")
    create_parser.add_argument("--no-preview", action="store_true")
    for name in ("validate", "inspect", "render"):
        command_parser = sub.add_parser(name)
        command_parser.add_argument("--workspace", required=True)
        command_parser.add_argument("--file", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            result = doctor(args.workspace)
        elif args.command == "create":
            spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
            result = create_diagram(args.workspace, args.output, spec, overwrite=args.overwrite, render_preview=not args.no_preview)
        elif args.command == "validate":
            result = validate_diagram(args.workspace, args.file)
        elif args.command == "inspect":
            result = inspect_diagram(args.workspace, args.file)
        else:
            result = render_diagram(args.workspace, args.file)
        _print_json(result)
        return 0
    except (StudioError, OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        _print_json({"status": "error", "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
