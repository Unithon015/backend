from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.application.incident_index.service import SyncNamuWikiIncidentIndexService
from src.infrastructure.persistence.database import build_engine, build_session_factory
from src.infrastructure.persistence.models import Base


async def main(years: list[int]) -> None:
    engine = build_engine()
    Base.metadata.create_all(engine)
    service = SyncNamuWikiIncidentIndexService(build_session_factory())
    summaries = await service.sync_years(years)
    for summary in summaries:
        print(
            f"{summary.incident_year}: discovered={summary.discovered_count} "
            f"inserted={summary.inserted_count} updated={summary.updated_count}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync yearly Namu Wiki incident indexes.")
    parser.add_argument("--years", nargs="+", type=int, required=True, choices=(2024, 2025, 2026))
    arguments = parser.parse_args()
    asyncio.run(main(arguments.years))
