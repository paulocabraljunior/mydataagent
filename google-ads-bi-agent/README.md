# Google Ads BI Agent (A2A + MCP + Gemini)

Sistema distribuído assíncrono para análise de performance de Google Ads.

## 🏗️ Arquitetura

O sistema segue o padrão **Agent-to-Agent (A2A)** com barramento de eventos.

1.  **Orquestrador (`main.py`)**: Inicia o loop assíncrono e dispara o comando inicial.
2.  **Event Bus (`a2a/event_bus.py`)**: Pub/Sub Singleton que gerencia a comunicação entre agentes.
3.  **Google Ads Agent**: Escuta comandos, consulta ferramentas MCP e publica dados brutos.
4.  **MCP Server (`my_mcp/server.py`)**: Exponibiliza ferramentas de dados (protocolo Model Context Protocol).
5.  **BI Analytics Agent**: Escuta dados, processa estatísticas (Pandas) e gera insights estratégicos usando **Google Gemini 1.5 Flash**.

## 🚀 Como Rodar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz:
```ini
# Obrigatório para a Inteligência (Soft Skills)
GOOGLE_API_KEY=sua_chave_gemini_aqui

# Opcional (se for rodar o MCP com dados reais no futuro)
GOOGLE_ADS_CLIENT_ID=...
```

### 3. Executar
```bash
# Certifique-se de adicionar o diretório ao PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python main.py
```

## 🔄 Fluxo de Eventos

1.  `CMD_START_EXTRACT` (Orchestrator -> Ads Agent)
2.  `DATA_FETCHED` (Ads Agent -> BI Agent)
3.  `REPORT_READY` (BI Agent -> Orchestrator)
