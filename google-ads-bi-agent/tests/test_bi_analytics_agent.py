import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import asyncio
from agents.bi_analytics_agent import BIAnalyticsAgent

class TestBIAnalyticsAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_bus = MagicMock()
        # Mock subscribe to do nothing
        self.mock_bus.subscribe = MagicMock()
        self.mock_bus.publish = MagicMock()
        # Setup publish to return a future so await works
        f = asyncio.Future()
        f.set_result(None)
        self.mock_bus.publish.return_value = f

        # Patch Gemini to avoid API calls and key checks
        with patch('agents.bi_analytics_agent.ChatGoogleGenerativeAI') as MockGemini:
            with patch('os.getenv', return_value="fake-key"):
                self.agent = BIAnalyticsAgent(bus=self.mock_bus)
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
        
        # Test the hard metrics calculation directly (Sync method)
        df = pd.DataFrame([item['metrics'] | {'name': item['name'], 'id': item['id'], 'status': item['status']} for item in raw_data])
        stats = self.agent._calculate_hard_metrics(df)
        
        self.assertEqual(stats['total_spend'], 150.00)
        self.assertEqual(stats['total_conversions'], 5)
        self.assertEqual(stats['global_cpa'], 30.0) # 150 / 5
        self.assertEqual(len(stats['wasteful_spend']), 1) # Campaign B has 0 conversions and cost > 0
        self.assertEqual(stats['wasteful_spend'][0]['name'], "Campaign B")

    async def test_handle_data_flow(self):
        """Tests if data reception triggers report generation and publishing"""
        raw_data = [{"id": "1", "name": "Test", "status": "ENABLED", "metrics": {"clicks": 1, "impressions": 1, "cost": 10.0, "conversions": 1, "cpa": 10.0}}]

        # Mock generate_performance_report to avoid LLM call
        self.agent.generate_performance_report = MagicMock()
        f = asyncio.Future()
        f.set_result({"report": "mock"})
        self.agent.generate_performance_report.return_value = f

        await self.agent.handle_data(raw_data)

        # Verify it published REPORT_READY
        self.mock_bus.publish.assert_called_with("REPORT_READY", {"report": "mock"})

if __name__ == '__main__':
    unittest.main()
