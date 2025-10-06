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
    * sort_by: most_relevant is the default value newest is the secondary option
    * inlcude_competitors: local businesses in similar industries. Boolean value
    * include_popular_times: Hours of the day the business is at it's peak opposed to hours it scales down. Boolean value
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

```
* Once application server is started & CloudFlare has been started take the URL provided
* Open swagger docs(PROVIDED URL HERE/docs)
* Click the link /openapi.json
* Copy the schema and paste into the action section of ChatGPT
* Add in the server section to the schema. This enables ChatGPT to contact the application.
```

![Screenshot](/static/OpenAPI-schema.png)

![Screenshot](/static/chatgpt-actions.png)

![Screenshot](/static/servers-section.png)

### Create Free Privacy Policy

![Screenshot](/static/privacy-policies.png)

### Generated Policy Link for GPT

![Screenshot](/static/generated-privacy-policy.png)

```
* Create a privacy policy if you want others to be accessible to the GPT otherwise click update and test the GPT
    * https://www.privacypolicies.com/
```

### Application Logs

![Screenshot](/static/application-log.png)
![Screenshot](/static/swagger-logs.png)

```
* You should see logs of the request on your VSCODE terminal & Swagger

```
