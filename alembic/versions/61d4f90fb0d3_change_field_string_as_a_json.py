"""change field string as a JSON

Revision ID: 61d4f90fb0d3
Revises: f8ab38c82523
Create Date: 2025-08-26 21:05:04.855779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61d4f90fb0d3'
down_revision: Union[str, None] = 'f8ab38c82523'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Usar SQL directo en lugar de alter_column para manejar la conversión
    op.execute("""
        ALTER TABLE practice_exercises 
        ALTER COLUMN score_distribution TYPE JSON 
        USING CASE 
            WHEN score_distribution IS NULL THEN NULL
            WHEN score_distribution = '' THEN NULL
            WHEN score_distribution = 'null' THEN NULL
            ELSE score_distribution::JSON 
        END
    """)


def downgrade() -> None:
    # Para revertir la migración
    op.execute("""
        ALTER TABLE practice_exercises 
        ALTER COLUMN score_distribution TYPE VARCHAR 
        USING CASE 
            WHEN score_distribution IS NULL THEN NULL
            ELSE score_distribution::VARCHAR 
        END
    """)