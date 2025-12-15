import asyncio
import os
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

from a2a.event_bus import EventBus
from agents.google_ads_agent import GoogleAdsAgent
from agents.bi_analytics_agent import BIAnalyticsAgent

async def main():
    print("🚀 Google Ads BI Agent System (Async A2A + Gemini + MCP)")
    print("=======================================================")
    
    # Validação Básica de Chave
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ GOOGLE_API_KEY not found. Please set it in .env for Gemini to work.")
        # Não abortamos, mas o BI Agent vai reclamar.

    # 1. Inicializa o Barramento de Eventos
    bus = EventBus()

    # 2. Inicializa os Agentes (Eles se inscrevem no Bus no __init__)
    ads_agent = GoogleAdsAgent(bus)
    bi_agent = BIAnalyticsAgent(bus)
    
    # Variável de controle para encerrar o loop (Future)
    loop = asyncio.get_running_loop()
    completion_future = loop.create_future()

    # 3. Handler para encerramento
    async def finish_pipeline(payload):
        print("\n✅ Pipeline Finished! Report received.")
        print("-" * 40)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("-" * 40)
        if not completion_future.done():
            completion_future.set_result(True)

    async def handle_error(payload):
        print(f"\n❌ Pipeline Error: {payload}")
        if not completion_future.done():
            completion_future.set_result(False)

    bus.subscribe("REPORT_READY", finish_pipeline)
    bus.subscribe("ERROR", handle_error)

    # 4. Inicia o Fluxo
    print("\n▶️ Sending Start Command...")
    await bus.publish("CMD_START_EXTRACT", {"customer_id": "1234567890"})

    # 5. Mantém rodando até finalizar ou Timeout (30s)
    try:
        await asyncio.wait_for(completion_future, timeout=30.0)
    except asyncio.TimeoutError:
        print("\n⏳ Timeout waiting for pipeline completion.")

if __name__ == "__main__":
    asyncio.run(main())
