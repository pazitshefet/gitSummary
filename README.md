# gitSummary

This guide explains how to set up the project dependencies and start the gitSummary server locally.

---

## Prerequisites

- Python 3.10 or higher installed  
- Git installed (optional, for cloning the repo)  
- Recommended: use a virtual environment to manage dependencies  

---

## Setup Instructions

### 1. Clone the repository (if you haven’t already)

git clone https://github.com/pazitshefet/gitSummary.git
cd gitSummary

### 2. Create and activate a virtual environment

**Windows (cmd):**

python -m venv venv
venv\Scripts\activate.bat

**Windows (PowerShell):**

python -m venv venv
.\venv\Scripts\Activate.ps1

**macOS / Linux:**

python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies

pip install --upgrade pip
pip install -r requirements.txt

> Make sure the `requirements.txt` file exists in the project root and lists all necessary packages.

### 4. Start the server

uvicorn main:app

`main` is the Python file containing FastAPI app instance named `app`.  

### 5. Open the app in browser

Visit: http://127.0.0.1:8000

