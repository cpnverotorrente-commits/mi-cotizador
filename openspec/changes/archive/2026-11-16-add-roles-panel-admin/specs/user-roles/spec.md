# Spec Delta

## Purpose

Distingue administradores de usuarios comunes y permite desactivar cuentas, haciendo que PocketBase imponga por sí mismo quién puede ver y modificar cuentas, sin depender de la aplicación de escritorio.

## ADDED Requirements

### Requirement: Rol de usuario
Cada usuario SHALL tener un rol, `usuario` o `admin`, y los usuarios sin rol definido SHALL tratarse como `usuario`.

#### Scenario: Registro de un usuario nuevo
- **WHEN** una persona se registra
- **THEN** su cuenta se crea con rol `usuario`

#### Scenario: Usuario existente sin rol
- **WHEN** inicia sesión un usuario creado antes de este cambio, sin rol
- **THEN** la aplicación lo trata como `usuario`

### Requirement: Estado activo de la cuenta
Cada usuario SHALL tener un estado activo o desactivado, y las cuentas nuevas SHALL crearse activas.

#### Scenario: Cuenta nueva
- **WHEN** una persona se registra
- **THEN** su cuenta queda activa

### Requirement: Cuentas desactivadas no inician sesión
PocketBase SHALL rechazar el inicio de sesión de una cuenta desactivada, y la aplicación SHALL mostrar un mensaje de que la cuenta está desactivada o las credenciales son incorrectas, sin abrir el conversor.

#### Scenario: Login de cuenta desactivada
- **WHEN** un usuario desactivado ingresa su email y contraseña correctos
- **THEN** no se inicia sesión y se muestra un mensaje de error

### Requirement: El registro no puede elegir rol ni estado
PocketBase SHALL rechazar un registro que incluya un valor de rol o de estado, para que nadie se cree como admin.

#### Scenario: Registro con rol admin forzado
- **WHEN** alguien llama a la API de registro enviando `rol` igual a `admin`
- **THEN** PocketBase rechaza la solicitud y no crea la cuenta

### Requirement: Un usuario común solo accede a su propia cuenta
Un usuario común SHALL poder ver y editar solamente su propio registro, y SHALL NOT poder cambiar su rol ni su estado.

#### Scenario: Listar cuentas como usuario común
- **WHEN** un usuario común consulta la lista de usuarios por la API
- **THEN** recibe solamente su propio registro

#### Scenario: Auto-promoción
- **WHEN** un usuario común intenta cambiar su propio rol a `admin`
- **THEN** PocketBase rechaza el cambio

#### Scenario: Modificar a otro usuario
- **WHEN** un usuario común intenta cambiar el estado o la contraseña de otra cuenta
- **THEN** PocketBase rechaza la solicitud

### Requirement: Un admin administra todas las cuentas
Un admin SHALL poder listar todas las cuentas, cambiar el estado de cualquiera y establecer una contraseña nueva para cualquiera.

#### Scenario: Listar como admin
- **WHEN** un admin consulta la lista de usuarios
- **THEN** recibe todas las cuentas con su email, rol y estado

#### Scenario: Cuentas sin autenticar
- **WHEN** alguien sin sesión consulta la lista de usuarios
- **THEN** PocketBase no devuelve ninguna cuenta

### Requirement: Configuración reproducible
El proyecto SHALL incluir un script que aplique el campo de rol, el campo de estado y las reglas a PocketBase y que cree o promueva un admin, y que pueda ejecutarse varias veces sin duplicar ni romper nada.

#### Scenario: Ejecutar el script dos veces
- **WHEN** el script se ejecuta por segunda vez sobre el mismo PocketBase
- **THEN** termina sin errores y deja la misma configuración
