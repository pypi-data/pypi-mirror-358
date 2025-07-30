from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .storage import get_async_session

app = FastAPI(title="Phoenix‑AI Audit Services", version="0.6.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


class ToolIn(BaseModel):
    tool_name: str
    tool_type: str
    endpoint_url: str
    description: str | None = None
    version: str | None = None


class AgentIn(BaseModel):
    agent_name: str
    agent_type: str
    description: str | None = None


class PrincipalIn(BaseModel):
    principal_oid: str
    principal_type: str
    principal_upn: str
    display_name: str
    tenant_id: str


class AgentACLIn(BaseModel):
    agent_id: int
    principal_oid: str
    role: str


class PromptIn(BaseModel):
    prompt_name: str
    prompt_type: str
    content: str
    version: str | None = None


class OrchestrationIn(BaseModel):
    source_agent_id: int
    target_agent_id: int
    trigger_type: str
    handoff_type: str
    conditions: dict
    tool_context_share: bool


class AuditIn(BaseModel):
    agent_id: int
    event_type: str
    session_id: str
    payload: dict


@app.post("/tool")
async def create_tool(data: ToolIn, db: AsyncSession = Depends(get_async_session)):
    await crud.create_tool(db, data.model_dump())
    return {"result": "created"}


@app.get("/tools")
async def list_tools(db: AsyncSession = Depends(get_async_session)):
    return await crud.list_tools(db)


@app.put("/tool/{tool_name}")
async def update_tool(
    tool_name: str, data: ToolIn, db: AsyncSession = Depends(get_async_session)
):
    await crud.update_tool(db, tool_name, data.model_dump())
    return {"result": "updated"}


@app.delete("/tool/{tool_name}")
async def delete_tool(tool_name: str, db: AsyncSession = Depends(get_async_session)):
    await crud.delete_tool(db, tool_name)
    return {"result": "deleted"}


@app.post("/agent")
async def create_agent(data: AgentIn, db: AsyncSession = Depends(get_async_session)):
    await crud.create_agent(db, data.model_dump())
    return {"result": "created"}


@app.get("/agents")
async def list_agents(db: AsyncSession = Depends(get_async_session)):
    return await crud.list_agents(db)


@app.put("/agent/{agent_name}")
async def update_agent(
    agent_name: str, data: AgentIn, db: AsyncSession = Depends(get_async_session)
):
    await crud.update_agent(db, agent_name, data.model_dump())
    return {"result": "updated"}


@app.post("/principal")
async def upsert_principal(
    data: PrincipalIn, db: AsyncSession = Depends(get_async_session)
):
    await crud.upsert_principal(db, data.model_dump())
    return {"result": "upserted"}


@app.post("/agent-acl")
async def grant_acl(data: AgentACLIn, db: AsyncSession = Depends(get_async_session)):
    await crud.grant_acl(db, data.model_dump())
    return {"result": "granted"}


@app.get("/agent/{agent_id}/acl")
async def list_acl(agent_id: int, db: AsyncSession = Depends(get_async_session)):
    return await crud.list_acl(db, agent_id)


@app.delete("/agent-acl")
async def revoke_acl(
    agent_id: int = Query(...),
    principal_oid: str = Query(...),
    db: AsyncSession = Depends(get_async_session),
):
    await crud.revoke_acl(db, agent_id, principal_oid)
    return {"result": "revoked"}


@app.post("/prompt")
async def create_prompt(data: PromptIn, db: AsyncSession = Depends(get_async_session)):
    await crud.create_prompt(db, data.model_dump())
    return {"result": "created"}


@app.get("/prompts")
async def list_prompts(db: AsyncSession = Depends(get_async_session)):
    return await crud.list_prompts(db)


@app.put("/prompt/{prompt_name}")
async def update_prompt(
    prompt_name: str, data: PromptIn, db: AsyncSession = Depends(get_async_session)
):
    await crud.update_prompt(db, prompt_name, data.model_dump())
    return {"result": "updated"}


@app.post("/orchestration")
async def create_orch(
    data: OrchestrationIn, db: AsyncSession = Depends(get_async_session)
):
    await crud.create_orch(db, data.model_dump())
    return {"result": "created"}


@app.get("/orchestrations")
async def list_orch(db: AsyncSession = Depends(get_async_session)):
    return await crud.list_orch(db)


@app.delete("/orchestration/{orch_id}")
async def delete_orch(orch_id: int, db: AsyncSession = Depends(get_async_session)):
    await crud.delete_orch(db, orch_id)
    return {"result": "deleted"}


@app.post("/audit")
async def emit_audit(data: AuditIn, db: AsyncSession = Depends(get_async_session)):
    await crud.emit_audit(db, data.model_dump())
    return {"result": "recorded"}
