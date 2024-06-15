from fastapi import APIRouter
from settings.settings import settings

routes = APIRouter()


def add_benefits_route(route_prefix: str):
    from .benefits.benefits import router as benefits_router

    routes.include_router(benefits_router, prefix=route_prefix)


add_benefits_route(settings.API_ROUTE_PREFIX)