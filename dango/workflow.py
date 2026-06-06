"""
Agno Workflow definition for the Discord AI pipeline.
"""

from agno.workflow import Step, Workflow

from .steps.call_agent import _initialize_agents, call_discord_agent
from .steps.fetch_history import fetch_and_process_history
from .steps.send_response import send_discord_response
from .steps.table_steps import extract_and_render_tables


def create_discord_workflow() -> Workflow:
    _initialize_agents()
    return Workflow(
        name="DiscordAIPipeline",
        steps=[
            Step(name="FetchHistory", executor=fetch_and_process_history),
            Step(name="LLMChat", executor=call_discord_agent),
            Step(name="ExtractRenderTables", executor=extract_and_render_tables),
            Step(name="SendResponse", executor=send_discord_response),
        ],
    )
