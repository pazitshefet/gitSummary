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
git clone https://github.com
cd gitSummary

### 2. Create and activate a virtual environment
Set up an isolated environment to manage all required packages:

**Windows (CMD/PowerShell):**
python -m venv venv
.\venv\Scripts\activate

**macOS / Linux:**
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies
Update pip and install the required libraries:
pip install --upgrade pip
pip install -r requirements.txt

### 4. Start the server
Run the FastAPI application with Uvicorn:
uvicorn main:app

### 5. Open the app in browser
Visit the following link once the server is up:
http://127.0.0.1:8000

