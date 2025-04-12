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


from supabase import create_client
import os

# Supabase setup (add to top of file)
SUPABASE_URL = "https://utcuhckkcgdzwcktvgva.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0Y3VoY2trY2dkendja3R2Z3ZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ0Njk2ODMsImV4cCI6MjA2MDA0NTY4M30.J3bYl36RNzNrqFmUq8x1vaww_f_Jegd35dL2ScqKvyk"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Replace `print(...)` with this:
async def log_call(method, path, model, status_code):
    supabase.table("api_calls").insert({
        "method": method,
        "path": path,
        "model": model,
        "status_code": status_code,
        "timestamp": "now()"
    }).execute()
