# Spec Delta

## REMOVED Requirements

### Requirement: Registro de cada conversión
**Reason**: El historial ya no se guarda en `historial.txt`; ahora cada conversión se registra en PocketBase a nombre del usuario.
**Migration**: Ver el requisito "Registro de cada conversión" de la capacidad `conversion-records`.

### Requirement: Historial acumulativo
**Reason**: Dejó de existir el archivo `historial.txt`; el historial se acumula en la colección `consultas` de PocketBase.
**Migration**: Ver `conversion-records`; las consultas se conservan en PocketBase entre ejecuciones.

### Requirement: Ubicación del historial
**Reason**: Ya no hay un archivo junto a la aplicación; los datos viven en PocketBase.
**Migration**: Ninguna; las consultas se leen desde "Mi historial" (capacidad `conversion-records`).

### Requirement: Fallo al escribir el historial
**Reason**: El fallo relevante ahora es no poder guardar en PocketBase, no escribir un archivo.
**Migration**: Ver el requisito "Fallo al guardar la consulta" de la capacidad `conversion-records`.
