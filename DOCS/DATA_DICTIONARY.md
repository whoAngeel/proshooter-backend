
# Diccionario de Datos

Este diccionario describe las entidades principales de la base de datos del sistema Proshooter, sus campos clave y relaciones.

---



## USERS
Contiene la información principal de los usuarios del sistema.

| Campo            | Tipo    | Descripción                                      |
|------------------|---------|--------------------------------------------------|
| id               | UUID    | Identificador único (PK)                         |
| email            | String  | Correo electrónico                               |
| hashed_password  | String  | Contraseña encriptada                            |
| role             | Enum    | Rol del usuario (admin, shooter, instructor, etc.)|
| is_active        | Boolean | Indica si el usuario está activo                 |





## USER_PERSONAL_DATA
Datos personales asociados a cada usuario.

| Campo           | Tipo   | Descripción                        |
|-----------------|--------|------------------------------------|
| user_id         | UUID   | Referencia a USERS (PK)            |
| first_name      | String | Nombre(s)                          |
| last_name       | String | Apellidos                          |
| birth_date      | Date   | Fecha de nacimiento                |
| gender          | Enum   | Género (M/F/Otro)                  |
| nationality     | String | Nacionalidad                       |
| document_type   | String | Tipo de documento de identidad     |
| document_number | String | Número de documento                |
| phone           | String | Teléfono de contacto               |
| address         | String | Dirección de residencia            |





## USER_MEDICAL_DATA
Datos médicos relevantes del usuario.

| Campo                  | Tipo   | Descripción                        |
|------------------------|--------|------------------------------------|
| user_id                | UUID   | Referencia a USERS (PK)            |
| blood_type             | String | Tipo de sangre                     |
| allergies              | String | Alergias conocidas                 |
| medical_conditions     | String | Condiciones médicas relevantes     |
| emergency_contact_name | String | Nombre del contacto de emergencia  |
| emergency_contact_phone| String | Teléfono del contacto de emergencia|





## USER_BIOMETRIC_DATA
Datos biométricos del usuario.

| Campo                | Tipo    | Descripción                        |
|----------------------|---------|------------------------------------|
| user_id              | UUID    | Referencia a USERS (PK)            |
| height_cm            | Integer | Estatura en centímetros            |
| weight_kg            | Integer | Peso en kilogramos                 |
| eye_color            | String  | Color de ojos                      |
| hair_color           | String  | Color de cabello                   |
| body_fat_percentage  | Float   | Porcentaje de grasa corporal       |
| bmi                  | Float   | Índice de masa corporal            |







## SHOOTERS
Usuarios registrados como tiradores.

| Campo        | Tipo    | Descripción                                 |
|--------------|---------|---------------------------------------------|
| user_id      | UUID    | Referencia a USERS (PK)                     |
| club_id      | UUID    | Referencia a SHOOTING_CLUBS                 |
| level        | Enum    | Nivel del tirador (ver ShooterLevelEnum)    |
| range        | String  | Rango/categoría del tirador                 |
| nickname     | String  | Apodo único del tirador                     |
| license_file | String  | Archivo de licencia (ruta/URL)              |
| created_at   | DateTime| Fecha de creación                           |
| updated_at   | DateTime| Fecha de última actualización               |





## SHOOTER_STATS
Estadísticas de rendimiento de cada tirador.

| Campo                         | Tipo    | Descripción                                         |
|-------------------------------|---------|-----------------------------------------------------|
| shooter_id                    | UUID    | Referencia a SHOOTERS (PK)                          |
| total_shots                   | Integer | Total de disparos realizados                        |
| accuracy                      | Integer | Porcentaje de precisión                             |
| reaction_shots                | Integer | Cantidad de disparos de reacción                    |
| presicion_shots               | Integer | Cantidad de disparos de precisión                   |
| draw_time_avg                 | Float   | Tiempo promedio de desenfunde                       |
| reload_time_avg               | Float   | Tiempo promedio de recarga                          |
| average_hit_factor            | Float   | Hit factor promedio                                 |
| effectiveness                 | Float   | Efectividad general                                 |
| trend_accuracy                | Float   | Tendencia de precisión                              |
| last_10_sessions_avg          | Float   | Promedio de las últimas 10 sesiones                 |
| precision_exercise_accuracy   | Float   | Precisión en ejercicios de precisión                |
| reaction_exercise_accuracy    | Float   | Precisión en ejercicios de reacción                 |
| movement_exercise_accuracy    | Float   | Precisión en ejercicios de movimiento               |
| average_score                 | Float   | Puntuación promedio general                         |
| best_score_session            | Integer | Mejor puntuación en una sesión                      |
| best_shot_ever                | Integer | Mejor disparo registrado                            |
| score_trend                   | Float   | Tendencia de puntuación                             |
| precision_exercise_avg_score  | Float   | Promedio de puntuación en ejercicios de precisión   |
| reaction_exercise_avg_score   | Float   | Promedio de puntuación en ejercicios de reacción    |
| movement_exercise_avg_score   | Float   | Promedio de puntuación en ejercicios de movimiento  |
| common_error_zones            | String  | Zonas comunes de error                              |
| created_at                    | DateTime| Fecha de creación                                   |
| updated_at                    | DateTime| Fecha de última actualización                       |






## SHOOTING_CLUBS
Clubes de tiro registrados en el sistema.

| Campo               | Tipo    | Descripción                                 |
|---------------------|---------|---------------------------------------------|
| id                  | UUID    | Identificador único (PK)                    |
| name                | String  | Nombre único del club                       |
| description         | String  | Descripción del club                        |
| chief_instructor_id | UUID    | Referencia a USERS (instructor jefe)        |
| is_active           | Boolean | Indica si el club está activo               |
| created_at          | DateTime| Fecha de creación                           |
| updated_at          | DateTime| Fecha de última actualización               |





## INDIVIDUAL_PRACTICE_SESSIONS
Sesiones individuales de práctica de tiro.

| Campo                      | Tipo     | Descripción                                                                 |
|----------------------------|----------|-----------------------------------------------------------------------------|
| id                         | UUID     | Identificador único (PK)                                                    |
| shooter_id                 | UUID     | Referencia a SHOOTERS                                                       |
| instructor_id              | UUID     | Referencia a USERS (puede ser nulo)                                         |
| date                       | DateTime | Fecha de la sesión                                                          |
| location                   | String   | Ubicación de la sesión                                                      |
| total_shots_fired          | Integer  | Total de disparos realizados                                                |
| total_hits                 | Integer  | Total de impactos                                                           |
| accuracy_percentage        | Float    | Porcentaje de aciertos                                                      |
| evaluation_pending         | Boolean  | Indica si la sesión está pendiente de evaluación                            |
| is_finished                | Boolean  | Indica si la sesión está finalizada                                         |
| total_session_score        | Integer  | Puntuación total de la sesión                                               |
| average_score_per_exercise | Float    | Puntuación promedio por ejercicio                                           |
| average_score_per_shot     | Float    | Puntuación promedio por disparo                                             |
| best_shot_score            | Integer  | Mejor disparo de la sesión                                                  |
| session_score_efficiency   | Float    | Eficiencia de puntuación (%) (calculada: total_session_score / (total_shots_fired * 10) * 100) |
| created_at                 | DateTime | Fecha de creación                                                           |
| updated_at                 | DateTime | Fecha de última actualización                                               |





## PRACTICE_EXERCISES
Ejercicios realizados dentro de una sesión de práctica.

| Campo                    | Tipo     | Descripción                                                                 |
|--------------------------|----------|-----------------------------------------------------------------------------|
| id                       | UUID     | Identificador único (PK)                                                    |
| session_id               | UUID     | Referencia a INDIVIDUAL_PRACTICE_SESSIONS                                   |
| exercise_type_id         | UUID     | Referencia a EXERCISE_TYPES                                                 |
| target_id                | UUID     | Referencia a TARGETS                                                        |
| weapon_id                | UUID     | Referencia a WEAPONS                                                        |
| ammunition_id            | UUID     | Referencia a AMMUNITION                                                     |
| distance                 | String   | Distancia al blanco (en metros)                                             |
| firing_cadence           | String   | Cadencia de disparo (puede ser nulo)                                        |
| time_limit               | String   | Límite de tiempo (puede ser nulo)                                           |
| ammunition_allocated     | Integer  | Munición asignada                                                           |
| ammunition_used          | Integer  | Munición utilizada                                                          |
| hits                     | Integer  | Impactos logrados                                                           |
| accuracy_percentage      | Float    | Porcentaje de aciertos                                                      |
| reaction_time            | Float    | Tiempo de reacción (puede ser nulo)                                         |
| total_score              | Float    | Puntuación total del ejercicio                                              |
| average_score_per_shot   | Float    | Puntuación promedio por disparo                                             |
| max_score_achieved       | Integer  | Mejor puntuación individual                                                 |
| score_distribution       | String   | Distribución de puntuación por zonas (JSON, puede ser nulo)                 |
| group_diameter           | Float    | Diámetro del grupo de disparos (píxeles, puede ser nulo)                    |
| target_image_id          | UUID     | Referencia a TARGET_IMAGES (puede ser nulo)                                 |
| created_at               | DateTime | Fecha de creación                                                           |
| updated_at               | DateTime | Fecha de última actualización                                               |
| score_efficiency_percentage | Float | Eficiencia de puntuación (%) (calculada: total_score / (ammunition_used * 10) * 100) |





## PRACTICE_EVALUATIONS
Evaluaciones realizadas sobre una sesión de práctica.

| Campo                   | Tipo     | Descripción                                         |
|-------------------------|----------|-----------------------------------------------------|
| id                      | UUID     | Identificador único (PK)                            |
| session_id              | UUID     | Referencia a INDIVIDUAL_PRACTICE_SESSIONS           |
| evaluator_id            | UUID     | Referencia a USERS (puede ser nulo)                 |
| final_score             | Float    | Calificación general                                |
| classification          | Enum     | Clasificación del tirador (ShooterLevelEnum)        |
| strengths               | String   | Fortalezas observadas (puede ser nulo)              |
| weaknesses              | String   | Debilidades observadas (puede ser nulo)             |
| recomendations          | String   | Recomendaciones (puede ser nulo)                    |
| overall_technique_rating| Float    | Calificación técnica global (puede ser nulo)        |
| instructor_notes        | String   | Notas del instructor (puede ser nulo)               |
| primary_issue_zone      | String   | Zona principal de error (puede ser nulo)            |
| secondary_issue_zone    | String   | Zona secundaria de error (puede ser nulo)           |
| avg_reaction_time       | Float    | Tiempo promedio de reacción (puede ser nulo)        |
| avg_draw_time           | Float    | Tiempo promedio de desenfunde (puede ser nulo)      |
| avg_reload_time         | Float    | Tiempo promedio de recarga (puede ser nulo)         |
| hit_factor              | Float    | Puntos/tiempo (métrica IPSC, puede ser nulo)        |
| date                    | DateTime | Fecha de la evaluación                              |
| created_at              | DateTime | Fecha de creación                                   |
| updated_at              | DateTime | Fecha de última actualización                       |





## EXERCISE_TYPES
Tipos de ejercicios disponibles.

| Campo        | Tipo      | Descripción                           |
|--------------|-----------|---------------------------------------|
| id           | UUID      | Identificador único (PK)              |
| name         | String    | Nombre del tipo de ejercicio          |
| description  | String    | Descripción del ejercicio             |
| difficulty   | Integer   | Dificultad del ejercicio              |
| objective    | String    | Objetivo del ejercicio                |
| development  | String    | Desarrollo o instrucciones            |
| is_active    | Boolean   | Indica si el tipo de ejercicio está activo |
| created_at   | DateTime  | Fecha de creación                     |
| updated_at   | DateTime  | Fecha de última actualización         |




## WEAPONS
Armas registradas en el sistema.

| Campo         | Tipo    | Descripción                              |
|---------------|---------|------------------------------------------|
| id            | UUID    | Identificador único (PK)                 |
| name          | String  | Nombre del arma                         |
| brand         | String  | Marca del arma                          |
| model         | String  | Modelo del arma                         |
| serial_number | String  | Número de serie (único)                 |
| weapon_type   | Enum    | Tipo de arma (ver WeaponTypeEnum)       |
| caliber       | String  | Calibre                                 |
| description   | String  | Descripción adicional                   |
| is_active     | Boolean | Indica si el arma está activa           |
| created_at    | DateTime| Fecha de creación                       |
| updated_at    | DateTime| Fecha de última actualización           |




## AMMUNITION
Municiones registradas en el sistema.

| Campo          | Tipo    | Descripción                              |
|----------------|---------|------------------------------------------|
| id             | UUID    | Identificador único (PK)                 |
| name           | String  | Nombre de la munición                    |
| brand          | String  | Marca de la munición                     |
| caliber        | String  | Calibre                                  |
| ammo_type      | Enum    | Tipo de munición (ver AmmoType)          |
| grain_weight   | Float   | Peso en granos                           |
| velocity       | Float   | Velocidad en pies por segundo            |
| description    | String  | Descripción adicional                    |
| price_per_round| Float   | Precio por unidad                        |
| is_active      | Boolean | Indica si la munición está activa        |
| created_at     | DateTime| Fecha de creación                        |
| updated_at     | DateTime| Fecha de última actualización            |




## WEAPON_AMMUNITION_COMPATIBILITY
Compatibilidad entre armas y municiones.

| Campo         | Tipo    | Descripción                        |
|---------------|---------|------------------------------------|
| id            | UUID    | Identificador único (PK)           |
| weapon_id     | UUID    | Referencia a WEAPONS               |
| ammunition_id | UUID    | Referencia a AMMUNITION            |
| created_at    | DateTime| Fecha de creación                  |




## TARGETS
Blancos utilizados en los ejercicios.

| Campo                | Tipo    | Descripción                                 |
|----------------------|---------|---------------------------------------------|
| id                   | UUID    | Identificador único (PK)                    |
| name                 | String  | Nombre del blanco                           |
| target_type          | Enum    | Tipo de blanco (ver TargetType)             |
| description          | String  | Descripción del blanco                      |
| scoring_zones        | JSON    | Configuración de zonas de puntuación        |
| dimensions           | String  | Dimensiones físicas (ancho x alto)          |
| distance_recommended | Float   | Distancia recomendada en metros             |
| is_active            | Boolean | Indica si el blanco está activo             |
| created_at           | DateTime| Fecha de creación                           |
| updated_at           | DateTime| Fecha de última actualización               |




## TARGET_IMAGES
Imágenes de los blancos generadas durante los ejercicios.

| Campo        | Tipo     | Descripción                                 |
|--------------|----------|---------------------------------------------|
| id           | UUID     | Identificador único (PK)                    |
| exercise_id  | UUID     | Referencia a PRACTICE_EXERCISES             |
| file_path    | String   | Ruta del archivo de imagen                  |
| file_size    | Integer  | Tamaño del archivo (bytes)                  |
| content_type | String   | Tipo de contenido (MIME)                    |
| uploaded_at  | DateTime | Fecha y hora de carga                       |
| created_at   | DateTime | Fecha de creación                           |
| updated_at   | DateTime | Fecha de última actualización               |


## TARGET_ANALYSES
Análisis realizados sobre imágenes de blancos detectados.

| Campo                      | Tipo     | Descripción                                                                 |
|----------------------------|----------|-----------------------------------------------------------------------------|
| id                         | UUID     | Identificador único (PK)                                                    |
| target_image_id            | UUID     | Referencia a TARGET_IMAGES                                                  |
| analysis_timestamp         | DateTime | Fecha y hora del análisis                                                   |
| total_impacts_detected     | Integer  | Total de impactos detectados                                                |
| fresh_impacts_inside       | Integer  | Impactos frescos dentro del blanco                                          |
| fresh_impacts_outside      | Integer  | Impactos frescos fuera del blanco                                           |
| covered_impacts_inside     | Integer  | Impactos cubiertos dentro del blanco                                        |
| covered_impacts_outside    | Integer  | Impactos cubiertos fuera del blanco                                         |
| accuracy_percentage        | Float    | Porcentaje de precisión (calculado)                                         |
| average_confidence         | Float    | Confianza promedio de detección                                             |
| impact_coordinates         | JSON     | Coordenadas de los impactos detectados                                      |
| zone_distribution          | JSON     | Distribución de impactos por zona (opcional)                                |
| confidence_stats           | JSON     | Estadísticas de confianza de los impactos                                   |
| analysis_method            | String   | Método de análisis utilizado (ej: YOLO_v8)                                  |
| model_version              | String   | Versión del modelo de análisis                                              |
| confidence_threshold       | Float    | Umbral de confianza utilizado                                               |
| total_score                | Integer  | Puntuación total obtenida                                                   |
| average_score_per_shot     | Float    | Puntuación promedio por disparo                                             |
| max_score_achieved         | Integer  | Mejor puntuación individual                                                 |
| score_distribution         | JSON     | Distribución de puntuación por zonas (ej: {"10": 2})                      |
| shooting_group_diameter    | Float    | Diámetro del grupo de disparos (opcional)                                   |
| group_center_x             | Float    | Coordenada X del centro del grupo (opcional)                                |
| group_center_y             | Float    | Coordenada Y del centro del grupo (opcional)                                |
| created_at                 | DateTime | Fecha de creación                                                           |
| updated_at                 | DateTime | Fecha de última actualización                                               |
| score_efficiency_percentage| Float    | Eficiencia de puntuación (%) (calculada: total_score / (fresh_shots_count * 10) * 100) |
| has_scoring_data           | Boolean  | Indica si el análisis tiene datos de puntuación (calculado)                 |
| group_center               | JSON     | Centro del grupo como diccionario {"x": float, "y": float} (calculado)   |


## SHOOTING_RECOMMENDATIONS
Recomendaciones generadas a partir de los análisis de tiro.

| Campo                         | Tipo    | Descripción                                 |
|-------------------------------|---------|---------------------------------------------|
| id                            | UUID    | Identificador único (PK)                    |
| analysis_id                   | UUID    | Referencia a TARGET_ANALYSES                |
| primary_issue_zone            | String  | Zona principal de error                     |
| primary_issue_zone_description| String  | Descripción de la zona principal de error    |
| secondary_issue_zone          | String  | Zona secundaria de error                    |
| secondary_issue_zone_description | String| Descripción de la zona secundaria de error  |
| recommended_exercises         | JSON    | Ejercicios recomendados                     |
| recommendation_description    | String  | Descripción de la recomendación             |
| created_at                    | DateTime| Fecha de creación                           |
| updated_at                    | DateTime| Fecha de última actualización               |
