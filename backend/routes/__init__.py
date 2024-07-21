from fastapi import APIRouter
from settings.settings import settings

routes = APIRouter()


def add_benefits_route(route_prefix: str):
    # SINASUITE
    from .benefits.benefits import router as benefits_router
    from .benefits.benefits_types import router as benefits_types_router
    from .benefits.benefits_subtypes import router as benefits_subtypes_router
    from .centers.centers import router as centers_router
    from .forms.foin_configurations.foin_configurations import router as foin_configurations_router
    from .services_specialities.services_specialities import router as services_specialities_router
    from .activities.sina_bc.sina_bc import router as sina_bc_router
    from backend.routes.chat.chat import router as chat_router

    routes.include_router(benefits_router, prefix=route_prefix)
    routes.include_router(benefits_types_router, prefix=route_prefix)
    routes.include_router(benefits_subtypes_router, prefix=route_prefix)
    routes.include_router(centers_router, prefix=route_prefix)
    routes.include_router(foin_configurations_router, prefix=route_prefix)
    routes.include_router(services_specialities_router, prefix=route_prefix)
    routes.include_router(sina_bc_router, prefix=route_prefix)
    routes.include_router(chat_router, prefix=route_prefix)

    # SINA_INTERFACE_ERP
    from .erp_interface.prestacion.prestacion import router as erp_prestacion_router
    from .erp_interface.prestacion_servicio.prestacion_servicio import router as erp_prestacionservicio_router
    from .erp_interface.origen_prestacion.origen_prestacion import router as erp_origenprestacion_router

    routes.include_router(erp_prestacion_router, prefix=route_prefix)
    routes.include_router(erp_prestacionservicio_router, prefix=route_prefix)
    routes.include_router(erp_origenprestacion_router, prefix=route_prefix)

    # DATABASE
    from .database.pool.pool import router as pool_router

    routes.include_router(pool_router, prefix=route_prefix)


add_benefits_route(settings.API_ROUTE_PREFIX)
