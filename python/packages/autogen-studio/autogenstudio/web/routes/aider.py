from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from autogen_ext.agents.aider_agent import AiderAgent

router = APIRouter()

class AiderRequest(BaseModel):
    message: str

class AiderResponse(BaseModel):
    response: str

@router.post("/process", response_model=AiderResponse)
async def process_aider_request(request: AiderRequest):
    try:
        agent = AiderAgent("AiderAgent")
        response = await agent.process_message(request.message)
        return AiderResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
