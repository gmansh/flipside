import asyncio
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

import vesta.client as client
from vesta.formatter import make_board
from vesta.character_codes import CODE_TO_CHAR, COLOR_RGB
from image.pixelmap import pixelmap_bytes
import automations.scheduler as scheduler

router = APIRouter(prefix="/api")

TEMPLATES_DIR = Path("templates")
TEMPLATES_DIR.mkdir(exist_ok=True)


# --- Models ---

class RawMessage(BaseModel):
    message: list[list[int]]


class TextMessage(BaseModel):
    text: str
    valign: str = "center"


class AnimatedMessage(BaseModel):
    message: list[list[int]]
    strategy: str = "column"
    step_interval_ms: int = 100
    step_size: int = 1


class TemplateBody(BaseModel):
    name: str
    message: list[list[int]]


# --- Preview ---

def _board_to_html(board: list[list[int]]) -> str:
    """Render a board as a standalone HTML snippet for preview."""
    cells = []
    for row in board:
        for code in row:
            if code == 0:
                cells.append('<div class="sim-cell"></div>')
            elif code in COLOR_RGB:
                r, g, b = COLOR_RGB[code]
                cells.append(
                    f'<div class="sim-cell" style="background:rgb({r},{g},{b})"></div>'
                )
            else:
                ch = CODE_TO_CHAR.get(code, "")
                cells.append(
                    f'<div class="sim-cell ch">{ch}</div>'
                )
    return '<div class="sim-board">' + "".join(cells) + "</div>"


@router.get("/preview")
def get_preview():
    """Return an HTML preview of the current board state."""
    board = client.read()
    if board is None:
        raise HTTPException(status_code=502, detail="Could not read board state")
    return {"html": _board_to_html(board), "message": board}


@router.post("/preview")
def post_preview(body: RawMessage):
    """Return an HTML preview for an arbitrary board without sending it."""
    return {"html": _board_to_html(body.message)}


# --- Message routes ---

@router.get("/message")
def get_message():
    board = client.read()
    if board is None:
        raise HTTPException(status_code=502, detail="Could not read board state")
    return {"message": board}


@router.post("/message")
def post_message(body: RawMessage):
    ok = client.send(body.message)
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to send to board")
    return {"ok": True}


@router.post("/message/text")
def post_text(body: TextMessage):
    lines = body.text.split("\n")
    board = make_board(lines, valign=body.valign)
    ok = client.send(board)
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to send to board")
    return {"ok": True, "board": board}


@router.post("/message/image")
async def post_image(file: UploadFile = File(...)):
    data = await file.read()
    board = pixelmap_bytes(data)
    ok = client.send(board)
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to send to board")
    return {"ok": True, "board": board}


@router.post("/message/animated")
def post_animated(body: AnimatedMessage):
    ok = client.send_animated(
        body.message,
        strategy=body.strategy,
        step_interval_ms=body.step_interval_ms,
        step_size=body.step_size,
    )
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to send to board")
    return {"ok": True}


# --- Automations routes ---

@router.get("/automations")
def list_automations():
    return {"automations": scheduler.get_jobs()}


@router.post("/automations/{name}/trigger")
async def trigger_automation(name: str):
    automations = scheduler.get_automations()
    if name not in automations:
        raise HTTPException(status_code=404, detail=f"Automation '{name}' not found")
    automation = automations[name]
    board = await automation.run()
    ok = client.send(board)
    if not ok:
        raise HTTPException(status_code=502, detail="Failed to send to board")
    return {"ok": True, "board": board}


# --- Templates routes ---

@router.get("/templates")
def list_templates():
    templates = []
    for f in TEMPLATES_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            templates.append({"name": f.stem, "message": data["message"]})
        except Exception:
            pass
    return {"templates": templates}


@router.post("/templates")
def save_template(body: TemplateBody):
    path = TEMPLATES_DIR / f"{body.name}.json"
    path.write_text(json.dumps({"message": body.message}))
    return {"ok": True}


@router.delete("/templates/{name}")
def delete_template(name: str):
    path = TEMPLATES_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{name}' not found")
    path.unlink()
    return {"ok": True}
