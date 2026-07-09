# Sistema Web para la Gestión de Reservas de Espacios Académicos

🌎 **Language / Idioma**

🇪🇸 Español | 🇺🇸 [English](README.en.md)

Sistema web desarrollado como **Proyecto de Grado** para optar al título de Ingeniería de Sistemas en la **Universidad Autónoma del Beni "José Ballivián" (UABJB)**, Facultad de Ingeniería y Tecnología.

El sistema automatiza el proceso de solicitud, aprobación y control de reservas del **Salón Bicentenario** y la **Sala Audiovisual** del Campus Universitario "Hernán Melgar Justiniano", en Trinidad, Beni, Bolivia.

**Autora:** Carmen Mirna Ibañez Sanguino
**Tutores:** Ing. Johnny Rosas Callaú · Lic. William Chao Rivero
**Fecha:** Noviembre de 2025

---

## Descripción

Actualmente la gestión de espacios académicos compartidos se realiza de forma manual, generando duplicidad de solicitudes, falta de trazabilidad y demoras en la aprobación. Este sistema centraliza el proceso mediante una plataforma web accesible para tres perfiles de usuario, garantizando trazabilidad completa de las operaciones y una experiencia de usuario más ágil.

## Objetivo General

Desarrollar un sistema web escalable, transparente y mantenible para la gestión eficiente de reservas del Salón Bicentenario y la Sala Audiovisual de la Facultad de Ingeniería y Tecnología de la U.A.B.J.B., optimizando el proceso de solicitud, aprobación y control de reservas mediante automatización.

## Módulos del Sistema

El sistema está organizado en seis módulos principales:

- **Módulo de Seguridad** — Autenticación, autorización y control de acceso basado en roles (administrador, encargado, usuario regular).
- **Módulo de Gestión de Usuarios** — Registro autónomo, perfiles diferenciados y administración de información institucional.
- **Módulo de Gestión de Espacios Académicos** — Registro de facultades, carreras, espacios de campus y espacios de carrera, con asignación de encargados.
- **Módulo de Gestión de Solicitudes y Reservas** — Creación, modificación, aprobación y rechazo de solicitudes con validación automática de conflictos.
- **Módulo de Calendario y Notificaciones** — Visualización en tiempo real de disponibilidad y notificaciones automáticas por correo electrónico.
- **Módulo de Reportes** — Generación de informes estadísticos exportables en múltiples formatos.

## Perfiles de Usuario

- **Administrador del Sistema** — Configura la estructura organizativa: facultades, carreras, espacios y encargados.
- **Encargado de Espacios** — Aprueba o rechaza solicitudes de reserva y controla el uso de los espacios bajo su responsabilidad.
- **Usuario Solicitante** — Miembro de la comunidad universitaria que solicita reservas adjuntando la documentación requerida.

## 🛠️ Tecnologías

| Categoría | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Framework web | Django 4.2 (arquitectura MTV) |
| Base de datos | PostgreSQL 15 |
| Contenedorización | Docker / Docker Compose |
| Servidor de aplicación | Gunicorn |
| Archivos estáticos | WhiteNoise |
| Reportes | ReportLab, openpyxl, python-docx |
| Frontend | HTML, CSS, JavaScript |

## 📦 Requisitos Previos

- [Docker](https://www.docker.com/) y Docker Compose instalados
- Git

## 🚀 Instalación y Puesta en Marcha

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/carmenmirna-is/ProyectoGrado_GSA_UABJB.git
   cd ProyectoGrado_GSA_UABJB
   ```

2. Levantar los contenedores (base de datos PostgreSQL + servidor Django):
   ```bash
   docker-compose up --build
   ```

   Este comando aplica automáticamente las migraciones, recolecta los archivos estáticos y levanta el servidor de desarrollo.

3. Acceder a la aplicación en:
   ```
   http://localhost:8000
   ```

## Estructura del Proyecto

```
ProyectoGrado_GSA_UABJB/
├── administrador/                  # App: módulo de administración
├── encargados/                     # App: gestión de encargados de espacio
├── gestion_espacios_academicos/     # Configuración principal del proyecto Django
├── usuarios/                        # App: registro y perfiles de usuario
├── reportes/                         # App: generación de reportes
├── templates/                        # Plantillas HTML
├── static/ · staticfiles/            # Archivos estáticos (CSS, JS, imágenes)
├── media/                            # Archivos subidos por usuarios
├── assets/                           # Recursos del proyecto (capturas, etc.)
├── logs/                             # Registros del sistema
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

## Capturas de Pantalla

### Index
![Index](assets/Index.png)

### Inicio de sesión
![Login](assets/Login.png)

### Dashboard de Usuario
![DashboardUsuario](assets/DashboardUsuario.png)

### Dashboard de Encargado
![DashboardEncargado](assets/DashboardEncargado.png)

### Dashboard de Administrador del Sistema
![DashboardAdministrador](assets/DashboardAdministrador.png)

## Contexto Académico

Este proyecto corresponde al Proyecto de Grado presentado ante la Carrera de Ingeniería de Sistemas de la Facultad de Ingeniería y Tecnología, UABJB, como requisito para optar al título de Ingeniería de Sistemas (noviembre de 2025).

## Licencia

Este proyecto fue desarrollado con fines académicos como parte del proceso de titulación en la UABJB.