# University Research Opportunity Portal

## Course Assignment
**Computer Networks (CN) — Assignment #01**

## Project Description
The University Research Opportunity Portal is a web-based application that allows users to view and manage research opportunities. It provides functionality to create, retrieve, update, and delete research opportunities.

## Technologies Used
- **Backend:** Python and Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **API Testing:** Postman
- **Cross-Origin Requests:** Flask-CORS

## Features
- Display all research opportunities.
- Retrieve a single opportunity by ID.
- Create new research opportunities.
- Update existing opportunities.
- Change opportunity status from Open to Closed.
- Delete research opportunities.
- Validate input data and handle errors.
- Test API endpoints using Postman.

## Project Structure
The project contains frontend and backend folders, database setup files, and the exported Postman collection.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Install Dependencies
Install Python, MySQL, and the required Python packages. If a `requirements.txt` file is provided, run:

```bash
pip install -r requirements.txt
```

Otherwise, install the packages required by the project, including Flask, the MySQL connector used by the application, and Flask-CORS.

### 3. Set Up the Database
Create the MySQL database and tables using the SQL setup file included in the repository. Configure the database connection settings in the backend according to your local MySQL setup.

### 4. Run the Backend
From the project directory, run the Flask application using the command appropriate for your project, for example:

```bash
python backend/app.py
```

### 5. Open the Frontend
Open the frontend using the method supported by your project and ensure the backend server is running.

### 6. Test the API
Import the exported Postman collection into Postman and send the requests to the local API server.

## API Testing
The Postman collection is included in this repository. It contains requests for testing the API. Successful responses and error responses should be verified during testing.

## Author
Student project submitted for the Computer Networks course.
