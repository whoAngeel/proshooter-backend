# Entidades del sistema

## 1. User y sus datos relacionados

### User

* `id` (Integer, PK)
* `email` (String, único)
* `hashed_password` (String)
* `role` (Enum con valores: `TIRADOR`, `INSTRUCTOR`, `JEFE_INSTRUCTORES`)
* `is_active` (Boolean)
* `created_at` (DateTime)
* `updated_at` (DateTime)
* Comentario: User es la entidad principal de autenticación y permisos. El role puede indicar la jerarquía (Tirador, Instructor, Jefe de Instructores).

### UserPersonalData

* `id` (Integer, PK)
* `user_id` (FK hacia User.id)
* `first_name` (String)
* `last_name` (String)
* `phone_number` (String)
* `date_of_birth` (Date)
* `address` (String)
* `city` (String)
* `state` (String)
* `country` (String)
* Comentario: Datos personales básicos. Separados en otra tabla para no sobrecargar la tabla principal de User.

### UserMedicalData

* `id` (Integer, PK)
* `user_id` (FK hacia User.id)
* `blood_type` (String)
* `allergies` (String)
* `medical_conditions` (String)
* `is_disabled` (Boolean)
* `doctor_name` (String)
* `emergency_contact` (String)
* Comentario: Datos médicos y de contacto de emergencia. Pueden ser opcionales según tus reglas de negocio.

### UserBiometricData

* `id` (Integer, PK)
* `user_id` (FK hacia User.id)
* `height` (Float)
* `weight` (Float)
* `hand_dominance` (String) // "Right-handed", "Left-handed", "Ambidextrous"
* `eye_sight` (String) // Ej: "20/20", "20/40"
* Comentario: Datos que podrían ser relevantes para el desempeño del usuario en el tiro.

## 2. Jerarquía de Roles

### Tirador

* `id` (Integer, PK)
* `user_id` (FK hacia User.id)
* `total_score` (Integer)
* `level` (Integer)
* `rank` (String)
* `average_accuracy` (Float)
* `experience_points` (Integer)
* Comentario: Si cada tirador tiene estadísticas específicas (puntuación, nivel), puedes usar una tabla `ShooterStats` para no mezclarlo con los datos de User.

### Instructor

* `id` (Integer, PK)
* `user_id` (FK hacia User.id)
* `certification_level` (String)
* `years_of_experience` (Integer)
* `is_active_instructor` (Boolean)
* Comentario: Podrías almacenar certificados, experiencia o especialidades. Al ser `role` = `INSTRUCTOR`, tienes la opción de mantenerlo todo en la entidad `User` con un simple campo `role`. Solo usa una tabla extra si quieres campos específicos de instructor.

### JefeInstructores

* `id` (Integer, PK)
* `user_id` (FK hacia User.id)
* `special_authorities` (String)
* Comentario: Similar a `Instructor`, lo puedes manejar en la tabla `User` con `role` = `JEFE_INSTRUCTORES`, o con una tabla separada si deseas campos adicionales.

## 3. Club de Tiro

### ClubTiro

* `id` (Integer, PK)
* `name` (String)
* `location` (String)
* `foundation_date` (Date)
* `jefe_instructor_id` (FK hacia User.id, único si es 1:1)
* Comentario: Un JefeInstructores crea un solo club (1:1). Puedes poner constraint de uniqueness para `jefe_instructor_id`, asegurándote de que cada jefe tenga un solo club.

### Relación ClubTiro → Tirador

* `club_id` (FK hacia ClubTiro.id)
* `tirador_id` (FK hacia User.id o ShooterStats.user_id)
* Comentario: Esto puede existir como un simple campo `club_id` en `ShooterStats` si cada tirador está asociado con un club. O puedes crear una tabla intermedia si necesitas más flexibilidad.

## 4. Grupos de Tiro

### GrupoTiro

* `id` (Integer, PK)
* `name` (String)
* `description` (String)
* `creation_date` (DateTime)
* `instructor_id` (FK hacia User.id)
* Comentario: Un Instructor puede crear varios grupos (1:N).

### Relación Tirador → GrupoTiro (N:M)

* Una tabla pivote, por ejemplo: `TiradorGrupoTiro`:
	+ `id` (Integer, PK)
	+ `grupo_tiro_id` (FK hacia GrupoTiro.id)
	+ `tirador_id` (FK hacia User.id o ShooterStats.user_id)
	+ `joined_at` (DateTime)
	+ Comentario: Aquí guardas la fecha de ingreso de un tirador al grupo y cualquier otro dato relevante.

## 5. Sesiones de Práctica

### SesionPractica (para sesiones individuales y/o grupales)

* `id` (Integer, PK)
* `session_type` (Enum: `INDIVIDUAL`, `GRUPAL`)
* `practice_date` (Date)
* `start_time` (DateTime)
* `end_time` (DateTime)
* `tipo_practica` (String / Enum: "Tiro Rápido", "Tiro a Distancia", "Tiro de Precisión")
* `weapon_id` (FK)
* `ammunition_id` (FK)
* `target_id` (FK)
* `instructor_id` (FK hacia User.id – opcional si necesitas saber quién supervisa)
* `location` (String) // Dónde se lleva a cabo
* Comentario: Puedes usar un solo modelo para ambos tipos de sesión, con `session_type` indicando si es individual o grupal.

### EvaluacionIndividual

* `id` (Integer, PK)
* `session_id` (FK hacia SesionPractica.id)
* `tirador_id` (FK hacia User.id)
* `final_score` (Integer)
* `accuracy` (Float)
* `remarks` (String)
* `evaluation_date` (DateTime)
* Comentario: Cada sesión (individual o grupal) genera una evaluación por tirador. Para sesiones grupales, se registra en la tabla pivote (ver abajo).

### Sesion_Tirador (tabla intermedia para sesiones grupales)

* `id` (Integer, PK)
* `session_id` (FK hacia SesionPractica.id)
* `tirador_id` (FK hacia User.id)
* `evaluacion_individual_id` (FK hacia EvaluacionIndividual.id, 1:1)
* Comentario: Asocia múltiples tiradores a la misma sesión grupal y guarda el ID de su evaluación individual.

### EvaluacionGrupal

* `id` (Integer, PK)
* `session_id` (FK hacia SesionPractica.id) // Solo aplica si `session_type` = `GRUPAL`
* `overall_score` (Integer)
* `average_accuracy` (Float)
* `remarks` (String)
* `evaluation_date` (DateTime)
* Comentario: Al final de una sesión grupal, se genera una evaluación conjunta.

## 6. Recursos: Arma, Munición, Blanco

### Arma

* `id` (Integer, PK)
* `name` (String)
* `model` (String)
* `brand` (String)
* `caliber` (String)
* `serial_number` (String)
* `is_active` (Boolean)
* Comentario: Campos típicos para un arma; `is_active` para marcar si está en servicio o fuera de circulación.

### Municion

* `id` (Integer, PK)
* `caliber` (String)
* `brand` (String)
* `bullet_type` (String) // Ej: FMJ, Hollow Point, etc.
* `is_active` (Boolean)
* Comentario: Si diferentes municiones son relevantes para el registro.

### Blanco (Target)

* `id` (Integer, PK)
* `name` (String)
* `material` (String)
* `size` (String) // ej: dimensiones
* `shape` (String) // Circular, Silueta, etc.
* `is_active` (Boolean)
* Comentario: Configurable según tu sistema. Puede haber blancos reutilizables o de un solo uso.
