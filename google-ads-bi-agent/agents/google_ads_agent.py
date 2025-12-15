import os
from mcp.google_ads_client import GoogleAdsClientWrapper
from typing import List, Dict

class GoogleAdsAgent:
    def __init__(self, config_path=None):
        # Lógica robusta de Path:
        # Se nenhum path for passado, assume que está em 'config/settings.yaml' 
        # relativo à raiz do projeto, independente de onde o script é rodado.
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "settings.yaml")
        
        self.mcp_client = GoogleAdsClientWrapper(config_path)

    def fetch_campaign_data(self, customer_id: str, date_range: str = "LAST_30_DAYS") -> List[Dict]:
        """
        Busca dados, converte micros e calcula métricas derivadas (CPA).
        """
        query = f"""
            SELECT 
                campaign.id, 
                campaign.name, 
                campaign.status,
                metrics.clicks, 
                metrics.impressions, 
                metrics.ctr, 
                metrics.average_cpc, 
                metrics.cost_micros, 
                metrics.conversions 
            FROM campaign 
            WHERE segments.date DURING {date_range}
        """
        
        # O Wrapper retorna uma lista de dicionários brutos
        raw_data = self.mcp_client.execute_query(customer_id, query)
        
        processed_data = []
        for row in raw_data:
            # Tratamento de Moeda (Micros -> Real)
            cost_real = row.get('cost_micros', 0) / 1_000_000
            conversions = row.get('conversions', 0)
            
            # Tratamento de Divisão por Zero
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
