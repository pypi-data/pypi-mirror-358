from mcp.server.fastmcp import FastMCP
from vic_au_important_dates_mcp import VictoriaDatesClient, ImportantDatesResponse
from typing import Optional
import asyncio

mcp = FastMCP("important_dates_server")

@mcp.tool()
async def get_dates(from_date, to_date, type="PUBLIC_HOLIDAY") -> Optional[ImportantDatesResponse]:
    """Get a list of important dates for the state of Victoria, Australia.

    Args:
        from_date: From date in the format YYYY-MM-DD
        to_date: To date in the format YYYY-MM-DD
        type: can be one of PUBLIC_HOLIDAY,DAYLIGHT_SAVING,SCHOOL_TERM,SCHOOL_HOLIDAY,FLAG_NOTIFICATION,PARLIAMENT_SITTING,MULTI_FAITH
    """
    client = VictoriaDatesClient()
    return client.fetch_dates(type=type, from_date=from_date, to_date=to_date)

def main():
    """Entry point for the MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()