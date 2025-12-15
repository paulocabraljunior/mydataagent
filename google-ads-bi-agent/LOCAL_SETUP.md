# Guia de Configuração Local - Google Ads BI Agent

Este guia descreve o passo a passo para rodar o projeto na sua máquina local após clonar o repositório.

## Pré-requisitos

*   **Python 3.10+** instalado.
*   Uma chave de API do Google Gemini (AI Studio).

## 1. Configurar o Ambiente

Recomendamos criar um ambiente virtual para isolar as dependências.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Instalar Dependências

Com o ambiente ativo, instale as bibliotecas necessárias:

```bash
cd google-ads-bi-agent
pip install -r requirements.txt
```

## 3. Configurar Variáveis de Ambiente

1.  Crie um arquivo chamado `.env` dentro da pasta `google-ads-bi-agent`.
2.  Adicione sua chave do Gemini nele:

```ini
GOOGLE_API_KEY=SuaChaveAqui
```

## 4. Rodar o Sistema

Para que o Python encontre os módulos do projeto corretamente, você precisa ajustar o `PYTHONPATH` antes de rodar.

**Opção A: Rodar via comando (Linux/Mac)**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python main.py
```

**Opção B: Rodar via comando (Windows PowerShell)**
```powershell
$env:PYTHONPATH = "$(pwd)"
python main.py
```

**Opção C: VS Code**
Se estiver usando VS Code, abra a pasta `google-ads-bi-agent` como raiz do workspace. O editor geralmente detecta o path.

## 5. Rodar os Testes

Para verificar se tudo está funcionando:

```bash
# Linux/Mac
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m unittest discover tests

# Windows
$env:PYTHONPATH = "$(pwd)"
python -m unittest discover tests
```

## Solução de Problemas Comuns

*   **ModuleNotFoundError**: Geralmente significa que o `PYTHONPATH` não foi configurado corretamente. Certifique-se de que o comando de exportação foi executado na mesma sessão do terminal.
*   **Erro 404/429 no Gemini**:
    *   **404**: O modelo configurado no código não está disponível para sua chave/região. O código atual usa `gemini-2.0-flash`.
    *   **429**: Você atingiu o limite de requisições do plano gratuito (Free Tier). Aguarde alguns minutos e tente novamente.
