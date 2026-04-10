"""Playground script to test the TCL client against the live API."""

import asyncio
import os

import aiohttp

from transports_commun_lyon import PassageType, TCLClient


async def main() -> None:
    username = os.environ.get("TCL_USERNAME")
    password = os.environ.get("TCL_PASSWORD")

    async with aiohttp.ClientSession() as session:
        client = TCLClient(session, username=username, password=password)

        ligne = "37"
        arret = 290
        ptype = PassageType.THEORETICAL

        print(f"=== Passages {ptype} - Ligne {ligne}, arrêt {arret} ===")
        passages = await client.get_passages(ligne, arret, ptype)
        for p in passages:
            print(f"  {p.ligne} → {p.direction} | {p.delai_passage} ({p.heure_passage:%H:%M})")

        print()
        print(f"=== Tous les passages - arrêt {arret} ===")
        all_passages = await client.get_stop_passages(arret)
        for p in all_passages:
            print(f"  {p.ligne} → {p.direction} | {p.delai_passage} ({p.heure_passage:%H:%M}) [{p.type}]")

        print()
        ptype = PassageType.ESTIMATED
        print(f"=== Passages {ptype} - Ligne {ligne}, arrêt {arret} ===")
        passages = await client.get_passages(ligne, arret, ptype)
        for p in passages:
            print(f"  {p.ligne} → {p.direction} | {p.delai_passage} ({p.heure_passage:%H:%M})")

        print()
        station_id = 10044
        print(f"=== Vélo'v station {station_id} ===")
        station = await client.get_velov_station(station_id)
        if station:
            print(f"  {station.name} ({station.commune})")
            print(f"  Status: {station.status} | Availability: {station.availability}")
            print(f"  Bikes: {station.available_bikes}/{station.bike_stands}")
            ts = station.total_stands
            print(f"  Detail: {ts.mechanical_bikes} mechanical, {ts.electrical_bikes} electrical")
            print(f"  Free stands: {station.available_bike_stands}")
        else:
            print(f"  Station {station_id} not found")


if __name__ == "__main__":
    asyncio.run(main())
