# user-authentication Specification

## Purpose
Permite que solo usuarios registrados accedan al conversor de Mi Cotizador, gestionando el registro y el inicio de sesión contra los usuarios de PocketBase.

## Requirements

### Requirement: Pantalla de inicio de sesión al abrir
Al abrirse, la aplicación SHALL mostrar la pantalla de inicio de sesión, con campos de email y contraseña, un botón "Iniciar sesión" y un enlace para ir al registro, sin mostrar el conversor.

#### Scenario: Apertura de la aplicación
- **WHEN** el usuario abre Mi Cotizador
- **THEN** se muestra la pantalla de inicio de sesión y no el conversor

### Requirement: Inicio de sesión
La aplicación SHALL autenticar email y contraseña contra los usuarios de PocketBase y, si son correctos, cerrar la pantalla de inicio de sesión y abrir el conversor.

#### Scenario: Credenciales correctas
- **WHEN** el usuario ingresa el email y la contraseña de un usuario registrado y pulsa "Iniciar sesión"
- **THEN** se abre el conversor

#### Scenario: Credenciales incorrectas
- **WHEN** el usuario ingresa un email o una contraseña que no coinciden con ningún usuario
- **THEN** se muestra un mensaje de error de credenciales y el conversor no se abre

#### Scenario: Campos vacíos
- **WHEN** el usuario pulsa "Iniciar sesión" con el email o la contraseña vacíos
- **THEN** se muestra un mensaje pidiendo completar ambos campos y no se consulta a PocketBase

### Requirement: Pantalla de registro
La aplicación SHALL ofrecer una pantalla de registro con email, contraseña y confirmación de contraseña, accesible desde el inicio de sesión, con un enlace para volver a él.

#### Scenario: Ir al registro
- **WHEN** el usuario pulsa el enlace de registro en el inicio de sesión
- **THEN** se muestra la pantalla de registro

### Requirement: Registro de usuarios
La aplicación SHALL crear un usuario en PocketBase con el email y la contraseña ingresados, y tras el registro exitoso SHALL llevar al usuario al inicio de sesión con un mensaje de cuenta creada.

#### Scenario: Registro exitoso
- **WHEN** el usuario ingresa un email nuevo, una contraseña de 8 o más caracteres y la misma confirmación, y pulsa "Registrarme"
- **THEN** el usuario queda creado en PocketBase y se muestra el inicio de sesión con un mensaje de cuenta creada

#### Scenario: Email ya registrado
- **WHEN** el usuario intenta registrar un email que ya existe
- **THEN** se muestra un mensaje indicando que el email ya está en uso y no se crea otro usuario

### Requirement: Validación del registro
La aplicación SHALL rechazar el registro, sin consultar a PocketBase, cuando falta algún campo, el email no tiene formato válido, la contraseña tiene menos de 8 caracteres o la confirmación no coincide.

#### Scenario: Confirmación distinta
- **WHEN** la contraseña y su confirmación no coinciden
- **THEN** se muestra un mensaje de error y no se crea ningún usuario

#### Scenario: Contraseña corta
- **WHEN** la contraseña tiene menos de 8 caracteres
- **THEN** se muestra un mensaje indicando el mínimo requerido y no se crea ningún usuario

### Requirement: Conversor solo con sesión iniciada
La aplicación SHALL abrir el conversor únicamente tras un inicio de sesión exitoso, y SHALL ofrecer una acción "Cerrar sesión" que cierra el conversor y vuelve al inicio de sesión.

#### Scenario: Cerrar sesión
- **WHEN** el usuario pulsa "Cerrar sesión" en el conversor
- **THEN** se muestra el inicio de sesión y, para volver al conversor, se debe iniciar sesión otra vez

#### Scenario: Sesión no recordada
- **WHEN** el usuario cierra la aplicación y la vuelve a abrir
- **THEN** se muestra el inicio de sesión

### Requirement: PocketBase no disponible
Si no se puede contactar a PocketBase, la aplicación SHALL mostrar un mensaje claro de que el servicio no está disponible, sin abrir el conversor y sin cerrarse.

#### Scenario: Servidor apagado
- **WHEN** PocketBase no está corriendo y el usuario intenta iniciar sesión o registrarse
- **THEN** se muestra un mensaje de servicio no disponible y el usuario puede reintentar
