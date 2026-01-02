📝 Task Management APIA robust Django REST API built for efficient task organization, featuring JWT authentication, real-time filtering, task sharing, and deadline tracking.🚀 FeaturesAuth: Secure User registration & JWT authentication (SimpleJWT).Tasks: Full CRUD operations with task categories.Organization: Filter by status, priority, and due date; sort by urgency.Collaboration: Share tasks with other users on the platform.Smart Alerts: Dedicated endpoints for upcoming deadlines (24h) and overdue tasks.Tracking: History tracking and completion status toggles.Production Ready: Configured for PostgreSQL and Render deployment.🛠 Tech StackComponentTechnologyBackendDjango 5.2API FrameworkDjango REST Framework (DRF)DatabasePostgreSQL (Prod), SQLite (Dev)AuthenticationJWT (SimpleJWT)DeploymentRenderEnvironmentPython 3.12+📥 Quick Start1. InstallationBash# Clone the repository
git clone https://github.com/HasnaChalla/Task-Management-API.git
cd Task-Management-API

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
2. ConfigurationCreate a .env file in the root directory:Code snippetSECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/taskdb
3. Database & SuperuserBashpython manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Visit the API at: http://127.0.0.1:8000/api/📑 API EndpointsAuthenticationMethodEndpointDescriptionPOST/api/auth/register/Register a new userPOST/api/auth/login/Get JWT tokensPOST/api/auth/logout/Blacklist tokenGET/api/auth/profile/View current user detailsTasksMethodEndpointDescriptionGET/api/tasks/List all tasks (with filter/sort)POST/api/tasks/Create a new taskPATCH/api/tasks/{id}/mark_complete/Set status to completedGET/api/tasks/upcoming_deadline/Tasks due in < 24 hoursPOST/api/tasks/{id}/share_task/Share task with another user🌐 Deployment (Render)Build Script: Ensure build.sh exists in the root:Bashpip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
Blueprint: Create a render.yaml or manually create a Web Service on Render.Environment Variables:PYTHON_VERSION: 3.12.0DATABASE_URL: (Connect your Render PostgreSQL instance)DEBUG: False
