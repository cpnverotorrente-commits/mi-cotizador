# Spec Delta

## Purpose

Guarda cada conversión de Mi Cotizador en PocketBase a nombre del usuario que la hizo, y garantiza que cada usuario vea únicamente su propio historial.

## ADDED Requirements

### Requirement: Registro de cada conversión
La aplicación SHALL guardar en PocketBase, por cada conversión exitosa, una consulta con el usuario con sesión iniciada, el monto en pesos, la cotización, el resultado en dólares y la fecha y hora de creación.

#### Scenario: Conversión exitosa
- **WHEN** un usuario con sesión iniciada convierte 100000 con cotización 1000
- **THEN** se crea una consulta a su nombre con monto 100000, cotización 1000, resultado 100 y la fecha y hora del momento

#### Scenario: Conversión inválida
- **WHEN** la validación rechaza las entradas
- **THEN** no se crea ninguna consulta

### Requirement: Fecha y hora fijadas por el servidor
La fecha y hora de cada consulta SHALL ser asignada por PocketBase al crearla, sin que el cliente pueda indicarla.

#### Scenario: Fecha del servidor
- **WHEN** se crea una consulta
- **THEN** su fecha y hora corresponde al momento de creación en el servidor

### Requirement: Sin historial.txt
La aplicación SHALL NOT escribir ni leer `historial.txt`.

#### Scenario: Después de convertir
- **WHEN** un usuario hace una conversión
- **THEN** no se crea ni se modifica `historial.txt`

### Requirement: Fallo al guardar la consulta
Si la consulta no puede guardarse en PocketBase, la aplicación SHALL mostrar igualmente el resultado y avisar que no se guardó en el historial.

#### Scenario: PocketBase no disponible al convertir
- **WHEN** PocketBase no responde y el usuario convierte un monto válido
- **THEN** se muestra el resultado y un aviso de que la consulta no se guardó

### Requirement: Cada usuario ve solo su historial
PocketBase SHALL devolver a cada usuario únicamente las consultas que le pertenecen, también cuando el usuario es admin, y SHALL NOT devolver ninguna consulta a quien no tiene sesión.

#### Scenario: Dos usuarios
- **WHEN** el usuario A y el usuario B tienen consultas y A consulta la lista
- **THEN** recibe solo las consultas de A

#### Scenario: Admin
- **WHEN** un admin consulta la lista de consultas
- **THEN** recibe solo las suyas

#### Scenario: Sin sesión
- **WHEN** alguien sin sesión consulta la lista
- **THEN** no recibe ninguna consulta

### Requirement: Crear consultas solo a nombre propio
PocketBase SHALL permitir crear una consulta solo a un usuario con sesión iniciada y solo a su propio nombre.

#### Scenario: Consulta a nombre de otro
- **WHEN** el usuario A intenta crear una consulta indicando como usuario a B
- **THEN** PocketBase rechaza la solicitud

#### Scenario: Sin sesión
- **WHEN** alguien sin sesión intenta crear una consulta
- **THEN** PocketBase rechaza la solicitud

### Requirement: Consultas inmutables
PocketBase SHALL impedir que los usuarios, incluidos los admins, modifiquen o borren consultas.

#### Scenario: Editar o borrar
- **WHEN** un usuario intenta modificar o borrar una de sus consultas por la API
- **THEN** PocketBase rechaza la solicitud

### Requirement: Pantalla de historial propio
La aplicación SHALL ofrecer, desde el conversor, una pantalla "Mi historial" con la fecha y hora (en hora local), el monto, la cotización y el resultado de las consultas del usuario, las más recientes primero, y un modo de volver al conversor.

#### Scenario: Ver el historial
- **WHEN** el usuario abre "Mi historial"
- **THEN** ve una fila por consulta propia, ordenadas de la más reciente a la más antigua

#### Scenario: Historial vacío
- **WHEN** un usuario sin consultas abre "Mi historial"
- **THEN** ve un mensaje de que todavía no hizo conversiones

#### Scenario: Servidor apagado
- **WHEN** PocketBase no está disponible al abrir el historial
- **THEN** se muestra un mensaje de error y el usuario puede volver al conversor

### Requirement: Configuración reproducible
El script de configuración de PocketBase SHALL crear la colección de consultas con sus campos y reglas, y poder ejecutarse varias veces sin duplicarla ni romper nada.

#### Scenario: Ejecutar el script dos veces
- **WHEN** el script se ejecuta por segunda vez
- **THEN** termina sin errores y la colección queda igual
