# plain_pages

**Minimalist base classes for microservice servers and matrix display pages.**

`plain_pages` is a lightweight Python package that provides two foundational classes—`ServerPage` and `DisplayPage`—designed to orchestrate real-time data collection and visual display in homelab environments. It’s built for clarity, composability, and just enough abstraction to stay out of your way.

## ✨ Why plain_pages?

This project grew out of a desire to keep things simple—but not simplistic. In a homelab where services talk over Redis, update displays via RGB matrices, and pull secrets from Vault or Kubernetes, `plain_pages` offers a clean interface for:

- Scheduling periodic updates
- Fetching and publishing data
- Rendering to LED panels or web displays
- Managing secrets and state with minimal ceremony

## 🧱 Core Components

### `ServerPage`

A base class for microservices that:

- Reads secrets from Vault, Kubernetes, or environment
- Connects to Redis and a backing database (Postgres, SQLite, MongoDB)
- Periodically fetches data from external APIs
- Writes state to the backing database, and
- Publishes updates via Redis pub/sub
- Supports liveness probes and production/development modes

### `DisplayPage`

A base class for display clients that:

- Reads data from the database
- Tracks freshness and avoids redundant redraws
- Provides helper methods for text alignment, color formatting, and time parsing
- Supports both RGB LED matrix output and static image generation (for testing without RGB LED hardware)

## 🌕 Example: Moon Phase Tracker

The `examples/moon_clock/` directory (coming soon) includes:

- `MoonServer`: Fetches sun/moon data from MET Norway’s API and publishes it
- `MoonDisplay`: Renders current time, moon phase, and next moonrise/set on an RGB matrix
- `clientdisplay.py`: Drives the LED panel and handles display cycling, pause/play, and override logic via Redis

## 📦 Installation

```bash
pip install dekeyrej-plain-pages
```

## 🛠️ Usage

```python
from pages.serverpage import ServerPage
from pages.displaypage import DisplayPage

class MyServer(ServerPage):
    def update(self):
        # Fetch data, write to DB, publish to Redis
        pass

class MyDisplay(DisplayPage):
    def display(self):
        # Render data to matrix or image
        pass
```

## 🔐 Secrets & Config
ServerPage supports multiple secret sources from dekeyrej-secretmanager:
- KubeVault - encrypted Kubernetes Secrets with Vault Transit decrypt
- Kubernetes Secrets
- Vault static keys - coming soon!
- Environment variables
- Local JSON files

## 🧪 Status
This project is under active development. Expect updates, refinements, and the occasional moonbeam.

## 📄 License
MIT License. See LICENSE for details.
