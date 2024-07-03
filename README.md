FastAPI Application internship_meduzzen_backend

Clone the repository:
git clone https://github.com/VadimTrubay/internship_meduzzen_backend

Navigate into the project directory:
cd internship_meduzzen_backend

Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate  # for Windows or 
source venv/bin/activate  # for Linux/macOS

Install the dependencies:
pip install -r requirements.txt

Running the Application
cd app
uvicorn main:app --reload

Stopped the application
Ctrl + C  # for Windows or
Ctrl + Cmd # for Linux

Running the Tests
cd internship_meduzzen_backend
pytest tests/test_main.py -v
