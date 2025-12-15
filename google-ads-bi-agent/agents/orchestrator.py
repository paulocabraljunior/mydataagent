import asyncio
import json
from a2a.communication_layer import EventBus
from agents.google_ads_agent import GoogleAdsAgent
from agents.bi_analytics_agent import BIAnalyticsAgent

class Orchestrator:
    def __init__(self):
        print("🤖 Initializing Orchestrator...")
        # 1. Inicializa o Barramento de Eventos
        self.bus = EventBus()

        # 2. Inicializa os Agentes (Eles se inscrevem no Bus no __init__)
        self.ads_agent = GoogleAdsAgent(self.bus)
        self.bi_agent = BIAnalyticsAgent(self.bus)
        
        self.completion_future = None

    async def start(self):
        print("🚀 Starting Async Pipeline via Orchestrator")
        
        # Variável de controle para encerrar o loop (Future)
        loop = asyncio.get_running_loop()
        self.completion_future = loop.create_future()

        # Inscrevendo o próprio Orquestrador para ouvir o final
        self.bus.subscribe("REPORT_READY", self.finish_pipeline)
        self.bus.subscribe("ERROR", self.handle_error)

        # 4. Inicia o Fluxo
        print("\n▶️ Sending Start Command...")
        await self.bus.publish("CMD_START_EXTRACT", {"customer_id": "1234567890"})

        # 5. Mantém rodando até finalizar ou Timeout (30s)
        try:
            await asyncio.wait_for(self.completion_future, timeout=30.0)
        except asyncio.TimeoutError:
            print("\n⏳ Timeout waiting for pipeline completion.")

    async def finish_pipeline(self, payload):
        print("\n✅ Pipeline Finished! Report received.")
        print("-" * 40)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("-" * 40)
        if self.completion_future and not self.completion_future.done():
            self.completion_future.set_result(True)

    async def handle_error(self, payload):
        print(f"\n❌ Pipeline Error: {payload}")
        if self.completion_future and not self.completion_future.done():
            self.completion_future.set_result(False)
