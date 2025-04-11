from fastapi import FastAPI, Request
import httpx
import json
from datetime import datetime

app = FastAPI()

@app.api_route("/proxy/openai/{path:path}", methods=["POST", "GET", "PUT", "DELETE"])
async def proxy_openai(request: Request, path: str):
    # Forward request to OpenAI
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"https://api.openai.com/{path}",
            headers={
                "Authorization": request.headers.get("Authorization"),
                "Content-Type": "application/json"
            },
            content=await request.body()
        )
    
    # Log the request details
    try:
        body = await request.body()
        body_data = json.loads(body)
        model = body_data.get("model", "unknown")
    except:
        model = "unknown"
    
    print(f"""
    [{datetime.now().isoformat()}]
    Endpoint: {path}
    Model: {model}
    Status: {response.status_code}
    """)
    
    return response.json()

@app.get("/")
async def health_check():
    return {"status": "OK", "message": "OpenAI Proxy is running"}