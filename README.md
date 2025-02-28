# FastAPI Backend 

This is a FastAPI backend boilerplate project.

## Requirements

- Python 3.10+
- MySQL database

## Installation

- ### Clone the repository:
```sh
git clone <repository-url>
cd <repository-directory>
```

- ### Create and activate a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

- ### Install the dependencies:
```sh
pip install -r requirements.txt
```

- ### Set up the environment variables:
    Create a .env file in the root directory and add the following:
```sh
DATABASE_URL=mysql+pymysql://root:xplorers@34.46.187.244:3306/bookTable
```

- ### Database Migration
    Run the following command to create the database tables:
```sh
python migrate.py
```

- ### Running the Application
    Start the FastAPI application:
```sh
uvicorn app.main:app --reload
```

- ### API Endpoints
    The API endpoints are prefixed with `/api`. For example, to create a user, send a POST request to `http://127.0.0.1:8000/api/users/`.