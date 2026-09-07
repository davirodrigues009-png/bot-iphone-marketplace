import os
import time
import threading
import requests
from flask import Flask
from google import genai

# --- SERVIDOR WEB FALSO PARA ENGANAR O RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de monitoramento está ativo e rodando!"

def rodar_servidor():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- LÓGICA DO BOT DO TELEGRAM E GEMINI ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

def obter_chat_id():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        if response.get("result"):
            return response["result"][-1]["message"]["chat"]["id"]
    except Exception as e:
        print(f"Erro ao buscar chat_id: {e}")
    return None

def enviar_mensagem_telegram(chat_id, texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def analisar_oferta_com_gemini(titulo, preco, descricao):
    prompt = f"""
    Você é um especialista em compra e revenda de iPhones usados.
    Analise o seguinte anúncio:
    - Produto: {titulo}
    - Preço pedido: R$ {preco}
    - Descrição: "{descricao}"

    Sua tarefa:
    1. Avalie se o preço está significativamente abaixo do valor de mercado.
    2. Verifique se há sinais de defeitos graves (iCloud preso, Face ID quebrado, tela paralela, peças trocadas, para retirar peças).
    3. Determine se é uma OPORTUNIDADE REAL de revenda com lucro.

    Responda EXATAMENTE neste formato:
    OPORTUNIDADE: [SIM ou NAO]
    MOTIVO: [Explicação curta de 1 a 2 frases]
    LUCRO_ESTIMADO: [Valor estimado de lucro em R$ ou 'N/A']
    """

    try:
        # Chamada direta e compatível com o SDK google-genai
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Erro na análise da IA: {e}")
        return None
                             

def monitorar_marketplace():
    print("Iniciando monitoramento de iPhones...")
    
    # Aguarda 10 segundos para dar tempo do servidor web iniciar
    time.sleep(10)
    
    chat_id = obter_chat_id()

    if not chat_id:
        print("Atenção: Mande uma mensagem (ex: /start) no Telegram para o seu bot para ativá-lo!")
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
            enviar_mensagem_telegram(chat_id, mensagem)
            print("Alerta enviado para o Telegram!")

def iniciar_bot():
    while True:
        try:
            monitorar_marketplace()
        except Exception as e:
            print(f"Erro no loop do bot: {e}")
        time.sleep(300)

if __name__ == "__main__":
    # Inicia o robô em uma thread paralela
    thread_bot = threading.Thread(target=iniciar_bot)
    thread_bot.daemon = True
    thread_bot.start()

    # Roda o servidor web na porta exigida pelo Render
    rodar_servidor()
    
