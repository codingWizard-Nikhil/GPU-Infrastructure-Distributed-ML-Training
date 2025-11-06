# GPU Infrastructure for Distributed ML Training

A distributed job execution platform that replicates production ML infrastructure patterns. Demonstrates core concepts used in real-world GPU clusters where researchers submit training jobs to remote compute resources.

## Overview

This system is built to simulate and learn about the real-world production ML infrastructure architectures used at companies like OpenAI, Google, and NVIDIA. It separates job submission (lightweight client) from job execution (GPU server), enabling the same workflow patterns used in large-scale ML platforms.


The system is framework-agnostic, supporting any Python ML library (PyTorch, TensorFlow, JAX, scikit-learn, etc.).

## Architecture
```
┌─────────────┐         HTTP/REST API          ┌──────────────┐
│   Client    │ ────────────────────────────▶  │  API Server  │
│   (Mac)     │         Job Submission         │  (FastAPI)   │
└─────────────┘                                 └──────┬───────┘
                                                       │
                                                       │ PostgreSQL
                                                       ▼
                                                ┌─────────────┐
                                                │  Database   │
                                                │  (Jobs)     │
                                                └──────┬──────┘
                                                       │
                                                       │ Poll every 10s
                                                       ▼
                                                ┌─────────────┐
                                                │   Worker    │
                                                │  (Execute)  │
                                                └──────┬──────┘
                                                       │
                                                       │ CUDA/PyTorch
                                                       ▼
                                                ┌─────────────┐
                                                │     GPU     │
                                                │  RTX 4080   │
                                                └─────────────┘
```

## Components

### 1. API Server (`server/main.py`)
- FastAPI REST API for job management
- Endpoints: Submit jobs, retrieve status, list jobs
- PostgreSQL integration via SQLAlchemy ORM
- Designed for low-latency job submission

### 2. Worker Process (`server/worker.py`)
- Polls database for pending jobs every 10 seconds
- Executes Python code via subprocess with isolation
- Captures stdout/stderr and execution results
- Updates job status (pending → running → completed/failed)
- Enforces timeout limits and error handling

### 3. Database (PostgreSQL)
- Job persistence and state management
- Tracks: job ID, code, status, timestamps, results, errors
- Atomic state transitions with ACID guarantees

### 4. CLI Client (`client/cli.py`)
- User-friendly command-line interface
- Commands: `submit`, `get`, `list`
- Rich terminal output with colors and tables

## Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy ORM
- **ML Frameworks**: PyTorch (with CUDA), TensorFlow, JAX, etc.
- **Execution**: subprocess management with isolation
- **Containerization**: Docker, Docker Compose
- **Environment**: WSL2 (Windows Subsystem for Linux)
- **CLI**: Click, Rich
- **Networking**: Cross-machine HTTP over local network

## Setup

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- NVIDIA GPU with CUDA support (for GPU execution)

### Server Setup (GPU Machine)

1. **Clone the repository**
```bash
git clone https://github.com/codingWizard-Nikhil/GPU-Infrastructure-Distributed-ML-Training
cd GPU-Infrastructure-Distributed-ML-Training
```

2. **Start PostgreSQL**
```bash
docker-compose up -d
```

3. **Set up Python environment**
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Install PyTorch with GPU support** (or other ML frameworks)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

5. **Initialize database**
```bash
python3 test_db.py
```

6. **Start API server**
```bash
uvicorn main:app --host 0.0.0.0 --reload
```

7. **Start worker (in separate terminal)**
```bash
cd server
source venv/bin/activate
python3 worker.py
```

### Client Setup

1. **Set up Python environment**
```bash
cd client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure server connection**
Create `client/secrets.py`:
```python
API_URL = "http://YOUR_SERVER_IP:8000"
```

## Usage

### Submit a job
```bash
python cli.py submit "import torch; print(torch.cuda.is_available())"
```

### Check job status
```bash
python cli.py get JOB_ID
```

### List all jobs
```bash
python cli.py list
```

### Example: GPU Matrix Multiplication
```bash
python cli.py submit "import torch; x = torch.randn(5000, 5000).cuda(); y = x @ x; print(f'Result shape: {y.shape}')"
```

## Features

- ✅ Distributed job execution across machines
- ✅ CUDA/GPU support for ML workloads
- ✅ Framework-agnostic (PyTorch, TensorFlow, JAX, etc.)
- ✅ Job state tracking (pending/running/completed/failed)
- ✅ Automatic error handling and timeout management
- ✅ PostgreSQL-backed job persistence
- ✅ RESTful API for programmatic access
- ✅ User-friendly CLI interface
- ✅ Cross-platform support (Mac/Windows/Linux)

## Performance

- GPU utilization: Full CUDA acceleration (RTX 4080, 16GB VRAM)
- Worker polling: 10-second intervals (configurable)
- Job timeout: 60 seconds default (configurable)
- Job execution: Isolated subprocess with comprehensive error capture

## Future Enhancements

- [ ] Authentication/API keys for secure access
- [ ] Job priority queues
- [ ] Multi-GPU support and resource allocation
- [ ] Memory and CPU limits per job
- [ ] Web dashboard for monitoring
- [ ] Job scheduling (cron-like)
- [ ] Distributed workers across multiple machines
- [ ] Job dependencies and DAG execution

## Author

Nikhil Jain