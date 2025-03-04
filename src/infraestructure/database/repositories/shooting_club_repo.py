from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from src.infraestructure.database.models.shooter_model import ShooterModel
from src.infraestructure.database.models.user_model import UserModel
from src.infraestructure.database.models.shooting_club_model import ShootingClubModel
from src.infraestructure.database.models.shooter_stats_model import ShooterStatsModel

class ShootingClubRepository:
    @staticmethod
    def create(db: Session, club_data: Dict[str, Any])-> ShootingClubModel:
        """
        Crea un nuevo club de tiro.

        Args:
            db (Session): Sesión de base de datos activa
            club_data (Dict[str, Any]): Diccionario con los datos del club a crear

        Returns:
            ShootingClubModel: Instancia del club de tiro creado
        """
        new_club = ShootingClubModel(**club_data)
        db.add(new_club)
        db.flush()
        return new_club

    @staticmethod
    def get_by_id(db: Session, club_id: UUID) -> Optional[ShootingClubModel]:
        """
        Obtiene un club de tiro por su ID.

        Args:
            db (Session): Sesión de base de datos activa
            club_id (UUID): ID del club a buscar

        Returns:
            Optional[ShootingClubModel]: Instancia del club de tiro si existe, None en caso contrario
        """
        return db.execute(
            select(ShootingClubModel).options(
                joinedload(ShootingClubModel.chief_instructor).joinedload(UserModel.personal_data),
                joinedload(ShootingClubModel.members).joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShootingClubModel.members).joinedload(ShooterModel.stats)
            ).where(ShootingClubModel.id == club_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[ShootingClubModel]:
        """
        Obtiene un club de tiro por su nombre.

        Args:
            db (Session): Sesión de base de datos activa
            name (str): Nombre del club a buscar

        Returns:
            Optional[ShootingClubModel]: Instancia del club de tiro si existe, None en caso contrario
        """
        return db.execute(
            select(ShootingClubModel).where(ShootingClubModel.name == name)
        ).scalar_one_or_none()

    @staticmethod
    def get_by_chief_instructor(db: Session, chief_instructor_id: UUID) -> Optional[ShootingClubModel]:
        """
        Obtiene un club de tiro por el ID del jefe de instructores.

        Args:
            db (Session): Sesión de base de datos activa
            chief_instructor_id (UUID): ID del jefe de instructores

        Returns:
            Optional[ShootingClubModel]: Instancia del club de tiro si existe, None en caso contrario
        """
        return db.execute(
            select(ShootingClubModel)
            .options(
                joinedload(ShootingClubModel.chief_instructor).joinedload(UserModel.personal_data),
                joinedload(ShootingClubModel.members).joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShootingClubModel.members).joinedload(ShooterModel.stats)
            )
            .where(ShootingClubModel.chief_instructor_id == chief_instructor_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100)-> List[ShootingClubModel]:
        """
        Obtiene todos los clubes de tiro registrados.

        Args:
            db (Session): Sesión de base de datos activa
            skip (int): Número de registros a omitir (para paginación)
            limit (int): Límite de registros a devolver (para paginación)

        Returns:
            List[ShootingClubModel]: Lista de clubes de tiro
        """
        return db.execute(
            select(ShootingClubModel)
            .options(
                joinedload(ShootingClubModel.chief_instructor).joinedload(UserModel.personal_data)
            )
            .order_by(ShootingClubModel.name)
            .offset(skip)
            .limit(limit)
        ).scalars().all()


    @staticmethod
    def get_all_with_member_count(db: Session, skip: int = 0, limit: int = 100) -> List[Tuple[ShootingClubModel, int]]:
        """
        Obtiene todos los clubes de tiro registrados con la cantidad de miembros asociados.

        Args:
            db (Session): Sesión de base de datos activa
            skip (int): Número de registros a omitir (para paginación)
            limit (int): Límite de registros a devolver (para paginación)

        Returns:
            List[Tuple[ShootingClubModel, int]]: Lista de clubes de tiro con la cantidad de miembros asociados
        """
        return db.execute(
            select(
                ShootingClubModel,
                func.count(ShooterModel.user_id).label("member_count")
            )
            .outerjoin(ShooterModel, ShootingClubModel.id == ShooterModel.club_id)
            .options(
                joinedload(ShootingClubModel.chief_instructor).joinedload(UserModel.personal_data)
            )
            .group_by(ShootingClubModel.id)
            .order_by(ShootingClubModel.name)
            .offset(skip)
            .limit(limit)
        ).all()


    @staticmethod
    def search_clubs(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[ShootingClubModel]:
        """
        Busca clubes de tiro por su nombre o descripción.

        Args:
            db (Session): Sesión de base de datos activa
            search_term (str): Término de búsqueda
            skip (int): Número de registros a omitir (para paginación)
            limit (int): Límite de registros a devolver (para paginación)

        Returns:
            List[ShootingClubModel]: Lista de clubes de tiro que coinciden con la búsqueda
        """
        search_pattern = f"${search_term}%"
        return db.execute(
            select(ShootingClubModel).options(
                joinedload(ShootingClubModel.chief_instructor).joinedload(UserModel.personal_data)
            ).where(
                (ShootingClubModel.name.ilike(search_pattern)) |
                (ShootingClubModel.description.ilike(search_pattern))
            ).order_by(ShootingClubModel.name).offset(skip).limit(limit)
        ).scalars().all()


    @staticmethod
    def get_club_members(db: Session, club_id: UUID, skip: int = 0, limit: int = 100) -> List[ShooterModel]:
        """
        Obtiene todos los miembros de un club de tiro específico.

        Args:
            db (Session): Sesión de base de datos activa
            club_id (UUID): ID del club
            skip (int): Número de registros a omitir (para paginación)
            limit (int): Límite de registros a devolver (para paginación)

        Returns:
            List[ShooterModel]: Lista de tiradores miembros del club
        """
        return db.execute(
            select(ShooterModel).options(
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShooterModel.stats)
            ).where(ShooterModel.club_id == club_id).offset(skip).limit(limit)
        ).scalars().all()


    @staticmethod
    def count_club_members(db: Session, club_id: UUID) -> int:
        """
        Cuenta el número de miembros en un club de tiro.

        Args:
            db (Session): Sesión de base de datos activa
            club_id (UUID): ID del club

        Returns:
            int: Número de miembros en el club
        """
        result = db.execute(
            select(func.count(ShooterModel.user_id))
            .where(ShooterModel.club_id == club_id)
        ).scalar_one_or_none()

        return result or 0

    @staticmethod
    def update(db: Session, club_id: UUID, updated_data: Dict[str, Any]) -> Optional[ShootingClubModel]:
        """
        Actualiza los datos de un club de tiro existente.

        Args:
            db (Session): Sesión de base de datos activa
            club_id (UUID): ID del club a actualizar
            update_data (Dict[str, Any]): Datos a actualizar

        Returns:
            Optional[ShootingClubModel]: Club actualizado o None si no existe
        """
        club = db.execute(
            select(ShootingClubModel).where(ShootingClubModel.id == club_id)
        ).scalar_one_or_none()

        if club :
            for key, value in updated_data.items():
                setattr(club, key, value)
            db.flush()
            return club

        return None

    @staticmethod
    def delete(db: Session, club_id: UUID) -> bool:
        """
        Elimina un club de tiro de la base de datos.

        Args:
            db (Session): Sesión de base de datos activa
            club_id (UUID): ID del club a eliminar

        Returns:
            bool: True si se eliminó correctamente, False si no se encontró
        """
        club = db.execute(
            select(ShootingClubModel).where(ShootingClubModel.id == club_id)
        ).scalar_one_or_none()

        if club:
            db.delete(club)
            db.flush()
            return True
        return False

    @staticmethod
    def add_member(db: Session, club_id: UUID, user_id: UUID) -> Optional[ShooterModel]:
        """
        Agrega un tirador a un club de tiro.

        Args:
            db (Session): Sesión de base de datos activa
            club_id (UUID): ID del club
            user_id (UUID): ID del tirador a agregar

        Returns:
            Optional[ShooterModel]: Tirador agregado o None si no se pudo agregar
        """
        shooter = db.execute(
            select(ShooterModel).where(ShooterModel.user_id == user_id)
        ).scalar_one_or_none()

        if shooter:
            shooter.club_id = club_id
            db.flush()
            return shooter
        return None

    @staticmethod
    def remove_member(db: Session, shooter_id: UUID) -> Optional[ShooterModel]:
        """
        Remueve un tirador de su club actual (establece club_id a NULL).

        Args:
            db (Session): Sesión de base de datos activa
            shooter_id (UUID): ID del tirador

        Returns:
            Optional[ShooterModel]: Tirador actualizado o None si no existe
        """
        shooter = db.execute(
            select(ShooterModel).where(ShooterModel.user_id == shooter_id)
        ).scalar_one_or_none

        if shooter:
            shooter.club_id = None
            db.flush()
            return shooter
        return None

    @staticmethod
    def get_club_statistics(db: Session, club_id: UUID) -> Dict[str, Any]:
        """
        Calcula estadísticas para un club específico: número de miembros,
        precisión promedio, mejor tirador, etc.

        Args:
            db (Session): Sesión de base de datos activa
            club_id (UUID): ID del club

        Returns:
            Dict[str, Any]: Diccionario con estadísticas del club
        """
        # Verificar que el club existe
        club = ShootingClubRepository.get_by_id(db, club_id)
        if not club:
            return {}

        # Obtener miembros del club con sus estadísticas
        members = db.execute(
            select(ShooterModel)
            .options(
                joinedload(ShooterModel.user).joinedload(UserModel.personal_data),
                joinedload(ShooterModel.stats)
            )
            .where(ShooterModel.club_id == club_id)
        ).scalars().all()

        if not members:
            return {
                "member_count": 0,
                "message": "El club no tiene miembros"
            }

        # Inicializar estadísticas
        stats = {
            "member_count": len(members),
            "average_accuracy": 0,
            "best_shooter": None,
            "best_accuracy": 0,
            "total_shots": 0,
            "total_sessions": 0,
            "classification_distribution": {}
        }

        # Calcular estadísticas
        total_accuracy = 0
        best_accuracy = 0
        best_shooter = None
        valid_members = 0
        classification_counts = {}

        for member in members:
            # Contar clasificaciones
            classification = member.classification or "Sin clasificar"
            classification_counts[classification] = classification_counts.get(classification, 0) + 1

            if member.stats and hasattr(member.stats, 'accuracy') and member.stats.accuracy is not None:
                valid_members += 1
                total_accuracy += member.stats.accuracy

                if member.stats.accuracy > best_accuracy:
                    best_accuracy = member.stats.accuracy
                    best_shooter = {
                        "id": member.user_id,
                        "name": f"{member.user.personal_data.first_name} {member.user.personal_data.last_name}" if hasattr(member.user, 'personal_data') and member.user.personal_data else "Unknown",
                        "classification": member.classification,
                        "accuracy": member.stats.accuracy
                    }

                if hasattr(member.stats, 'total_shots'):
                    stats["total_shots"] += member.stats.total_shots

                if hasattr(member.stats, 'total_sessions'):
                    stats["total_sessions"] += member.stats.total_sessions

        # Calcular promedios si hay datos válidos
        if valid_members > 0:
            stats["average_accuracy"] = round(total_accuracy / valid_members, 2)

        if best_shooter:
            stats["best_shooter"] = best_shooter
            stats["best_accuracy"] = best_accuracy

        stats["classification_distribution"] = classification_counts

        return stats

    @staticmethod
    def get_top_clubs_by_accuracy(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene los clubes con la mejor precisión promedio.

        Args:
            db (Session): Sesión de base de datos activa
            limit (int): Cantidad de clubes a retornar

        Returns:
            List[Dict[str, Any]]: Lista de los mejores clubes con estadísticas
        """
        # Obtenemos todos los clubes
        clubs = ShootingClubRepository.get_all(db)
        club_stats = []

        for club in clubs:
            stats = ShootingClubRepository.get_club_statistics(db, club.id)
            if stats.get("member_count", 0) > 0 and stats.get("average_accuracy", 0) > 0:
                club_stats.append({
                    "id": club.id,
                    "name": club.name,
                    "chief_instructor_name": f"{club.chief_instructor.personal_data.first_name} {club.chief_instructor.personal_data.last_name}" if hasattr(club.chief_instructor, 'personal_data') and club.chief_instructor.personal_data else "Unknown",
                    "member_count": stats.get("member_count", 0),
                    "average_accuracy": stats.get("average_accuracy", 0),
                    "best_shooter": stats.get("best_shooter", None)
                })

        # Ordenamos por precisión promedio (de mayor a menor)
        club_stats.sort(key=lambda x: x["average_accuracy"], reverse=True)

        return club_stats[:limit]
