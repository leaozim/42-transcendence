# 42--trascendence

Online Pong with chat, tournaments and 42 intra login (Django + Channels).

The project runs natively: **no Docker, root access, PostgreSQL, Redis or nginx
is required**, so it works on a plain VM or inside a sandbox. The only
requirement is **Python 3.10, 3.11 or 3.12** with `venv`/`pip` (plus internet
access to PyPI for the first install).

## Quick start

```bash
make setup   # creates .venv, installs requirements, creates .env with a SECRET_KEY
make run     # migrates the DB and serves on http://localhost:8000 (Ctrl+C to stop)
```

Or run it in the background:

```bash
make start   # logs go to data/server.log
make logs
make stop
```

Without `make`, use the scripts directly: `./scripts/setup.sh` then `./scripts/start.sh`.

| Command      | What it does                                                  |
|--------------|---------------------------------------------------------------|
| `make setup` | Create `.venv`, install Python deps, create `.env`            |
| `make run`   | Run in the foreground                                         |
| `make start` / `make stop` | Run / stop in the background                    |
| `make build` | `setup` + `start` (the default target, like the old `docker-compose up -d --build`) |
| `make down`  | Alias for `stop`                                              |
| `make test`  | Run the test suite with coverage (fails under 80%)            |
| `make clear` | Stop, then delete `.venv` and `data/` (**including the database and uploaded avatars**) |

`scripts/setup.sh` options: `PYTHON=/path/to/python3.11` to pick the
interpreter, `USE_VENV=0` to install into the current environment (handy in
sandboxes that are already isolated or lack `python3-venv`).

## How it runs

`scripts/start.sh` applies migrations, creates the bot superuser (user id 1,
which the chat depends on), compiles translations, and starts **one Daphne
process** that serves HTTP, WebSockets and static files.

| Before (Docker)             | Now (default)                         | Optional                               |
|-----------------------------|---------------------------------------|----------------------------------------|
| `postgres` container        | SQLite file `data/db.sqlite3`         | PostgreSQL via `POSTGRES_HOST`, ...    |
| `redis` container           | In-memory channel layer               | Redis via `REDIS_URL`                  |
| `nginx` container           | Static files and avatars served by the app | `nginx/pong.conf` + `SERVE_STATIC=false`, `SERVE_MEDIA=false` |
| `server` (gunicorn) + `daphne` | A single Daphne process            |                                        |
| `gettext` package in image  | `msgfmt` if installed, otherwise the pure-Python `scripts/compile_messages.py` |      |

> The in-memory channel layer only works within one process. Run a single
> server process (as `start.sh` does), or set `REDIS_URL` before running more.

## Accounts and two-factor authentication

- **Sign up** at `/signup/` (linked from the landing page), then log in with
  username and password on the landing page.
- **Avatar:** choose one when signing up, or change it later from the profile
  card on the home page. It is shown in the centre of the main circle.
  - Accepted: JPEG, PNG, GIF or WebP, up to 5 MB.
  - Images are cropped to a 256×256 JPEG and stored in `data/media/avatars/`.
  - Without an upload, the local default (`static/images/sloth.jpg`) is used.
- **Language:** English or Brazilian Portuguese (`pt-br`), from the menu in
  the top-right corner, before and after logging in.
  - Translations live in `transcendence/locale/pt_BR/`.
  - Browsers that ask for plain `pt` or `pt-PT` get Brazilian Portuguese.
- **Games:** the game card opens the **New game** window.
  - **Time (minutes):** 1-10, default 1.
  - **Points to win:** 1-21, optional.
  - A game ends when the time is up or a player reaches the points, whichever
    comes first.
  - From there you can play against the computer or challenge another player.
- **Challenges:** a challenge appears at once on the opponent's home page, in
  the **Open games** panel.
  - The panel offers **Join** and **Decline**, and shows whether the
    challenger is in the game room.
  - The challenger can **Cancel** until the game starts.
- **Starting a game:** in the game room, each player presses **Ready**.
  - The clock starts only when both players are in the room and ready, after
    a 3-second countdown.
  - Until then nothing moves, however long the game has been waiting.
- **Game physics:** the server runs each game in real time, at 60 updates a
  second (`srcs_game/physics.py`).
  - The ball bounces off the edge of the paddles.
  - Where it hits the paddle sets the bounce angle: straight back from the
    middle, up to 60° near the ends.
  - The ball speeds up with every hit (360 to 840 px/s).
  - Browsers only send key presses and draw what the server sends, so a slow
    or background tab does not slow the game down.
  - If every player leaves during play, the ball stops but the clock keeps
    running. The game then ends with the score it was left at.
- **Playing alone:** against the computer, only you need to press Ready.
  - The computer controls the right paddle on the server
    (`srcs_game/computer.py`).
  - It reacts late and aims imperfectly, so it can be beaten.
  - The game-over screen offers **Play again** with the same settings.
- **Enable 2FA** from the profile card on the home page: switch on
  "Two-factor authentication", pick **Google Authenticator** or **Authy**,
  scan the QR code (or type the setup key) in that app, and confirm with a code.
- **Log in with 2FA:** after the password, the app asks for the 6-digit code
  from the chosen app. You are only logged in after a valid code.
  - Each code works once. Right after enabling 2FA, wait for the app to show
    the next code.
  - Wrong codes are throttled: 1 s, 2 s, 4 s, ... between attempts.
  - You have 5 minutes after the password step to enter the code.

Both apps use the same standard (TOTP, RFC 6238), so codes from either are
accepted. The choice only changes the setup instructions and which app the
login page tells you to open.

No page loads anything from the internet: fonts, icons, Popper and images are
all served from `transcendence/static/`. Avatars of 42 users are the
exception; they still point to the 42 intra.

## Configuration

All settings live in `.env` (see `.env.example` for the full list). Real
environment variables take precedence over `.env`.

### Accessing the app from outside the VM

By default only `localhost` is accepted. To open the app at, say,
`http://192.168.56.10:8000` from your host machine, add to `.env`:

```bash
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.56.10
CSRF_TRUSTED_ORIGINS=http://192.168.56.10:8000
SITE_URL=http://192.168.56.10:8000
REDIRECT_URI=http://192.168.56.10:8000/oauth2/login/redirect/
```

Make sure port 8000 is reachable: open it in the VM firewall, or set up port
forwarding (e.g. VirtualBox NAT: host 8000 → guest 8000). Change the port with
`PORT=...` and the listen address with `BIND_ADDRESS=...`.

Keep `SECURE_COOKIES=false` (the default for development) while the site is
served over plain HTTP. Browsers drop secure cookies on `http://<ip>` URLs,
so login would not stick.

### 42 login

Set `AUTH_URL_INTRA`, `CLIENT_ID`, `CLIENT_SECRET` and `REDIRECT_URI` from your
42 intra OAuth application. Its redirect URI must match `REDIRECT_URI`.

### Production

Set `DJANGO_SETTINGS_MODULE=srcs_core.settings_prod` (DEBUG off, secure cookies
on by default) and serve it over HTTPS, e.g. behind nginx using
`nginx/pong.conf`.

## Translations

```bash
cd transcendence
../.venv/bin/python manage.py makemessages -a -s   # update .po files
```

`.mo` files are compiled automatically on every start.
