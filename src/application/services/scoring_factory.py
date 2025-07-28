from src.application.services.scoring_calculator import ScoringCalculatorService
from src.domain.value_objects.target_config import TargetConfigurations, TargetType


class ScoringCalculatorFactory:

    @staticmethod
    def create_calculator(target_type: TargetType) -> ScoringCalculatorService:
        config = TargetConfigurations.get_config(target_type)
        return ScoringCalculatorService(config)

    @staticmethod
    def create_pro_shooter_calculator() -> ScoringCalculatorService:
        return ScoringCalculatorFactory.create_calculator(TargetType.PRO_SHOOTER)
