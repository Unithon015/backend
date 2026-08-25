from sqlalchemy import Connection, inspect, text


TABLE_NAME = "namu_wiki_incident_index_entries"


def upgrade_incident_index_schema(connection: Connection) -> None:
    """Apply the small backwards-compatible schema upgrade used by the MVP."""
    if connection.dialect.name != "postgresql":
        return

    columns = {column["name"] for column in inspect(connection).get_columns(TABLE_NAME)}
    if "article_url" in columns and "source_url" not in columns:
        connection.execute(text(f"ALTER TABLE {TABLE_NAME} RENAME COLUMN article_url TO source_url"))
    if "incident_year" in columns and "year" not in columns:
        connection.execute(text(f"ALTER TABLE {TABLE_NAME} RENAME COLUMN incident_year TO year"))

    columns = {column["name"] for column in inspect(connection).get_columns(TABLE_NAME)}
    if "risk_categories" not in columns:
        connection.execute(
            text(
                f"ALTER TABLE {TABLE_NAME} ADD COLUMN risk_categories JSONB NOT NULL "
                "DEFAULT '[]'::jsonb"
            )
        )
    if "match_keywords" not in columns:
        connection.execute(
            text(
                f"ALTER TABLE {TABLE_NAME} ADD COLUMN match_keywords JSONB NOT NULL "
                "DEFAULT '[]'::jsonb"
            )
        )
        connection.execute(
            text(
                f"UPDATE {TABLE_NAME} "
                "SET match_keywords = jsonb_build_array(title, normalized_title) "
                "WHERE match_keywords = '[]'::jsonb"
            )
        )
    if "source_type" not in columns:
        connection.execute(
            text(
                f"ALTER TABLE {TABLE_NAME} ADD COLUMN source_type VARCHAR(64) NOT NULL "
                "DEFAULT 'NAMU_WIKI'"
            )
        )
