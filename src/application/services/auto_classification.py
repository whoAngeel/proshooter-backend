from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from uuid import UUID
from src.domain.enums.classification_enum import ShooterLevelEnum
from src.infraestructure.database.repositories.practice_evaluation_repo import (
    PracticeEvaluationRepository,
)
from src.infraestructure.database.repositories.shooter_repo import ShooterRepository
from src.infraestructure.database.session import get_db
import logging

logger = logging.getLogger(__name__)


class AutoClassificationService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.evaluation_repo = PracticeEvaluationRepository
        self.shooter_repo = ShooterRepository

    def check_and_update_classification(
        self, shooter_id: UUID, new_evaluation_classification: str
    ):
        try:
            shooter = self.shooter_repo.get_by_id(self.db, shooter_id)
            if not shooter:
                return False

            recent_evaluations = self.evaluation_repo.get_shooter_evaluation_history(
                self.db, shooter_id, limit=10
            )

            if len(recent_evaluations) < 5:
                return False

            # Analizar ultimas 5 evaluaciones
            last_5 = recent_evaluations[5:]
            classification = [self._eval_to_level(eval.final_score) for eval in last_5]

            # contar ocurrencias
            from collections import Counter

            counts = Counter(classification)
            most_common_level = counts.most_common(1)[0][0]
            frequency = counts[most_common_level]

            # criterio: 4 de 5 ultimas evaluacions en el mismo nivel
            if frequency >= 4:
                current_level = shooter.level
                target_level = ShooterLevelEnum[most_common_level]

                # solo ascensos automaticos
                if self._is_valid_upgrade(current_level, target_level):
                    shooter.level = target_level
                    self.db.commit()

                    logger.info(
                        f"✅ Clasificación actualizada para el tirador {shooter_id} de {current_level} a {target_level.value}"
                    )
                    return True
            return False
        except Exception as e:
            logger.error(
                f"❌ Error al actualizar clasificación para el tirador {shooter_id}: {e}"
            )
            return False

    def _eval_to_level(self, final_score: float) -> str:
        """Convierte puntuación a nivel"""
        if final_score >= 90:
            return ShooterLevelEnum.EXPERTO.value
        elif final_score >= 70:
            return ShooterLevelEnum.CONFIABLE.value
        elif final_score >= 40:
            return ShooterLevelEnum.MEDIO.value
        else:
            return ShooterLevelEnum.REGULAR.value

    def _is_valid_upgrade(
        self, current: ShooterLevelEnum, target: ShooterLevelEnum
    ) -> bool:
        """Verifica que sea ascenso válido (un nivel a la vez)"""
        levels = [
            ShooterLevelEnum.REGULAR,
            ShooterLevelEnum.MEDIO,
            ShooterLevelEnum.CONFIABLE,
            ShooterLevelEnum.EXPERTO,
        ]

        try:
            current_idx = levels.index(current)
            target_idx = levels.index(target)

            # Solo un nivel hacia arriba
            return target_idx == current_idx + 1
        except ValueError:
            return False
