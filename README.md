# FastAPI Application internship_meduzzen_backend

## Getting Started

To get started with this project, you will need to have Python and pip installed on your machine.
### Prerequisites

- Python (version 3.6 or higher)
- pip (version 3.7 or higher)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/VadimTrubay/internship_meduzzen_backend.git
    cd internship_meduzzen_backend
    ```
2. **Create and activate a virtual environment:**

    Create a `.env` file based on `.env.sample`:
    ```bash
    python -m venv venv
   
   .\venv\Scripts\activate
    ```
   
3. **Install dependencies:**

    Using pip:
    ```bash
    pip install -r requirements.txt
    ```
   
4. **Create environment variables:**

    Create a `.env` file based on `.env.sample`:
    ```bash
    cp .env.sample .env
    ```

### Running the Development Server

To start the development server, run:

Using:
```bash
python -m app.main
```

After the server starts, open your web browser and navigate to:
http://127.0.0.1:8000/

### Stopped the application
To stop the development server, run:

Using:
```bash
Ctrl + C
```

### Running the Tests
To running the tests, run:

Using:
```bash
pytest
```

### Using Docker
Build the Docker Image, run:

Using:
```bash
docker build -t internship_meduzzen_backend .
```

Run the Docker Container, run:

Using:
```bash
docker run -d -p 8000:8000 --env-file .env internship_meduzzen_backend
```

Stopping the Docker Container, run:

Using:
```bash
docker stop <container_id>
```