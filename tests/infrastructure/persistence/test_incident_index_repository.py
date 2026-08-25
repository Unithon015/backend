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
        first = IncidentIndexEntry("사건 A", "사건a", "https://namu.wiki/w/a", 2025)
        second = IncidentIndexEntry("사건 B", "사건b", "https://namu.wiki/w/b", 2025)

        initial = self.repository.sync_year(self.session, 2025, [first, second])
        self.session.commit()
        follow_up = self.repository.sync_year(self.session, 2025, [first])
        self.session.commit()

        removed = self.session.query(NamuWikiIncidentIndexEntryModel).filter_by(article_url=second.article_url).one()
        self.assertEqual(initial.inserted_count, 2)
        self.assertEqual(follow_up.inserted_count, 0)
        self.assertFalse(removed.is_active)
