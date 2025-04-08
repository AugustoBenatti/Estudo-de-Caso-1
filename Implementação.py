# Importação de bibliotecas
import pandas as pd  # Para manipulação de dados em DataFrames
from sklearn.ensemble import IsolationForest  # Algoritmo de detecção de anomalias
from sklearn.feature_extraction.text import TfidfVectorizer  # Para transformar texto em vetores numéricos (com peso TF-IDF)
from sklearn.preprocessing import LabelEncoder  # Para codificar variáveis categóricas (como o nível do log)
import numpy as np  # Para operações numéricas
from datetime import datetime  # Para gerar timestamps
import random  # Para gerar dados aleatórios

### Geração de Logs Aleatórios ###
def gerar_logs_aleatorios(num_logs=20):
    """
    Gera logs simulados com níveis INFO, WARN e ERROR.
    Retorna um DataFrame com colunas: timestamp, nivel, mensagem.
    """
    logs = []
    niveis = ["INFO", "WARN", "ERROR"]
    mensagens_info = ["Conexão estabelecida.", "Pagamento aprovado."]
    mensagens_warn = ["Tentativa de login falhou.", "Servidor lento."]
    mensagens_error = [
        "Falha crítica: servidor BD offline.",
        "Erro interno: exceção não tratada.",
        "Timeout conexão API.",
        "Divisão por zero detectada."
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

    return pd.DataFrame(logs)  # Retorna os logs em formato de tabela

### Extração de Features (Pré-processamento) ###
def extrair_features(df):
    """
    Transforma os logs em features numéricas para o modelo de ML.
    Retorna uma matriz numpy combinando:
    - Nível do log (codificado como 0, 1, 2)
    - Vetores TF-IDF das mensagens.
    """
    # Codifica o nível do log (INFO=0, WARN=1, ERROR=2)
    encoder = LabelEncoder()
    df["nivel_encoded"] = encoder.fit_transform(df["nivel"])

    # Vetoriza o texto das mensagens com TF-IDF (considera importância das palavras)
    vectorizer = TfidfVectorizer(max_features=50)
    X_text = vectorizer.fit_transform(df["mensagem"]).toarray()

    # Combina as features em uma única matriz
    X = np.hstack([df["nivel_encoded"].values.reshape(-1, 1), X_text])
    return X

### Detecção de Anomalias (Machine Learning) ###
def detectar_erros_sistema(df):
    """
    Identifica logs anômalos usando IsolationForest.
    Retorna um DataFrame com logs classificados como anomalias ou ERRORs.
    """
    if df.empty:
        print("Nenhum log para análise.")
        return pd.DataFrame()

    # Extrai features (pré-processamento)
    X = extrair_features(df)

    # ALGORITMO DE APRENDIZADO DE MÁQUINA; #
    # Configura e treina o IsolationForest
    model = IsolationForest(
        contamination=0.2,  # Proporção esperada de anomalias
        n_estimators=200,   # Número de árvores 
        random_state=42     # Semente para reprodutibilidade
    )
    # Treina o modelo e prediz anomalias (-1 é anomalia, 1 é normal)
    df["anomalia"] = model.fit_predict(X)

    # Filtra anomalias OU logs de ERROR (garante cobertura total)
    erros = df[(df["anomalia"] == -1) | (df["nivel"] == "ERROR")]
    return erros[["timestamp", "nivel", "mensagem"]]

### Exibição de Logs ###
def exibir_logs(df, titulo):
    """Exibe logs formatados no console."""
    print(f"\n{titulo}:")
    for _, row in df.iterrows():
        print(f"{row['timestamp']} - {row['nivel']} - {row['mensagem']}")

if __name__ == "__main__":
    # Gerar logs aleatórios
    df_logs = gerar_logs_aleatorios(50)  # Gera 50 logs
    exibir_logs(df_logs, "Logs gerados")

    # Detectar anomalias/erros (usando Machine Learning)
    erros = detectar_erros_sistema(df_logs)

    # Exibir resultados
    if not erros.empty:
        exibir_logs(erros, "Erros/anomalias detectados")
    else:
        print("\nNenhuma anomalia encontrada.")
