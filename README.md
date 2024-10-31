# AAA Health Backend
This repository contains the backend setup for the AAA Health application, built with PostgreSQL and pgAdmin for database management. Follow the steps below to get started.

## Setup Instructions
### 1. Create a .env File
Add your credentials to the .env file by copying the template below. Replace <password> and <email> with your actual PostgreSQL and pgAdmin credentials.

.env file:

Copy code
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<password>
POSTGRES_DB=aaa-health
POSTGRES_HOST=db
POSTGRES_PORT=5432
PGADMIN_DEFAULT_EMAIL=<email>
PGADMIN_DEFAULT_PASSWORD=<password>
```

### 2. Launch the Application with Docker
Open your terminal and navigate to the project directory. Use the following commands to manage the Docker containers:

First-time Setup:

Copy code
```
docker-compose up --build
```
This command builds and starts the containers.

If no changes are made and want to run container Run:

Copy code
```
docker-compose up
```
Starts the containers without rebuilding.

Shut Down the Containers:

Copy code
```
docker-compose down
```


### Accessing the Application
Application URL: http://127.0.0.1:8000
pgAdmin URL: http://127.0.0.1:8888
Use the credentials set in the .env file to log into pgAdmin and manage your PostgreSQL database.
