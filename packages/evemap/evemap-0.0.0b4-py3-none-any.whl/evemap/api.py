from typing import List

from ninja import NinjaAPI
from ninja.security import django_auth

from django.conf import settings
from eveuniverse.models import EveAsteroidBelt, EvePlanet, EveSolarSystem

from evemap.utils.geospatial import Geospatial
from evemap.utils.graph import Graph

api = NinjaAPI(
    title="Evemap API",
    urls_namespace="evemap:api",
    auth=django_auth,
    csrf=True,
    openapi_url=settings.DEBUG and "/openapi.json" or "",
)


@api.get("geospatial/layer/{layer}", response={200: dict}, tags=["Geospatial"])
def geospatial(request, layer: str):

    if not request.user.has_perm("evemap.basic_access"):
        return api.create_response(request, {"detail": "Forbidden"}, status=403)

    return 200, Geospatial.layer(layer)


@api.get("geospatial/region/{name}", response={200: dict}, tags=["Geospatial"])
def region(request, name: str):

    if not request.user.has_perm("evemap.basic_access"):
        return api.create_response(request, {"detail": "Forbidden"}, status=403)

    return 200, Geospatial.region(name)


@api.get("geospatial/region-plan/{region}", response={200: dict}, tags=["Geospatial"])
def regionPlan(request, region: str):

    if not request.user.has_perm("evemap.basic_access"):
        return api.create_response(request, {"detail": "Forbidden"}, status=403)

    geojson_data = Geospatial.region(region)
    return 200, Graph().plot(geojson_data=geojson_data)


# TODO - move and separate to various calls, there is a lot of info for a given system
@api.get("universe/system/{name}", response={200: dict}, tags=["Universe"])
def system(request, name: str):

    if not request.user.has_perm("evemap.basic_access"):
        return api.create_response(request, {"detail": "Forbidden"}, status=403)

    solar_system = EveSolarSystem.objects.get(name=name)

    obj, _ = EveSolarSystem.objects.get_or_create_esi(
        id=solar_system.id,
        include_children=True,
        enabled_sections=[
            EveSolarSystem.Section.PLANETS,
        ],
    )

    ct_asteroid_belts = 0
    planets = EvePlanet.objects.filter(eve_solar_system_id=solar_system.id).all()
    for planet in planets:
        obj, _ = EvePlanet.objects.get_or_create_esi(
            id=planet.id,
            include_children=True,
            enabled_sections=[
                EvePlanet.Section.ASTEROID_BELTS,
            ],
        )
        planet_belts = EveAsteroidBelt.objects.filter(eve_planet_id=planet.id).count()
        ct_asteroid_belts = ct_asteroid_belts + planet_belts

    ct_planets = EvePlanet.objects.filter(eve_solar_system_id=solar_system.id).count()

    solar_system_json = {
        "id": solar_system.id,
        "name": solar_system.name,
        "security_status": solar_system.security_status,
        "planets": ct_planets,
        "asteroid_belts": ct_asteroid_belts,
    }
    return 200, solar_system_json


# TODO - move and separate
@api.get("universe/region-plan-details/{name}", response={200: List}, tags=["Universe"])
def region_plan_details(request, name: str):

    if not request.user.has_perm("evemap.basic_access"):
        return api.create_response(request, {"detail": "Forbidden"}, status=403)

    systems = EveSolarSystem.objects.filter(eve_constellation__eve_region__name=name)
    data = [
        {
            "id": system.id,
            "name": system.name,
            "security_status": round(system.security_status, 1),
        }
        for system in systems
    ]
    return 200, data
