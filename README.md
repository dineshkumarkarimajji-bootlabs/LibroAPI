📚 LibroAPI – Transactional Library Management System

1. Project Overview

LibroAPI is a RESTful backend API for managing a community library’s book catalog and loan operations. The API ensures transactional integrity for critical operations like borrowing and returning books, preventing inconsistencies such as multiple users borrowing the last copy simultaneously.

Use Case:

The local library needed a reliable digital system for:

Managing book catalog (CRUD)

Registering and managing users

Borrowing and returning books

Tracking overdue loans

Maintaining an audit trail

Core Challenge:

Ensuring data consistency across interdependent operations using ACID-compliant database transactions.
2. Features

Book Management (CRUD):

Create, read, update, soft-delete books

Track total and available copies

User Management:

Create and read library members

Soft-delete inactive users

Loan Management:

Borrow books (transactionally decreases available copies)

Return books (transactionally increases available copies)

Track overdue loans

Audit Logging:

Snapshot of total users, books, loans, and active/inactive statuses
Soft Deletion:

Marks books, users, and loans as deleted without removing them from the database
Transactional Integrity:

Borrow and return operations succeed or fail together

Prevents race conditions using pessimistic locking

Authentication & Authorization (Swagger UI):

JWT-based Authentication (Bearer token) implemented for secure access

Role-based Authorization (Admin/User) controls endpoint access

Swagger UI allows logging in and testing endpoints with access tokens

3. Technologies Used

Backend: Python 3.10+, FastAPI

ORM & Database: SQLAlchemy, PostgreSQL

Database Adapter: psycopg2-binary

Migrations: Alembic

Data Validation: Pydantic

Authentication: JWT (python-jose), Password hashing (passlib)

Testing: pytest, httpx, TestClient

Environment Management: python-dotenv

4. Project Setup

4.1 Prerequisites

Python 3.10+

PostgreSQL running locally or via Docker

Example Docker command:

$ docker run --name libro-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres

4.2 Clone & Install Dependencies

$ git clone https://github.com/dineshkumarkarimajji-bootlabs/LibroAPI.git $ cd LibroAPI $ python3 -m venv venv $ source venv/bin/activate # Windows: venv\Scripts\activate $ pip install -r requirements.txt

4.3 Environment Variables

Create a .env file in the project root:

DATABASE_URL=postgresql://username:password@localhost:5432/librodb
SECRET_KEY=
4.4 Database Setup

Create SQLAlchemy engine, SessionLocal, and Base

Run Alembic migrations:

$ alembic upgrade head

5. API Endpoints

5.1 Books

Method Endpoint Description

POST /books/ Create a new book

GET /books/{book_id} Get a specific book

GET /books/ List all books (pagination supported)

PUT /books/{book_id} Update book details

DELETE /books/{book_id} Soft delete a book

POST /books/{book_id}/borrow Borrow a book (transactional)

5.2 Users

Method Endpoint Description

POST /users/ Create a new user

GET /users/{user_id} Get user by ID

GET /users/ List all users

DELETE /users/{user_id} Soft delete a user

5.3 Loans

Method Endpoint Description

GET /loans/ List loans (filterable)

GET /loans/{loan_id} Get loan by ID

POST /loans/{loan_id}/return Return a borrowed book (transactional)

DELETE /loans/{loan_id} Soft delete a loan

5.4 Audit

Method Endpoint Description

GET /audit/ Create and view audit records

6. Testing

6.1 Setup

Tests use in-memory SQLite for isolation and speed

conftest.py provides test database sessions and FastAPI TestClient

6.2 Run Tests

$ pytest

Testing covers:

CRUD operations for books, users, and loans

Borrow/return transactions

Error handling and rollback

API endpoint integration tests

7. Manual Testing & Swagger UI

Run the FastAPI server:

$ uvicorn app.main:app --reload

Open Swagger UI: http://127.0.0.1:8000/docs
Steps to test with Authentication & Authorization:

Login with a registered user (POST /login) to receive a JWT token.

Click Authorize in Swagger UI and paste the token as Bearer .

Test endpoints according to roles:

Admin-only endpoints: Soft delete books/users, audit logs

User endpoints: Borrow/return books

Observe transaction effects (available copies, loan history).

Workflow Example:

Create books and users

Borrow a book → available_copies decrements

Return a book → available_copies increments

Soft delete a book or user (Admin)

Track overdue loans

🔐 Authentication & Authorization Flow

flowchart TD

A[User Login (POST /login)] --> B[Server validates credentials]

B --> C{Credentials valid?}

C -- No --> D[Return 401 Unauthorized]

C -- Yes --> E[Create JWT Token (access_token)]

E --> F[Return token to client]

subgraph Client

G[Swagger UI / Frontend]

G --> H[Attach JWT in Authorization header: Bearer ]

end

H --> I[API Endpoint (Protected)]

I --> J{Role check}

J -- Admin only --> K[Allow if Admin, else 403 Forbidden]

J -- User / Admin --> L[Allow access]

K --> M[Perform requested action (CRUD / Borrow / Return)]

L --> M

8. Key Learning Outcomes

Implemented transactional integrity to prevent inconsistencies

Learned CRUD API development with FastAPI and SQLAlchemy

Handled concurrency with database locks

Applied Pydantic for data validation

Implemented JWT authentication and role-based authorization

Managed environment variables securely

Conducted unit and integration testing to ensure reliability

9. Self-Reflection

This project demonstrates how transactional operations can ensure data integrity in real-world applications. Borrowing and returning books are tightly coupled operations that must succeed or fail together. Implementing these operations helped me understand:

ACID transactions

Concurrency and race condition handling

Structuring a maintainable FastAPI project

JWT authentication and role-based authorization

Testing transactional logic