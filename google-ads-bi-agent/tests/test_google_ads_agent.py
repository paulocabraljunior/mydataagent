import unittest
from unittest.mock import MagicMock, patch
import json
import asyncio
from agents.google_ads_agent import GoogleAdsAgent

class TestGoogleAdsAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_bus = MagicMock()
        self.mock_bus.subscribe = MagicMock()
        self.mock_bus.publish = MagicMock()

        # Setup publish to return a future so await works
        f = asyncio.Future()
        f.set_result(None)
        self.mock_bus.publish.return_value = f

        self.agent = GoogleAdsAgent(bus=self.mock_bus)

    async def test_handle_command(self):
        """Tests if command triggers tool call and data publishing"""
        payload = {"customer_id": "123"}
        
        # Mock the tool call inside handle_command
        # handle_command has imports inside. A global patch on 'my_mcp.server.fetch_campaign_data' should work if the import resolves.

        mock_data_json = json.dumps([
            {"campaign_id": "111", "campaign_name": "Test", "clicks": 10, "impressions": 100, "cost_micros": 1000000, "conversions": 1, "status": "ENABLED"}
        ])

        with patch('my_mcp.server.fetch_campaign_data', return_value=mock_data_json):
            # Also patch asyncio.sleep to be instant
            with patch('asyncio.sleep', return_value=asyncio.Future()) as mock_sleep:
                mock_sleep.return_value.set_result(None)

                await self.agent.handle_command(payload)
        
        # Verify it published DATA_FETCHED
        self.mock_bus.publish.assert_called()
        args, _ = self.mock_bus.publish.call_args
        event_type, data = args
        
        self.assertEqual(event_type, "DATA_FETCHED")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['metrics']['cost'], 1.0) # 1000000 micros = 1.0

if __name__ == '__main__':
    unittest.main()
