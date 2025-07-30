from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (Agent, AgentACL, Audit, Orchestration, Principal, Prompt,
                     Tool)


async def _create(db: AsyncSession, model, data: dict):
    db.add(model(**data))
    await db.commit()


async def _update(db: AsyncSession, model, name_field: str, name: str, data: dict):
    await db.execute(
        update(model).where(getattr(model, name_field) == name).values(**data)
    )
    await db.commit()


async def _delete(db: AsyncSession, model, name_field: str, name: str):
    await db.execute(delete(model).where(getattr(model, name_field) == name))
    await db.commit()


async def _list_all(db: AsyncSession, model):
    res = await db.execute(select(model))
    return [row._asdict() for row in res.mappings().all()]


async def create_tool(db, data):
    await _create(db, Tool, data)


async def list_tools(db):
    return await _list_all(db, Tool)


async def update_tool(db, n, d):
    await _update(db, Tool, "tool_name", n, d)


async def delete_tool(db, n):
    await _delete(db, Tool, "tool_name", n)


async def create_agent(db, data):
    await _create(db, Agent, data)


async def list_agents(db):
    return await _list_all(db, Agent)


async def update_agent(db, n, d):
    await _update(db, Agent, "agent_name", n, d)


async def upsert_principal(db, data):
    await _create(db, Principal, data)


async def grant_acl(db, data):
    await _create(db, AgentACL, data)


async def list_acl(db, aid):
    res = await db.execute(select(AgentACL).where(AgentACL.agent_id == aid))
    return [row._asdict() for row in res.mappings().all()]


async def revoke_acl(db, aid, poid):
    await db.execute(
        delete(AgentACL)
        .where(AgentACL.agent_id == aid)
        .where(AgentACL.principal_oid == poid)
    )
    await db.commit()


async def create_prompt(db, d):
    await _create(db, Prompt, d)


async def list_prompts(db):
    return await _list_all(db, Prompt)


async def update_prompt(db, n, d):
    await _update(db, Prompt, "prompt_name", n, d)


async def create_orch(db, d):
    await _create(db, Orchestration, d)


async def list_orch(db):
    return await _list_all(db, Orchestration)


async def delete_orch(db, oid):
    await db.execute(delete(Orchestration).where(Orchestration.orchestration_id == oid))
    await db.commit()


async def emit_audit(db, d):
    await _create(db, Audit, d)
