import yaml
import os
from google_auth_oauthlib.flow import InstalledAppFlow

def get_refresh_token():
    # 1. Carregar configurações existentes
    # Ajuste: O script está em utils/, então subir um nível para achar config/
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.yaml")
    
    if not os.path.exists(config_path):
        print(f"❌ Erro: Arquivo não encontrado em {config_path}")
        return

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    client_id = config.get('google_ads', {}).get('client_id')
    client_secret = config.get('google_ads', {}).get('client_secret')

    if not client_id or "INSERT" in client_id:
        print("❌ Erro: Preencha o client_id e client_secret no settings.yaml primeiro.")
        return

    # 2. Configuração do Fluxo OAuth
    # Escopo necessário para gerenciar campanhas
    scopes = ["https://www.googleapis.com/auth/adwords"]
    
    # Criar configuração de cliente em memória
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    try:
        flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)

        # 3. Executar o servidor local para callback
        print("\n🚀 Iniciando autenticação...")
        print("Seu navegador será aberto. Faça login com a conta que gerencia o Google Ads.")
        
        # Porta 0 deixa o SO escolher uma porta livre
        # Se der erro de redirect_uri, force port=8080 e garanta que http://localhost:8080/ está no GCP Console
        flow.run_local_server(port=0) 
        
        credentials = flow.credentials
        
        print("\n" + "="*60)
        print("✅ SUCESSO! Copie o token abaixo para seu settings.yaml:")
        print("="*60)
        print(f"refresh_token: {credentials.refresh_token}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Erro durante a autenticação: {e}")
        print("Dica: Verifique se você adicionou seu e-mail como 'Test User' na tela de consentimento OAuth no GCP.")

if __name__ == "__main__":
    get_refresh_token()
