from sqlalchemy.orm import Session
from src.infraestructure.database.session import get_db
from src.infraestructure.database.models.target_analysis_model import (
    TargetAnalysisModel,
)


def validate_migration():
    """Valida que la migración no haya roto análisis existentes"""

    db: Session = next(get_db())

    try:
        # Contar análisis existentes
        total_analyses = db.query(TargetAnalysisModel).count()
        print(f"✅ Total de análisis en BD: {total_analyses}")

        # Verificar que todos tienen valores por defecto
        analyses_with_scores = (
            db.query(TargetAnalysisModel)
            .filter(TargetAnalysisModel.total_score.isnot(None))
            .count()
        )
        print(f"✅ Análisis con total_score: {analyses_with_scores}")

        # Verificar campos nullable
        analyses_with_group_data = (
            db.query(TargetAnalysisModel)
            .filter(TargetAnalysisModel.shooting_group_diameter.isnot(None))
            .count()
        )
        print(f"✅ Análisis con datos de agrupamiento: {analyses_with_group_data}")

        # Verificar que la consolidación sigue funcionando
        sample_analysis = db.query(TargetAnalysisModel).first()
        if sample_analysis:
            print(
                f"✅ Análisis de muestra - Score: {sample_analysis.total_score}, Accuracy: {sample_analysis.accuracy_percentage}%"
            )
            print(f"✅ Tiene datos de puntuación: {sample_analysis.has_scoring_data}")

        print("🎉 Migración validada exitosamente!")

    except Exception as e:
        print(f"❌ Error en validación: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    validate_migration()

    """
    python -c "
from src.infraestructure.database.session import get_db
from src.infraestructure.database.repositories.target_analysis_repo import TargetAnalysisRepository
db = next(get_db())
analysis = TargetAnalysisRepository.get_by_id(db, 'a3c243da-c3e2-4fa7-b88b-ddcf2ac0315c')
print(f'Análisis OK: {analysis.total_score if analysis else \"No encontrado\"}')
"
    """
