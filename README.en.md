<p align="center">
  <img src="assets/banner.png" width="100%">
</p>

<h1 align="center">
Academic Space Reservation Management System
</h1>

<p align="center">

[🇺🇸 English](README.en.md) • [🇪🇸 Español](README.md)

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

</p>

## 📖 Overview

This web application was developed as an undergraduate capstone project for the Bachelor's Degree in Systems Engineering at Universidad Autónoma del Beni "José Ballivián" (UABJB).

The platform automates the reservation workflow for academic spaces by replacing manual procedures with a centralized, transparent and scalable web application.

---

## ✨ Features

- ✔ Role-Based Authentication
- ✔ User Management
- ✔ Academic Space Management
- ✔ Reservation Requests
- ✔ Automatic Conflict Detection
- ✔ Availability Calendar
- ✔ Email Notifications
- ✔ Exportable Reports
- ✔ Role-Based Dashboards
- ✔ Scalable Django Architecture

---

## 🎯 Project Goal

Develop a scalable, maintainable, and transparent web platform to automate the reservation process for academic spaces.

---

## 👥 User Roles

| Role | Responsibility |
|------|----------------|
| Administrator | System configuration |
| Space Manager | Approves reservations |
| User | Creates reservation requests |

---

## 🏗 Architecture

```
Users
   │
   ▼
Django 4.2
   │
PostgreSQL
   │
Docker
```

---

## 🛠 Technologies

| Category | Technology |
|------------|------------|
| Language | Python 3.11 |
| Framework | Django 4.2 |
| Database | PostgreSQL 15 |
| Containers | Docker |
| Server | Gunicorn |
| Static Files | WhiteNoise |
| Reporting | ReportLab · OpenPyXL · python-docx |
| Frontend | HTML · CSS · JavaScript |

---

## 📦 Installation

```bash
git clone https://github.com/carmenmirna-is/ProyectoGrado_GSA_UABJB.git

cd ProyectoGrado_GSA_UABJB

docker-compose up --build
```

Open:

```
http://localhost:8000
```

---

## 📂 Project Structure

```text
ProyectoGrado_GSA_UABJB/

administrador/

encargados/

usuarios/

reportes/

templates/

static/

media/

assets/

Dockerfile

docker-compose.yml

requirements.txt
```

---

## 📸 Screenshots

### Home Page

![Index](assets/Index.png)

### Login

![Login](assets/Login.png)

### User Dashboard

![User](assets/DashboardUsuario.png)

### Space Manager Dashboard

![Manager](assets/DashboardEncargado.png)

### Administrator Dashboard

![Admin](assets/DashboardAdministrador.png)

---

## 🚀 Future Improvements

- REST API
- Responsive UI
- Google Calendar Integration
- Email Reminders
- QR Code Check-in
- Unit Testing
- GitHub Actions CI/CD

---

## 🎓 Academic Context

This project was developed as the undergraduate capstone project required to obtain the Bachelor's Degree in Systems Engineering at Universidad Autónoma del Beni "José Ballivián".

---

## 📄 License

This project was developed for academic purposes.

Although it originated as an undergraduate project, it follows modern software engineering practices including modular architecture, role-based access control, Docker containerization, PostgreSQL database design, and scalable web development using Django.