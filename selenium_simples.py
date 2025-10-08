#!/usr/bin/env python3
"""
Versão SUPER SIMPLES do web scraping com Selenium
"""

import os
import re
import sqlite3
import time
import threading

# Variável global para compatibilidade com app.py
progresso_busca = {'status': 'idle', 'progresso': 0, 'total_resultados': 0, 'topico_atual': ''}

def executar_web_scraping_selenium_simples(topicos_selecionados, ano_inicio, ano_fim, min_resultados):
    """Versão mais simples possível com Selenium"""
    global progresso_busca
    
    try:
        print("🚀 Iniciando Selenium SIMPLES...")
        progresso_busca['status'] = 'iniciando selenium'
        progresso_busca['progresso'] = 0
        
        # Tentar Chrome primeiro (mais simples)
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            
            print("📦 Configurando Chrome...")
            
            # Opções mínimas do Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Criar driver (Selenium vai tentar encontrar automaticamente)
            print("🌐 Iniciando Chrome...")
            driver = webdriver.Chrome(options=chrome_options)
            
            print("✅ Chrome iniciado com sucesso!")
            
        except Exception as e_chrome:
            print(f"❌ Chrome falhou: {e_chrome}")
            
            # Tentar Edge se Chrome falhar
            try:
                print("📦 Tentando Edge...")
                edge_options = webdriver.EdgeOptions()
                edge_options.add_argument("--headless")
                edge_options.add_argument("--no-sandbox")
                
                driver = webdriver.Edge(options=edge_options)
                print("✅ Edge iniciado com sucesso!")
                
            except Exception as e_edge:
                print(f"❌ Edge falhou: {e_edge}")
                progresso_busca['status'] = f'erro: Nenhum navegador disponível. Instale Chrome ou Edge.'
                return
        
        progresso_busca['status'] = 'navegador iniciado'
        progresso_busca['progresso'] = 15
        
        # Configurar banco de dados
        print("💾 Configurando banco...")
        conn = sqlite3.connect("buscas_completas_CQ.db")
        cursor = conn.cursor()
        
        # Limpar dados antigos antes de iniciar nova busca
        print("🧹 Limpando dados antigos...")
        cursor.execute("DELETE FROM resultados_detalhados_CQ")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados_detalhados_CQ (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                termo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                ano_publicacao INTEGER,
                autores TEXT,
                fonte_publicacao TEXT,
                resumo TEXT,
                url_artigo TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("✅ Banco limpo e configurado!")
        
        total_resultados = 0
        
        # Processar cada tópico
        for i, topico in enumerate(topicos_selecionados):
            print(f"🔍 Buscando: {topico}")
            progresso_busca['topico_atual'] = topico
            progresso_busca['progresso'] = 15 + ((i / len(topicos_selecionados)) * 80)
            
            # URL simples do Google Scholar
            query = topico.replace(' ', '+')
            url = f"https://scholar.google.com.br/scholar?q={query}&as_ylo={ano_inicio}&as_yhi={ano_fim}"
            
            print(f"📄 Acessando: {url}")
            
            try:
                resultados_coletados = 0
                pagina_atual = 0
                
                # Loop para coletar a quantidade desejada de resultados
                while resultados_coletados < min_resultados:
                    # Calcular offset para paginação
                    start_param = pagina_atual * 10
                    url_pagina = f"{url}&start={start_param}"
                    
                    print(f"📄 Acessando página {pagina_atual + 1}: {url_pagina}")
                    
                    # Abrir página
                    driver.get(url_pagina)
                    time.sleep(3)  # Aguardar carregar
                    
                    # Buscar resultados (seletor simples)
                    resultados = driver.find_elements(By.CSS_SELECTOR, "div.gs_ri")
                    print(f"📋 Encontrados {len(resultados)} resultados na página {pagina_atual + 1}")
                    
                    # Se não há mais resultados, parar
                    if len(resultados) == 0:
                        print("❌ Não há mais resultados disponíveis")
                        break
                    
                    # Calcular quantos resultados processar nesta página
                    resultados_restantes = min_resultados - resultados_coletados
                    resultados_processar = min(len(resultados), resultados_restantes)
                    
                    # Extrair dados de cada resultado
                    for j, resultado in enumerate(resultados[:resultados_processar]):
                        try:
                            # Título (simples)
                            titulo = "Título não encontrado"
                            try:
                                titulo_elem = resultado.find_element(By.CSS_SELECTOR, "h3 a")
                                titulo = titulo_elem.text
                                url_artigo = titulo_elem.get_attribute("href")
                            except:
                                url_artigo = None
                            
                            # Autores (simples)
                            autores = "N/A"
                            fonte = "N/A"
                            ano = None
                            try:
                                autor_elem = resultado.find_element(By.CSS_SELECTOR, "div.gs_a")
                                texto_autor = autor_elem.text
                                
                                # Extrair ano (regex simples)
                                ano_match = re.search(r'(20\d{2})', texto_autor)
                                if ano_match:
                                    ano = int(ano_match.group(1))
                                
                                # Dividir autores e fonte
                                if ' - ' in texto_autor:
                                    partes = texto_autor.split(' - ')
                                    autores = partes[0].strip()
                                    if len(partes) > 1:
                                        fonte = partes[1].strip()
                                else:
                                    autores = texto_autor.strip()
                            except:
                                pass
                            
                            # Resumo (simples)
                            resumo = None
                            try:
                                resumo_elem = resultado.find_element(By.CSS_SELECTOR, "div.gs_rs")
                                resumo = resumo_elem.text
                            except:
                                pass
                            
                            # Salvar no banco
                            cursor.execute(
                                "INSERT INTO resultados_detalhados_CQ (termo, titulo, ano_publicacao, autores, fonte_publicacao, resumo, url_artigo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (topico, titulo, ano, autores, fonte, resumo, url_artigo)
                            )
                            
                            total_resultados += 1
                            resultados_coletados += 1
                            print(f"   ✅ {resultados_coletados}/{min_resultados}. {titulo[:50]}...")
                            
                        except Exception as e_item:
                            print(f"   ⚠️ Erro no item {j+1}: {e_item}")
                    
                    conn.commit()
                    
                    # Se já coletamos o suficiente, parar
                    if resultados_coletados >= min_resultados:
                        break
                    
                    # Próxima página
                    pagina_atual += 1
                    
                    # Limite de segurança para evitar loop infinito
                    if pagina_atual >= 10:  # Máximo 10 páginas (100 resultados por tópico)
                        print("⚠️ Limite de páginas atingido (10 páginas)")
                        break
                    
                    # Pausa entre páginas
                    time.sleep(2)
                
                print(f"✅ Coletados {resultados_coletados} resultados para '{topico}'")
                
            except Exception as e_topico:
                print(f"❌ Erro no tópico '{topico}': {e_topico}")
            
            # Pausa entre tópicos
            time.sleep(2)
        
        # Finalizar
        progresso_busca['total_resultados'] = total_resultados
        progresso_busca['progresso'] = 100
        progresso_busca['status'] = 'concluido'
        
        print(f"🎉 Concluído! Total: {total_resultados} resultados")
        
        # Fechar tudo
        driver.quit()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        progresso_busca['status'] = f'erro: {str(e)}'
        if 'driver' in locals():
            driver.quit()
        if 'conn' in locals():
            conn.close()

# Teste direto
if __name__ == "__main__":
    print("🧪 TESTE SELENIUM SIMPLES")
    print("=" * 30)
    
    # Teste com um tópico
    topicos = ["computação quântica"]
    executar_web_scraping_selenium_simples(topicos, 2024, 2025, 3)