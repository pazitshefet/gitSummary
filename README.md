# gitSummary

This guide explains how to set up the project dependencies, install and start the gitSummary server locally.

---

## Prerequisites

- Python 3.10 or higher installed
- Git installed
- A virtual environment (recommended)

---

## Setup Instructions

### 1. Clone the repository
Get the source code onto your machine:

git clone https://github.com/pazitshefet/gitSummary/

cd gitSummary

### 2. Create and activate a virtual environment
Set up an isolated environment to manage all required packages:

**Windows (CMD):**

python -m venv venv

.\venv\Scripts\activate

**macOS / Linux:**

python3 -m venv venv

source venv/bin/activate

### 3. Install dependencies

Update pip and install the required libraries:

pip install --upgrade pip

pip install -r requirements.txt

### 4. verify that NEBIUS_API_KEY is set 
**Windows:**

echo %NEBIUS_API_KEY%

if it is not available, set it:

setx NEBIUS_API_KEY <your_key>

**Linux**

echo $NEBIUS_API_KEY

if it is not available, set it:

export NEBIUS_API_KEY=<your key>

### 5. Start the server
Run the main

**Windows:**

python src\main.py

**Linux:**

python3 src/main.py

u should see:
Uvicorn running on http://127.0.0.1:8000

leave it running!!

### 6. Open second Terminal - Send a Request
open another terminal and send a request

**Windows**

curl -X POST http://127.0.0.1:8000/summarize ^
  -H "Content-Type: application/json" ^
  -d "{\"github_url\":\"https://github.com/psf/requests\"}"

**Linux**

curl -X POST http://127.0.0.1:8000/summarize \
  -H "Content-Type: application/json" \
  -d "{\"github_url\":\"https://github.com/psf/requests\"}"



