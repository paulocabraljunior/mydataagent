import pandas as pd
import json
import os
from typing import Dict, List, Any
# Importação condicional para evitar crash se a lib não estiver instalada, embora esteja no reqs
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

from pydantic import BaseModel, Field

# --- Modelos de Saída (Structured Output) ---
class ActionItem(BaseModel):
    action: str = Field(description="Ação recomendada (ex: 'Pausar Campanha', 'Aumentar Budget')")
    campaign_name: str = Field(description="Nome da campanha alvo")
    reasoning: str = Field(description="Por que essa ação deve ser tomada baseada nos dados")
    priority: str = Field(description="Prioridade: ALTA, MEDIA, BAIXA")

class StrategicReport(BaseModel):
    summary: str = Field(description="Resumo executivo da performance geral")
    key_insights: List[str] = Field(description="Lista de insights de mercado ou comportamento")
    recommended_actions: List[ActionItem] = Field(description="Lista de ações táticas")

# --- A Classe do Agente ---
class BIAnalyticsAgent:
    def __init__(self, bus):
        self.bus = bus
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = None
        self.parser = None

        if HAS_LANGCHAIN:
            self.parser = JsonOutputParser(pydantic_object=StrategicReport)
            if self.api_key:
                try:
                    # Configurando Gemini
                    # Usando 'gemini-2.0-flash' conforme disponibilidade verificada na API
                    self.llm = ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash",
                        temperature=0.1,
                        google_api_key=self.api_key,
                        max_retries=3,
                        request_timeout=60
                    )
                except Exception as e:
                    print(f"⚠️ Erro ao configurar Gemini: {e}")
            else:
                print("⚠️ GOOGLE_API_KEY ausente. BI Agent rodará em modo degradado (sem IA).")

        # Inscrevendo-se no EventBus
        self.bus.subscribe("DATA_FETCHED", self.handle_data)

    async def handle_data(self, payload: List[Dict]):
        print("🤖 BI Agent: Recebi dados via A2A. Iniciando análise...")
        try:
            report = await self.generate_performance_report(payload)
            await self.bus.publish("REPORT_READY", report)
        except Exception as e:
            print(f"❌ BI Agent Error: {e}")
            import traceback
            traceback.print_exc()
            await self.bus.publish("ERROR", {"source": "BI_AGENT", "message": str(e)})

    async def generate_performance_report(self, raw_data: List[Dict]) -> Dict:
        """
        Orquestra o pipeline: Dados Brutos -> Pandas (Hard Stats) -> LLM (Soft Skills) -> JSON
        """
        if not raw_data:
            return {"error": "Nenhum dado recebido para análise."}

        # 1. Análise Quantitativa (Pandas)
        df = pd.DataFrame([item['metrics'] | {'name': item['name'], 'id': item['id'], 'status': item['status']} for item in raw_data])
        stats = self._calculate_hard_metrics(df)
        
        # 2. Análise Qualitativa (LLM ou Mock)
        strategic_analysis = await self._generate_ai_insights(stats, df)
        
        # 3. Merge dos resultados
        return {
            "period_stats": stats,
            "strategy": strategic_analysis
        }

    def _calculate_hard_metrics(self, df: pd.DataFrame) -> Dict:
        """Cálculos determinísticos para evitar alucinação numérica."""
        # Evitar divisão por zero
        df['cpa'] = df.apply(lambda x: x['cost'] / x['conversions'] if x['conversions'] > 0 else 0, axis=1)
        df['ctr_percent'] = (df['clicks'] / df['impressions'] * 100).fillna(0)

        # Identificando outliers
        high_cpa_threshold = df['cpa'].mean() * 1.5
        top_performers = df.nlargest(3, 'conversions')[['name', 'conversions', 'cpa']].to_dict('records')
        low_performers = df[(df['cpa'] > high_cpa_threshold) & (df['conversions'] > 0)][['name', 'cpa']].to_dict('records')
        zero_conversion_spend = df[(df['conversions'] == 0) & (df['cost'] > 0)].nlargest(3, 'cost')[['name', 'cost']].to_dict('records')

        return {
            "total_spend": round(df['cost'].sum(), 2),
            "total_conversions": int(df['conversions'].sum()),
            "global_cpa": round(df['cost'].sum() / df['conversions'].sum(), 2) if df['conversions'].sum() > 0 else 0,
            "top_campaigns": top_performers,
            "inefficient_campaigns": low_performers,
            "wasteful_spend": zero_conversion_spend
        }

    async def _generate_ai_insights(self, stats: Dict, df: pd.DataFrame) -> Dict:
        """Usa o LLM para interpretar os números e sugerir ações."""
        
        if not self.llm:
            return {
                "warning": "IA não configurada (Sem Chave). Retornando placeholder.",
                "summary": "Campanhas processadas, mas análise qualitativa indisponível.",
                "recommended_actions": [
                    {"action": "Configurar API Key", "campaign_name": "System", "reasoning": "Necessário para insights de IA", "priority": "ALTA"}
                ]
            }

        # Convertendo o DF para markdown para o LLM ler facilmente
        # Limitando o número de linhas para economizar tokens e respeitar limites do Free Tier
        MAX_ROWS_FOR_LLM = 50
        df_sorted = df.sort_values(by='cost', ascending=False).head(MAX_ROWS_FOR_LLM)
        df_view = df_sorted[['name', 'cost', 'conversions', 'cpa', 'ctr_percent']].to_markdown(index=False)

        if len(df) > MAX_ROWS_FOR_LLM:
            df_view += f"\n\n(Aviso: Exibindo apenas as Top {MAX_ROWS_FOR_LLM} campanhas de {len(df)} por custo para análise focada.)"

        system_prompt = """
        Você é um Especialista Sênior em Performance de Google Ads (PPC).
        Sua missão é analisar os dados fornecidos e gerar um plano de ação tático.
        Não invente números. Use as estatísticas fornecidas.
        Seja direto, crítico e focado em ROI.
        """

        human_prompt = """
        Analise os dados desta semana:

        --- ESTATÍSTICAS GERAIS ---
        Gasto Total: R$ {total_spend}
        Conversões: {total_conversions}
        CPA Global: R$ {global_cpa}

        --- DESTAQUES ---
        Campanhas Top (Scale): {top_campaigns}
        Campanhas Ineficientes (CPA Alto): {inefficient_campaigns}
        Gasto sem Retorno (Waste): {wasteful_spend}

        --- TABELA DETALHADA ---
        {df_view}

        Gere um relatório estruturado respondendo: O que devo fazer para melhorar o resultado?
        {format_instructions}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
        ])

        chain = prompt | self.llm | self.parser
        
        try:
            return await chain.ainvoke({
                "total_spend": stats['total_spend'],
                "total_conversions": stats['total_conversions'],
                "global_cpa": stats['global_cpa'],
                "top_campaigns": stats['top_campaigns'],
                "inefficient_campaigns": stats['inefficient_campaigns'],
                "wasteful_spend": stats['wasteful_spend'],
                "df_view": df_view,
                "format_instructions": self.parser.get_format_instructions()
            })
        except Exception as e:
            return {"error": f"Falha na geração de insights: {str(e)}"}
