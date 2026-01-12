# ClinixTech: Intelligent Hospital Management System

> **A Next-Generation Healthcare Platform integrating Advanced Data Structures with Modern Web Technologies.** Clinixtech is LIVE 🎉🎉🎉🎉 https://clinixtech.onrender.com

## 📋 Overview
ClinixTech is a comprehensive Hospital Management System designed to bridge the gap between traditional record-keeping and algorithmic efficiency. Unlike standard CRUD applications, ClinixTech leverages **Data Structures and Algorithms (DSA)** to optimize hospital operations—managing emergency triage via Priority Queues, handling prescriptions via Stacks, and analyzing patient vitals with linear regression algorithms.

## 🚀 Key Features

### 🩺 Patient Portal
* **Intelligent Dashboard:** Real-time view of upcoming appointments, recent medical records, and active prescriptions.
* **Vitals Tracking & Analytics:** Logs heart rate, BP, BMI, and oxygen saturation.
    * *Feature:* Automated "Health Risk" alerts based on vital thresholds.
    * *Feature:* Graphical trend analysis of patient health over time.
* **Medical History PDF:** Auto-generates downloadable PDF medical summaries using `ReportLab`.
* **Appointment Management:** Book, view, and cancel appointments with conflict detection.

### 👨‍⚕️ Doctor Portal
* **Algorithmic Appointment Queue:**
    * Uses a **Priority Queue (Min-Heap)** to sort patients not just by time, but by medical urgency (Emergency > Urgent > Normal).
* **Prescription Stack (LIFO):**
    * Implements a **Stack Data Structure** for prescription management, allowing doctors to draft multiple prescriptions and "pop" them (issue/delete) efficiently.
* **Schedule Management:** Granular control over availability (Day/Time slots).
* **Digital Prescriptions:** Generate professional PDF prescriptions with license details and instructions.

### 🔐 Security & Architecture
* **Role-Based Access Control (RBAC):** Distinct sessions for Admin, Doctor, and Patient.
* **Data Integrity:** SQLAlchemy ORM with foreign key constraints to ensure relational integrity.
* **Input Validation:** Server-side validation for appointment conflicts and vital signs ranges.

## 🛠 Technical Stack

### Backend
* **Framework:** Flask (Python)
* **Database:** SQLite (Development) / SQLAlchemy ORM
* **PDF Generation:** ReportLab
* **Algorithms:** `heapq` (Priority Queues), Custom Stack Logic

### Frontend
* **Templating:** Jinja2
* **Styling:** CSS3, Bootstrap
* **Interactivity:** JavaScript (ES6+)
* **Client-Side Analytics:** Custom JS classes for `PriorityQueue`, `Graph`, and `MedicalDataAnalyzer`.

## 🧠 Data Structures & Algorithms Implementation

This project applies theoretical DSA concepts to real-world scenarios:

| Concept | Implementation | Real-World Application |
| :--- | :--- | :--- |
| **Min-Heap / Priority Queue** | `heapq` in Python & `PriorityQueue` class in JS | **Triage System:** Ensures emergency patients are seen before routine checkups, regardless of booking time. |
| **Stack (LIFO)** | Python List operations in `doctor_prescriptions` | **Workflow Management:** Doctors can stack up prescriptions during rounds and process the most recent ones first. |
| **Graph / Dijkstra** | `Graph` class in JS | **Pathfinding:** Prepared for future implementation of hospital navigation and referral networks. |
| **Linear Regression** | `MedicalDataAnalyzer` in JS | **Predictive Health:** Calculates trends in patient weight and heart rate to predict health risks. |

## 🗄️ Database Schema

The system uses a relational database with the following core entities:
* **Users:** `Patient`, `Doctor`, `Admin` (with secure password handling).
* **Clinical:** `Appointment` (Links Patient & Doctor), `MedicalRecord`, `Prescription`.
* **Monitoring:** `Vitals` (Time-series data for health tracking).
* **Logistics:** `DoctorAvailability` (Time-slot mapping).

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/clinixtech.git](https://github.com/yourusername/clinixtech.git)
    cd clinixtech
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database:**
    The application will automatically create `clinic.db` on the first run.

5.  **Run the Application:**
    ```bash
    python app.py
    ```
    Access the app at `http://127.0.0.1:5000/`

## 🔮 Future Roadmap (The "ClinixIntelligence" Update)
* **Polyglot Persistence:** Migrating to PostgreSQL for relational data and MongoDB for unstructured medical logs.
* **AI Diagnostics:** Integration of Deep Learning models for X-ray analysis.
* **Blockchain Ledger:** Immutable hashing of medical records for security and audit trails.
* **Smart Payments:** Stripe integration for consultation fees.

---
*Developed by [Name] for [Course Name/Semester]*
