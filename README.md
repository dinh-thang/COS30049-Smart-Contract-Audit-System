# Smart Contract Audit System

This project implements a web platform for auditing Solidity smart contracts using Slither static analysis.

## Architecture

- **Frontend**: React + Tailwind CSS
- **Backend**: Python FastAPI
- **Smart Contract Analysis**: Slither API
- **Database**: MySQL

## Project folder structure

```bash
group2-25/
├── backend/                 # Backend application folder
│   ├── slither.wiki/        # Contains documentation cloned from slither.wiki
│   │   └── Detector-Documentation.md  # Documentation file about Slither detectors
│   ├── uploads/             # Folder for storing uploaded contract files by user
│   ├── __init__.py          
│   ├── crud.py              # Manages CRUD (Create, Read, Update, Delete) operations for database interactions
│   ├── database.py          # Handles database connection and session management
│   ├── main.py              # Main entry point for the backend application
│   ├── models.py            # Defines database models using SQLAlchemy's declarative base
│   ├── services.py          # Provides utility functions such as Slither-related commands for application logic
│   └── requirements.txt     # Lists required Python packages to install for the backend
├── frontend/                # Frontend application folder
│   ├── node_modules/        # Contains dependencies for the frontend
│   ├── public/              # public folder
│   └── src/                 # Source code folder for the frontend
│       ├── assets/          # Stores static images used by the frontend
│       ├── components/      # Contains reusable React components
│       ├── pages/           # React components representing different pages of the application
│       ├── api.js           # Handles API calls and interactions with the backend from the frontend
│       ├── App.js           # The main React component for the application
│       ├── constant.js      # Defines constants used throughout the frontend application
│       ├── index.css        # CSS file for styling
│       ├── index.js         # Entry point for frontend app
│       ├── package-lock.json  # Generated by React
│       ├── package.json     # Specify the project's dependencies
│       └── tailwind.config.js  # Configuration file for Tailwind CSS
└── README.md                # Project README file providing an overview of the project
```

## Setup

### Prerequisites

- Node.js
- Python 3

#### Frontend

```bash
cd frontend
npm install
npm start
```

#### Backend

```bash
cd backend
pip3 install virtualenv
virtualenv venv
venv\Scripts\activate
pip3 install -r requirements.txt
uvicorn main:app --reload
```

On wins: Set-ExecutionPolicy Unrestricted -Scope Process (only if have error: cannot run scripts due to restricted permissions)

**Note:** 
- MacOS use: ```source venv/bin/activate```
- Windows use: ```venv\Scripts\activate```


### Usage

The frontend will be available at http://localhost:3000

Use the upload form to submit a solidity smart contract file (.sol) for auditing.

The backend will run static analysis via Slither and save results to the database.

Audit reports for each submission can be viewed on the **Report History** page.

### Running Slither

Slither analyse cmd in CLI

```
solc-select install 0.8.4
solc-select use 0.8.4 
slither contract.sol --checklist > result.md
```

### Documentation

- Backend API is documented at http://localhost:8000/docs
