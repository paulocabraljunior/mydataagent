import unittest
from agents.bi_analytics_agent import BIAnalyticsAgent
import pandas as pd
from unittest.mock import MagicMock, patch

class TestBIAnalyticsAgent(unittest.TestCase):
    def setUp(self):
        # Mocking OpenAI to avoid API calls during initialization if any, 
        # though user code initializes in __init__. 
        # We need to patch ChatOpenAI before creating the agent instance if we want to test without a key or to mock it.
        with patch('agents.bi_analytics_agent.ChatOpenAI') as MockChat:
            with patch('os.getenv', return_value="fake-key"):
                self.agent = BIAnalyticsAgent()
                self.agent.llm = MagicMock() # Mock LLM interactions

    def test_calculate_hard_metrics(self):
        # Sample raw data mirroring the output of GoogleAdsAgent
        raw_data = [
            {
                "id": "1", "name": "Campaign A", "status": "ENABLED",
                "metrics": {"clicks": 100, "impressions": 1000, "cost": 50.00, "conversions": 5, "ctr": 0.1, "average_cpc": 0.5, "cost_micros": 50000000}
            },
            {
                "id": "2", "name": "Campaign B", "status": "ENABLED",
                "metrics": {"clicks": 200, "impressions": 2000, "cost": 100.00, "conversions": 0, "ctr": 0.1, "average_cpc": 0.5, "cost_micros": 100000000}
            }
        ]
        
        # Test the hard metrics calculation directly
        df = pd.DataFrame([item['metrics'] | {'name': item['name'], 'id': item['id'], 'status': item['status']} for item in raw_data])
        stats = self.agent._calculate_hard_metrics(df)
        
        self.assertEqual(stats['total_spend'], 150.00)
        self.assertEqual(stats['total_conversions'], 5)
        self.assertEqual(stats['global_cpa'], 30.0) # 150 / 5
        self.assertEqual(len(stats['wasteful_spend']), 1) # Campaign B has 0 conversions and cost > 0
        self.assertEqual(stats['wasteful_spend'][0]['name'], "Campaign B")

if __name__ == '__main__':
    unittest.main()
