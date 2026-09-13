# Student Clearance Signing (Python/Django version)

A Django + Inertia.js port of the [Laravel version](../student-clearance-signing) of this
app. Same workflow, same Vue 3 + Vuetify frontend, same demo accounts — different backend.

## Stack

- **Backend:** Django 6 + [inertia-django](https://github.com/inertiajs/inertia-django)
- **Frontend:** Vue 3 + Vuetify 3 (ported unchanged from the Laravel version) via
  [django-vite](https://github.com/MrBin99/django-vite)
- **Database:** SQLite by default (zero setup); MySQL optional via `.env`

## Setup

```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo   # creates offices + demo accounts (password: "password")

# Frontend
npm install
```

## Running locally

Two processes, same as the Laravel version's `npm run dev` + `php artisan serve`:

```bash
# Terminal 1 — Vite dev server (HMR)
npm run dev

# Terminal 2 — Django dev server
source venv/bin/activate
python manage.py runserver
```

Visit http://127.0.0.1:8000/login. Demo accounts (password `password`):

| Role | Email |
|---|---|
| Student | student@demo.test |
| Adviser | adviser@demo.test |
| Library | library@demo.test |
| Treasurer | treasurer@demo.test |
| Guidance | guidance@demo.test |
| Admin | admin@demo.test |

For a production-style run (no Vite dev server), `npm run build` then set
`DEBUG=false` in `.env` before `python manage.py runserver`.

## Running with Docker

`docker-compose.yml` runs the same two dev processes above as containers,
plus an optional local LLM server, so `docker compose up` replaces both
terminals:

- **`web`** — Django dev server (SQLite, bind-mounted code, port `8000`).
- **`vite`** — Vite dev server with HMR (`node:22-slim`, port `5173`).
- **`ollama`** — [Ollama](https://ollama.com), serving the models behind the
  Clearance Assistant chatbot (see below), port `11434`, models persisted in
  a named volume so they survive rebuilds.

```bash
docker compose up --build

# first time only — pull both models into the ollama container
docker compose exec ollama ollama pull qwen2.5:3b
docker compose exec ollama ollama pull all-minilm

# first time only — chunk + embed the mock policy docs into the DB
docker compose exec web python manage.py ingest_assistant_docs
```

Visit http://127.0.0.1:8000/login same as the local-processes setup. Query
the model directly at `http://127.0.0.1:11434/api/generate` (POST, JSON body
`{"model": "qwen2.5:3b", "prompt": "...", "stream": false}`) — useful for
testing prompts from Postman before wiring anything into the Django app.

If you already have Ollama running natively (the CLI or the desktop app) on
the same machine, stop it first (`pkill -f "ollama serve"`, or quit the app)
since it binds the same `11434` port the container publishes.

> **Note (macOS 12/13):** the native Ollama app/CLI on these OS versions can
> hit a Metal-backend crash (`GGML_ASSERT(buf_dst) failed`) during generation
> — a [known llama.cpp regression](https://github.com/ggml-org/llama.cpp/issues/16266),
> not specific to any one model. The dockerized `ollama` service sidesteps it
> entirely, since Docker Desktop on macOS has no GPU/Metal passthrough and
> always runs CPU-only. If you hit that crash running Ollama natively instead,
> the workaround is forcing CPU with `"options": {"num_gpu": 0}` in the
> request body (or bake it into a model variant: `ollama create <name>-cpu -f Modelfile`
> with a `PARAMETER num_gpu 0` line).

## AI Clearance Assistant

A RAG chatbot (floating widget, bottom-right on every logged-in page) that
answers student questions about clearance requirements, grounded in a small
set of mock policy documents (`assistant/documents/*.md`) and citing which
document it drew each answer from.

Native (non-Docker) setup, once Ollama is installed and running:

```bash
ollama pull qwen2.5:3b     # generation
ollama pull all-minilm     # embeddings (~46MB)
python manage.py ingest_assistant_docs   # chunks + embeds the mock docs into the DB
```

For the Docker setup, see the `ollama pull`/`ingest_assistant_docs` commands
under "Running with Docker" above.

**Deliberately simplified stack.** The project brief that originally proposed
this feature calls for LangChain + ChromaDB + a separate embedding runtime.
This implementation swaps that for something much smaller, on purpose:
document chunks and their embeddings are just rows in the existing SQLite DB
(`assistant.DocumentChunk`), similarity search is a brute-force cosine
similarity loop in plain Python (`assistant/rag.py`), and Ollama is called
directly over HTTP with the stdlib (`core/ollama_client.py`) — zero new pip
dependencies. That's a reasonable trade at this demo's scale (a few dozen
chunks total), not a production pattern — see `core/ollama_client.py`'s
docstring for the one-paragraph version of this note, worth repeating on the
seminar slides: **a real-world version of this feature would use LangChain
+ ChromaDB + Ollama.**

## Tests

```bash
python manage.py test
```

## What changed vs. the Laravel version

- **Auth:** Django's session auth + a custom `User` model (`accounts/models.py`)
  instead of Laravel's `Authenticatable`. Login validation is hand-rolled (no
  Django Forms) to mirror the original controller's plain `validate()` call.
- **Routing:** Django URLs use the *same route names* as the Laravel app
  (`student.dashboard`, `approver.approvals.update`, etc.) so the Vue pages'
  `route('name', id)` calls didn't need to change. Since Ziggy is
  Laravel-specific, `resources/js/route.js` is a ~20-line stand-in that maps
  those same names to paths and installs `window.route` the same way Ziggy
  does.
- **CSRF:** Django's cookie is `csrftoken` / header `X-CSRFToken` (vs Laravel's
  `XSRF-TOKEN` / `X-XSRF-TOKEN`), configured in `resources/js/app.js`'s
  `createInertiaApp({ http: {...} })`. `inertia-django` sets the cookie
  automatically.
- **Request bodies:** Inertia sends JSON, and Django's `request.POST` only
  parses form-encoded/multipart bodies — `core/http.py`'s `inertia_data()`
  reads the JSON body directly.
- **Prop shaping:** Django doesn't have Eloquent's automatic relation
  serialization, so `clearance/serializers.py` builds the same prop shapes
  explicitly (office/approver nested under each approval, etc.).
- **New, not ported:** the AI/RAG "Clearance Assistant" chatbot from the
  original project brief — it was never implemented in the Laravel version
  either, so there was nothing to port. It's now built here (see "AI
  Clearance Assistant" above) as a deliberately simplified stand-in for the
  brief's LangChain + ChromaDB stack.

Everything else — models, business rules (routing order, single-rejection-
blocks-approval, resubmission), the Vue pages/components/CSS, and the demo
accounts — matches the Laravel version.
