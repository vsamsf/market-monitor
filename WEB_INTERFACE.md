# Market Monitor & Productivity System - Web Interface

## Running the Application

### Backend (FastAPI)

```bash
# Activate virtual environment
source venv/bin/activate

# Install API dependencies
pip install fastapi uvicorn python-multipart websockets

# Run API server
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000

### Frontend (React + TypeScript + MUI)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### Running Both Together

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Scheduler (Optional):**
```bash
source venv/bin/activate
python main.py daemon
```

## Features

### Dashboard
- Task statistics (total, today, overdue, high-priority)
- Active reminders count
- Real-time updates every 30 seconds

### Tasks
- Create, edit, delete tasks
- Mark tasks as complete/incomplete
- Priority levels (high, medium, low)
- Due date tracking
- Color-coded priorities

### Reminders
- Create, delete reminders
- Recurring reminders (daily, weekly, monthly)
- Date and time picker
- Description support

### Market Data
- Live market indices (NIFTY 50, SENSEX, etc.)
- Price changes and percentages
- Market summary
- Auto-refresh every minute

## API Endpoints

### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task by ID
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/{id}/complete` - Mark complete
- `GET /api/tasks/filter/today` - Get today's tasks
- `GET /api/tasks/filter/overdue` - Get overdue tasks

### Reminders
- `GET /api/reminders` - Get all reminders
- `POST /api/reminders` - Create reminder
- `GET /api/reminders/{id}` - Get reminder by ID
- `PUT /api/reminders/{id}` - Update reminder
- `DELETE /api/reminders/{id}` - Delete reminder

### Market
- `GET /api/market/summary` - Get market summary
- `GET /api/market/indices` - Get index data
- `GET /api/market/sectors` - Get sector performance

### System
- `GET /api/system/status` - Get system status
- `GET /api/dashboard/stats` - Get dashboard statistics

## Production Build

### Frontend
```bash
cd frontend
npm run build
```

Build output will be in `frontend/dist/`

### Serve with FastAPI
FastAPI can serve the built frontend:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

## Environment Variables

Create `.env` in project root:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
VITE_API_URL=http://localhost:8000
```

## Technology Stack

### Backend
- FastAPI - Modern Python web framework
- Uvicorn - ASGI server
- SQLAlchemy - Database ORM
- Pydantic - Data validation

### Frontend
- React 18 - UI library
- TypeScript - Type safety
- Material-UI (MUI) - Component library
- Vite - Build tool
- Axios - HTTP client
- React Router - Routing

## Notes

- Frontend proxy is configured to forward `/api` requests to backend
- CORS is enabled for local development
- Both services can run independently
- Compatible with existing CLI and scheduler service
