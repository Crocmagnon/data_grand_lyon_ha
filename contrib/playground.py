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
        ptype = PassageType.ESTIMATED
        print(f"=== Passages {ptype} - Ligne {ligne}, arrêt {arret} ===")
        passages = await client.get_passages(ligne, arret, ptype)
        for p in passages:
            print(f"  {p.ligne} → {p.direction} | {p.delai_passage} ({p.heure_passage:%H:%M})")


if __name__ == "__main__":
    asyncio.run(main())
