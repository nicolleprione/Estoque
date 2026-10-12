# Importações
import math
import time
from io import BytesIO

import pandas as pd
import streamlit as st

import funcoes

# Configurações
st.set_page_config(page_title='Omnis')
st.header("Bem-Vindo(a) ao Omnis!")

ITENS_POR_PAGINA = 20      # quantos itens renderizar por vez (menos widgets = mais rápido)
INTERVALO_SYNC = 30        # segundos entre sincronizações automáticas com o Supabase
FUNCIONARIOS = ['Selecione', 'Ana Clara', 'André']


# LEITURA DA PLANILHA
@st.cache_data
def carregar_planilha(conteudo_arquivo):
    df = pd.read_excel(BytesIO(conteudo_arquivo), dtype={'Códg Mestre': str})
    return df.drop_duplicates(subset='Códg Mestre')


# SESSION STATE
padroes = {
    'codigo_selecionado': None,
    'codigo_confirmado': False,
    'conferencias': {},
    'modo_edicao': False,
    'arquivo_carregado': None,
    'df_limpo': None,
    'conferencia_id': None,
    'status_conferencia': None,
    'arquivo_excel': None,      # bytes do Excel gerado (substitui o antigo planilha_gerada)
    'ultima_sync': 0.0,         # quando foi a última busca no Supabase
    'pagina': 0,
    'busca_anterior': '',
}
for chave, valor in padroes.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


# SINCRONIZAÇÃO COM O SUPABASE
def sincronizar(forcar=False):
    """Busca status e contagens no banco, no máximo a cada INTERVALO_SYNC segundos
    (ou imediatamente, se forcar=True)."""
    agora = time.time()
    if not forcar and agora - st.session_state.ultima_sync < INTERVALO_SYNC:
        return

    conferencia = funcoes.localizar_ou_criar_conferencia(st.session_state.arquivo_carregado)

    st.session_state.conferencia_id = conferencia['id']
    st.session_state.status_conferencia = conferencia['status']
    st.session_state.conferencias = funcoes.buscar_contagens(conferencia['id'])
    st.session_state.ultima_sync = agora


# DIÁLOGO DE CONFIRMAÇÃO
@st.dialog('⚠️ Finalizar Conferência')
def confirmar_finalizacao(nome_arquivo):
    st.write('Deseja finalizar esta conferência? '
             'Os dados serão preservados, mas não poderão ser alterados.')
    coluna01, coluna02 = st.columns(2)

    with coluna01:
        if st.button('SIM', type='primary', use_container_width=True):
            try:
                funcoes.finalizar_conferencia(st.session_state.conferencia_id)

                st.session_state.status_conferencia = 'finalizada'
                st.session_state.codigo_selecionado = None
                st.session_state.codigo_confirmado = False
                st.session_state.modo_edicao = False
                st.session_state.arquivo_excel = None

                st.rerun()

            except Exception as erro:
                st.error(f'Erro ao finalizar a conferência: {erro}')

    with coluna02:
        if st.button('NÃO', use_container_width=True):
            st.rerun()


# LISTA DE CONFERÊNCIA (fragmento: interações aqui não rodam o app inteiro)
@st.fragment
def lista_conferencia():
    # Só vai ao banco se passou o intervalo (ou se o usuário clicar em Atualizar)
    sincronizar()

    df_limpo = st.session_state.df_limpo

    st.subheader('Lista de Conferência')

    if st.button('Atualizar'):
        sincronizar(forcar=True)
        st.session_state.arquivo_excel = None  # os dados podem ter mudado

    conferencias = st.session_state.conferencias
    em_andamento = st.session_state.status_conferencia == 'em_andamento'

    # Progresso
    total_itens = len(df_limpo)
    concluidos = len(conferencias)
    progresso = min(concluidos / total_itens, 1.0) if total_itens > 0 else 0

    st.progress(progresso)
    st.write(f'{concluidos} de {total_itens} itens conferidos.')

    # Geração da planilha (só roda quando o botão é clicado)
    if concluidos == total_itens and total_itens > 0:
        st.success('Todos os itens foram conferidos!')

        col_gerar, col_baixar, col_finalizar = st.columns(3)

        with col_gerar:
            if st.button('Gerar Planilha'):
                with st.spinner('Gerando planilha...'):
                    df_final = funcoes.gerar_planilha(df_limpo, conferencias)
                    st.session_state.arquivo_excel = funcoes.gerar_excel(df_final)

        if st.session_state.arquivo_excel is not None:
            with col_baixar:
                st.download_button(
                    label='Baixar',
                    data=st.session_state.arquivo_excel,
                    file_name=f'conferencia-{st.session_state.arquivo_carregado}',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            with col_finalizar:
                if em_andamento and st.button('Finalizar'):
                    confirmar_finalizacao(st.session_state.arquivo_carregado)

    # BUSCA E FILTROS
    busca = st.text_input('Buscar por código ou descrição', key='busca').strip()
    mostrar_conferidos = st.checkbox('Mostrar itens já conferidos', value=True, key='mostrar_conferidos')

    if busca != st.session_state.busca_anterior:
        st.session_state.busca_anterior = busca
        st.session_state.pagina = 0

    # Pendentes primeiro, depois conferidos
    ja_conferido = df_limpo['Códg Mestre'].isin(list(conferencias))
    itens_pendentes = df_limpo[~ja_conferido]
    itens_conferidos = df_limpo[ja_conferido]

    if mostrar_conferidos:
        itens_ordenados = pd.concat([itens_pendentes, itens_conferidos])
    else:
        itens_ordenados = itens_pendentes

    if busca:
        filtro = (
            itens_ordenados['Códg Mestre'].str.contains(busca, case=False, regex=False, na=False)
            | itens_ordenados['Descrição'].astype(str).str.contains(busca, case=False, regex=False, na=False)
        )
        itens_ordenados = itens_ordenados[filtro]

    # PAGINAÇÃO
    total_paginas = max(1, math.ceil(len(itens_ordenados) / ITENS_POR_PAGINA))
    pagina = min(st.session_state.pagina, total_paginas - 1)

    col_ant, col_info, col_prox = st.columns([1, 2, 1], vertical_alignment='center')
    with col_ant:
        if st.button('◀', key='pagina_anterior', disabled=pagina == 0, use_container_width=True):
            pagina -= 1
    with col_prox:
        if st.button('▶', key='pagina_proxima', disabled=pagina >= total_paginas - 1, use_container_width=True):
            pagina += 1
    with col_info:
        st.caption(f'Página {pagina + 1} de {total_paginas} ({len(itens_ordenados)} itens)')

    st.session_state.pagina = pagina

    inicio = pagina * ITENS_POR_PAGINA
    itens_da_pagina = itens_ordenados.iloc[inicio:inicio + ITENS_POR_PAGINA]

    # SELEÇÃO DOS ITENS
    for _, item in itens_da_pagina.iterrows():

        coluna1, coluna2 = st.columns([3, 1], vertical_alignment='center')

        codigo = item['Códg Mestre']
        descricao = item['Descrição']
        locacao = item['Locações']

        # ITEM CONFERIDO
        if codigo in conferencias:
            with coluna1:
                st.success(f'✓ {codigo} - {descricao}')

            with coluna2:
                if em_andamento:
                    if st.button('Editar', key=f'editar_{codigo}'):
                        st.session_state.codigo_selecionado = codigo
                        st.session_state.codigo_confirmado = True
                        st.session_state.modo_edicao = True

                        st.rerun(scope="fragment")
                else:
                    st.button('Finalizado', key=f'finalizado_{codigo}', disabled=True)

        # ITEM NÃO CONFERIDO
        else:
            with coluna1:
                st.write(f'{codigo} - {descricao}')

            with coluna2:
                if em_andamento:
                    if st.button('Conferir', key=codigo):
                        st.session_state.codigo_selecionado = codigo
                        st.session_state.codigo_confirmado = False
                        st.session_state.modo_edicao = False

                        st.rerun(scope="fragment")
                else:
                    st.button('Finalizado', key=f'pendente_finalizado_{codigo}', disabled=True)

        # ITEM SELECIONADO
        if st.session_state.codigo_selecionado == codigo:

            with st.container(border=True):
                st.write(f"Código: {codigo}")
                st.write(f"Descrição: {descricao}")
                st.write(f"Locação: {locacao}")

                # CONFIRMAÇÃO DO CÓDIGO
                if not st.session_state.modo_edicao:
                    codigo_digitado = st.text_input('Confirme o código: ', key=f'codigo_digitado_{codigo}')

                    if st.button('Confirmar código', key=f'confirmar_{codigo}'):
                        if codigo_digitado == codigo:
                            # Sem st.rerun: o bloco abaixo já lê esse estado na mesma execução
                            st.session_state.codigo_confirmado = True
                        else:
                            st.session_state.codigo_confirmado = False
                            st.error('Código incorreto.')

            # CONFERÊNCIA
            if st.session_state.codigo_confirmado:
                with st.container(border=True):
                    conferencia_existente = conferencias.get(codigo)

                    if conferencia_existente:
                        conferencia_inicial = conferencia_existente['conferente']
                        contagem_inicial = conferencia_existente['contagem']
                    else:
                        conferencia_inicial = 'Selecione'
                        contagem_inicial = 0

                    if conferencia_inicial in FUNCIONARIOS:
                        indice_conferente = FUNCIONARIOS.index(conferencia_inicial)
                    else:
                        indice_conferente = 0

                    conferente = st.selectbox(
                        'Usuário',
                        FUNCIONARIOS,
                        index=indice_conferente,
                        key=f'usuario_{codigo}'
                    )

                    contagem = st.number_input(
                        'Quantidade física',
                        min_value=0,
                        step=1,
                        value=int(contagem_inicial),
                        key=f'contagem_{codigo}'
                    )

                    # SALVAR
                    if st.button('Salvar', key=f'salvar_{codigo}'):

                        if conferente == 'Selecione':
                            st.error('Selecione um usuário')

                        else:
                            funcoes.salvar_contagem(
                                st.session_state.conferencia_id,
                                codigo,
                                conferente,
                                int(contagem)
                            )

                            # Atualiza localmente, sem nova consulta ao banco
                            st.session_state.conferencias[codigo] = {
                                'conferente': conferente,
                                'contagem': int(contagem),
                                'data_contagem': funcoes.horario_atual()
                            }
                            st.session_state.arquivo_excel = None

                            # Limpa a seleção
                            st.session_state.codigo_selecionado = None
                            st.session_state.codigo_confirmado = False
                            st.session_state.modo_edicao = False

                            st.rerun(scope="fragment")

        st.divider()


# IMPORTAÇÃO DOS DADOS
importar_arquivo = st.file_uploader(label='Importe', type=['xlsx'])

if importar_arquivo:
    nome_arquivo = importar_arquivo.name

    # Só lê a planilha e consulta o banco quando o arquivo muda
    if st.session_state.arquivo_carregado != nome_arquivo:
        with st.spinner('Lendo planilha...'):
            st.session_state.df_limpo = carregar_planilha(importar_arquivo.getvalue())

        st.session_state.arquivo_carregado = nome_arquivo
        st.session_state.arquivo_excel = None
        st.session_state.codigo_selecionado = None
        st.session_state.codigo_confirmado = False
        st.session_state.modo_edicao = False
        st.session_state.pagina = 0

        sincronizar(forcar=True)

    lista_conferencia()