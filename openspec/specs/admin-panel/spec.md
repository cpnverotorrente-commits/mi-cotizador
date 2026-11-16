# admin-panel Specification

## Purpose
Da a los administradores un panel dentro de Mi Cotizador para ver las cuentas de usuario, activarlas o desactivarlas y resetear sus contraseñas.

## Requirements

### Requirement: Panel solo para admins
Tras iniciar sesión, la aplicación SHALL mostrar el panel de administración si el usuario es admin, y el conversor si es un usuario común, que SHALL NOT ver ni poder abrir el panel.

#### Scenario: Login de admin
- **WHEN** inicia sesión un usuario con rol admin
- **THEN** se muestra el panel de administración

#### Scenario: Login de usuario común
- **WHEN** inicia sesión un usuario con rol usuario
- **THEN** se abre el conversor, sin acceso al panel

### Requirement: Listado de cuentas
El panel SHALL listar todas las cuentas con su email, rol y estado (activa o desactivada), y SHALL ofrecer una acción para actualizar la lista.

#### Scenario: Ver cuentas
- **WHEN** el admin abre el panel
- **THEN** ve una fila por cuenta con email, rol y estado

### Requirement: Activar y desactivar cuentas
El panel SHALL permitir al admin desactivar una cuenta activa y reactivar una desactivada, pidiendo confirmación antes de desactivar, y SHALL NOT permitir que el admin desactive su propia cuenta.

#### Scenario: Desactivar una cuenta
- **WHEN** el admin selecciona una cuenta ajena activa, pulsa "Desactivar" y confirma
- **THEN** la cuenta queda desactivada y la lista lo refleja

#### Scenario: Reactivar una cuenta
- **WHEN** el admin selecciona una cuenta desactivada y pulsa "Activar"
- **THEN** la cuenta queda activa y puede volver a iniciar sesión

#### Scenario: Desactivarse a sí mismo
- **WHEN** el admin selecciona su propia cuenta
- **THEN** la acción de desactivar no está disponible o se rechaza con un mensaje

### Requirement: Resetear contraseña
El panel SHALL permitir al admin establecer una contraseña nueva para la cuenta seleccionada, validando un mínimo de 8 caracteres y la confirmación, y la contraseña anterior SHALL dejar de funcionar.

#### Scenario: Reseteo exitoso
- **WHEN** el admin selecciona una cuenta, ingresa una contraseña nueva válida con su confirmación y acepta
- **THEN** la cuenta pasa a usar la nueva contraseña y la anterior ya no inicia sesión

#### Scenario: Contraseña inválida
- **WHEN** la contraseña nueva tiene menos de 8 caracteres o no coincide con su confirmación
- **THEN** se muestra un mensaje de error y la contraseña de la cuenta no cambia

### Requirement: Acciones sin selección
El panel SHALL deshabilitar o rechazar las acciones de desactivar, activar y resetear cuando no hay una cuenta seleccionada.

#### Scenario: Sin selección
- **WHEN** no hay ninguna cuenta seleccionada
- **THEN** las acciones sobre cuentas no se pueden ejecutar

### Requirement: Navegación del admin
El panel SHALL ofrecer abrir el conversor, volver al panel desde él y cerrar sesión.

#### Scenario: Ir al conversor y volver
- **WHEN** el admin pulsa "Abrir conversor" y luego "Volver al panel"
- **THEN** ve el conversor y después el panel, sin volver a iniciar sesión

### Requirement: Errores del servicio
Si PocketBase no responde o rechaza una acción, el panel SHALL mostrar un mensaje claro sin cerrarse y sin dar por hecho un cambio que no se aplicó.

#### Scenario: Servidor apagado
- **WHEN** PocketBase no está disponible al desactivar o resetear una cuenta
- **THEN** se muestra un mensaje de error y el estado de la cuenta en la lista no cambia
