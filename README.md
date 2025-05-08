# Book Exchange App

An open-source web application to facilitate textbook and reading book exchanges among school families.

## Repository

This project is hosted on GitHub at:

https://github.com/i10s/book-exchange-app

You can clone it using:

```bash
git clone https://github.com/i10s/book-exchange-app.git
```

To set the remote and push your initial commit:

```bash
git remote add origin https://github.com/i10s/book-exchange-app.git
git branch -M main
git push -u origin main
```

## Features

- List available textbooks and reading books
- Propose exchanges between families
- Search and filter by book title, author, or grade
- User authentication and family grouping

## Tech Stack

- **Backend:** FastAPI, SQLModel
- **Frontend:** Jinja2 templates (or React if preferred)
- **Database:** SQLite (development), PostgreSQL (production)

## Installation

Ensure you have Poetry installed. Then:

```bash
poetry install
``` 

## Running Locally

Start the development server with Uvicorn:

```bash
poetry run uvicorn book_exchange_app.main:app --reload
```

## Testing

Run unit tests with pytest:

```bash
poetry run pytest
```

## License

This project is licensed under the [MIT License](LICENSE).
