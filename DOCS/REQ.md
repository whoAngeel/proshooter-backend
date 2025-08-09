# Documento de Requisitos del Sistema



## Requerimientos Funcionales

| ID    | Requerimiento Funcional |
|-------|-----------------------------------------------------------------------------------------------------------------------------------|
| RF-01 | El sistema deberá permitir el registro de usuarios, asignando uno de los siguientes roles: Tirador, Instructor, Jefe de Instructor o Administrador. |
| RF-02 | El sistema deberá almacenar información personal de los usuarios, incluyendo nombre, dirección, teléfono y otros datos relevantes. |
| RF-03 | El sistema deberá almacenar datos biométricos y médicos de los usuarios, tales como peso, altura, tipo de sangre y alergias. |
| RF-04 | El sistema deberá permitir la promoción de usuarios entre roles, de Tirador a Instructor y de Instructor a Jefe de Instructor, bajo las reglas de negocio definidas. |
| RF-05 | El sistema deberá permitir que un usuario con rol de Jefe de Instructor cree y administre clubes de tiro. |
| RF-06 | El sistema deberá permitir que el Jefe de Instructor, como propietario de un club, agregue tiradores a su club. |
| RF-07 | El sistema deberá permitir a los tiradores crear sesiones de práctica individuales, seleccionando el tipo de ejercicios a realizar (precisión, reacción, etc.). |
| RF-08 | El sistema deberá permitir la asignación de un instructor evaluador a una sesión individual, mostrando únicamente los instructores disponibles del mismo club. |
| RF-09 | El sistema deberá validar que, para solicitar evaluación de una sesión, el tirador pertenezca a un club y existan instructores disponibles en dicho club. |
| RF-10 | El sistema deberá garantizar que el instructor evaluador asignado pertenezca al mismo club que el tirador. |
| RF-11 | El sistema deberá permitir al instructor visualizar las sesiones pendientes de evaluación que le han sido asignadas. |
| RF-12 | El sistema deberá permitir al instructor evaluar una sesión, accediendo a todos los datos, ejercicios, análisis e imágenes asociados. |
| RF-13 | Al completar la evaluación de una sesión, el sistema deberá actualizar automáticamente las estadísticas del tirador evaluado. |
| RF-14 | El sistema deberá capturar y analizar los patrones de disparo de cada ejercicio realizado en una sesión. |
| RF-15 | El sistema deberá mantener un catálogo de armas disponibles para las prácticas y establecer compatibilidad entre armas y tipos de munición. |
| RF-16 | El sistema deberá registrar y contabilizar la munición utilizada por cada tirador en cada sesión. |
| RF-17 | El sistema deberá consolidar y validar los ejercicios antes de permitir la finalización de una sesión. |
| RF-18 | El sistema deberá permitir la reapertura de sesiones bajo condiciones controladas y según reglas de negocio. |
| RF-19 | El sistema deberá calcular y mostrar estadísticas avanzadas del tirador, incluyendo puntuación, precisión, tendencias y promedios por tipo de ejercicio. |
| RF-20 | El sistema deberá permitir la exportación y consulta de reportes históricos de desempeño de los tiradores. |
| RF-21 | La aplicación debe estar desarrollada en React y optimizada para dispositivos móviles. |
| RF-22 | El frontend debe consumir los servicios REST del backend para todas las operaciones de usuario, sesiones, evaluaciones y reportes. |
| RF-23 | La interfaz debe permitir el registro, autenticación y gestión de usuarios según su rol. |
| RF-24 | El frontend debe mostrar formularios y flujos para la creación y evaluación de sesiones, visualización de estadísticas y reportes. |
| RF-25 | La aplicación debe mostrar solo las opciones y vistas permitidas según el rol del usuario autenticado. |
| RF-26 | El frontend debe permitir la carga y visualización de imágenes asociadas a ejercicios y evaluaciones. |
| RF-27 | La aplicación debe ser desplegada en AWS Amplify y estar disponible mediante HTTPS. |
| RF-28 | El sistema debe permitir el entrenamiento y actualización del modelo de detección de impactos (YOLO) a partir de nuevos datasets etiquetados, cuando sea requerido. |
| RF-29 | El sistema debe integrar el modelo de detección de impactos y exponer su funcionalidad mediante la API para consumo de otros módulos. |




## Requerimientos No Funcionales

| ID      | Requerimiento No Funcional |
|---------|----------------------------------------------------------------------------------------------------------------------------------|
| RNF-01  | El sistema debe operar en un entorno dockerizado. |
| RNF-02  | El despliegue debe realizarse mediante un flujo CI/CD automatizado en una instancia EC2 de AWS. |
| RNF-03  | El sistema debe garantizar la seguridad y confidencialidad de los datos personales, médicos y biométricos. |
| RNF-04  | El sistema debe permitir el acceso a través de diferentes dispositivos. |
| RNF-05  | La API debe implementar autenticación y autorización basada en roles. |
| RNF-06  | El sistema debe implementar logs estructurados para monitoreo y diagnóstico de errores. |
| RNF-07  | El sistema debe ser escalable y soportar paginación y filtros en las consultas. |
| RNF-08  | El sistema debe permitir backup y restauración de la base de datos. |
| RNF-09  | La documentación de la API y del sistema debe estar disponible y actualizada. |
| RNF-10  | El backend debe permitir solicitudes CORS desde el dominio del frontend desplegado en AWS Amplify. |
| RNF-11  | La aplicación debe ser responsive y funcionar correctamente en dispositivos móviles. |
| RNF-12  | El frontend debe integrarse con el backend mediante CORS seguro y autenticación JWT. |
| RNF-13  | El despliegue debe realizarse de forma automatizada en AWS Amplify. |
| RNF-14  | La interfaz debe ser intuitiva y accesible para todos los roles de usuario. |


## Requerimientos de Datos

| ID     | Requerimiento |
|--------|----------------------------------------------------------------------------------------------------------------------------------|
| RD-01  | El sistema debe almacenar el historial completo de prácticas y evaluaciones de cada tirador. |
| RD-02  | El sistema debe mantener estadísticas actualizadas de desempeño por tirador. |
| RD-03  | El sistema debe almacenar datos de manera que se puedan realizar análisis estadísticos y reportes históricos. |

---
