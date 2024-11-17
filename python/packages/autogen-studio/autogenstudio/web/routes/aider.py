from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AiderRequest(BaseModel):
    message: str

class AiderResponse(BaseModel):
    response: str

@router.post("/process", response_model=AiderResponse)
async def process_aider_request(request: AiderRequest):
    # This is a placeholder. The actual implementation will be in the Docker container.
    return AiderResponse(response="Aider processing is not available in this environment. Please use the Docker container.")
