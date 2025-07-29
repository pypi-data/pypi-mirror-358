
import typer
from rich import print
from typing import Annotated, Optional
import json
import aiohttp
from meshagent.tools import Toolkit
from meshagent.api import RoomClient, ParticipantToken, WebSocketClientProtocol, RoomException
from meshagent.api.helpers import meshagent_base_url, websocket_room_url
from meshagent.api.services import send_webhook
from meshagent.cli import async_typer
from meshagent.cli.helper import get_client, print_json_table, set_active_project, resolve_project_id
from meshagent.cli.helper import set_active_project, get_active_project, resolve_project_id, resolve_api_key
from meshagent.agents.chat import ChatBot
from meshagent.openai import OpenAIResponsesAdapter
from meshagent.openai.tools.responses_adapter import LocalShellTool


from meshagent.agents.chat import ChatBotThreadOpenAIImageGenerationTool

from typing import List

from meshagent.api import RequiredToolkit, RequiredSchema

app = async_typer.AsyncTyper()

@app.async_command("join")
async def make_call(
    *,
    project_id: str = None,
    room: Annotated[str, typer.Option()],
    api_key_id: Annotated[Optional[str], typer.Option()] = None,
    name: Annotated[str, typer.Option(..., help="Participant name")] = "cli",
    role: str = "agent",
    agent_name: Annotated[str, typer.Option(..., help="Name of the agent to call")],
    rule: Annotated[List[str], typer.Option("--rule", "-r", help="a system rule")] = [],
    toolkit: Annotated[List[str], typer.Option("--toolkit", "-t", help="the name or url of a required toolkit")] = [],
    schema: Annotated[List[str], typer.Option("--schema", "-s", help="the name or url of a required schema")] = [],
    image_generation: Annotated[Optional[str], typer.Option(..., help="Name of an image gen provider (openai)")] = None,
):
    account_client = await get_client()
    try:
        project_id = await resolve_project_id(project_id=project_id)
        api_key_id = await resolve_api_key(project_id, api_key_id)
        
        key = (await account_client.decrypt_project_api_key(project_id=project_id, id=api_key_id))["token"]

        token = ParticipantToken(
            name=name,
            project_id=project_id,
            api_key_id=api_key_id
        )
        token.add_role_grant(role=role)
        token.add_room_grant(room)

        
        print("[bold green]Connecting to room...[/bold green]")
        async with RoomClient(
            protocol=WebSocketClientProtocol(url=websocket_room_url(room_name=room, base_url=meshagent_base_url()),
                                            token=token.to_jwt(token=key))
        ) as client:
            
            requirements = []
            
            toolkits = []

            for t in toolkit:
                requirements.append(RequiredToolkit(name=t))
            
            for t in schema:
                requirements.append(RequiredSchema(name=t))

            class CustomChatbot(ChatBot):

                async def get_thread_toolkits(self, *, thread_context, participant):
                    toolkits = await super().get_thread_toolkits(thread_context=thread_context, participant=participant)
                    
                    thread_toolkit = Toolkit(name="thread_toolkit", tools=[])
                    if image_generation != None:
                        if image_generation == "openai":
                            print("adding openai image gen to thread")
                            thread_toolkit.tools.append(ChatBotThreadOpenAIImageGenerationTool(thread_context=thread_context, partial_images=3))
                        else:
                            raise Exception("image-generation must be openai")
                    toolkits.append(thread_toolkit)
                    return toolkits
                
                
            bot = CustomChatbot(
                llm_adapter=OpenAIResponsesAdapter(),
                name=agent_name,
                requires=requirements,
                toolkits=toolkits,
                rules=rule if len(rule) > 0 else None
            )

            await bot.start(room=client)
            try:
                await client.protocol.wait_for_close()
            except KeyboardInterrupt:
                await bot.stop()
        
    finally:
        await account_client.close()
