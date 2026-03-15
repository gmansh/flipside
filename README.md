# flipside

Local Vestaboard management system. Controls a Vestaboard display over the local network with support for automations, image pixelmapping, and a web-based board editor.

## Requirements

- Python 3.10+
- A Vestaboard with local API enabled (Settings → Local API on the Vestaboard app)

## Setup

```bash
# Clone and enter the repo
git clone https://github.com/gmansh/flipside.git
cd flipside

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Vestaboard's IP and API key
```

**.env** variables:

| Variable | Description | Default |
|---|---|---|
| `VESTABOARD_LOCAL_IP` | Local IP of your Vestaboard | `192.168.1.42` |
| `VESTABOARD_LOCAL_API_KEY` | API key from the Vestaboard app | *(required)* |
| `VESTABOARD_PORT` | Local API port | `7000` |
| `BOARD_ROWS` | Number of rows on the board | `6` |
| `BOARD_COLS` | Number of columns on the board | `22` |
| `WEATHER_LAT` | Latitude for weather automation | `37.7749` |
| `WEATHER_LON` | Longitude for weather automation | `-122.4194` |
| `WEATHER_SCHEDULE` | Cron schedule for weather updates | `0 7 * * *` (7am daily) |

## Running

```bash
# Quick start
./start.sh

# Or with options
./start.sh --port 9000 --host 127.0.0.1

# Or directly
python main.py
```

Server starts at `http://localhost:8000`.

## Board Simulator

Preview how boards will look without sending to the physical device:

```bash
# Read and display the current board in the terminal
python simulate.py live

# Preview all weather icons
python simulate.py weather

# Render a saved board JSON file
python simulate.py board.json

# Pipe board JSON from stdin
echo '[[0,1,...], ...]' | python simulate.py -
```

The simulator is also importable:

```python
from simulate import render_board
render_board(board, label="My Board")
```

The web UI also has a **Board Preview** panel in the sidebar for previewing
the current board state or the editor contents without sending to the device.

## Tests

```bash
# Unit tests (fast, no browser needed)
pytest tests/ -v -m "not e2e"

# E2E browser tests (requires Playwright)
pytest tests/e2e/ -v

# Install Playwright browsers (first time only)
pip install pytest-playwright
playwright install chromium
```

Both suites run automatically on every pull request via GitHub Actions. PRs must pass before merging.

## Manual Testing

**Board editor:** Open `http://localhost:8000` in a browser — interactive 6×22 grid, text mode, image import, and template management.

**Send text:**
```bash
curl -X POST localhost:8000/api/message/text \
  -H "Content-Type: application/json" \
  -d '{"text": "HELLO WORLD"}'
```

**Read current board:**
```bash
curl localhost:8000/api/message
```

**Trigger weather automation:**
```bash
curl -X POST localhost:8000/api/automations/weather/trigger
```

**List automations:**
```bash
curl localhost:8000/api/automations
```

**Send raw char code array** (6×22 grid of [character codes](vesta/character_codes.py)):
```bash
curl -X POST localhost:8000/api/message \
  -H "Content-Type: application/json" \
  -d '{"characters": [[0,0,...], ...]}'
```

**Upload image:**
```bash
curl -X POST localhost:8000/api/message/image \
  -F "file=@/path/to/image.png"
```

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/message` | Read current board |
| `POST` | `/api/message` | Send raw 6×22 char code array |
| `POST` | `/api/message/text` | Send `{text, valign}` — auto-formats and centers |
| `POST` | `/api/message/image` | Upload image → pixelmap → send |
| `POST` | `/api/message/animated` | Send with animation strategy |
| `GET` | `/api/preview` | HTML preview of the current board |
| `POST` | `/api/preview` | HTML preview for an arbitrary board (no send) |
| `GET` | `/api/automations` | List automations + next run time |
| `POST` | `/api/automations/{name}/trigger` | Manually trigger an automation |
| `GET` | `/api/templates` | List saved templates |
| `POST` | `/api/templates` | Save named template |
| `DELETE` | `/api/templates/{name}` | Delete a template |

## Architecture

Single process: `main.py` starts both the FastAPI web server and the APScheduler daemon.

```
flipside/
├── main.py              # entry point: FastAPI app + scheduler startup
├── start.sh             # convenience script to start the server
├── simulate.py          # terminal board simulator
├── config.py            # env config via python-dotenv
├── vesta/
│   ├── client.py        # Vestaboard local API wrapper (httpx)
│   ├── character_codes.py  # char code constants + text encoder
│   └── formatter.py     # centering, layout, template rendering
├── automations/
│   ├── scheduler.py     # APScheduler wrapper + job registry
│   ├── base.py          # BaseAutomation abstract class
│   └── weather.py       # daily weather via Open-Meteo (no API key needed)
├── image/
│   └── pixelmap.py      # image → 6×22 char code array via Pillow
├── api/
│   └── routes.py        # FastAPI route definitions
└── web/                 # board editor SPA (vanilla HTML/JS)
```

## Adding Automations

Subclass `BaseAutomation` in `automations/`:

```python
from automations.base import BaseAutomation
from vesta.formatter import make_board

class MyAutomation(BaseAutomation):
    name = "my_automation"
    schedule = "0 9 * * *"  # cron expression

    async def run(self) -> list[list[int]]:
        return make_board(["LINE ONE", "LINE TWO"])
```

Then register it in `main.py`:

```python
from automations.my_automation import MyAutomation
scheduler.register(MyAutomation())
```
