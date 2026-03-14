import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import router
import automations.scheduler as scheduler
from automations.weather import WeatherAutomation

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.register(WeatherAutomation())
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="Flipside", lifespan=lifespan)

# Static web files
web_dir = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# API routes
app.include_router(router)


@app.get("/")
def index():
    return FileResponse(str(web_dir / "index.html"))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
