"""Playground script to test the client against the live API."""

import asyncio
import os

import aiohttp

from data_grand_lyon_ha import (
    DataGrandLyonClient,
    filter_tcl_passages_by_line,
    filter_tcl_passages_by_stop,
    find_tcl_park_and_ride_by_id,
    find_velov_station_by_id,
    sort_tcl_passages_by_time,
)
from data_grand_lyon_ha.tcl import find_tcl_stop_by_id


async def main() -> None:
    username = os.environ.get("TCL_USERNAME")
    password = os.environ.get("TCL_PASSWORD")

    async with aiohttp.ClientSession() as session:
        client = DataGrandLyonClient(session, username=username, password=password)

        all_passages = await client.get_tcl_passages()

        ligne = "37"
        arret = 290

        all_stops = await client.get_tcl_stops()
        print("=== Stops - Total:", len(all_stops))
        stop = find_tcl_stop_by_id(all_stops, arret)
        print("Found stop: ", stop)

        print(f"=== Passages - Ligne {ligne}, arrêt {arret} ===")
        passages = filter_tcl_passages_by_line(all_passages, ligne)
        passages = filter_tcl_passages_by_stop(passages, arret)
        passages = sort_tcl_passages_by_time(passages)
        for p in passages:
            print(f"  {p.ligne} → {p.direction} | {p.delai_passage} ({p.heure_passage:%H:%M})")

        print()
        station_id = 10044
        print(f"=== Vélo'v station {station_id} ===")
        all_stations = await client.get_velov_stations()
        station = find_velov_station_by_id(all_stations, station_id)
        if station:
            print(f"  {station.name} ({station.commune})")
            print(f"  Status: {station.status} | Availability: {station.availability}")
            print(f"  Bikes: {station.available_bikes}/{station.bike_stands}")
            ts = station.total_stands
            print(f"  Detail: {ts.mechanical_bikes} mechanical, {ts.electrical_bikes} electrical")
            print(f"  Free stands: {station.available_bike_stands}")
        else:
            print(f"  Station {station_id} not found")

        print()
        park_id = "VAI2"
        print(f"=== Park-and-ride {park_id} ===")
        all_parks = await client.get_tcl_park_and_rides()
        print("Total P+R:", len(all_parks))
        park = find_tcl_park_and_ride_by_id(all_parks, park_id)
        if park:
            print(f"  {park.nom}")
            print(f"  Places dispo: {park.nb_tot_place_dispo}/{park.capacite}")
            print(f"  Places handi: {park.place_handi} | Surveillé: {park.p_surv}")
            print(f"  Horaires: {park.horaires}")
        else:
            print(f"  Park-and-ride {park_id} not found")


if __name__ == "__main__":
    asyncio.run(main())
