# Pulse

Real-time API Monitoring and Uptime Tracking System

Pulse is a backend system designed to monitor APIs continuously, track uptime, log performance metrics, and provide a simple dashboard for real-time insights.

---

## Features

- Automated API monitoring using background scheduler  
- Uptime and success rate tracking  
- Response time analytics  
- Failure detection and logging  
- Live service status (UP / DOWN)  
- Service grouping support  
- Lightweight dashboard (Jinja2)  
- Modular backend architecture  

---

## Tech Stack

- Backend: FastAPI  
- Database: SQLite (SQLModel)  
- Scheduler: APScheduler  
- HTTP Client: httpx  
- Templating: Jinja2  

---

## Project Structure

app/
├── api/            # API routes  
├── db/             # Database models and engine  
├── scheduler/      # Background jobs  
├── services/       # Monitoring logic  
├── templates/      # Dashboard UI  
├── utils/          # Logging utilities  
└── main.py         # Entry point  

---

## Installation

git clone https://github.com/arman-0909/pulse.git  
cd pulse  

python -m venv env  
env\Scripts\activate  

pip install -r requirements.txt  

---

## Run Locally

uvicorn app.main:app --reload  

---

## API Documentation

http://127.0.0.1:8000/docs  

---

## Dashboard

http://127.0.0.1:8000/dashboard  

---

## How It Works

1. Services are registered with their URLs  
2. A background scheduler periodically checks each service  
3. Metrics such as status and response time are stored  
4. APIs expose analytics like uptime and failures  
5. Dashboard displays current service state  

---

## Deployment

Deployed using Render (free tier)  

Note: Free tier instances may sleep after inactivity.  

---

## Future Improvements

- Alert system (email or messaging integration)  
- Multi-user support  
- PostgreSQL integration  
- Advanced analytics and visualization  

---

## License

Creative Commons v1.0
---

## Author

Arman  