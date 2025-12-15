import asyncio
import os
from dotenv import load_dotenv
from agents.orchestrator import Orchestrator

# Carrega variáveis de ambiente
load_dotenv()

async def main():
    print("Google Ads BI Agent System (Async A2A + Gemini + MCP)")
    print("=======================================================")
    
    # Validação Básica de Chave
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ GOOGLE_API_KEY not found. Please set it in .env for Gemini to work.")

    orch = Orchestrator()
    await orch.start()

if __name__ == "__main__":
    asyncio.run(main())
