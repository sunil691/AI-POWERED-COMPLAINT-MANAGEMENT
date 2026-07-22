"""Central API router composition."""

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.complaint import router as complaint_router
from app.api.health import router as health_router
from app.api.upload import router as upload_router

api_routers = (health_router, complaint_router, chat_router, upload_router)


def register_api_routers(application: FastAPI) -> None:
	"""Register concrete routers on the application composition root."""
	for router in api_routers:
		application.include_router(router)