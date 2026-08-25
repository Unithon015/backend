import os
import unittest
from unittest.mock import patch

from src.infrastructure.persistence.database import database_url


class TestDatabaseUrl(unittest.TestCase):
    def test_converts_asyncpg_url_to_sync_psycopg_for_index_workers(self):
        value = "postgresql+asyncpg://user:password@example.test:5432/bbik?ssl=require"
        with patch.dict(os.environ, {"DATABASE_URL": value}, clear=False):
            self.assertEqual(
                database_url(),
                "postgresql+psycopg://user:password@example.test:5432/bbik?sslmode=require",
            )
