# Spec Delta

## Purpose

Permite distribuir y usar Mi Cotizador en Windows como un único ejecutable, sin que el usuario tenga que instalar Python.

## ADDED Requirements

### Requirement: Ejecutable de Windows
El proyecto SHALL producir un archivo `MiCotizador.exe` que se ejecute en Windows 10 con doble clic, sin Python instalado.

#### Scenario: Ejecución sin Python
- **WHEN** el usuario hace doble clic en `MiCotizador.exe` en una máquina sin Python
- **THEN** se abre la ventana de Mi Cotizador

### Requirement: Sin ventana de consola
El ejecutable SHALL abrirse solo con la ventana de la aplicación, sin consola de comandos.

#### Scenario: Apertura limpia
- **WHEN** el usuario abre `MiCotizador.exe`
- **THEN** no aparece ninguna ventana de consola

### Requirement: Construcción reproducible
El proyecto SHALL incluir un comando o script documentado que genere el ejecutable desde el código fuente.

#### Scenario: Reconstrucción
- **WHEN** el usuario ejecuta el script de construcción
- **THEN** se genera `dist/MiCotizador.exe`
