from mcp.server.fastmcp import FastMCP
import logging

# Config logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP Server
mcp = FastMCP("GoogleAdsService")

@mcp.tool()
def fetch_campaign_data(customer_id: str, date_range: str = "LAST_30_DAYS") -> str:
    """
    Fetches campaign data for a given customer ID.
    Returns a JSON string with the data.
    """
    logger.info(f"MCP Tool called: fetch_campaign_data for {customer_id}")

    # Mock Response Logic (as per previous requirements)
    # In a real implementation, this would use the google-ads library
    mock_data = [
        {"campaign_id": "111", "campaign_name": "Campanha_Vendas_BlackFriday", "clicks": 150, "impressions": 5000, "cost_micros": 50000000, "conversions": 10, "status": "ENABLED"},
        {"campaign_id": "222", "campaign_name": "Campanha_Branding_Institucional", "clicks": 500, "impressions": 20000, "cost_micros": 120000000, "conversions": 2, "status": "ENABLED"},
        {"campaign_id": "333", "campaign_name": "Campanha_Teste_ProdutoX", "clicks": 20, "impressions": 800, "cost_micros": 8000000, "conversions": 0, "status": "PAUSED"},
    ]

    import json
    return json.dumps(mock_data)

if __name__ == "__main__":
    # If run directly, starts the MCP server over stdio
    mcp.run()
