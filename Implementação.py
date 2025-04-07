import pandas as pd  # Para manipulação de dados em formato de tabela (DataFrames)
from sklearn.ensemble import IsolationForest  # Algoritmo de detecção de anomalias
from sklearn.feature_extraction.text import CountVectorizer  # Para transformar texto em vetores numéricos
import numpy as np  # Para cálculos numéricos
from datetime import datetime  # Para gerar timestamps (marcas de tempo)
import random  # Para gerar dados aleatórios

# Função para gerar logs aleatórios
def gerar_logs_aleatorios(num_logs=20): #num_logs=20 define que 20 logs serão gerados

    logs = []  # Lista para armazenar os logs
    niveis = ["INFO", "WARN", "ERROR"]  # tipos de logs a serem gerados
    mensagens_info = [  # Mensagens para logs do tipo INFO
        "Conexão com o servidor estabelecida.",
        "Pagamento processado com sucesso.",
        "Produto adicionado ao carrinho.",
        "Usuário fez login com sucesso.",
        "Pedido finalizado com sucesso."
    ]
    mensagens_warn = [  # Mensagens para logs do tipo WARN
        "Tentativa de pagamento falhou, cartão expirado.",
        "Tentativa de login falhou, senha incorreta.",
        "Tempo de resposta do servidor acima do esperado."
    ]
    mensagens_error = [  # Mensagens para logs do tipo ERROR
        "Falha na conexão com o servidor de pagamento.",
        "Servidor de banco de dados offline.",
        "Timeout na conexão com a API de frete.",
        "Erro interno no processamento do pedido."
    ]

    # Gera os logs aleatórios
    for _ in range(num_logs):
        nivel = random.choice(niveis)  # Escolhe um nível de severidade aleatório
        if nivel == "INFO":
            mensagem = random.choice(mensagens_info)  # Escolhe uma mensagem do tipo INFO
        elif nivel == "WARN":
            mensagem = random.choice(mensagens_warn)  # Escolhe uma mensagem do tipo WARN
        else:
            mensagem = random.choice(mensagens_error)  # Escolhe uma mensagem do tipo ERROR

        # Gera um timestamp (marca de tempo) no formato AAAA-MM-DD HH:MM:SS,
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        # Adiciona o log à lista de logs
        logs.append({"timestamp": timestamp, "nivel": nivel, "mensagem": mensagem})

    # Converte a lista de logs em um DataFrame do Pandas e retorna
    return pd.DataFrame(logs)

# Função para detectar logs com erros de sistema
def detectar_erros_sistema(df): #df (pd.DataFrame): DataFrame contendo os logs.

    # Verifica se o DataFrame de logs está vazio
    if df.empty:
        print("Nenhum log disponível para análise.")
        return pd.DataFrame()  # Retorna um DataFrame vazio

    # Filtra apenas os logs do tipo ERROR
    df_erros = df[df['nivel'] == 'ERROR'].copy()
    if df_erros.empty:
        print("Nenhum erro de sistema encontrado.")
        return pd.DataFrame()  # Retorna um DataFrame vazio

    # Vetorização do texto das mensagens
    vectorizer = CountVectorizer()  # Cria um vetorizador de texto
    X = vectorizer.fit_transform(df_erros['mensagem']).toarray()  # Transforma as mensagens em vetores numéricos

    # Treinamento do IsolationForest para detectar anomalias
    iso_forest = IsolationForest(contamination=0.5)  # Cria o modelo de detecção de anomalias
    df_erros.loc[:, 'anomalia'] = iso_forest.fit_predict(X)  # Aplica o modelo e armazena as previsões

    # Filtra apenas os logs com erros de sistema (anomalias)
    erros_sistema = df_erros[df_erros['anomalia'] == -1]
    # Retorna apenas as colunas relevantes (timestamp, nivel, mensagem)
    return erros_sistema[['timestamp', 'nivel', 'mensagem']]

# Função para exibir logs formatados
def exibir_logs(df, titulo):

    print(f"\n{titulo}:")
    # Itera sobre cada linha do DataFrame
    for _, row in df.iterrows():
        # Exibe o log no formato TIMESTAMP - NÍVEL - MENSAGEM
        print(f"{row['timestamp']} - {row['nivel']} - {row['mensagem']}")

# Execução do código
if __name__ == "__main__":

    # Passo 1: Gerar logs aleatórios
    df_logs = gerar_logs_aleatorios()
    # Exibe os logs gerados
    exibir_logs(df_logs, "Logs gerados")

    # Passo 2: Detectar erros de sistema
    erros_sistema = detectar_erros_sistema(df_logs)
    # Se erros de sistema forem encontrados, exibe-os
    if not erros_sistema.empty:
        exibir_logs(erros_sistema, "Erros de sistema detectados")
    else:
        # Caso contrário, informa que nenhum erro foi detectado
        print("\nNenhum erro de sistema detectado.")