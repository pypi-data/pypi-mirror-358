# Victoria Important Dates MCP

A Model Context Protocol (MCP) server that provides access to Victoria, Australia's important dates and holidays API.

The API is documented [here](https://www.developer.vic.gov.au/index.php?option=com_apiportal&view=apitester&usage=api&apitab=tests&apiName=Victorian+Government+-+Important+Dates+API&apiId=65c5cce0-efcb-4dba-bdde-f391d3a35dc2&managerId=1&type=rest&apiVersion=2.0.0&Itemid=153&swaggerVersion=2.0) 

## Features

- Access to Victoria, Australia public holidays and important dates
- MCP-compatible server implementation
- Easy integration with MCP clients
- RESTful API wrapper for Victoria government data

## Installation

```bash
pip install vic-au-important-dates-mcp
```

## Usage

### Running the MCP Server

After installation, you can run the MCP server directly:

```bash
vic-au-dates-mcp-server
```

Or using uv:

```bash
uv run vic-au-dates-mcp-server
```


### Direct API Usage

```python
from vic_au_important_dates_mcp.client import VictoriaImportantDatesClient

# Create a client instance
client = VictoriaImportantDatesClient()

# Get holidays for a specific year
holidays = client.get_holidays(2024)

# Get holidays for a specific date range
holidays = client.get_holidays_range("2024-01-01", "2024-12-31")
```

## Configuration

The package uses environment variables for configuration:

- `DEVELOPER_VIC_GOV_AU_KEY`: 
- `DEVELOPER_VIC_GOV_AU_SECRET`: 
- `BASE_URL` (The current known URL is `https://wovg-community.gateway.prod.api.vic.gov.au/vicgov/v2.0/` and is subject to change in the future )

Register at [developer.vic.gov.au][https://developer.vic.gov.au] to get your developer key/secret


## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issues page.
