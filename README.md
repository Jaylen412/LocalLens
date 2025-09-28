# ForgeAI

### Install

```bash
python3 -m pip install "fastapi[standard]" httpx
```

### Getting started

```bash
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

### Query Params

![Screenshot](/static/query-params.png)

```
* The reviews endpoint requires the following:
    * q: The business name
        - the more specific the better ex: Fixins Soul Kitchen Detroit
    * limit: The amount of reviews to pull in
    * sort_by: most_relevant is the default value
```

### SerpAPI

```
* visit https://serpapi.com/
* Create an account
* Copy API key
* Create .env file locally
* create environment variable SERP_API_KEY and past key value
```

![Screenshot](/static/env-variables.png)

### CloudFlare Tunneling

### Install

```bash
brew install cloudflare/cloudflare/cloudflared

```

### Initialize Tunnel

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

### Shutdown Tunnel

```
CTRL + C
```

### ChatGPT Integration
