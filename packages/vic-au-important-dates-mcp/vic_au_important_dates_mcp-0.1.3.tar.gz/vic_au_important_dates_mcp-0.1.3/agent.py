from dotenv import load_dotenv
from agents.mcp import MCPServerStdio
from agents import Agent, Runner, trace
from IPython.display import display, Markdown
import asyncio

load_dotenv(override=True)

params = {"command": "uv", "args": ["run", "server.py"]}
async def main():
  async with MCPServerStdio(params=params) as server:
    mcp_tools = await server.list_tools()
    print(mcp_tools)

    instructions = "You are able to answer questions about upcoming important dates in victoria, australia"
    request = "What are the upcoming school holidays in 2025?"
    model = "gpt-4o-mini"
    async with MCPServerStdio(params=params) as mcp_server:
        agent = Agent(name="date_checker", instructions=instructions, model=model, mcp_servers=[mcp_server])
        with trace("date_checker"):
            result = await Runner.run(agent, request)
        print(result.final_output)
    

if __name__ == "__main__":
    asyncio.run(main())
