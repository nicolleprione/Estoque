from io import BytesIO
import pandas as pd
import streamlit as st
import psycopg
from datetime import datetime
from zoneinfo import ZoneInfo

def conectar_banco():
    return psycopg.connect(
        host=st.secrets['database']['host'],
        port=st.secrets['database']['port'],
        dbname=st.secrets['database']['dbname'],
        user=st.secrets['database']['user'],
        password=st.secrets['database']['password'],
        sslmode=st.secrets['database']['sslmode']
    )

def localizar_ou_criar_conferencia(nome_arquivo):
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:

            #1. Tentar criar a conferência, se ainda não existir
            cursor.execute(
                """
                INSERT INTO conferencias (
                    nome_arquivo, 
                    criada_em
                )
                VALUES (%s, NOW())
                ON CONFLICT (nome_arquivo) DO NOTHING
                RETURNING id, nome_arquivo, status, criada_em, finalizada_em
                """,
                (nome_arquivo,)
            )
            conferencia = cursor.fetchone()

            #2. Se já existia, localiza o registro existente
            if conferencia is None:
                cursor.execute(
                    """
                    SELECT id, nome_arquivo, status, criada_em, finalizada_em
                    FROM conferencias
                    WHERE nome_arquivo = %s
                    """,
                    (nome_arquivo,)
                )
                conferencia = cursor.fetchone()

            #3. Organizar os dados para facilitar o uso no Python
            if conferencia is None:
                raise RuntimeError('Não foi possível localizar a conferência.')

            return {
                'id': conferencia[0],
                'nome_arquivo': conferencia[1],
                'status': conferencia[2],
                'criada_em': conferencia[3],
                'finalizada_em': conferencia[4]
            }

def buscar_contagens(conferencia_id):
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT codigo, conferente, quantidade, data_contagem
                FROM contagens
                WHERE conferencia_id = %s
                """,
                (conferencia_id, )
            )
            registros = cursor.fetchall()

    conferencias = {}

    for codigo, conferente, quantidade, data_contagem in registros:
        data_local = data_contagem.astimezone(
            ZoneInfo('America/Sao_Paulo')
        )
        conferencias[codigo] = {
            'conferente': conferente,
            'contagem': quantidade,
            'data_contagem': data_local.strftime("%d/%m/%Y - %H:%M:%S")
        }
    return conferencias

def salvar_contagem(conferencia_id, codigo, conferente, quantidade):
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:

            # Verifica se a conferência ainda está em andamento
            cursor.execute(
                """
                SELECT status
                FROM conferencias
                WHERE id = %s
                FOR UPDATE
                """,
                (conferencia_id,)
            )
            resultado = cursor.fetchone()

            if resultado is None:
                raise ValueError('Conferência não encontrada.')

            if resultado[0] != 'em_andamento':
                raise ValueError('Esta conferência está finalizada e não pode ser alterada')

            # Insere uma nova contagem ou atualiza a existente
            cursor.execute(
                """
                INSERT INTO contagens (
                    conferencia_id,
                    codigo,
                    conferente,
                    quantidade,
                    data_contagem    
                )
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (conferencia_id, codigo)
                DO UPDATE SET
                    conferente = EXCLUDED.conferente,
                    quantidade = EXCLUDED.quantidade,
                    data_contagem = NOW()
                """,
                (conferencia_id, str(codigo), conferente, quantidade)
            )

def finalizar_conferencia(conferencia_id):
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                UPDATE conferencias
                SET status = 'finalizada',
                    finalizada_em = NOW()
                WHERE id = %s
                    AND status = 'em_andamento'
                RETURNING id
                """,
                (conferencia_id,)
            )
            resultado = cursor.fetchone()

            if resultado is None:
                raise ValueError('Conferência não encontrada ou já finalizada')
    return True

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

# Horário atual
def horario_atual():
    return datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y - %H:%M:%S')
