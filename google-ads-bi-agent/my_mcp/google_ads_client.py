import os
import yaml
import logging
from typing import List, Dict, Any

# Config logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conditional import for real client to allow running in envs without google-ads installed
try:
    from google.ads.googleads.client import GoogleAdsClient as OfficialClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_LIB_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_LIB_AVAILABLE = False
    logger.warning("⚠️ google-ads library not found. Running in restricted mode (Mock only).")

class GoogleAdsClientWrapper:
    def __init__(self, config_path="config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.use_mock = self.config.get('google_ads', {}).get('use_mock', True)
        self.client = None
        
        if not self.use_mock:
            if not GOOGLE_ADS_LIB_AVAILABLE:
                logger.error("❌ Cannot switch to REAL mode: google-ads library missing.")
                raise ImportError("google-ads library is required for real mode.")
            self._authenticate()
        else:
            logger.warning("⚠️ Starting GoogleAdsClient in MOCK MODE")

    def _load_config(self, path) -> dict:
        try:
            # Adjust path if running from root or elsewhere, simplistic approach
            if not os.path.exists(path):
                # Try relative to the module if needed, but assuming CWD is root
                pass
                
            with open(path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Config file not found at: {path}")
            return {}

    def _authenticate(self):
        try:
            ads_config = self.config.get('google_ads', {})
            # Remove use_mock and other custom keys if necessary before passing to Google
            clean_config = {k: v for k, v in ads_config.items() if k != 'use_mock'}
            
            self.client = OfficialClient.load_from_dict(clean_config)
            logger.info("✅ Successfully authenticated with Google Ads API.")
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            raise

    def execute_query(self, customer_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Executes a GAQL query.
        """
        if self.use_mock:
            return self._mock_response()

        try:
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            
            results = []
            for row in response:
                item = {
                    "campaign_id": row.campaign.id,
                    "campaign_name": row.campaign.name,
                    "clicks": row.metrics.clicks,
                    "impressions": row.metrics.impressions,
                    "cost_micros": row.metrics.cost_micros,
                    "conversions": row.metrics.conversions,
                    "status": row.campaign.status.name
                }
                results.append(item)
            return results

        except GoogleAdsException as ex:
            logger.error(f"Google API Error: {ex.error.code().name}")
            return []

    def _mock_response(self):
        """Mock data for testing"""
        return [
            {"campaign_id": "111", "campaign_name": "Campanha_Vendas_BlackFriday", "clicks": 150, "impressions": 5000, "cost_micros": 50000000, "conversions": 10, "status": "ENABLED"},
            {"campaign_id": "222", "campaign_name": "Campanha_Branding_Institucional", "clicks": 500, "impressions": 20000, "cost_micros": 120000000, "conversions": 2, "status": "ENABLED"},
            {"campaign_id": "333", "campaign_name": "Campanha_Teste_ProdutoX", "clicks": 20, "impressions": 800, "cost_micros": 8000000, "conversions": 0, "status": "PAUSED"},
        ]
