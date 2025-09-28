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
# uvicorn <filename without .py>:<FastAPI instance name>
uvicorn main:app --reload
```

### Swagger Docs

```
* On locally running server visit /docs
```

![Screenshot](/static/swagger-docs.png)

### Qeury Params

![Screenshot](/static/query-params.png)

```
* The reviews endpoint requires the following:
    * q: The business name
        - the more specific the better ex: Fixins Soul Kitchen Detroit
    * limit: The amount of reviews to pull in
    * sort_by: most_relevant is the default value
```

### CloudFlare Tunneling

### Install

```bash
brew install cloudflare/cloudflare/cloudflared

```

### Initialize Tunnel

```bash
cloudflared tunnel --url http://localhost:8000 #port number here

```

### Shutdown Tunnel

```
CTRL + C
```
