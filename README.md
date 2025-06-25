# 🚀 ResolveX - Support Case Management System

**ResolveX** is a robust and user-friendly support case management system designed to streamline the process of logging, assigning, and resolving customer support issues. It features role-based access for **Customers**, **Support Agents**, and **Managers**.

Built with **Flask**, **SQLAlchemy**, and **MySQL**, ResolveX provides a real-world simulation of a helpdesk system with clean UI and secure login features.

---

## 🔧 Features

### 🧑‍💻 Customer
- Register and login securely
- Lodge new support cases
- View personal case status updates

### 👨‍🔧 Support Agent
- Login and view assigned cases
- Update the status of assigned cases

### 👨‍💼 Manager
- View all support cases
- Assign cases to available agents
- Promote streamlined case resolution

---

## 🏗️ Tech Stack

- **Frontend**: HTML, CSS (Bootstrap/Jinja2 Templates)
- **Backend**: Python (Flask)
- **Database**: MySQL or SQLite (via SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Password Security**: Werkzeug (Hashing)
- **Environment Management**: python-dotenv

---

## 🔐 Security & Environment

- Environment variables managed via `.env` file
  - `SECRECT_KEY` for Flask session
  - `DATABASE_URI` for SQLAlchemy connection

Example `.env`:

```env
SECRECT_KEY=your_super_secret_key
DATABASE_URI=sqlite:///database.db
```
## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sreansh-sudo/resolvex.git
cd resolvex
```
### 2. Create Virtual Environment and Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Set Up Environment

Create a `.env` file in the root directory:

```env
SECRECT_KEY=your_super_secret_key
DATABASE_URI=sqlite:///database.db  # or your MySQL URI
```
### 4. Run the App

```bash
python app.py
Then open your browser and go to : http://127.0.0.1:5000
```
