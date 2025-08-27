# Zombie-Agent Telegram Starter (Server Deploy)

A minimal, production-ready starter kit to run a network of "zombie-agents" in Telegram:
- Ingest posts from source channels
- Transform them into a dark/ironic "anti" style with an LLM
- Schedule and publish to your Telegram channel
- Store everything in Postgres, run on Docker

## Quick Start

1) Copy `.env.example` to `.env` and fill in values.
2) (Optional) Edit `SOURCE_USERNAMES` in `.env` with the channels you want to mirror-invert (comma-separated).
3) Run:

```bash
docker compose up -d --build
```

4) Check logs:

```bash
docker compose logs -f zombie
```

## What it does (MVP)
- Polls source channels every 90 seconds via Telethon (read-only user client).
- Writes raw posts to Postgres.
- Transforms new raw posts via `OpenAI` (or a safe stub if no key present).
- Schedules publishing with randomized delays.
- Publisher posts to your target channel via Bot API (aiogram).

> **Note**: This is a foundation. Tweak prompts, safety, and scheduling to your taste.

## Server checklist

- Ubuntu 22.04 LTS recommended
- `docker` and `docker compose` installed
- Open ports not required (bot is outbound only)
- Create a dedicated system user (optional)

### Install Docker (Ubuntu)
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg]   https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out/in once to apply the docker group membership.

## Telegram prep

1. Create a bot via **@BotFather** and copy `BOT_TOKEN`. Add the bot as **admin** in your target channel.
2. Create/obtain an **API_ID** and **API_HASH** for a **user** client at https://my.telegram.org.
3. On first run, the Telethon session will prompt phone login in the container logs — **we disable prompts in this starter** and use `TELETHON_LOGIN_CODE` flow only if needed. For simplicity now, mount a session file or run once interactively (see comments in `listener.py`).

## Migrations
This MVP auto-creates tables at startup with SQLAlchemy. For production, adopt Alembic migrations.

## Backups
- Postgres volume persists on the host via docker volume `zombie_pgdata`.
- Take periodic `pg_dump` backups.

## Monitoring
- Use `docker compose logs -f zombie` for live logs.
- Integrate Prometheus + Grafana later if needed.