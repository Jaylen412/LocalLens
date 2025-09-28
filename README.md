# ForgeAI

### Install

```bash
python3 -m pip install "fastapi[standard]" httpx
```

### Getting started

```bash
# create file: main.py

#FastAPI import
from fastapi import FastAPI

# FastAPI instance name
app = FastAPI()
```

### Start server

```bash
uvicorn main:app --reload
# uvicorn <filename without .py>:<FastAPI instance name>
```

## CloudFlare Tunneling

### Install

```bash
brew install cloudflare/cloudflare/cloudflared

```

### Initialize Tunnel

```bash
cloudflared tunnel --url http://localhost:8000 #port number here

```

### Shutdown Tunnel

`CTRL + C`
