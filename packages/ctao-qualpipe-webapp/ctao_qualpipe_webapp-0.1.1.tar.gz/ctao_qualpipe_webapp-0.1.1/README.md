# QualPipe-Webapp

<!-- ## 🚀 FastAPI + D3.js QualPipe Dashboard Project -->

The QualPipe-webapp project uses **FastAPI** as backend and frontend, plus **D3.js** for dynamic frontend visualizations, separated into clean services using **Docker Compose**.

---

## 📂 Project Structure

```bash
/qualpipe-webapp
│
├── docker-compose.dev.yml           # Docker compose for developer
├── docker-compose.yml               # Docker compose for user
├── Makefile                         # Makefile to build Backend and Frontend
│
├── docs/                            # Document folder
│
├── src/
│   └── qualpipe_webapp/             # FastAPI backend
│       ├── backend/                 # FastAPI backend
│       │   ├── main.py              # Main FastAPI app
│       │   ├── data/                # JSON data sources
│       │   ├── requirements.txt     # Backend dependencies
│       │   ├── requirements-dev.txt # Backend dependencies for developer
│       │   └── Dockerfile           # Backend container
│       │
│       ├── frontend/                # FastAPI frontend
│       │   ├── /templates/          # Template pages
│       │   ├── /static/             # Static files (css, js, lib)
│       │   ├── main.py              # Main FastAPI app
│       │   ├── requirements.txt     # Frontend dependencies
│       │   ├── requirements-dev.txt # Frontend dependencies for developer
│       │   └── Dockerfile           # Frontend container
│       │
│       ├── nginx/
│       │   ├── nginx.conf
│       │   └── ssl/                 # (optional later)
│
└── .gitignore
```

## Instructions

To run it in the background, from the project folder `qualpipe-webapp` simply execute:

```bash
make up
```

Then open your browser:

- Frontend: http://localhost/

- API: http://localhost/api/data

To stop everything, execute:

```bash
make down
```

If you also want to automatically see the logs you can then run it via docker compose

To run it the first time execute: (later on you can remove the `--build`)

```bash
docker-compose up --build
```

To stop it you can soft-kill with <kbd>CTRL-C</kbd> and shut down all the services executing `make down`.

If instead you do any modification to the `config`  while the containers are running or in case Docker caches wrong stuff, you can restart it running:

```bash
make restart
```

or

```bash
docker-compose down -v --remove-orphans
docker-compose up --build
```

## Makefile

Description of all the `Makefile` functionalities:

| Command            | What it does                                                |
| ------------------ | ----------------------------------------------------------- |
| make build         | Build the Docker images                                     |
| make up            | Build and start services (backend + frontend) in background |
| make down          | Stop all services                                           |
| make logs          | View combined logs (both frontend and backend)              |
| make logs-backend  | View only backend logs                                      |
| make logs-frontend | View only frontend logs                                     |
| make restart       | Restart the containers                                      |
| make prune         | Clean up unused Docker containers/images                    |
| ------------------ | ----------------------------------------------------------- |
| make build-dev     | Build the Docker images                                     |
| make up-dev        | Build and start services (backend + frontend) in background |

## Developers

For developers, you can build containers that automatically file changes, avoiding the need to restart the containers every time. To do so, simply execute:

```bash
make build-dev
make up-dev
```

This will automatically output also every log produced.

## Contributing

If you want to contribute in developing the code, be aware that we are using `pre-commit`, `code-spell` and `ruff` tools for automatic adherence to the code style. To enforce running these tools whenever you make a commit, setup the [`pre-commit hook`][pre-commit] executing:

```
pre-commit install
```

The `pre-commit hook` will then execute the tools with the same settings as when a merge request is checked on GitLab, and if any problems are reported the commit will be rejected. You then have to fix the reported issues before tying to commit again.


## License

This project is licensed under the BSD 3-Clause License. See the LICENSE file for details.


[pre-commit]:https://pre-commit.com/
