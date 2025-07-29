import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.context.context_helpers.get_canonmap_helper import get_canonmap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.canonmap = get_canonmap()
    yield

app = FastAPI(lifespan=lifespan)