import json
import logging
from typing import List, Dict

# Em um cenário real MCP, usaríamos um MCP Client para conectar ao server.
# Para este MVP "in-process", importaremos a função da ferramenta diretamente
# do nosso arquivo server.py

class GoogleAdsAgent:
    def __init__(self, bus):
        self.bus = bus
        self.bus.subscribe("CMD_START_EXTRACT", self.handle_command)

    async def handle_command(self, payload: Dict):
        print("📥 Google Ads Agent: Received extraction command.")
        customer_id = payload.get("customer_id")
        
        try:
            # Simulating MCP Client Call
            # In a real distributed system, this would be: client.call_tool("fetch_campaign_data", ...)

            # Importando do novo pacote renomeado para evitar conflito com 'mcp' lib
            try:
                from my_mcp.server import fetch_campaign_data
            except ImportError:
                 # Fallback path hack se rodar da raiz
                 import sys
                 sys.path.append('google-ads-bi-agent')
                 from my_mcp.server import fetch_campaign_data

            # Executando a ferramenta (Sync tool wrapped in async call if needed)
            import asyncio
            # Simulando latência de rede
            await asyncio.sleep(0.5)

            raw_json = fetch_campaign_data(customer_id)
            raw_data = json.loads(raw_json)

            processed_data = self._process_data(raw_data)

            print(f"✅ Google Ads Agent: Data fetched ({len(processed_data)} records). Publishing...")
            await self.bus.publish("DATA_FETCHED", processed_data)

        except Exception as e:
            print(f"❌ Google Ads Agent Error: {e}")
            import traceback
            traceback.print_exc()
            await self.bus.publish("ERROR", {"source": "ADS_AGENT", "message": str(e)})

    def _process_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Normaliza os dados brutos vindos do MCP Tool."""
        processed_data = []
        for row in raw_data:
            cost_real = row.get('cost_micros', 0) / 1_000_000
            conversions = row.get('conversions', 0)
            cpa = round(cost_real / conversions, 2) if conversions > 0 else 0.0
            
            processed_data.append({
                "id": str(row.get('campaign_id')),
                "name": row.get('campaign_name'),
                "status": row.get('status'),
                "metrics": {
                    "clicks": row.get('clicks'),
                    "impressions": row.get('impressions'),
                    "cost": round(cost_real, 2),
                    "conversions": conversions,
                    "cpa": cpa
                }
            })
        return processed_data
