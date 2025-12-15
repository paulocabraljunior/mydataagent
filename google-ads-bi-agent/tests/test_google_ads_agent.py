import unittest
from agents.google_ads_agent import GoogleAdsAgent
import os

class TestGoogleAdsAgent(unittest.TestCase):
    def setUp(self):
        # Ensure we point to the correct config file based on execution context
        # Assuming execution from /home/kid/Documents/mydataagent
        config_path = "google-ads-bi-agent/config/settings.yaml"
        self.agent = GoogleAdsAgent(config_path=config_path)
        self.customer_id = "1234567890"

    def test_fetch_structure(self):
        """Tests if the return structure has necessary keys for BI"""
        data = self.agent.fetch_campaign_data(self.customer_id)
        
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0, "Mock should return data")
        
        first_item = data[0]
        self.assertIn("id", first_item)
        self.assertIn("metrics", first_item)
        self.assertIn("cost", first_item["metrics"])
        
        # Verify micro conversion (Mock returns 50000000 -> 50.0)
        if first_item["id"] == "111":
            self.assertEqual(first_item["metrics"]["cost"], 50.0)

if __name__ == '__main__':
    unittest.main()
