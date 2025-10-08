# Configurações da aplicação Flask

# Configurações do Flask
FLASK_CONFIG = {
    'SECRET_KEY': 'sua_chave_secreta_muito_segura_aqui',
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 5000
}

# Configurações do Selenium
SELENIUM_CONFIG = {
    'WEBDRIVER': 'edge',  # edge, chrome, firefox
    'HEADLESS': True,     # True para executar sem interface gráfica
    'WINDOW_SIZE': '1920,1080',
    'TIMEOUT': 30,        # Timeout em segundos
    'IMPLICIT_WAIT': 10   # Espera implícita em segundos
}

# Configurações do banco de dados
DATABASE_CONFIG = {
    'DATABASE_NAME': 'buscas_completas_CQ.db',
    'TABLE_NAME': 'resultados_detalhados_CQ'
}

# Configurações de busca
SEARCH_CONFIG = {
    'DEFAULT_YEAR_START': 2024,
    'DEFAULT_YEAR_END': 2025,
    'DEFAULT_MIN_RESULTS': 50,
    'MAX_RESULTS_PER_TOPIC': 1000,
    'SEARCH_DELAY': 4,      # Delay entre requests em segundos
    'PAGE_DELAY': 2,        # Delay entre páginas em segundos
    'RETRY_ATTEMPTS': 3     # Tentativas em caso de erro
}

# Tópicos predefinidos de pesquisa
DEFAULT_TOPICS = [
    "Computação Quântica na Criptografia",
    "Otimização Quântica em Finanças",
    "Inteligência Artificial e Aprendizado de Máquina Quântico",
    "Computação Quântica e Descoberta de Medicamentos",
    "Química Quântica Computacional",
    "Perspectivas Futuras da Computação Quântica",
    "Computação Quântica Pós-Quântica",
    "Desafios e Oportunidades na Era Quântica"
]

# Configurações de análise de texto
TEXT_ANALYSIS_CONFIG = {
    'STOPWORDS_PORTUGUESE': True,
    'CUSTOM_STOPWORDS': [
        'computacao', 'quantica', 'quântico', 'quantum', 
        'trabalho', 'estudo', 'pesquisa', 'neste', 'este', 
        'para', 'com', 'que', 'uma', 'como', 'sobre', 
        'dados', 'resultados', 'artigo', 'paper', 'revista'
    ],
    'POSITIVE_WORDS': [
        'inovação', 'oportunidades', 'avanços', 'eficiente', 
        'sucesso', 'breakthrough', 'promissor', 'revolucionário',
        'otimização', 'melhoria', 'solução'
    ],
    'NEGATIVE_WORDS': [
        'desafios', 'problemas', 'riscos', 'limitações', 
        'ameaça', 'dificuldades', 'obstáculos', 'barreiras',
        'complexidade', 'erro'
    ]
}

# Configurações dos gráficos
PLOT_CONFIG = {
    'DPI': 300,
    'FIGURE_SIZE': (12, 8),
    'STYLE': 'seaborn-v0_8',
    'COLOR_PALETTE': 'viridis',
    'FONT_SIZE': 12,
    'TITLE_SIZE': 16,
    'SAVE_FORMAT': 'png'
}

# Configurações de export
EXPORT_CONFIG = {
    'CSV_ENCODING': 'utf-8-sig',  # Para compatibilidade com Excel
    'CSV_SEPARATOR': ',',
    'INCLUDE_INDEX': False,
    'DATE_FORMAT': '%Y-%m-%d %H:%M:%S'
}

# URLs e seletores CSS (podem mudar com atualizações do Google Scholar)
GOOGLE_SCHOLAR_CONFIG = {
    'BASE_URL': 'https://scholar.google.com.br/scholar',
    'RESULT_SELECTOR': 'div.gs_ri',
    'TITLE_SELECTOR': 'h3.gs_rt a',
    'AUTHOR_YEAR_SELECTOR': 'div.gs_a',
    'ABSTRACT_SELECTOR': 'div.gs_rs',
    'NEXT_BUTTON_ID': 'gs_n',
    'NEXT_BUTTON_TEXT': 'Próxima'
}

# Configurações de logging
LOGGING_CONFIG = {
    'LEVEL': 'INFO',
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'FILE': 'app.log',
    'MAX_SIZE': 10485760,  # 10MB
    'BACKUP_COUNT': 5
}

# Configurações de cache (para implementação futura)
CACHE_CONFIG = {
    'ENABLED': False,
    'TYPE': 'simple',
    'TIMEOUT': 3600,  # 1 hora
    'KEY_PREFIX': 'webscraping_'
}
