"""agregando campos de puntuacion en analisis

Revision ID: aea63a0a6738
Revises: b60f8d200c0d
Create Date: 2025-07-28 04:04:04.862944

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aea63a0a6738"
down_revision: Union[str, None] = "b60f8d200c0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Agregar campos de puntuación manteniendo compatibilidad"""

    # Agregar nuevas columnas como NULLABLE primero
    op.add_column(
        "target_analyses", sa.Column("total_score", sa.Integer(), nullable=True)
    )
    op.add_column(
        "target_analyses",
        sa.Column("average_score_per_shot", sa.Float(), nullable=True),
    )
    op.add_column(
        "target_analyses", sa.Column("max_score_achieved", sa.Integer(), nullable=True)
    )
    op.add_column(
        "target_analyses", sa.Column("score_distribution", sa.JSON(), nullable=True)
    )
    op.add_column(
        "target_analyses",
        sa.Column("shooting_group_diameter", sa.Float(), nullable=True),
    )
    op.add_column(
        "target_analyses", sa.Column("group_center_x", sa.Float(), nullable=True)
    )
    op.add_column(
        "target_analyses", sa.Column("group_center_y", sa.Float(), nullable=True)
    )

    # Establecer valores por defecto para registros existentes
    op.execute(
        """
        UPDATE target_analyses
        SET
            total_score = 0,
            average_score_per_shot = 0.0,
            max_score_achieved = 0,
            score_distribution = '{}'::json
        WHERE total_score IS NULL
    """
    )

    # Ahora hacer NOT NULL las columnas que necesiten valor por defecto
    op.alter_column(
        "target_analyses", "total_score", nullable=False, server_default="0"
    )
    op.alter_column(
        "target_analyses",
        "average_score_per_shot",
        nullable=False,
        server_default="0.0",
    )
    op.alter_column(
        "target_analyses", "max_score_achieved", nullable=False, server_default="0"
    )


def downgrade():
    """Remover campos de puntuación"""
    op.drop_column("target_analyses", "group_center_y")
    op.drop_column("target_analyses", "group_center_x")
    op.drop_column("target_analyses", "shooting_group_diameter")
    op.drop_column("target_analyses", "score_distribution")
    op.drop_column("target_analyses", "max_score_achieved")
    op.drop_column("target_analyses", "average_score_per_shot")
    op.drop_column("target_analyses", "total_score")
