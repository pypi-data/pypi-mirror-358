"""
Expects the structure of the New Eden's universe changes seldom enough to
negate the regeneration of the spatial data on every request.

Can be used by a dev to regenerate the spatial files and update the static
cache prior ot publishing a new release.
"""

import json
import os
from collections import defaultdict

import geojson
from shapely import MultiPoint
from shapely.geometry import mapping

from eveuniverse.models import EveConstellation, EveRegion, EveSolarSystem, EveStargate

from evemap import app_settings as settings


class Geospatial:

    @staticmethod
    def layer(name: str):
        match name:
            case "regions":
                return Geospatial.regions()
            case "region_stargates_lines":
                return Geospatial.region_stargates_lines()
            case "stargates_lines":
                return Geospatial.stargates_lines()
            case "solar_systems":
                return Geospatial.solar_systems()

    @staticmethod
    def solar_systems():
        features = []
        for system in EveSolarSystem.objects.all():
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [system.position_x, system.position_z],
                    },
                    "properties": {
                        "id": system.id,
                        "name": system.name,
                        "security_status": system.security_status,
                        "constellation_id": system.eve_constellation.id,
                        "constellation_name": system.eve_constellation.name,
                        "region_id": system.eve_constellation.eve_region.id,
                        "region_name": system.eve_constellation.eve_region.name,
                    },
                }
            )

        geojson = {"type": "FeatureCollection", "features": features}
        return geojson

    @staticmethod
    def constellations_polygons():
        constellations = {}
        for system in EveSolarSystem.objects.all():
            constellations.setdefault(system.eve_constellation.id, []).append(system)

        features = []
        for constellation_id, systems in constellations.items():
            points = [[system.position_x, system.position_z] for system in systems]
            if len(points) < 3:
                continue
            multipoint = MultiPoint(points)
            hull = multipoint.convex_hull
            centroid = hull.centroid
            constellation_name = EveConstellation.objects.get(id=constellation_id).name
            features.append(
                {
                    "type": "Feature",
                    "geometry": mapping(hull),
                    "properties": {
                        "constellation_id": constellation_id,
                        "constellation_name": constellation_name,
                        "centroid": list(centroid.coords)[0],
                    },
                }
            )

        geojson = {"type": "FeatureCollection", "features": features}
        return geojson

    @staticmethod
    def stargates_lines():

        stargates = {}
        connections = []
        for gate in EveStargate.objects.all():
            stargates[gate.id] = {
                "name": f"{gate.eve_solar_system.name} > {gate.destination_eve_solar_system.name}",
                "coords": [
                    gate.eve_solar_system.position_x,
                    gate.eve_solar_system.position_z,
                ],
            }

            # Sometimes gate.destination_eve_stargate_id is null
            # When this happens, pick the first gate found for gate.destination_eve_solar_system
            desto_gate = gate.destination_eve_stargate_id
            if desto_gate is None:
                desto_gate = (
                    EveStargate.objects.filter(
                        eve_solar_system=gate.destination_eve_solar_system
                    )
                    .first()
                    .id
                )
            connections.append((gate.id, desto_gate))

        features = []
        for conn in connections:
            id1, id2 = conn
            if id2 is None:  # Some stargates go nowhere?
                continue
            sg1 = stargates[id1]
            sg2 = stargates[id2]
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [sg1["coords"], sg2["coords"]],
                },
                "properties": {"from": sg1["name"], "to": sg2["name"]},
            }
            features.append(feature)

        geojson = {"type": "FeatureCollection", "features": features}
        return geojson

    @staticmethod
    def regions():

        regions = {}
        stargates = {}
        systems = {}
        connections = []

        stargates_qs = EveStargate.objects.all()
        for gate in stargates_qs:
            stargates[gate.id] = {
                "name": f"{gate.eve_solar_system.name} > {gate.destination_eve_solar_system.name}",
                "system_id": gate.eve_solar_system.id,
                "region_name": f"{gate.eve_solar_system.eve_constellation.eve_region.name}",
                "coords": [
                    gate.eve_solar_system.position_x,
                    gate.eve_solar_system.position_z,
                ],
            }
            systems[gate.eve_solar_system.id] = {
                "id": gate.eve_solar_system.id,
                "name": f"{gate.eve_solar_system.name}",
                "security_status": f"{gate.eve_solar_system.security_status}",
                "constellation": f"{gate.eve_solar_system.eve_constellation.name}",
                "region_name": f"{gate.eve_solar_system.eve_constellation.eve_region.name}",
                "coords": [
                    gate.eve_solar_system.position_x,
                    gate.eve_solar_system.position_z,
                ],
            }

            # Sometimes gate.destination_eve_stargate_id is null
            # When this happens, pick the first gate found for gate.destination_eve_solar_system
            desto_gate = gate.destination_eve_stargate_id
            if desto_gate is None:
                desto_gate = (
                    EveStargate.objects.filter(
                        eve_solar_system=gate.destination_eve_solar_system
                    )
                    .first()
                    .id
                )
            connections.append((gate.id, desto_gate))

        features = []

        # Group systems by region
        regions = defaultdict(list)
        for system in systems.values():
            region_name = system["region_name"]
            regions[region_name].append(system)

        features = []

        # Loop over each region and create a feature
        for region_name, region_systems in regions.items():
            points = [system["coords"] for system in region_systems]
            if len(points) < 3:
                # Convex hull will fail otherwise
                continue
            multipoint = MultiPoint(points)
            hull = multipoint.convex_hull
            centroid = hull.centroid
            features.append(
                {
                    "type": "Feature",
                    "geometry": mapping(hull),
                    "properties": {
                        "region_name": region_name,
                        "centroid": list(centroid.coords)[0],
                    },
                }
            )

        for system in systems.values():
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": system["coords"],
                },
                "properties": {
                    "name": system["name"],
                    "region_name": system["region_name"],
                    "id": system["id"],
                    "security_status": system["security_status"],
                    "constellation": system["constellation"],
                },
            }
            features.append(feature)

        for conn in connections:
            id1, id2 = conn
            if id1 not in stargates:
                print(f"{conn}")
            if id2 not in stargates:
                continue
            sg1 = stargates[id1]
            sg2 = stargates[id2]
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [sg1["coords"], sg2["coords"]],
                },
                "properties": {
                    "region_name": sg1["region_name"],
                    "target_region_name": sg2["region_name"],
                    "source": sg1["system_id"],
                    "target": sg2["system_id"],
                },
            }
            features.append(feature)

        geojson = {"type": "FeatureCollection", "features": features}
        return geojson

    @staticmethod
    def region(region_name):
        geojson_path = os.path.join(settings.BASE_DIR, "data", "regions.geojson")

        # Load the GeoJSON data
        with open(geojson_path, "r") as f:
            data = json.load(f)

        filtered = []
        for feature in data["features"]:
            props = feature.get("properties", {})
            if props.get("region_name") == region_name:
                if (
                    props.get("target_region_name") is None
                    or props.get("target_region_name") == region_name
                ):
                    filtered.append(feature)

        return {"type": "FeatureCollection", "features": filtered}

    @staticmethod
    def region_plan_details(name):
        systems = EveSolarSystem.objects.filter(
            eve_constellation__eve_region__name=name
        )
        return [
            {
                "id": system.id,
                "name": system.name,
                "security_status": round(system.security_status, 1),
            }
            for system in systems
        ]

    @staticmethod
    def region_stargates_lines():

        regions = {}
        stargates = {}
        connections = []
        features = []

        for system in EveSolarSystem.objects.all():
            regions.setdefault(system.eve_constellation.eve_region.id, []).append(
                system
            )

        region_centroids = {}
        for region_id, systems in regions.items():
            points = [[system.position_x, system.position_z] for system in systems]

            security_statuses = [system.security_status for system in systems]
            avg_security = (
                sum(security_statuses) / len(security_statuses)
                if security_statuses
                else 0
            )
            max_security = max(security_statuses) if security_statuses else 0

            if len(points) < 3:
                continue
            multipoint = MultiPoint(points)
            hull = multipoint.convex_hull
            centroid = hull.centroid
            region_name = EveRegion.objects.get(id=region_id).name
            region_centroids[region_id] = {
                "region_id": region_id,
                "region_name": region_name,
                "avg_security": avg_security,
                "max_security": max_security,
                "centroid": list(centroid.coords)[0],
            }
            # add a point for region
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": list(centroid.coords)[0],
                },
                "properties": {
                    "id": region_id,
                    "name": region_name,
                    "avg_security": round(avg_security, 1),
                    "max_security": round(max_security, 1),
                },
            }
            features.append(feature)

        for gate in EveStargate.objects.all():

            # TODO make these work
            if (
                gate.eve_solar_system.eve_constellation.eve_region.name == "Pochven"
                or gate.destination_eve_solar_system.eve_constellation.eve_region.name
                == "Pochven"
                or gate.eve_solar_system.eve_constellation.eve_region.name
                == "Yasna Zakh"
                or gate.destination_eve_solar_system.eve_constellation.eve_region.name
                == "Yasna Zakh"
            ):
                continue

            # want coords of region
            region_id = gate.eve_solar_system.eve_constellation.eve_region.id
            region_name = gate.eve_solar_system.eve_constellation.eve_region.name
            region_coords = region_centroids[region_id]["centroid"]
            stargates[gate.id] = {
                "name": f"{gate.eve_solar_system.eve_constellation.eve_region.name}",
                "coords": region_coords,
            }

            # Sometimes gate.destination_eve_stargate_id is null
            # When this happens, pick the first gate found for gate.destination_eve_solar_system
            desto_gate_id = gate.destination_eve_stargate_id
            if desto_gate_id is None:
                desto_gate_id = (
                    EveStargate.objects.filter(
                        eve_solar_system=gate.destination_eve_solar_system
                    )
                    .first()
                    .id
                )

            connections.append((gate.id, desto_gate_id))

        just_add_one_line = []
        for conn in connections:
            id1, id2 = conn
            if id2 is None:  # Some stargates go nowhere?
                continue

            sg1 = stargates[id1]
            sg2 = stargates[id2]
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [sg1["coords"], sg2["coords"]],
                },
                "properties": {"from": sg1["name"], "to": sg2["name"]},
            }

            # Only want a single line
            if ((sg1["coords"], sg2["coords"])) not in just_add_one_line:
                just_add_one_line.append((sg1["coords"], sg2["coords"]))
                just_add_one_line.append((sg2["coords"], sg1["coords"]))
                features.append(feature)

        return geojson.FeatureCollection(features)
