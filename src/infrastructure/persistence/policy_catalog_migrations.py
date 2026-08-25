from sqlalchemy import Connection, inspect, text


TABLE_NAME = "policy_catalog_entries"


def upgrade_policy_catalog_schema(connection: Connection) -> None:
    """Add policy-context fields without requiring a destructive database reset."""
    if connection.dialect.name != "postgresql":
        return

    columns = {column["name"] for column in inspect(connection).get_columns(TABLE_NAME)}
    additions = {
        "policy_summary": "TEXT NOT NULL DEFAULT ''",
        "detection_hints": "JSONB NOT NULL DEFAULT '[]'::jsonb",
        "match_keywords": "JSONB NOT NULL DEFAULT '[]'::jsonb",
        "applicable_media_types": "JSONB NOT NULL DEFAULT '[]'::jsonb",
        "is_active": "BOOLEAN NOT NULL DEFAULT TRUE",
    }
    for column_name, definition in additions.items():
        if column_name not in columns:
            connection.execute(text(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {column_name} {definition}"))
