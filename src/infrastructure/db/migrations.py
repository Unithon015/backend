from sqlalchemy import Connection, inspect, text


def upgrade_application_schema(connection: Connection) -> None:
    """Apply backwards-compatible application schema changes for the MVP."""
    if connection.dialect.name != "postgresql":
        return

    columns = {
        column["name"] for column in inspect(connection).get_columns("analysis_runs")
    }
    if "review_context_snapshot" not in columns:
        connection.execute(
            text(
                "ALTER TABLE analysis_runs ADD COLUMN review_context_snapshot JSONB "
                "NOT NULL DEFAULT '{}'::jsonb"
            )
        )

    foreign_keys = inspect(connection).get_foreign_keys("content_submissions")
    has_owner_foreign_key = any(
        key.get("referred_table") == "users" and key.get("constrained_columns") == ["owner_id"]
        for key in foreign_keys
    )
    if not has_owner_foreign_key:
        connection.execute(
            text(
                "ALTER TABLE content_submissions "
                "ADD CONSTRAINT fk_content_submissions_owner_id_users "
                "FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE NOT VALID"
            )
        )
