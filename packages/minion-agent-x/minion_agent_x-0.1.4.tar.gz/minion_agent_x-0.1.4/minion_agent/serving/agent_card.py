from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from minion_agent import AgentFramework

if TYPE_CHECKING:
    from minion_agent import MinionAgent
    from minion_agent.config import ServingConfig


def _get_agent_card(agent: MinionAgent, serving_config: ServingConfig) -> AgentCard:
    skills = []
    for tool in agent._main_agent_tools:
        if hasattr(tool, "name"):
            tool_name = tool.name
            tool_description = tool.description
        elif agent.framework is AgentFramework.LLAMA_INDEX:
            tool_name = tool.metadata.name
            tool_description = tool.metadata.description
        else:
            tool_name = tool.__name__
            tool_description = inspect.getdoc(tool)
        skills.append(
            AgentSkill(
                id=f"{agent.config.name}-{tool_name}",
                name=tool_name,
                description=tool_description,
                tags=[],
            )
        )
    if agent.config.description is None:
        msg = "Agent description is not set. Please set the `description` field in the `AgentConfig`."
        raise ValueError(msg)
    return AgentCard(
        name=agent.config.name,
        description=agent.config.description,
        version=serving_config.version,
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        url=f"http://{serving_config.host}:{serving_config.port}/",
        capabilities=AgentCapabilities(
            streaming=False, pushNotifications=False, stateTransitionHistory=False
        ),
        skills=skills,
    )
