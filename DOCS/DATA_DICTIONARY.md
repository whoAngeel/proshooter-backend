
# Diccionario de Datos

Este diccionario describe las entidades principales de la base de datos del sistema Proshooter, sus campos clave y relaciones.

---


## USERS
Contiene la información principal de los usuarios del sistema.
Campos:
- id: UUID, identificador único (PK)
- email: String, correo electrónico
- hashed_password: String, contraseña encriptada
- role: Enum, rol del usuario (admin, shooter, instructor, etc.)
- is_active: Boolean, indica si el usuario está activo



## USER_PERSONAL_DATA
Datos personales asociados a cada usuario.
Campos:
- user_id: UUID, referencia a USERS (PK)
- first_name: String, nombre(s)
- last_name: String, apellidos
- birth_date: Date, fecha de nacimiento
- gender: Enum, género (M/F/Otro)
- nationality: String, nacionalidad
- document_type: String, tipo de documento de identidad
- document_number: String, número de documento
- phone: String, teléfono de contacto
- address: String, dirección de residencia



## USER_MEDICAL_DATA
Datos médicos relevantes del usuario.
Campos:
- user_id: UUID, referencia a USERS (PK)
- blood_type: String, tipo de sangre
- allergies: String, alergias conocidas
- medical_conditions: String, condiciones médicas relevantes
- emergency_contact_name: String, nombre del contacto de emergencia
- emergency_contact_phone: String, teléfono del contacto de emergencia



## USER_BIOMETRIC_DATA
Datos biométricos del usuario.
Campos:
- user_id: UUID, referencia a USERS (PK)
- height_cm: Integer, estatura en centímetros
- weight_kg: Integer, peso en kilogramos
- eye_color: String, color de ojos
- hair_color: String, color de cabello
- body_fat_percentage: Float, porcentaje de grasa corporal
- bmi: Float, índice de masa corporal





## SHOOTERS
Usuarios registrados como tiradores.
Campos:
- user_id: UUID, referencia a USERS (PK)
- club_id: UUID, referencia a SHOOTING_CLUBS
- level: Enum, nivel del tirador (ver ShooterLevelEnum)
- range: String, rango/categoría del tirador
- nickname: String, apodo único del tirador
- license_file: String, archivo de licencia (ruta/URL)
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## SHOOTER_STATS
Estadísticas de rendimiento de cada tirador.
Campos:
- shooter_id: UUID, referencia a SHOOTERS (PK)
- total_shots: Integer, total de disparos realizados
- accuracy: Integer, porcentaje de precisión
- reaction_shots: Integer, cantidad de disparos de reacción
- presicion_shots: Integer, cantidad de disparos de precisión
- draw_time_avg: Float, tiempo promedio de desenfunde
- reload_time_avg: Float, tiempo promedio de recarga
- average_hit_factor: Float, hit factor promedio
- effectiveness: Float, efectividad general
- trend_accuracy: Float, tendencia de precisión
- last_10_sessions_avg: Float, promedio de las últimas 10 sesiones
- precision_exercise_accuracy: Float, precisión en ejercicios de precisión
- reaction_exercise_accuracy: Float, precisión en ejercicios de reacción
- movement_exercise_accuracy: Float, precisión en ejercicios de movimiento
- common_error_zones: String, zonas comunes de error
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización




## SHOOTING_CLUBS
Clubes de tiro registrados en el sistema.
Campos:
- id: UUID, identificador único (PK)
- name: String, nombre único del club
- description: String, descripción del club
- chief_instructor_id: UUID, referencia a USERS (instructor jefe)
- is_active: Boolean, indica si el club está activo
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## INDIVIDUAL_PRACTICE_SESSIONS
Sesiones individuales de práctica de tiro.
Campos:
- id: UUID, identificador único (PK)
- shooter_id: UUID, referencia a SHOOTERS
- instructor_id: UUID, referencia a USERS (puede ser nulo)
- date: DateTime, fecha de la sesión
- location: String, ubicación de la sesión
- total_shots_fired: Integer, total de disparos realizados
- total_hits: Integer, total de impactos
- accuracy_percentage: Float, porcentaje de aciertos
- evaluation_pending: Boolean, indica si la sesión está pendiente de evaluación
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## PRACTICE_EXERCISES
Ejercicios realizados dentro de una sesión de práctica.
Campos:
- id: UUID, identificador único (PK)
- session_id: UUID, referencia a INDIVIDUAL_PRACTICE_SESSIONS
- exercise_type_id: UUID, referencia a EXERCISE_TYPES
- target_id: UUID, referencia a TARGETS
- weapon_id: UUID, referencia a WEAPONS
- ammunition_id: UUID, referencia a AMMUNITION
- distance: String, distancia al blanco (en metros)
- firing_cadence: String, cadencia de disparo
- time_limit: String, límite de tiempo
- ammunition_allocated: Integer, munición asignada
- ammunition_used: Integer, munición utilizada
- hits: Integer, impactos logrados
- accuracy_percentage: Float, porcentaje de aciertos
- reaction_time: Float, tiempo de reacción
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## PRACTICE_EVALUATIONS
Evaluaciones realizadas sobre una sesión de práctica.
Campos:
- id: UUID, identificador único (PK)
- session_id: UUID, referencia a INDIVIDUAL_PRACTICE_SESSIONS
- evaluator_id: UUID, referencia a USERS
- final_score: Float, calificación general
- classification: Enum, clasificación del tirador (ver ShooterLevelEnum)
- strengths: String, fortalezas observadas
- weaknesses: String, debilidades observadas
- recomendations: String, recomendaciones
- posture_rating: Integer, calificación de postura (1-10)
- grip_rating: Integer, calificación de agarre (1-10)
- sight_alignment_rating: Integer, calificación de alineación de miras (1-10)
- trigger_control_rating: Integer, calificación de control de disparador (1-10)
- breathing_rating: Integer, calificación de respiración (1-10)
- primary_issue_zone: String, zona principal de error
- secondary_issue_zone: String, zona secundaria de error
- avg_reaction_time: Float, tiempo promedio de reacción
- avg_draw_time: Float, tiempo promedio de desenfunde
- avg_reload_time: Float, tiempo promedio de recarga
- hit_factor: Float, puntos/tiempo (métrica IPSC)
- date: DateTime, fecha de la evaluación
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## EXERCISE_TYPES
Tipos de ejercicios disponibles.
Campos:
- id: UUID, identificador único (PK)
- name: String, nombre del tipo de ejercicio
- description: String, descripción del ejercicio
- difficulty: Integer, dificultad del ejercicio
- objective: String, objetivo del ejercicio
- development: String, desarrollo o instrucciones
- is_active: Boolean, indica si el tipo de ejercicio está activo
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## WEAPONS
Armas registradas en el sistema.
Campos:
- id: UUID, identificador único (PK)
- name: String, nombre del arma
- brand: String, marca del arma
- model: String, modelo del arma
- serial_number: String, número de serie (único)
- weapon_type: Enum, tipo de arma (ver WeaponTypeEnum)
- caliber: String, calibre
- description: String, descripción adicional
- is_active: Boolean, indica si el arma está activa
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## AMMUNITION
Municiones registradas en el sistema.
Campos:
- id: UUID, identificador único (PK)
- name: String, nombre de la munición
- brand: String, marca de la munición
- caliber: String, calibre
- ammo_type: Enum, tipo de munición (ver AmmoType)
- grain_weight: Float, peso en granos
- velocity: Float, velocidad en pies por segundo
- description: String, descripción adicional
- price_per_round: Float, precio por unidad
- is_active: Boolean, indica si la munición está activa
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## WEAPON_AMMUNITION_COMPATIBILITY
Compatibilidad entre armas y municiones.
Campos:
- id: UUID, identificador único (PK)
- weapon_id: UUID, referencia a WEAPONS
- ammunition_id: UUID, referencia a AMMUNITION
- created_at: DateTime, fecha de creación



## TARGETS
Blancos utilizados en los ejercicios.
Campos:
- id: UUID, identificador único (PK)
- name: String, nombre del blanco
- target_type: Enum, tipo de blanco (ver TargetType)
- description: String, descripción del blanco
- scoring_zones: JSON, configuración de zonas de puntuación
- dimensions: String, dimensiones físicas (ancho x alto)
- distance_recommended: Float, distancia recomendada en metros
- is_active: Boolean, indica si el blanco está activo
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## TARGET_IMAGES
Imágenes de los blancos generadas durante los ejercicios.
Campos:
- id: UUID, identificador único (PK)
- exercise_id: UUID, referencia a PRACTICE_EXERCISES
- file_path: String, ruta del archivo de imagen
- file_size: Integer, tamaño del archivo (bytes)
- content_type: String, tipo de contenido (MIME)
- uploaded_at: DateTime, fecha y hora de carga
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## TARGET_ANALYSES
Resultados de análisis realizados sobre imágenes de blancos.
Campos:
- id: UUID, identificador único (PK)
- target_image_id: UUID, referencia a TARGET_IMAGES
- analysis_timestamp: DateTime, fecha y hora del análisis
- total_impacts_detected: Integer, impactos detectados
- zone_distribution: JSON, distribución de impactos por zona
- impact_coordinates: JSON, coordenadas de los impactos
- analysis_confidence: Float, confianza del análisis
- analysis_method: String, método de análisis utilizado
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización



## SHOOTING_RECOMMENDATIONS
Recomendaciones generadas a partir de los análisis de tiro.
Campos:
- id: UUID, identificador único (PK)
- analysis_id: UUID, referencia a TARGET_ANALYSES
- primary_issue_zone: String, zona principal de error
- primary_issue_zone_description: String, descripción de la zona principal de error
- secondary_issue_zone: String, zona secundaria de error
- secondary_issue_zone_description: String, descripción de la zona secundaria de error
- recommended_exercises: JSON, ejercicios recomendados
- recommendation_description: String, descripción de la recomendación
- created_at: DateTime, fecha de creación
- updated_at: DateTime, fecha de última actualización
