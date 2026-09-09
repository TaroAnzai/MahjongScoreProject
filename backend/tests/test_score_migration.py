import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


def test_score_migration_preserves_integers_and_blocks_downgrade(tmp_path):
    path = Path(__file__).parents[1] / "migrations/versions/e5a103bc9201_score_decimal.py"
    spec = importlib.util.spec_from_file_location("score_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine(f"sqlite:///{tmp_path / 'migration.sqlite'}")
    with engine.begin() as conn:
        conn.execute(sa.text("CREATE TABLE tbl_scores (id INTEGER PRIMARY KEY, score INTEGER NOT NULL)"))
        values = [100, 0, -100, 25000, -12000, 2147483647, -2147483648]
        for i, value in enumerate(values):
            conn.execute(sa.text("INSERT INTO tbl_scores VALUES (:id, :score)"), {"id": i, "score": value})
        with Operations.context(MigrationContext.configure(conn)):
            migration.upgrade()
        column = sa.inspect(conn).get_columns("tbl_scores")[1]
        assert column["type"].precision == 15
        assert column["type"].scale == 5
        assert column["nullable"] is False
        scores = sa.table("tbl_scores", sa.column("id", sa.Integer), sa.column("score", sa.Numeric(15, 5)))
        assert conn.execute(sa.select(scores.c.score).order_by(scores.c.id)).scalars().all() == [Decimal(v) for v in values]
        conn.execute(scores.insert().values(id=100, score=Decimal("-12.34567")))
        with Operations.context(MigrationContext.configure(conn)), pytest.raises(RuntimeError, match="data loss"):
            migration.downgrade()
        assert conn.execute(sa.select(scores.c.score).where(scores.c.id == 100)).scalar_one() == Decimal("-12.34567")
    engine.dispose()
