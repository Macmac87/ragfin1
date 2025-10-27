"""
╔══════════════════════════════════════════════════════════╗
║                      🌐 RAGFIN1 API                      ║
║                       BY MGA                             ║
║              FOUNDER: Mario Cardozo | CEO                ║
║                                                          ║
║   Intelligent Remittance Information for the Americas    ║
║              © 2025 All rights reserved                  ║
╚══════════════════════════════════════════════════════════╝

FastAPI REST API Server
7 endpoints for remittance intelligence powered by Groq AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import uvicorn
from groq import Groq

# Initialize Groq client
groq_client = None
if os.getenv('GROQ_API_KEY'):
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Pydantic models
class QueryRequest(BaseModel):
    question: str = Field(..., description="User's question about remittances")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context")

class QueryResponse(BaseModel):
    answer: str
    intent: str
    sources: List[str]
    context_used: bool
    confidence: float
    timestamp: str

# Initialize FastAPI
app = FastAPI(
    title="RAGFIN1 API",
    description="Intelligent Remittance Information API powered by Groq AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RAGFIN1",
        "version": "1.0.0",
        "message": "Welcome to RAGFIN1 API"
    }

@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Main query endpoint using Groq AI"""
    try:
        if not groq_client:
            # Fallback response if no API key
            return QueryResponse(
                answer=f"I received your question: '{request.question}'. To provide AI-powered answers, please configure GROQ_API_KEY.",
                intent="informational",
                sources=["system"],
                context_used=False,
                confidence=0.5,
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are RAGFIN1, an expert on international remittances, money transfers, and financial services for the Americas. Provide accurate, helpful information about sending money internationally, comparing providers, exchange rates, and regulations."
                },
                {
                    "role": "user",
                    "content": request.question
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = chat_completion.choices[0].message.content
        
        return QueryResponse(
            answer=answer,
            intent="comparison" if "compare" in request.question.lower() else "informational",
            sources=["groq_ai", "general_knowledge"],
            context_used=bool(request.context),
            confidence=0.85,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/providers")
async def get_providers():
    """List available remittance providers"""
    providers = [
        {"id": "wise", "name": "Wise", "countries": ["USA", "UK", "EU", "MEX", "COL"]},
        {"id": "remitly", "name": "Remitly", "countries": ["USA", "MEX", "PHL", "IND"]},
        {"id": "western_union", "name": "Western Union", "countries": ["Worldwide"]},
        {"id": "moneygram", "name": "MoneyGram", "countries": ["Worldwide"]},
        {"id": "xoom", "name": "Xoom", "countries": ["USA", "MEX", "PHL", "IND"]}
    ]
    return {"providers": providers, "total": len(providers)}

@app.get("/api/v1/countries")
async def get_countries():
    """List supported countries"""
    countries = [
        {"code": "USA", "name": "United States"},
        {"code": "MEX", "name": "Mexico"},
        {"code": "COL", "name": "Colombia"},
        {"code": "BRA", "name": "Brazil"},
        {"code": "ARG", "name": "Argentina"}
    ]
    return {"countries": countries, "total": len(countries)}

@app.post("/api/v1/compare")
async def compare_providers(
    amount: float,
    from_country: str,
    to_country: str
):
    """Compare remittance providers"""
    return {
        "comparison": [
            {
                "provider": "Wise",
                "fee": amount * 0.01,
                "exchange_rate": 17.5,
                "total_received": amount * 17.5 - (amount * 0.01),
                "delivery_time": "1-2 days"
            },
            {
                "provider": "Remitly",
                "fee": 3.99,
                "exchange_rate": 17.3,
                "total_received": amount * 17.3 - 3.99,
                "delivery_time": "minutes"
            }
        ],
        "best_rate": "Wise",
        "fastest": "Remitly"
    }

@app.post("/api/v1/recommend")
async def get_recommendation(
    amount: float,
    from_country: str,
    to_country: str,
    priority: str = "cost"
):
    """Get provider recommendation"""
    return {
        "recommendation": {
            "provider": "Wise" if priority == "cost" else "Remitly",
            "reason": f"Best option for {priority}",
            "estimated_cost": amount * 0.01 if priority == "cost" else 3.99
        }
    }

@app.get("/api/v1/rates")
async def get_exchange_rates(from_currency: str, to_currency: str):
    """Get current exchange rates"""
    rates = {
        "USD-MXN": 17.5,
        "USD-COL": 4200,
        "USD-BRL": 5.2
    }
    key = f"{from_currency}-{to_currency}"
    return {
        "from": from_currency,
        "to": to_currency,
        "rate": rates.get(key, 1.0),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/regulations")
async def get_regulations(country: str):
    """Get regulatory information"""
    return {
        "country": country,
        "regulations": [
            "Maximum single transfer limit",
            "KYC requirements",
            "Tax implications"
        ],
        "updated": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    print("\n" + "="*50)
    print("🌐 RAGFIN1 API Server")
    print("="*50)
    print(f"Starting on http://0.0.0.0:{port}")
    print(f"Docs: http://0.0.0.0:{port}/docs")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
