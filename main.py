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
        # Passando a requisição direta sem gatilhos de chamadas automáticas de função
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={"tools": []}  # Lista de ferramentas vazia para evitar o alerta de AFC
        )
        return response.text
    except Exception as e:
        print(f"Erro na análise da IA: {e}")
        return None
    
