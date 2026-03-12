<img width="511" height="100" alt="LOGINLOGO" src="https://github.com/user-attachments/assets/8c0fdf99-0b07-4b17-9a07-baa0088660e5" />

# SamanLoop

### Borrow Smart. Earn Easy.

![Django](https://img.shields.io/badge/Backend-Django-green)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange)
![Status](https://img.shields.io/badge/Project-Production-success)
![License](https://img.shields.io/badge/License-MIT-orange)
![Platform](https://img.shields.io/badge/Platform-Web-blue)
![Deployment](https://img.shields.io/badge/Deployed-Railway-purple)


![GitHub repo size](https://img.shields.io/github/repo-size/Tushya-web/samanloop)
![GitHub stars](https://img.shields.io/github/stars/Tushya-web/samanloop)
![GitHub forks](https://img.shields.io/github/forks/Tushya-web/samanloop)
![GitHub last commit](https://img.shields.io/github/last-commit/Tushya-web/samanloop)

A **peer-to-peer rental marketplace** that allows people to **borrow and lend everyday items locally** instead of buying them for short-term use.

SamanLoop promotes **cost saving, sustainability, and smarter resource utilization** by enabling communities to share underused items.

---

# 🌐 Live Application

🚀 **Try the Live Platform**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-SamanLoop-green)](https://samanloop.up.railway.app)

🔗 https://samanloop.up.railway.app/

---

# 📑 Table of Contents

- [📖 About the Project](#-about-the-project)
- [⚠️ Problem Statement](#️-problem-statement)
- [💡 Proposed Solution](#-proposed-solution)
- [✨ Key Features](#-key-features)
- [🔄 System Workflow](#-system-workflow)
- [🔁 Data Flow Architecture](#-data-flow-architecture)
- [🧰 Technology Stack](#-technology-stack)
- [🗄 Database Design](#-database-design)
- [⚙️ Installation Guide](#️-installation-guide-local-setup)
- [🚀 Deployment](#-deployment)
- [📚 Documentation](#-documentation)
- [📊 Project Presentation](#-project-presentation)
- [🔮 Future Enhancements](#-future-enhancements)
- [👨‍💻 Author](#-author)

---

# 📖 About the Project

Many people buy items that they **rarely use**, such as tools, cameras, projectors, or camping gear.

At the same time, others need these items only **temporarily**.

SamanLoop bridges this gap by allowing users to:

• Borrow items when needed
• Lend unused items to earn money
• Reduce waste and unnecessary purchases

The platform works as a **secure rental ecosystem** between borrowers and lenders.

---

# ⚠️ Problem Statement

Traditional item ownership leads to:

| Problem             | Description                                      |
| ------------------- | ------------------------------------------------ |
| High Cost           | Buying expensive items for short-term use        |
| Resource Waste      | Many items stay unused most of the time          |
| Lack of Access      | People can't afford tools they occasionally need |
| No Sharing Platform | No simple local platform for borrowing items     |

---

# 💡 Proposed Solution

SamanLoop provides a **digital platform where users can easily list, borrow, and return items securely.**

Core solution features include:

• Item listing by owners
• Borrow requests by users
• Deposit-based security system
• Return confirmation workflow
• User dashboards for lenders and borrowers

---

# ✨ Key Features

### 👤 User Features

* User Registration & Login
* Browse available items
* Search items by category
* Borrow items with deposit
* Return items
* Track borrowing history

### 🏷️ Lender Features

* Add items for rent
* Approve borrow requests
* Track item usage
* Confirm item return
* Earn rental income

### 🔐 Platform Features

* Secure user sessions
* Rental deposit management
* Transaction workflow
* Dashboard management
* Item availability tracking

# 🔄 System Workflow

The SamanLoop platform operates through three main roles: Borrower, Lender, and Admin.
Each role has specific responsibilities in the rental lifecycle.

### 👤 Borrower Workflow

1️⃣ User registers or logs into the platform

2️⃣ User browses available items

3️⃣ User selects an item and sends a borrow request

4️⃣ Borrower pays the required deposit / rental fee

5️⃣ Borrower collects the item from the lender

6️⃣ Borrower uses the item for the agreed rental duration

7️⃣ Borrower returns the item on or before the return date

8️⃣ Lender confirms the return

9️⃣ Deposit is released or refunded

### 🏷️ Lender Workflow

1️⃣ Lender registers and logs into the platform

2️⃣ Lender lists an item with details (name, category, price, deposit, availability)

3️⃣ Lender receives borrow requests from users

4️⃣ Lender reviews and approves or rejects the request

5️⃣ Lender hands over the item to the borrower

6️⃣ Lender monitors the item usage period

7️⃣ Lender verifies item condition upon return

8️⃣ Lender confirms the return in the system

9️⃣ Platform completes the transaction

### 🛠️ Admin Workflow

1️⃣ Admin manages platform users

2️⃣ Admin monitors listed items and categories

3️⃣ Admin reviews reported issues or disputes

4️⃣ Admin manages system queries and support requests

5️⃣ Admin ensures platform security and data integrity

6️⃣ Admin monitors transactions and platform activity

7️⃣ Admin performs system updates and maintenance

# 🔁 Data Flow Architecture

```
User
 ↓
Frontend (HTML / CSS / JS)
 ↓
Django Views
 ↓
Django Models
 ↓
Database (SQLite / PostgreSQL)
 ↓
Business Logic
 ↓
Response to User
```

---

# 🧰 Technology Stack

| Layer | Technology |
|------|-------------|
| Frontend | ![HTML](https://img.shields.io/badge/HTML5-orange) ![CSS](https://img.shields.io/badge/CSS3-blue) ![Bootstrap](https://img.shields.io/badge/Bootstrap-purple) |
| Backend | ![Django](https://img.shields.io/badge/Django-green) ![Python](https://img.shields.io/badge/Python-yellow) |
| Database | ![SQLite](https://img.shields.io/badge/SQLite-lightblue) OR ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-blue) |
| Authentication | ![Django Auth](https://img.shields.io/badge/Django-Authentication-green)  ![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange)|
| Deployment | ![Railway](https://img.shields.io/badge/Railway-Cloud-purple) |
| Version Control | ![Git](https://img.shields.io/badge/Git-orange) ![GitHub](https://img.shields.io/badge/GitHub-black) |
---

# 🗄 Database Design

Main database tables used:

| Table     | Purpose                        |
| --------- | ------------------------------ |
| Users     | Stores registered user data    |
| Item      | Item details listed by lenders |
| Category  | Item categorization            |
| ItemUsage | Tracks borrowing transactions  |
| Payment   | Deposit / rental payments      |
| Query     | User support queries           |

---

# 🚀 Deployment

The project is deployed using **Railway cloud hosting.**

Live link:

https://samanloop.up.railway.app/

Deployment includes:

* Production server
* Static files configuration
* Database migrations
* Secure environment variables

---

# 📚 Documentation

Project documentation will include:

* System Architecture
* API Design
* Database Schema
* User Workflows
* Deployment Guide

Documentation Link:

```
(Add documentation link here)
Soon...
```

---

# 📊 Project Presentation

Project PPT used for demonstration and explanation.

Presentation Link:

```
(Add Google Drive PPT link here)
Soon...
```

---

# 🔮 Future Enhancements

Planned improvements for SamanLoop:

* Integrated online payments [✔ Implemented]
* Real-time item availability [✔ Implemented]
* Location-based search [✔ Implemented]
* Ratings & reviews [✔ Implemented]
* Mobile application
* AI-powered item recommendations [Soon...]
* Fraud detection system

---

# 👨‍💻 Author

**Tushya R Parmar**

AI Engineer (Aspiring)
Full Stack Developer

GitHub
https://github.com/Tushya-web

Project Repository
https://github.com/Tushya-web/samanloop

---

# ⭐ Support

If you like this project, please **star the repository** to support development.
