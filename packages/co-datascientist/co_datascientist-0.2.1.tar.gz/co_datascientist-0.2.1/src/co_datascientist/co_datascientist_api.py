import httpx
import logging
from pydantic import BaseModel

from .models import Workflow, CodeVersion, SystemInfo, Prompt, CodeResult
from .settings import settings, Settings


class CoDatascientistBackendResponse(BaseModel):
    workflow: Workflow
    code_to_run: CodeVersion | None = None


async def test_connection() -> str:
    return await _call_co_datascientist_client("/test_connection", {})


async def start_workflow(code: str, system_info: SystemInfo) -> CoDatascientistBackendResponse:
    response = await _call_co_datascientist_client("/start_workflow", {
        "prompt": Prompt(code=code).model_dump(),
        "system_info": system_info.model_dump()
    })
    return CoDatascientistBackendResponse.model_validate(response)


async def finished_running_code(workflow_id, code_version_id, result: CodeResult) -> CoDatascientistBackendResponse:
    response = await _call_co_datascientist_client(
        "/finished_running_code",
        {"workflow_id": workflow_id, "code_version_id": code_version_id, "result": result.model_dump()})
    return CoDatascientistBackendResponse.model_validate(response)


async def stop_workflow(workflow_id) -> None:
    await _call_co_datascientist_client("/stop_workflow", {"workflow_id": workflow_id})


# NEW BATCH EXECUTION API METHODS
class BatchResponse(BaseModel):
    workflow: Workflow
    batch_to_run: list[CodeVersion] | None = None
    batch_id: str


async def get_batch_to_run(workflow_id: str, batch_size: int = None) -> BatchResponse:
    """Get a batch of programs to run in parallel"""
    request_data = {"workflow_id": workflow_id}
    if batch_size is not None:
        request_data["batch_size"] = batch_size
    
    response = await _call_co_datascientist_client("/get_batch_to_run", request_data)
    return BatchResponse.model_validate(response)


async def finished_running_batch(workflow_id: str, batch_id: str, results: list) -> BatchResponse:
    """Submit results for an entire batch"""
    response = await _call_co_datascientist_client("/finished_running_batch", {
        "workflow_id": workflow_id,
        "batch_id": batch_id,
        "results": results
    })
    return BatchResponse.model_validate(response)


# NEW COST TRACKING API METHODS
async def get_user_costs() -> dict:
    """Get detailed costs for the authenticated user"""
    return await _call_co_datascientist_client("/user/costs", {})


async def get_user_costs_summary() -> dict:
    """Get summary costs for the authenticated user"""
    return await _call_co_datascientist_client("/user/costs/summary", {})


async def get_user_usage_status() -> dict:
    """Get usage status including remaining money and limits"""
    return await _call_co_datascientist_client("/user/usage_status", {})


async def get_workflow_costs(workflow_id: str) -> dict:
    """Get costs for a specific workflow"""
    return await _call_co_datascientist_client(f"/user/costs/workflow/{workflow_id}", {})


async def _call_co_datascientist_client(path, data):
    # Ensure API key is available before making the request
    if not settings.api_key.get_secret_value():
        settings.get_api_key()
    
    url = settings.backend_url + path
    logging.info(f"Dev mode: {settings.dev_mode}")
    logging.info(f"Backend URL: {settings.backend_url}")
    logging.info(f"Making request to: {url}")
    logging.info(f"Request data keys: {list(data.keys()) if data else 'No data'}")
    
    # Prepare headers
    headers = {"Authorization": f"Bearer {settings.api_key.get_secret_value()}"}
    
    # Add OpenAI key header if available
    openai_key = settings.get_openai_key(prompt_if_missing=False)
    if openai_key:
        headers["X-OpenAI-Key"] = openai_key
        logging.info("Including user OpenAI key in request")
    else:
        logging.info("No user OpenAI key - using TropiFlow's free tier")
    
    try:
        async with httpx.AsyncClient(verify=settings.verify_ssl, timeout=None) as client:
            if data:
                # POST request
                response = await client.post(url, headers=headers, json=data)
            else:
                # GET request
                response = await client.get(url, headers=headers)
            
            logging.info(f"Response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logging.error(f"Request to {url} failed: {e}")
        raise

