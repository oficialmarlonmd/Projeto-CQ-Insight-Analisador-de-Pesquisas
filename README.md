# Projeto-CQ-Insight-Analisador-de-PesquisasDescrição Geral

CQ Insight é uma aplicação web desenvolvida em Python (Flask) que realiza web scraping automatizado com Selenium no Google Scholar, coleta artigos sobre o que o usuario escolher e realiza análises de texto, tendências e sentimentos com visualizações automáticas em gráficos.
O sistema integra scraping, persistência em banco de dados SQLite, pré-processamento de texto com NLTK, geração de gráficos com Matplotlib/Seaborn, e exibição via interface web interativa.

# 🚀 Principais Funcionalidades

✅ Web Scraping Automatizado (Google Scholar)

Busca artigos acadêmicos de tópicos específicos em Computação Quântica.

Utiliza Selenium WebDriver (Chrome/Edge) em modo headless.

Extrai título, autores, ano, resumo e URL.

Armazena automaticamente em SQLite (buscas_completas_CQ.db).

# ✅ Análises Automáticas de Texto e Tendências

WordCloud com as palavras mais frequentes.

Análise de Sentimento com palavras positivas e negativas definidas.

Análise Temporal (publicações por ano).

Tendências por Tópico (evolução dos temas ao longo do tempo).

Top 20 Palavras Mais Frequentes (frequência lexical).

# ✅ Painel Web Interativo (Flask)

Página inicial com seleção de tópicos e parâmetros (ano inicial, final, mínimo de resultados).

Barra de progresso da coleta em tempo real.

Página de resultados com todos os gráficos gerados.

Endpoint JSON para exibir a tabela de artigos no front-end.

# ✅ Configuração Flexível

Arquivo config.py centraliza todas as opções da aplicação:

Parâmetros do Flask, Selenium e Banco de Dados.

Listas customizadas de stopwords, palavras positivas e negativas.

Parâmetros de busca e gráficos (resolução, tema, cores).

# 🧩 Estrutura do Projeto
CQ-Insight/
│
├── app.py                  # Aplicação principal Flask
├── selenium_simples.py     # Módulo de scraping simplificado (Selenium)
├── config.py               # Configurações centralizadas
├── buscas_completas_CQ.db  # Banco de dados SQLite com resultados
│
├── static/
│   ├── plots/              # Gráficos gerados automaticamente
│   ├── css/                # Estilos (se aplicável)
│   └── js/                 # Scripts JS (se aplicável)
│
├── templates/
│   ├── index.html          # Página inicial com seleção de tópicos
│   └── resultados.html     # Página de resultados e visualizações
│
└── README.md               # (este arquivo)

# 🛠️ Tecnologias Utilizadas
Categoria	Biblioteca / Ferramenta
Backend	Flask
Web Scraping	Selenium
Banco de Dados	SQLite3
Análise de Texto	NLTK, TfidfVectorizer, WordCloud
Visualização	Matplotlib, Seaborn
Machine Learning (base)	scikit-learn (LDA e TF-IDF)
Frontend	HTML + CSS + JS (via Flask Templates)
Suporte	threading, re, pandas, io, base64
⚙️ Como Executar o Projeto
1️⃣ Clonar o repositório
git clone https://github.com/seuusuario/CQ-Insight.git
cd CQ-Insight

2️⃣ Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # (Windows)
source venv/bin/activate  # (Linux/Mac)

3️⃣ Instalar dependências
pip install flask selenium pandas matplotlib seaborn nltk wordcloud scikit-learn

4️⃣ Rodar a aplicação
python app.py


Acesse no navegador:

http://127.0.0.1:5000

# 📊 Resultados e Visualizações

Os gráficos são gerados automaticamente e salvos em static/plots/, incluindo:

wordcloud.png → Nuvem de palavras

sentimentos.png → Distribuição de sentimentos

temporal.png → Publicações por ano

tendencias.png → Tendência de tópicos

top_palavras.png → Palavras mais frequentes

# 💡 Destaques Técnicos

Uso de threads para permitir que o scraping rode em paralelo ao servidor Flask.

Integração direta entre Selenium → SQLite → Pandas → Matplotlib → Flask.

Pipeline automático de ETL (Extração, Transformação e Visualização).

Modularidade: todas as configurações estão em config.py.

Tolerância a erros e mensagens detalhadas no console.

# 🧑‍💻 Autor

# Marlon Dias Marques
📍 Desenvolvedor de Sistemas | Cientista de Dados em formação
