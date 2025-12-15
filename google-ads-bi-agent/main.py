from dotenv import load_dotenv
load_dotenv() # Load env vars first

from agents.orchestrator import Orchestrator

def main():
    print("Google Ads BI Agent System")
    print("==========================")
    
    # Check if OPENAI_API_KEY is set (basic check)
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY not found in environment. BI Agent might fail on 'Soft Skills' part.")
        print("Please check your .env file.")
    
    orch = Orchestrator()
    orch.run_pipeline(customer_id="1234567890")

if __name__ == "__main__":
    main()
