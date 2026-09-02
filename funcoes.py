from io import BytesIO
import pandas as pd

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