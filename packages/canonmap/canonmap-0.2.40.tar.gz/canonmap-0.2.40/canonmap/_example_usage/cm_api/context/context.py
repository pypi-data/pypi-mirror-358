from contextlib import asynccontextmanager

from fastapi import FastAPI

from cm_api.context.context_helpers.get_canonmap_helper import get_canonmap
from cm_api.utils.api_logger import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.canonmap = get_canonmap()
    yield

app = FastAPI(lifespan=lifespan)