# Report Assistant Backend

## Development Setup

### Prerequisites

- **Python 3.12+**
- **Django 5.1.1**
- **PostgreSQL** (for main database)
- **Neo4j** (for graph database)
- **Milvus** (for vector database)

### Environment Configuration

Create environment files based on the provided templates:

```bash
# Backend service
cp docker/dev/backend/.env.example docker/dev/backend/.env

# Database service  
cp docker/dev/database/.env.example docker/dev/database/.env

# Neo4j service
cp docker/dev/neo4j/.env.example docker/dev/neo4j/.env

# Vector database service
cp docker/dev/vectordb/.env.example docker/dev/vectordb/.env
```

### Installation

1. **Install Python dependencies**:
   ```bash
   poetry install
   ```

2. **Database migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create superuser account**:
   ```bash
   python manage.py createsuperuser
   ```

### **CRITICAL: Background Worker**

⚠️ **The `db_worker` MUST be started**

```bash
python manage.py db_worker
```
### Development Workflow

1. **Start the background worker first** (in a separate terminal):
   ```bash
   python manage.py db_worker
   ```

2. **Start the development server** (in another terminal):
   ```bash
   python manage.py runserver
   ```

3. **Access the application**:
   - Main app: `http://localhost:8000`
   - Admin panel: `http://localhost:8000/admin`
   - Translation editor: `http://localhost:8000/en/rosetta/`

### Useful Development Commands

#### Django Management
```bash
# Create new Django app
python manage.py startapp <app_name>

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Start development server
python manage.py runserver

# Create superuser for admin access
python manage.py createsuperuser
```

#### Background Tasks
```bash
# Start background worker (REQUIRED for database features)
python manage.py db_worker
```

#### Internationalization (i18n)
```bash
# Generate message files for translation
django-admin makemessages -l en
django-admin makemessages -l hu

# Compile translations
django-admin compilemessages
```

After running the above commands, edit translations at: `http://localhost:8000/en/rosetta/`

#### Production Readiness
```bash
# Check deployment configuration
python manage.py check --deploy
```

### Architecture Overview

The backend consists of several key Django apps:

- **`chat/`** - Chat interface and conversation management
- **`dashboard/`** - Dashboard creation and management
- **`db_configurator/`** - Database connection configuration
- **`dbloader/`** - Database loading and processing (requires worker)
- **`reporter_agent/`** - AI-powered reporting agents
- **`home/`** - Main application views

### Important Notes

- **Worker Dependency**: Many features depend on the background worker. Always ensure `python manage.py db_worker` is running during development.
- **Database Services**: Ensure PostgreSQL, Neo4j, and Milvus services are running (via Docker Compose or locally).
- **Environment Variables**: Check that all required environment variables are set in your `.env` files.
- **LLM Dependencies**: The system uses LangChain and LangGraph for AI agent orchestration.

### Troubleshooting

**Database connection issues:**
- Verify database services are running
- Check `.env` files for correct database credentials
- Ensure migrations have been applied

**Background worker not processing tasks:**
- Restart the `db_worker` process
- Check for error messages in the worker logs
- Verify database connections are working

**Missing translations:**
- Run `django-admin compilemessages`
- Check that message files exist in `locale/` directories
