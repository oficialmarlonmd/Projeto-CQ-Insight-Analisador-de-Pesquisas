import os
import re
import sqlite3
import time
import threading
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use backend não-interativo
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import base64
import io
from flask import Flask, render_template, request, jsonify, url_for
try:
    from selenium_simples import executar_web_scraping_selenium_simples, progresso_busca as progresso_selenium
except ImportError:
    progresso_selenium = None
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords

# Inicializa Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

# Variáveis globais para controle de progresso
progresso_busca = {'status': 'idle', 'progresso': 0, 'total_resultados': 0, 'topico_atual': ''}

def verificar_nltk():
    """Verifica e baixa recursos NLTK necessários"""
    for recurso in ['stopwords', 'punkt']:
        try:
            nltk.data.find(f'corpora/{recurso}')
        except LookupError:
            nltk.download(recurso)

def executar_web_scraping(topicos_selecionados, ano_inicio, ano_fim, min_resultados):
    """Chama a versão simples do Selenium"""
    global progresso_busca
    
    try:
        # Importar e sincronizar progresso
        import selenium_simples
        
        # Garantir que o progresso está sincronizado
        selenium_simples.progresso_busca = progresso_busca
        
        print(f"🎯 Iniciando busca para {len(topicos_selecionados)} tópicos")
        print(f"📊 Parâmetros: {ano_inicio}-{ano_fim}, min_resultados={min_resultados}")
        
        # Executar scraping
        selenium_simples.executar_web_scraping_selenium_simples(topicos_selecionados, ano_inicio, ano_fim, min_resultados)
        
        # Sincronizar progresso de volta
        progresso_busca.update(selenium_simples.progresso_busca)
        
        print("✅ Web scraping concluído com sucesso")
        
    except Exception as e:
        print(f"❌ Erro no web scraping: {e}")
        progresso_busca['status'] = f'erro: {str(e)}'
        progresso_busca['progresso'] = 0

def gerar_graficos():
    """Gera todos os gráficos e retorna os caminhos"""
    try:
        # Garantir que o diretório de plots existe
        plots_dir = os.path.join('static', 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Verificar NLTK
        verificar_nltk()
        
        # Carregar dados
        conn = sqlite3.connect("buscas_completas_CQ.db")
        df = pd.read_sql_query("SELECT * FROM resultados_detalhados_CQ", conn)
        conn.close()
        
        if df.empty:
            return None
        
        graficos = {}
        
        # Configurar matplotlib com fonte compatível
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.size'] = 10
        
        # Preparar dados
        df['texto_completo'] = df['titulo'].fillna('') + ' ' + df['resumo'].fillna('')
        df['texto_limpo'] = df['texto_completo'].str.lower().apply(lambda x: re.sub(r'[^a-z\s]', '', x))
        
        stopwords_custom = set(stopwords.words('portuguese')).union({
            'computacao', 'quantica', 'quântico', 'quantum', 'trabalho', 'estudo', 'pesquisa',
            'neste', 'este', 'para', 'com', 'que', 'uma', 'como', 'sobre', 'dados', 'resultados'
        })
        
        df['texto_filtrado'] = df['texto_limpo'].apply(lambda x: ' '.join([w for w in x.split() if w not in stopwords_custom]))
        
        # 1. WordCloud
        try:
            plt.figure(figsize=(12, 6))
            texto = ' '.join(df['texto_filtrado'].dropna())
            if texto and len(texto.strip()) > 0:
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='viridis',
                    max_words=100,
                    relative_scaling=0.5
                ).generate(texto)
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('Nuvem de Palavras-Chave', fontsize=16, fontweight='bold')
                plt.tight_layout()
                plt.savefig('static/plots/wordcloud.png', dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                graficos['wordcloud'] = 'plots/wordcloud.png'
                print("WordCloud gerado com sucesso!")
        except Exception as e:
            print(f"Erro ao gerar WordCloud: {e}")
            plt.close()
        
        # 2. Análise de Sentimento
        try:
            positivas = {'inovação', 'oportunidades', 'avanços', 'eficiente', 'sucesso', 'melhor', 'novo', 'promissor'}
            negativas = {'desafios', 'problemas', 'riscos', 'limitações', 'ameaça', 'dificuldade', 'complexo'}
            
            def sentimento(texto):
                if not isinstance(texto, str):
                    return 'Neutro'
                texto = texto.lower()
                p = sum(1 for w in positivas if w in texto)
                n = sum(1 for w in negativas if w in texto)
                return 'Positivo' if p > n else 'Negativo' if n > p else 'Neutro'
            
            df['sentimento'] = df['resumo'].apply(sentimento)
            
            plt.figure(figsize=(10, 6))
            sentimento_counts = df['sentimento'].value_counts()
            colors = ['#28a745', '#dc3545', '#6c757d']
            
            plt.pie(sentimento_counts.values, labels=sentimento_counts.index, 
                   autopct='%1.1f%%', colors=colors, startangle=90)
            plt.title('Análise de Sentimento dos Resumos', fontsize=16, fontweight='bold')
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig('static/plots/sentimentos.png', dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            graficos['sentimentos'] = 'plots/sentimentos.png'
            print("Análise de sentimento gerada com sucesso!")
        except Exception as e:
            print(f"Erro ao gerar análise de sentimento: {e}")
            plt.close()
        
        # 3. Análise Temporal
        try:
            df['ano_publicacao'] = pd.to_numeric(df['ano_publicacao'], errors='coerce')
            df_anos = df.dropna(subset=['ano_publicacao'])
            df_anos = df_anos[(df_anos['ano_publicacao'] >= 1900) & (df_anos['ano_publicacao'] <= 2025)]
            df_anos['ano_publicacao'] = df_anos['ano_publicacao'].astype(int)
            
            if not df_anos.empty:
                plt.figure(figsize=(12, 6))
                anos_contagem = df_anos['ano_publicacao'].value_counts().sort_index()
                
                plt.bar(anos_contagem.index, anos_contagem.values, 
                       color='skyblue', edgecolor='navy', alpha=0.7)
                plt.title('Publicações por Ano', fontsize=16, fontweight='bold')
                plt.xlabel('Ano', fontsize=12)
                plt.ylabel('Número de Artigos', fontsize=12)
                plt.xticks(rotation=45)
                plt.grid(axis='y', alpha=0.3)
                
                # Adicionar valores nas barras
                for i, v in enumerate(anos_contagem.values):
                    plt.text(anos_contagem.index[i], v + 0.1, str(v), 
                           ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                plt.savefig('static/plots/temporal.png', dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                graficos['temporal'] = 'plots/temporal.png'
                print("Gráfico temporal gerado com sucesso!")
        except Exception as e:
            print(f"Erro ao gerar gráfico temporal: {e}")
            plt.close()
        
        # 4. Tendências por Tópico
        try:
            if 'termo' in df.columns and not df_anos.empty:
                plt.figure(figsize=(14, 8))
                tendencias = df_anos.groupby(['ano_publicacao', 'termo']).size().unstack(fill_value=0)
                
                # Limitar a 10 tópicos mais frequentes para melhor visualização
                top_topicos = df['termo'].value_counts().head(10).index
                tendencias_top = tendencias[top_topicos]
                
                tendencias_top.plot(kind='line', marker='o', figsize=(14, 8), linewidth=2, markersize=6)
                plt.title('Tendência de Tópicos por Ano', fontsize=16, fontweight='bold')
                plt.xlabel('Ano', fontsize=12)
                plt.ylabel('Quantidade de Artigos', fontsize=12)
                plt.legend(title='Tópico', bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig('static/plots/tendencias.png', dpi=300, bbox_inches='tight', facecolor='white')
                plt.close()
                graficos['tendencias'] = 'plots/tendencias.png'
                print("Gráfico de tendências gerado com sucesso!")
        except Exception as e:
            print(f"Erro ao gerar gráfico de tendências: {e}")
            plt.close()
        
        # 5. Top Palavras
        try:
            if texto and len(texto.strip()) > 0:
                palavras_freq = Counter(texto.split()).most_common(20)
                if palavras_freq:
                    palavras, frequencias = zip(*palavras_freq)
                    
                    plt.figure(figsize=(12, 8))
                    colors = plt.cm.viridis(range(len(palavras)))
                    bars = plt.barh(range(len(palavras)), frequencias, color=colors)
                    plt.yticks(range(len(palavras)), palavras)
                    plt.title('Top 20 Palavras Mais Frequentes', fontsize=16, fontweight='bold')
                    plt.xlabel('Frequência', fontsize=12)
                    plt.gca().invert_yaxis()
                    plt.grid(axis='x', alpha=0.3)
                    
                    # Adicionar valores nas barras
                    for i, (bar, freq) in enumerate(zip(bars, frequencias)):
                        plt.text(freq + max(frequencias) * 0.01, i, str(freq), 
                               va='center', ha='left', fontweight='bold')
                    
                    plt.tight_layout()
                    plt.savefig('static/plots/top_palavras.png', dpi=300, bbox_inches='tight', facecolor='white')
                    plt.close()
                    graficos['top_palavras'] = 'plots/top_palavras.png'
                    print("Gráfico de top palavras gerado com sucesso!")
        except Exception as e:
            print(f"Erro ao gerar gráfico de top palavras: {e}")
            plt.close()
        
        return graficos
        
    except Exception as e:
        print(f"Erro ao gerar gráficos: {e}")
        return None

@app.route('/')
def index():
    """Página inicial"""
    topicos_predefinidos = [
        "Computação Quântica na Criptografia",
        "Otimização Quântica em Finanças",
        "Inteligência Artificial e Aprendizado de Máquina Quântico",
        "Computação Quântica e Descoberta de Medicamentos",
        "Química Quântica Computacional",
        "Perspectivas Futuras da Computação Quântica",
        "Computação Quântica Pós-Quântica",
        "Desafios e Oportunidades na Era Quântica"
    ]
    return render_template('index.html', topicos=topicos_predefinidos)

@app.route('/iniciar_busca', methods=['POST'])
def iniciar_busca():
    """Inicia o processo de web scraping"""
    try:
        print("📩 Recebendo requisição de busca...")
        dados = request.get_json()
        print(f"📋 Dados recebidos: {dados}")
        
        topicos_selecionados = dados.get('topicos', [])
        ano_inicio = int(dados.get('ano_inicio', 2024))
        ano_fim = int(dados.get('ano_fim', 2025))
        min_resultados = int(dados.get('min_resultados', 50))
        
        print(f"🎯 Tópicos: {topicos_selecionados}")
        print(f"📅 Período: {ano_inicio}-{ano_fim}")
        print(f"📊 Min resultados: {min_resultados}")
        
        if not topicos_selecionados:
            print("❌ Nenhum tópico selecionado")
            return jsonify({'erro': 'Nenhum tópico selecionado'}), 400
        
        # Resetar progresso
        global progresso_busca
        progresso_busca = {'status': 'recebido', 'progresso': 0, 'total_resultados': 0, 'topico_atual': ''}
        
        print("🧵 Iniciando thread de scraping...")
        # Iniciar o scraping em uma thread separada
        thread = threading.Thread(
            target=executar_web_scraping,
            args=(topicos_selecionados, ano_inicio, ano_fim, min_resultados),
            daemon=True
        )
        thread.start()
        
        print("✅ Thread iniciada com sucesso")
        return jsonify({'sucesso': True, 'mensagem': 'Busca iniciada com sucesso'})
    
    except Exception as e:
        print(f"❌ Erro na rota iniciar_busca: {e}")
        return jsonify({'erro': str(e)}), 500

@app.route('/progresso')
def obter_progresso():
    """Retorna o progresso atual da busca"""
    global progresso_busca
    print(f"📊 Progresso solicitado: {progresso_busca}")
    return jsonify(progresso_busca)

@app.route('/resultados')
def exibir_resultados():
    """Página para exibir os resultados e gráficos"""
    graficos = gerar_graficos()
    return render_template('resultados.html', graficos=graficos)

@app.route('/dados_tabela')
def obter_dados_tabela():
    """Retorna os dados em formato JSON para a tabela"""
    try:
        conn = sqlite3.connect("buscas_completas_CQ.db")
        cursor = conn.cursor()
        
        # Buscar dados com SQL direto para garantir compatibilidade
        cursor.execute("SELECT * FROM resultados_detalhados_CQ ORDER BY id DESC LIMIT 1000")
        colunas = [description[0] for description in cursor.description]
        linhas = cursor.fetchall()
        
        # Converter para lista de dicionários
        dados = []
        for linha in linhas:
            registro = {}
            for i, coluna in enumerate(colunas):
                registro[coluna] = linha[i]
            dados.append(registro)
        
        conn.close()
        
        print(f"📊 Retornando {len(dados)} registros para a tabela")
        return jsonify(dados)
    
    except Exception as e:
        print(f"❌ Erro na rota dados_tabela: {e}")
        return jsonify({'erro': str(e)}), 500

@app.route('/testar_graficos')
def testar_graficos():
    """Rota para testar a geração de gráficos"""
    try:
        # Garantir que o diretório existe
        os.makedirs('static/plots', exist_ok=True)
        
        # Tentar gerar um gráfico simples de teste
        plt.figure(figsize=(10, 6))
        plt.plot([1, 2, 3, 4], [1, 4, 2, 3], 'o-', linewidth=2, markersize=8)
        plt.title('Gráfico de Teste', fontsize=16, fontweight='bold')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('static/plots/teste.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Verificar se matplotlib e seaborn estão funcionando
        import matplotlib
        import seaborn as sns
        
        info = {
            'matplotlib_version': matplotlib.__version__,
            'seaborn_available': True,
            'plots_directory_exists': os.path.exists('static/plots'),
            'test_plot_created': os.path.exists('static/plots/teste.png')
        }
        
        return jsonify(info)
        
    except Exception as e:
        return jsonify({'erro': str(e), 'matplotlib_available': False}), 500

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('static/plots', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("Diretórios criados com sucesso!")
    print("Servidor iniciando...")
    
    # Executar aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
