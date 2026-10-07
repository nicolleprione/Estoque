from io import BytesIO
import pandas as pd
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo


def gerar_planilha(df_limpo, conferencias):

    # Copia da planilha já limpa
    df_final = df_limpo.copy()

    # Novas colunas
    df_final['Conferente'] = pd.Series(dtype='string', index=df_final.index)
    df_final['Data da Contagem'] = ''

    # Preenche a contagem
    for codigo, dados in conferencias.items():
        filtro = df_final['Códg Mestre'] == codigo
        df_final.loc[filtro, 'Contagem'] = dados['contagem']
        df_final.loc[filtro, 'Conferente'] = dados['conferente']
        df_final.loc[filtro, 'Data da Contagem'] = dados['data_contagem']

    return df_final


# Gerar excel
def gerar_excel(df_final):
    arquivo = BytesIO()

    with pd.ExcelWriter(arquivo, engine='openpyxl') as write:
        df_final.to_excel(write, index=False, sheet_name='Estoque')

    arquivo.seek(0)

    return arquivo


# Define o nome do JSON de acordo com a planilha
def caminho_progresso(nome_arquivo):
    nome = nome_arquivo.rsplit('.', 1)[0]
    return f'progresso-{nome}.json'


# Gravar o progresso
def salvar_progresso(nome_arquivo, conferencias):

    caminho = caminho_progresso(nome_arquivo)

    dados = {'arquivo': nome_arquivo, 'conferencias': conferencias}

    with open(caminho, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4, default=str)


# Carregar o progresso
def carregar_progresso(nome_arquivo):

    caminho = caminho_progresso(nome_arquivo)

    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        return dados['conferencias']

    except FileNotFoundError:
        return {}


# Limpar os dados
def limpar_progresso(nome_arquivo):

    caminho = caminho_progresso(nome_arquivo)

    try:
        os.remove(caminho)

    except FileNotFoundError:
        pass


# Horário atual
def horario_atual():
    return datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y - %H:%M:%S')
