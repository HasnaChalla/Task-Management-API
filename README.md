# 📝 Task Management API

A robust Django REST API built for efficient task organization, featuring JWT authentication, real-time filtering, task sharing, and deadline tracking.

# 🚀 Features
Auth: Secure User registration & JWT authentication (SimpleJWT).
Tasks: Full CRUD operations with task categories.Organization: Filter by status, priority, and due date; sort by urgency.
Collaboration: Share tasks with other users on the platform.
Smart Alerts: Dedicated endpoints for upcoming deadlines (24h) and overdue tasks.
Tracking: History tracking and completion status toggles.
Production Ready: Configured for PostgreSQL and Render deployment.


# 🛠 Tech Stack
Component Technology Backend Django 5.2
API Framework Django REST Framework (DRF)
DatabasePostgreSQL (Prod), SQLite (Dev)
AuthenticationJWT (SimpleJWT)
Deployment Render Environment 
Python 3.12+

# 📥 Quick Start1. 
Installation
Bash
Clone the repository
git clone https://github.com/HasnaChalla/Task-Management-API.git
cd Task-Management-API

Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

2. Configuration
Create a .env file in the root directory:
Code snippetSECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/taskdb

3. Database & Superuser
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

4. Apply Database Migrations
Bash

python manage.py makemigrations
python manage.py migrate

5. Run Development Server
python manage.py runserver

# Database Schema (Models)
User: Custom user model extending standard authentication.

Category: Organizational labels for tasks (e.g., Work, Personal, Urgent).

Task: Core entity storing title, description, priority, due date, and status.

TaskShare: Junction table managing permissions between task owners and shared users.

Notification: System-generated alerts for deadlines and shared task updates.

# Roadmap
✅ Phase 1-2: Project Initialization & Core CRUD Logic.

✅ Phase 3: JWT Authentication & Permission Classes.

✅ Phase 4: Task Sharing, Filtering, & Search Implementation.

✅ Phase 5: Render Deployment & PostgreSQL Integration.

⏳ Phase 6: Email Notifications & Frontend Integration (Planned).

API Access
API Base URL: https://task-management-api-pisq.onrender.com/

