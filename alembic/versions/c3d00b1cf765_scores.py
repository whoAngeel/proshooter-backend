"""scores

Revision ID: c3d00b1cf765
Revises: aea63a0a6738
Create Date: 2025-07-31 20:49:06.802685

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d00b1cf765"
down_revision: Union[str, None] = "aea63a0a6738"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Agregar campos de puntuación a ejercicios, sesiones y estadísticas"""

    # ✅ PRACTICE_EXERCISES - Agregar campos de puntuación
    op.add_column(
        "practice_exercises",
        sa.Column("total_score", sa.Integer(), nullable=True, default=0),
    )
    op.add_column(
        "practice_exercises",
        sa.Column("average_score_per_shot", sa.Float(), nullable=True, default=0.0),
    )
    op.add_column(
        "practice_exercises",
        sa.Column("max_score_achieved", sa.Integer(), nullable=True, default=0),
    )
    op.add_column(
        "practice_exercises", sa.Column("score_distribution", sa.JSON(), nullable=True)
    )
    op.add_column(
        "practice_exercises", sa.Column("group_diameter", sa.Float(), nullable=True)
    )

    # ✅ INDIVIDUAL_PRACTICE_SESSIONS - Agregar campos de puntuación
    op.add_column(
        "individual_practice_sessions",
        sa.Column("total_session_score", sa.Integer(), nullable=True, default=0),
    )
    op.add_column(
        "individual_practice_sessions",
        sa.Column("average_score_per_exercise", sa.Float(), nullable=True, default=0.0),
    )
    op.add_column(
        "individual_practice_sessions",
        sa.Column("average_score_per_shot", sa.Float(), nullable=True, default=0.0),
    )
    op.add_column(
        "individual_practice_sessions",
        sa.Column("best_shot_score", sa.Integer(), nullable=True, default=0),
    )

    # ✅ SHOOTER_STATS - Agregar campos de puntuación
    op.add_column(
        "shooter_stats",
        sa.Column("average_score", sa.Float(), nullable=True, default=0.0),
    )
    op.add_column(
        "shooter_stats",
        sa.Column("best_score_session", sa.Integer(), nullable=True, default=0),
    )
    op.add_column(
        "shooter_stats",
        sa.Column("best_shot_ever", sa.Integer(), nullable=True, default=0),
    )
    op.add_column(
        "shooter_stats",
        sa.Column("score_trend", sa.Float(), nullable=True, default=0.0),
    )
    op.add_column(
        "shooter_stats",
        sa.Column(
            "precision_exercise_avg_score", sa.Float(), nullable=True, default=0.0
        ),
    )
    op.add_column(
        "shooter_stats",
        sa.Column(
            "reaction_exercise_avg_score", sa.Float(), nullable=True, default=0.0
        ),
    )
    op.add_column(
        "shooter_stats",
        sa.Column(
            "movement_exercise_avg_score", sa.Float(), nullable=True, default=0.0
        ),
    )

    # Establecer valores por defecto para registros existentes
    op.execute(
        """
        UPDATE practice_exercises
        SET
            total_score = 0,
            average_score_per_shot = 0.0,
            max_score_achieved = 0
        WHERE total_score IS NULL
    """
    )

    op.execute(
        """
        UPDATE individual_practice_sessions
        SET
            total_session_score = 0,
            average_score_per_exercise = 0.0,
            average_score_per_shot = 0.0,
            best_shot_score = 0
        WHERE total_session_score IS NULL
    """
    )

    op.execute(
        """
        UPDATE shooter_stats
        SET
            average_score = 0.0,
            best_score_session = 0,
            best_shot_ever = 0,
            score_trend = 0.0,
            precision_exercise_avg_score = 0.0,
            reaction_exercise_avg_score = 0.0,
            movement_exercise_avg_score = 0.0
        WHERE average_score IS NULL
    """
    )

    # Hacer NOT NULL las columnas básicas
    op.alter_column(
        "practice_exercises", "total_score", nullable=False, server_default="0"
    )
    op.alter_column(
        "practice_exercises",
        "average_score_per_shot",
        nullable=False,
        server_default="0.0",
    )
    op.alter_column(
        "practice_exercises", "max_score_achieved", nullable=False, server_default="0"
    )

    op.alter_column(
        "individual_practice_sessions",
        "total_session_score",
        nullable=False,
        server_default="0",
    )
    op.alter_column(
        "individual_practice_sessions",
        "average_score_per_exercise",
        nullable=False,
        server_default="0.0",
    )
    op.alter_column(
        "individual_practice_sessions",
        "average_score_per_shot",
        nullable=False,
        server_default="0.0",
    )
    op.alter_column(
        "individual_practice_sessions",
        "best_shot_score",
        nullable=False,
        server_default="0",
    )


def downgrade():
    """Remover campos de puntuación"""
    # Practice exercises
    op.drop_column("practice_exercises", "group_diameter")
    op.drop_column("practice_exercises", "score_distribution")
    op.drop_column("practice_exercises", "max_score_achieved")
    op.drop_column("practice_exercises", "average_score_per_shot")
    op.drop_column("practice_exercises", "total_score")

    # Individual practice sessions
    op.drop_column("individual_practice_sessions", "best_shot_score")
    op.drop_column("individual_practice_sessions", "average_score_per_shot")
    op.drop_column("individual_practice_sessions", "average_score_per_exercise")
    op.drop_column("individual_practice_sessions", "total_session_score")

    # Shooter stats
    op.drop_column("shooter_stats", "movement_exercise_avg_score")
    op.drop_column("shooter_stats", "reaction_exercise_avg_score")
    op.drop_column("shooter_stats", "precision_exercise_avg_score")
    op.drop_column("shooter_stats", "score_trend")
    op.drop_column("shooter_stats", "best_shot_ever")
    op.drop_column("shooter_stats", "best_score_session")
    op.drop_column("shooter_stats", "average_score")
