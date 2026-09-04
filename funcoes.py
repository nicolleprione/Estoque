from io import BytesIO
import pandas as pd
import json

def gerar_planilha(df_limpo, conferencias):

    # Copia da planilha já limpa
    df_final = df_limpo.copy()

    # Novas colunas
    df_final['Conferente'] = pd.Series(dtype='string', index=df_final.index)
    df_final['Data da Contagem'] = pd.Series(dtype='datetime64[ns]', index=df_final.index)

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

# Gravar o progresso
def salvar_progresso(nome_arquivo, conferencias):
    dados = {'arquivo': nome_arquivo, 'conferencias': conferencias}

    with open('progresso.json', 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4, default=str)

# Carregar o progesso
def carregar_progresso(nome_arquivo):
    try:
        with open('progresso.json', 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        if dados['arquivo'] == nome_arquivo:
            return dados['conferencias']

        return {}
    
    except FileNotFoundError:
        return{}

# Limpar os dados
def limpar_progresso():
    dados = {'arquivo': None, 'conferencias': {}}

    with open('progresso.json', 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)