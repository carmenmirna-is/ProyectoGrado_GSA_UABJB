# Web System for Academic Space Reservation Management
🌎 **Language / Language**

🇺🇸 English | 🇪🇸 [Español](README.md)

Web system developed as an **Undergraduate Capstone Project** to obtain the Bachelor's Degree in Systems Engineering at the **José Ballivián Autonomous University of Beni (UABJB)**, Faculty of Engineering and Technology.

The system automates the request, approval, and management process for reservations of the **Bicentennial Hall** and the **Audiovisual Room** at the "Hernán Melgar Justiniano" University Campus, located in Trinidad, Beni, Bolivia.

**Author:** Carmen Mirna Ibañez Sanguino  
**Advisors:** Eng. Johnny Rosas Callaú · Lic. William Chao Rivero  
**Date:** November 2025

---

## Description

Currently, the management of shared academic spaces is carried out manually, resulting in duplicate requests, lack of traceability, and delays in the approval process. This system centralizes the entire workflow through a web platform accessible to three different user profiles, ensuring complete traceability and a faster user experience.

## General Objective

Develop a scalable, transparent, and maintainable web system for the efficient management of reservations of the Bicentennial Hall and the Audiovisual Room at the Faculty of Engineering and Technology of UABJB, optimizing the reservation request, approval, and control process through automation.

## System Modules

The system is organized into six main modules:

- **Security Module** — Authentication, authorization, and role-based access control (administrator, manager, regular user).
- **User Management Module** — Self-registration, differentiated user profiles, and institutional information management.
- **Academic Space Management Module** — Registration of faculties, degree programs, campus facilities, and department spaces, including manager assignment.
- **Reservation Management Module** — Creation, modification, approval, and rejection of reservation requests with automatic conflict validation.
- **Calendar & Notification Module** — Real-time availability calendar and automatic email notifications.
- **Reporting Module** — Generation of statistical reports exportable to multiple formats.

## User Roles

- **System Administrator** — Configures the organizational structure, including faculties, degree programs, academic spaces, and space managers.
- **Space Manager** — Approves or rejects reservation requests and supervises the use of assigned academic spaces.
- **Requester** — University community member who submits reservation requests along with the required documentation.

## 🛠️ Technologies

| Category | Technology |
|---|---|
| Programming Language | Python 3.11 |
| Web Framework | Django 4.2 (MTV Architecture) |
| Database | PostgreSQL 15 |
| Containerization | Docker / Docker Compose |
| Application Server | Gunicorn |
| Static Files | WhiteNoise |
| Reporting | ReportLab, openpyxl, python-docx |
| Frontend | HTML, CSS, JavaScript |

## 📦 Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed
- Git

## 🚀 Installation & Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/carmenmirna-is/ProyectoGrado_GSA_UABJB.git
   cd ProyectoGrado_GSA_UABJB
   ```

2. Start the containers (PostgreSQL database + Django server):

   ```bash
   docker-compose up --build
   ```

   This command automatically applies database migrations, collects static files, and starts the development server.

3. Open the application at:

   ```
   http://localhost:8000
   ```

## Project Structure

```
ProyectoGrado_GSA_UABJB/
├── administrador/                  # Administration module
├── encargados/                     # Space manager module
├── gestion_espacios_academicos/    # Main Django project configuration
├── usuarios/                       # User registration and profiles
├── reportes/                       # Reporting module
├── templates/                      # HTML templates
├── static/ · staticfiles/          # Static resources (CSS, JS, images)
├── media/                          # User-uploaded files
├── assets/                         # Project resources (screenshots, etc.)
├── logs/                           # System logs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

## Screenshots

### Home Page

![Home](assets/Index.png)

### Login

![Login](assets/Login.png)

### User Dashboard

![UserDashboard](assets/DashboardUsuario.png)

### Space Manager Dashboard

![ManagerDashboard](assets/DashboardEncargado.png)

### System Administrator Dashboard

![AdminDashboard](assets/DashboardAdministrador.png)

## Academic Context

This project was developed as an Undergraduate Capstone Project submitted to the Systems Engineering Program of the Faculty of Engineering and Technology at UABJB, as a requirement for obtaining the Bachelor's Degree in Systems Engineering (November 2025).

## License

This project was developed for academic purposes as part of the undergraduate degree completion process at UABJB.