import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.incident_index.entity import IncidentIndexEntry
from src.infrastructure.persistence.incident_index_repository import SqlAlchemyIncidentIndexRepository
from src.infrastructure.persistence.models import Base, NamuWikiIncidentIndexEntryModel


class TestSqlAlchemyIncidentIndexRepository(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()
        self.repository = SqlAlchemyIncidentIndexRepository()

    def tearDown(self) -> None:
        self.session.close()

    def test_upserts_and_marks_removed_entries_inactive(self) -> None:
        first = IncidentIndexEntry(
            title="사건 A",
            year=2025,
            source_url="https://namu.wiki/w/a",
            match_keywords=("사건 A", "사건a"),
        )
        second = IncidentIndexEntry(
            title="사건 B",
            year=2025,
            source_url="https://namu.wiki/w/b",
            risk_categories=("VIOLENCE",),
            match_keywords=("사건 B", "사건b"),
        )

        initial = self.repository.sync_year(self.session, 2025, [first, second])
        self.session.commit()
        follow_up = self.repository.sync_year(self.session, 2025, [first])
        self.session.commit()

        removed = self.session.query(NamuWikiIncidentIndexEntryModel).filter_by(source_url=second.source_url).one()
        self.assertEqual(initial.inserted_count, 2)
        self.assertEqual(follow_up.inserted_count, 0)
        self.assertFalse(removed.is_active)

    def test_finds_active_entries_and_only_reports_unsynced_years(self) -> None:
        entry = IncidentIndexEntry(
            title="사건 A",
            year=2025,
            source_url="https://namu.wiki/w/a",
            risk_categories=("VIOLENCE",),
            match_keywords=("사건 A", "사건a"),
        )
        self.repository.sync_year(self.session, 2025, [entry])
        self.session.commit()

        active_entries = self.repository.find_active_entries(self.session, 2025)
        missing_years = self.repository.years_needing_initial_sync(
            self.session, [2024, 2025, 2026]
        )

        self.assertEqual(active_entries, [entry])
        self.assertEqual(missing_years, [2024, 2026])
