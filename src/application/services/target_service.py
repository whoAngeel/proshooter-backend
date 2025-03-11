from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from src.domain.enums.target_enum import TargetType
from src.infraestructure.database.models.target_model import TargetModel
from src.infraestructure.database.repositories.target_repo import TargetRepository
from src.infraestructure.database.session import get_db
from src.presentation.schemas.target_schema import (
    TargetCreate,
    TargetUpdate,
    TargetRead,
    TargetDetail,
    TargetScoreInput,
    TargetScoreOutput
)

class TargetService:

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def create_target(self, target_data: TargetCreate) -> Tuple[Optional[TargetRead], Optional[str]]:
        try:
            target_type = target_data.target_type
            scoring_zones = target_data.scoring_zones

            if target_type == TargetType.CONCENTRIC and scoring_zones:
                if "rings" not in scoring_zones:
                    return None, "MISSING_RINGS"
            elif target_type == TargetType.IPSC and scoring_zones:
                if "zones" not in scoring_zones:
                    return None, "MISSING_ZONES"

            # verificar si ya existe un blanco con el mismo nombre
            existing_target = await TargetRepository.search_by_name(self.db, target_data.name)
            if any(t.name.lower() == target_data.name.lower() for t in existing_target):
                return None, "TARGET_ALREADY_EXISTS"

            target_dict = target_data.model_dump(exclude_unset=True)
            new_target = await TargetRepository.create(self.db, target_dict)

            self.db.commit()
            self.db.refresh(new_target)
            return TargetDetail.model_validate(new_target), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_CREATING_TARGET: {str(e)}"

    async def get_target_by_id(self, target_id: UUID) -> Tuple[Optional[TargetRead], Optional[str]]:
        target = await TargetRepository.get_by_id(self.db, target_id)
        if not target:
            return None, "TARGET_NOT_FOUND"
        return TargetRead.model_validate(target), None

    async def get_target_detail(self, target_id : UUID) -> Tuple[Optional[TargetDetail], Optional[str]]:
        target = await TargetRepository.get_by_id(self.db, target_id)
        if not target:
            return None, "TARGET_NOT_FOUND"
        return TargetDetail.model_validate(target), None

    async def get_all_targets(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[TargetRead]:
        if active_only:
            targets = await TargetRepository.get_active(self.db)
        else:
            targets = await TargetRepository.get_all(self.db, skip, limit)
        return [TargetRead.model_validate(t) for t in targets]

    async def get_targets_by_type(self, target_type: TargetType) -> List[TargetRead]:
        targets = await TargetRepository.get_by_type(self.db, target_type)
        return [TargetRead.model_validate(t) for t in targets]

    async def update_target(
        self,
        target_id: UUID,
        target_data: TargetUpdate,
    ) -> Tuple[Optional[TargetRead], Optional[str]]:
        try:
            existing_target = await TargetRepository.get_by_id(self.db, target_id)
            if not existing_target:
                return None, "TARGET_NOT_FOUND"

            # verificar si hay otro blanco con el mismo nombre que no sea el actual
            if target_data.name and target_data.name.lower() != existing_target.name.lower():
                existing_targets = await TargetRepository.search_by_name(self.db, target_data.name)
                if any(t.name.lower() == target_data.name.lower() and t.id != target_id for t in existing_targets):
                    return None, "TARGET_ALREADY_EXISTS"

            target_dict = target_data.model_dump(exclude_unset=True)
            updated_target = await TargetRepository.update(self.db, target_id, target_dict)
            self.db.commit()

            return TargetRead.model_validate(updated_target), None
        except Exception as e:
            self.db.rollback()
            return None, f"ERROR_UPDATING_TARGET: {str(e)}"


    async def delete_target(self, target_id: UUID, soft_delete: bool = True) -> Tuple[bool, Optional[str]]:
        try:
            existing_target = await TargetRepository.get_by_id(self.db, target_id)
            if not existing_target:
                return False, "TARGET_NOT_FOUND"

            if soft_delete:
                await TargetRepository.deactivate(self.db, target_id)
            else:
                await TargetRepository.delete(self.db, target_id)

            self.db.commit()
            return True, None

        except Exception as e:
            self.db.rollback()
            return False, f"ERROR_DELETING_TARGET: {str(e)}"

    async def search_targets(self, name: str) -> List[TargetRead]:
        """
        Busca blancos por nombre.

        Args:
            name: Nombre o parte del nombre a buscar

        Returns:
            Lista de blancos que coinciden con la búsqueda
        """
        targets = await TargetRepository.search_by_name(self.db, name)
        return [TargetRead.model_validate(t) for t in targets]

    # TODO: cambiar segun la evaluacion
    async def calculate_score(
        self,
        score_input: TargetScoreInput
    ) -> Tuple[Optional[TargetScoreOutput], Optional[str]]:
        """
        Calcula la puntuación para un impacto en un blanco específico.

        Args:
            score_input: Datos del impacto y el blanco

        Returns:
            Tupla con la información de puntuación y un mensaje de error (si hay error)
        """
        try:
            target, error = await self.get_target_by_id(score_input.target_id)
            if error:
                return None, error

            if not target.scoring_zones:
                return None, "El blanco no tiene zonas de puntuación definidas"

            hit_coordinates = score_input.hit_coordinates
            if "x" not in hit_coordinates or "y" not in hit_coordinates:
                return None, "Las coordenadas del impacto deben incluir 'x' y 'y'"

            x = hit_coordinates["x"]
            y = hit_coordinates["y"]

            score = 0
            zone_hit = None

            if target.target_type == TargetType.CONCENTRIC:
                score, zone_hit = self._calculate_concentric_score_with_zone(target.scoring_zones, x, y)

            elif target.target_type == TargetType.IPSC:
                score, zone_hit = self._calculate_ipsc_score_with_zone(target.scoring_zones, x, y)

            else:
                return None, f"Cálculo de puntuación no implementado para el tipo {target.target_type}"

            result = TargetScoreOutput(
                target_id=target.id,
                target_name=target.name,
                target_type=target.target_type,
                score=score,
                hit_coordinates=hit_coordinates,
                zone_hit=zone_hit
            )

            return result, None

        except Exception as e:
            return None, f"ERROR_CALCULATING_SCORE: {str(e)}"

    # TODO: Implementar métodos privados para el cálculo de puntuación
    def _calculate_concentric_score_with_zone(self, scoring_zones: Dict, x: float, y: float) -> Tuple[float, Optional[str]]:
        """
        Calcula la puntuación para un blanco concéntrico y devuelve la zona impactada.

        Args:
            scoring_zones: Definición de las zonas de puntuación
            x: Coordenada X del impacto
            y: Coordenada Y del impacto

        Returns:
            Tupla con la puntuación obtenida y el nombre de la zona impactada
        """
        # Obtener el centro del blanco
        center = scoring_zones.get("center", {"x": 0, "y": 0})
        center_x = center.get("x", 0)
        center_y = center.get("y", 0)

        # Calcular la distancia desde el centro
        distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5

        # Determinar en qué anillo cayó el impacto
        rings = scoring_zones.get("rings", [])
        for ring in sorted(rings, key=lambda r: r.get("radius", 0)):
            if distance <= ring.get("radius", 0):
                return ring.get("score", 0), f"Anillo {ring.get('score', 0)}"

        # Si no cayó en ningún anillo, es un fallo
        return 0, "Fallo"

    def _calculate_ipsc_score_with_zone(self, scoring_zones: Dict, x: float, y: float) -> Tuple[float, Optional[str]]:
        """
        Calcula la puntuación para un blanco IPSC y devuelve la zona impactada.

        Args:
            scoring_zones: Definición de las zonas de puntuación
            x: Coordenada X del impacto
            y: Coordenada Y del impacto

        Returns:
            Tupla con la puntuación obtenida y el nombre de la zona impactada
        """
        # Implementación simplificada para blancos IPSC
        zones = scoring_zones.get("zones", [])

        for zone in zones:
            bounds = zone.get("bounds", {})
            if bounds:
                min_x = bounds.get("min_x", 0)
                max_x = bounds.get("max_x", 0)
                min_y = bounds.get("min_y", 0)
                max_y = bounds.get("max_y", 0)

                if min_x <= x <= max_x and min_y <= y <= max_y:
                    return zone.get("score", 0), zone.get("name", "Zona desconocida")

        # Verificar si impactó una zona de penalización
        penalty_zones = scoring_zones.get("penalty_zones", [])
        for zone in penalty_zones:
            bounds = zone.get("bounds", {})
            if bounds:
                min_x = bounds.get("min_x", 0)
                max_x = bounds.get("max_x", 0)
                min_y = bounds.get("min_y", 0)
                max_y = bounds.get("max_y", 0)

                if min_x <= x <= max_x and min_y <= y <= max_y:
                    return zone.get("penalty", 0), zone.get("name", "Zona de penalización")

        # Si no impactó ninguna zona, es un fallo
        return 0, "Fallo"
