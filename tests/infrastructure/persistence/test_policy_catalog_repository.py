import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.persistence.models import Base, PolicyCatalogEntryModel
from src.infrastructure.persistence.policy_catalog_repository import SqlAlchemyPolicyCatalogRepository
from src.infrastructure.policy_catalog.meta_community_standards import META_COMMUNITY_STANDARDS


class TestSqlAlchemyPolicyCatalogRepository(unittest.TestCase):
    def test_seeds_all_meta_policy_entries_idempotently(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        repository = SqlAlchemyPolicyCatalogRepository()

        first_change_count = repository.upsert_many(session, "META_COMMUNITY_STANDARDS", META_COMMUNITY_STANDARDS)
        session.commit()
        second_change_count = repository.upsert_many(session, "META_COMMUNITY_STANDARDS", META_COMMUNITY_STANDARDS)
        session.commit()

        self.assertEqual(first_change_count, 27)
        self.assertEqual(second_change_count, 0)
        self.assertEqual(session.query(PolicyCatalogEntryModel).count(), 27)
        session.close()
