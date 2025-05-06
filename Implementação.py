import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from datetime import datetime
import random,3

import re

def gerar_logs_aleatorios(num_logs=20):
    logs = []
    niveis = ["INFO", "WARN", "ERROR"]

    mensagens_info = [
        "Conexão com o servidor estabelecida.",
        "Pagamento processado com sucesso.",
        "Produto adicionado ao carrinho.",
        "Usuário fez login com sucesso.",
        "Pedido finalizado com sucesso."
    ]

    mensagens_warn = [
        "Tentativa de pagamento falhou, cartão expirado.",
        "Tentativa de login falhou, senha incorreta.",
        "Tempo de resposta do servidor acima do esperado."
    ]

    mensagens_error = [
        "Erro ao processar pagamento com cartão de crédito.",
        "Timeout na API do gateway de pagamento.",
        "Discrepância nos valores da transação detectada.",
        "Falha ao validar dados bancários do cliente.",
        "Erro interno no sistema de pagamento.",
        "Transação duplicada identificada no sistema.",
        "Erro ao calcular total da compra com desconto aplicado."
    ]

    for _ in range(num_logs):
        nivel = random.choice(niveis)
        if nivel == "INFO":
            mensagem = random.choice(mensagens_info)
        elif nivel == "WARN":
            mensagem = random.choice(mensagens_warn)
        else:
            mensagem = random.choice(mensagens_error)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        logs.append({"timestamp": timestamp, "nivel": nivel, "mensagem": mensagem})

    return pd.DataFrame(logs)


def detectar_por_regras(df):
    padrao = r"\berro\b|\bfalha\b|\btimeout\b|\bduplicada\b|\binválido\b|\bdiscrepância\b"
    return df[df['mensagem'].str.contains(padrao, flags=re.IGNORECASE, regex=True)]


def detectar_por_ia(df):
    df_erros = df[df['nivel'] == 'ERROR'].copy()
    if df_erros.empty:
        return pd.DataFrame()

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df_erros['mensagem']).toarray()

    modelo = OneClassSVM(gamma='auto', nu=0.2)  # nu controla sensibilidade a anomalias
    df_erros['anomalia'] = modelo.fit_predict(X)
    
    return df_erros[df_erros['anomalia'] == -1]


def detectar_erros_sistema(df):
    if df.empty:
        print("Nenhum log disponível para análise.")
        return pd.DataFrame()

    por_regras = detectar_por_regras(df)
    por_ia = detectar_por_ia(df)

    # Combinar resultados e remover duplicatas
    df_resultado = pd.concat([por_regras, por_ia]).drop_duplicates()
    return df_resultado[['timestamp', 'nivel', 'mensagem']]


def exibir_logs(df, titulo):
    print(f"\n{titulo}:")
    for _, row in df.iterrows():
        print(f"{row['timestamp']} - {row['nivel']} - {row['mensagem']}")


if __name__ == "__main__":
    df_logs = gerar_logs_aleatorios(30)
    exibir_logs(df_logs, "Logs gerados")

    erros_sistema = detectar_erros_sistema(df_logs)
    if not erros_sistema.empty:
        exibir_logs(erros_sistema, "Erros de transações financeiras detectados")
    else:
        print("\nNenhum erro de sistema detectado.")
