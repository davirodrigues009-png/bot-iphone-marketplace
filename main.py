import os
import time
import threading
import requests
from flask import Flask
from google import genai

# --- SERVIDOR WEB LEVE PARA O RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de monitoramento de iPhones ativo e rodando!"

def rodar_servidor():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- CONFIGURAÇÕES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CHAT_ID = os.environ.get("CHAT_ID")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

def enviar_mensagem_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.ok
    except Exception as e:
        print(f"Erro ao enviar no Telegram: {e}")
        return False

def analisar_oferta_com_gemini(titulo, preco, descricao):
    prompt = f"""
    Você é um especialista em compra e revenda de iPhones usados.
    Analise o seguinte anúncio:
    - Produto: {titulo}
    - Preço pedido: R$ {preco}
    - Descrição: "{descricao}"

    Sua tarefa:
    1. Avalie se o preço está significativamente abaixo do valor de mercado.
    2. Verifique se há sinais de defeitos graves.
    3. Determine se é uma OPORTUNIDADE REAL de revenda com lucro.

    Responda EXATAMENTE neste formato:
    OPORTUNIDADE: [SIM ou NAO]
    MOTIVO: [Explicação curta de 1 a 2 frases]
    LUCRO_ESTIMADO: [Valor estimado de lucro em R$ ou 'N/A']
    """

    try:
        chat = ai_client.chats.create(model='gemini-2.5-flash')
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        print(f"Erro na IA: {e}")
        return None

def monitorar_marketplace():
    print("Iniciando monitoramento de iPhones...")
    
    if not CHAT_ID:
        print("Atenção: Adicione a variável CHAT_ID no painel do Render!")
        return

    anuncios_testes = [
        {
            "id": "101",
            "titulo": "iPhone 12 128GB Preto",
            "preco": 1600,
            "descricao": "iPhone 12 em perfeito estado, saúde da bateria 86%, com caixa e carregador original. Sem marcas de uso.",
            "url": "https://facebook.com/marketplace/item/101"
        }
    ]

    for anuncio in anuncios_testes:
        print(f"Analisando: {anuncio['titulo']} por R$ {anuncio['preco']}...")
        
        analise = analisar_oferta_com_gemini(
            anuncio["titulo"], 
            anuncio["preco"], 
            anuncio["descricao"]
        )

        if analise and "OPORTUNIDADE: SIM" in analise.upper():
            mensagem = (
                f"🚨 *NOVA OPORTUNIDADE ENCONTRADA!*\n\n"
                f"📱 *{anuncio['titulo']}*\n"
                f"💰 *Preço:* R$ {anuncio['preco']}\n\n"
                f"📊 *Análise da IA:*\n{analise}\n\n"
                f"🔗 [Clique aqui para abrir o anúncio]({anuncio['url']})"
            )
            enviar_mensagem_telegram(CHAT_ID, mensagem)
            print("Alerta enviado para o Telegram com sucesso!")

def iniciar_loop():
    time.sleep(5)
    while True:
        try:
            monitorar_marketplace()
        except Exception as e:
            print(f"Erro no loop: {e}")
        time.sleep(300)

if __name__ == "__main__":
    thread_bot = threading.Thread(target=iniciar_loop)
    thread_bot.daemon = True
    thread_bot.start()

    rodar_servidor()
    
