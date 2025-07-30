from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Tool(Base):
    __tablename__ = "tool"
    tool_id = Column(Integer, primary_key=True)
    tool_name = Column(String(100), unique=True, nullable=False)
    tool_type = Column(String(50))
    endpoint_url = Column(String(255))
    description = Column(Text)
    version = Column(String(20))


class Agent(Base):
    __tablename__ = "agent"
    agent_id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), unique=True, nullable=False)
    agent_type = Column(String(50))
    description = Column(Text)


class Principal(Base):
    __tablename__ = "principal"
    principal_oid = Column(String(36), primary_key=True)
    principal_type = Column(String(20))
    principal_upn = Column(String(255))
    display_name = Column(String(255))
    tenant_id = Column(String(36))


class AgentACL(Base):
    __tablename__ = "agent_acl"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agent.agent_id"))
    principal_oid = Column(String(36))
    role = Column(String(20))


class Prompt(Base):
    __tablename__ = "prompt"
    prompt_id = Column(Integer, primary_key=True)
    prompt_name = Column(String(100), unique=True, nullable=False)
    prompt_type = Column(String(20))
    content = Column(Text)
    version = Column(String(20))


class Orchestration(Base):
    __tablename__ = "orchestration"
    orchestration_id = Column(Integer, primary_key=True)
    source_agent_id = Column(Integer)
    target_agent_id = Column(Integer)
    trigger_type = Column(String(50))
    handoff_type = Column(String(50))
    conditions = Column(JSON)
    tool_context_share = Column(Boolean)


class Audit(Base):
    __tablename__ = "audit"
    audit_id = Column(Integer, primary_key=True)
    agent_id = Column(Integer)
    event_type = Column(String(50))
    session_id = Column(String(100))
    payload = Column(JSON)
