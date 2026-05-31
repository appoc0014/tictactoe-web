# 🎮 Tic-Tac-Toe Web App

A full-stack Tic-Tac-Toe web application built with Python/Flask and PostgreSQL. Containerized with Docker and automatically deployed to a self-hosted Kubernetes cluster via GitHub Actions and Flux CD.

---

## 📸 Screenshot

![Tic-Tac-Toe](./Tic-Tac-Toe.png)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Database | PostgreSQL 16 |
| Server | Gunicorn |
| Containerization | Docker |
| Registry | Docker Hub |
| CI/CD | GitHub Actions |
| Deployment | Kubernetes (k3s) via Flux CD |

---

## 📁 Project Structure

```
tictactoe-web/
├── app.py                      # Flask application and API routes
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container image definition
├── templates/
│   └── index.html              # Game frontend (HTML/CSS/JS)
└── .github/
    └── workflows/
        └── build-push.yaml     # GitHub Actions CI/CD workflow
```

---

## 🚀 CI/CD Pipeline

Every push to `main` triggers an automated pipeline:

```
Code push → GitHub Actions builds Docker image →
Pushes to Docker Hub with commit SHA tag →
Auto-updates image tag in Dell-Cluster repo →
Flux CD detects change and deploys to k3s cluster
```

### Workflow Steps

1. **Checkout code** — pulls the latest source
2. **Login to Docker Hub** — authenticates using repository secrets
3. **Extract version tag** — uses the short Git commit SHA as the image tag
4. **Build and push image** — builds and pushes two tags:
   - `appoc14/tictactoe-web:<commit-sha>` — immutable versioned tag
   - `appoc14/tictactoe-web:latest` — always points to newest build
5. **Update cluster repo** — commits the new image tag to `Dell-Cluster/Helm/game/values.yaml`

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `CLUSTER_REPO_TOKEN` | GitHub Personal Access Token with repo scope |

---

## 🐳 Docker

The image is available on Docker Hub:

```bash
docker pull appoc14/tictactoe-web:latest
```

### Build locally

```bash
docker build -t tictactoe-web .
```

### Run locally with Docker Compose

```bash
docker compose up
```

Requires a PostgreSQL instance. Set the `DB_URL` environment variable:

```
DB_URL=postgresql://user:password@localhost:5432/ttt
```

---

## 🗄 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the game UI |
| `GET` | `/api/leaderboard` | Returns player win/draw/game stats |
| `POST` | `/api/match` | Records a completed match result |

### POST `/api/match` payload

```json
{
  "x_player": "Player1",
  "o_player": "Player2",
  "winner": "X"
}
```

Winner can be `"X"`, `"O"`, or `"DRAW"`.

---

## 🗃 Database Schema

```sql
-- Players table
CREATE TABLE players (
  id         SERIAL PRIMARY KEY,
  name       TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

-- Matches table
CREATE TABLE matches (
  id           SERIAL PRIMARY KEY,
  played_at    TIMESTAMPTZ NOT NULL,
  x_player_id  INTEGER REFERENCES players(id),
  o_player_id  INTEGER REFERENCES players(id),
  winner       TEXT CHECK (winner IN ('X', 'O', 'DRAW'))
);
```

---

## ☸️ Kubernetes Deployment

This app is deployed to a self-hosted k3s cluster managed by the [Dell-Cluster](https://github.com/appoc0014/Dell-Cluster) repo.

The Helm chart handles:
- Flask web app Deployment
- PostgreSQL Deployment with PersistentVolumeClaim
- ClusterIP Services
- Traefik Ingress with TLS via cert-manager
- SOPS-encrypted Kubernetes Secrets
- Prometheus ServiceMonitor for metrics scraping

Live at: **https://game.marcodevops.org**

---

## 👤 Author

**Marco Gonzalez (appoc14)**
Home lab enthusiast | DevOps learner

- 🐙 GitHub: [@appoc0014](https://github.com/appoc0014)
- 🐳 Docker Hub: [appoc14](https://hub.docker.com/u/appoc14)
- 💼 LinkedIn: [marcodevops](https://www.linkedin.com/in/marco-gonzalez-48434777/)

---

*Part of a larger home lab DevOps portfolio — [Dell-Cluster repo](https://github.com/appoc0014/Dell-Cluster)*
