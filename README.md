# Book Exchange App

An open-source FastAPI application that allows school families to exchange textbooks and reading books.  
Designed with Spanish data-protection (LOPD/GDPR) in mind and easily extensible.

---

## Table of Contents

- [Book Exchange App](#book-exchange-app)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
    - [Clone the repo](#clone-the-repo)
    - [Configuration](#configuration)
    - [Run with Docker Compose](#run-with-docker-compose)
    - [Run locally with Poetry](#run-locally-with-poetry)
  - [API Reference](#api-reference)
    - [Root \& Health](#root--health)
    - [Books Endpoints (`/books`)](#books-endpoints-books)
    - [Users Endpoints (`/users`)](#users-endpoints-users)
    - [Exchanges Endpoints (`/exchanges`)](#exchanges-endpoints-exchanges)
    - [Interactive Docs](#interactive-docs)
  - [Data Protection](#data-protection)
  - [Contributing](#contributing)
  - [License](#license)

---

## Features

- **FastAPI** & **SQLModel** for rapid development  
- **Docker** & **Docker Compose** for easy environment setup  
- **JWT Authentication** (via OAuth2 password flow)  
- **Spanish GDPR / LOPD**–ready (consent handling, data export/delete endpoints can be added)  
- **Open-source**: MIT license, PRs welcome  

---

## Prerequisites

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)  
- [Poetry](https://python-poetry.org/) (for local development)  
- Python 3.11 (if running outside Docker)  

---

## Getting Started

### Clone the repo

```bash
git clone https://github.com/i10s/book-exchange-app.git
cd book-exchange-app
```

### Configuration

1. Copy the example environment file and edit values:

   ```bash
   cp .env.example .env
   ```

2. In `.env`, set at least:

   ```dotenv
   DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
   SECRET_KEY=your_secret_key_here
   ```

   - **DATABASE_URL**: connection string for your database  
   - **SECRET_KEY**: used to sign JWT tokens (keep this secret in production)  

### Run with Docker Compose

```bash
docker-compose down --volumes --remove-orphans
docker-compose up --build
```

- The FastAPI app will be available at [http://localhost:8000](http://localhost:8000).  
- The PostgreSQL database runs in a container on port 5432.  

### Run locally with Poetry

```bash
poetry install
poetry run uvicorn main:app --reload
```

- Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) once started.  

---

## API Reference

### Root & Health

- **`GET /`**  
  Returns a welcome JSON message.

- **`GET /health`**  
  Health check → `{ "status": "ok" }`.

### Books Endpoints (`/books`)

| Method | Path             | Description                     |
| ------ | ---------------- | ------------------------------- |
| `GET`  | `/books`         | List all books (paginated)      |
| `POST` | `/books`         | Create a new book               |
| `GET`  | `/books/{id}`    | Get book by ID                  |
| `PUT`  | `/books/{id}`    | Update book by ID               |
| `DELETE`| `/books/{id}`   | Delete book by ID               |

### Users Endpoints (`/users`)

| Method | Path             | Description                         |
| ------ | ---------------- | ----------------------------------- |
| `GET`  | `/users`         | List all users (paginated)          |
| `POST` | `/users`         | Create a new user (hashes password) |
| `GET`  | `/users/{id}`    | Get user by ID                      |
| `PUT`  | `/users/{id}`    | Update user by ID                   |
| `DELETE`| `/users/{id}`   | Delete user by ID                   |

### Exchanges Endpoints (`/exchanges`)

| Method | Path               | Description                           |
| ------ | ------------------ | ------------------------------------- |
| `GET`  | `/exchanges`       | List all exchange proposals           |
| `POST` | `/exchanges`       | Propose a new exchange                |
| `GET`  | `/exchanges/{id}`  | Get exchange by ID                    |
| `PUT`  | `/exchanges/{id}`  | Update exchange status (accept/reject)|
| `DELETE`| `/exchanges/{id}` | Delete exchange proposal              |

### Interactive Docs

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)  

---

## Data Protection

This project is designed to comply with Spanish LOPD/GDPR requirements:

- All personal data (user emails, etc.) are stored securely.  
- Planned features:
  - Explicit consent fields on user/family models.  
  - Endpoints to export or delete personal data on request.  

---

## Contributing

1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/my-feature`)  
3. Commit your changes (`git commit -m "Add my feature"`)  
4. Push to your branch (`git push origin feature/my-feature`)  
5. Open a Pull Request  

Please follow the existing code style (Black, isort, mypy checks).

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
