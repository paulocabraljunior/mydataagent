from agents.google_ads_agent import GoogleAdsAgent
from agents.bi_analytics_agent import BIAnalyticsAgent
import json

class Orchestrator:
    def __init__(self):
        print("🤖 Initializing Orchestrator...")
        self.ads_agent = GoogleAdsAgent()
        self.bi_agent = BIAnalyticsAgent(model_name="gpt-4o") # Model name as per user config in BI agent
        print("✅ Agents Ready.")

    def run_pipeline(self, customer_id: str):
        print(f"\n🚀 Starting Analysis Pipeline for Customer: {customer_id}")
        
        # Step 1: Fetch
        print("\n[1/3] Fetching Campaign Data from Google Ads (Mock/Real)...")
        campaign_data = self.ads_agent.fetch_campaign_data(customer_id)
        if not campaign_data:
            print("❌ No data found.")
            return

        print(f"✅ Retrieved {len(campaign_data)} campaigns.")

        # Step 2: Analyze
        print("\n[2/3] Analyzing Performance & Generating Insights (BI Agent)...")
        # Note: In a real scenario without an API key, the LLM part of BI agent might fail if not mocked or key provided.
        # But per user instruction, we have a .env with a placeholder. 
        # The user provided BI agent uses ChatOpenAI. If key is invalid, it might error.
        # For now, we assume the user might want a demo or test.
        # However, the user's BI agent has a 'model_name' param.
        
        try:
            report = self.bi_agent.generate_performance_report(campaign_data)
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return

        # Step 3: Report
        print("\n[3/3] Pipeline Complete. Result:")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return report

if __name__ == "__main__":
    # Demo execution
    orch = Orchestrator()
    orch.run_pipeline(customer_id="1234567890")
