from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.persistence.database import build_engine, build_session_factory
from src.infrastructure.persistence.models import Base
from src.infrastructure.persistence.policy_catalog_repository import SqlAlchemyPolicyCatalogRepository
from src.infrastructure.policy_catalog.meta_community_standards import META_COMMUNITY_STANDARDS


def main() -> None:
    engine = build_engine()
    Base.metadata.create_all(engine)
    session_factory = build_session_factory()
    with session_factory() as session:
        try:
            changed = SqlAlchemyPolicyCatalogRepository().upsert_many(
                session, provider="META_COMMUNITY_STANDARDS", entries=META_COMMUNITY_STANDARDS
            )
            session.commit()
        except Exception:
            session.rollback()
            raise
    print(f"Meta policy catalog seeded: changed={changed} total={len(META_COMMUNITY_STANDARDS)}")


if __name__ == "__main__":
    main()
