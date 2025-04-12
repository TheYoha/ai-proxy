from fastapi import FastAPI, Request
import httpx
import json
from datetime import datetime
from supabase import create_client
import os

app = FastAPI()

# Supabase setup
SUPABASE_URL = "https://utcuhckkcgdzwcktvgva.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0Y3VoY2trY2dkendja3R2Z3ZhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDQ2OTY4MywiZXhwIjoyMDYwMDQ1NjgzfQ.KTu3kyUkkX1iGzy1L4HQZVsHxB3MRoBnNUvg-suhb1E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def log_call(method, path, model, status_code):
    await supabase.table("api_calls").insert({
        "method": method,
        "path": path,
        "model": model,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat()
    }).execute()
    print("Insert response:", res)


@app.api_route("/proxy/openai/{path:path}", methods=["POST", "GET", "PUT", "DELETE"])
async def proxy_openai(request: Request, path: str):
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

    try:
        body = await request.body()
        body_data = json.loads(body)
        model = body_data.get("model", "unknown")
    except:
        model = "unknown"

    await log_call(request.method, path, model, response.status_code)

    return response.json()

@app.get("/")
async def health_check():
    return {"status": "OK", "message": "OpenAI Proxy is running"}
