# Importações
import streamlit as st
import pandas as pd
import funcoes
from io import BytesIO

# Configurações
st.set_page_config(page_title='Omnis')
st.header("Bem-Vindo(a) ao Omnis!")

@st.cache_data
def carregar_planilha(conteudo_arquivo):
    df = pd.read_excel(BytesIO(conteudo_arquivo), dtype={'Códg Mestre':str})
    df_limpo = df.drop_duplicates(subset='Códg Mestre')
    return df_limpo

# SESSION STATE

# Estado do código selecionado
if 'codigo_selecionado' not in st.session_state:
    st.session_state.codigo_selecionado = None

# Estado da confirmação
if 'codigo_confirmado' not in st.session_state:
    st.session_state.codigo_confirmado = False

# Estado de conferências
if 'conferencias' not in st.session_state:
    st.session_state.conferencias = {}

# Estado de edição
if 'modo_edicao' not in st.session_state:
    st.session_state.modo_edicao = False

# Estado do arquivo carregado
if 'arquivo_carregado' not in st.session_state:
    st.session_state.arquivo_carregado = None

# Estado da planilha gerada
if 'planilha_gerada' not in st.session_state:
    st.session_state.planilha_gerada = False

if 'conferencia_id' not in st.session_state:
    st.session_state.conferencia_id = None

if 'status_conferencia' not in st.session_state:
    st.session_state.status_conferencia = None

# Diálogo de confirmação
@st.dialog('⚠️ Finalizar Conferência')
def confirmar_finalizacao(nome_arquivo):
    st.write('Deseja finalizar esta conferência? '
             'Os dados serão preservado, mas não poderão ser alterados.'
             )
    coluna01, coluna02 = st.columns(2)

    with coluna01:
        if st.button('SIM', type='primary', use_container_width=True):
            try:
                funcoes.finalizar_conferencia(st.session_state.conferencia_id)

                st.session_state.status_conferencia = 'finalizada'
                st.session_state.codigo_selecionado = None
                st.session_state.codigo_confirmado = False
                st.session_state.modo_edicao = False
                st.session_state.planilha_gerada = False

                st.rerun()

            except Exception as erro:
                st.error(f'Erro ao finalizar a conferência: {erro}')

    with coluna02:
        if st.button('NÃO', use_container_width=True):
            st.rerun()

# Importação dos dados
importar_arquivo = st.file_uploader(label='Importe', type=['xlsx'])

# Verifica se foi importado algo
if importar_arquivo:

    nome_arquivo = importar_arquivo.name

    # Leitura otimizada dos dados
    df_limpo = carregar_planilha(importar_arquivo.getvalue())

    # Informações da planilha
    total_itens = len(df_limpo)

    # Carregar o progresso correspondente à planilha
    if st.session_state.arquivo_carregado != nome_arquivo:
        conferencia = funcoes.localizar_ou_criar_conferencia(nome_arquivo)

        st.session_state.conferencia_id = conferencia['id']
        st.session_state.status_conferencia = conferencia['status']

        st.session_state.conferencias = funcoes.buscar_contagens(conferencia['id'])

        st.session_state.arquivo_carregado = nome_arquivo
        st.session_state.planilha_gerada = False

    # LISTA DE CONFERÊNCIA
@st.fragment
def atualizar_contagem():
    if st.session_state.conferencia_id is not None:
        conferencia = funcoes.localizar_ou_criar_conferencia(st.session_state.arquivo_carregado)

        st.session_state.status_conferencia = conferencia['status']
        st.session_state.conferencias = funcoes.buscar_contagens(st.session_state.conferencia_id)

    st.subheader('Lista de Conferência')

    if st.button('Atualizar'):
        st.rerun(scope="fragment")

    # Atualização do progresso
    total_itens = len(df_limpo)
    concluidos = len(st.session_state.conferencias)

    progresso = concluidos / total_itens if total_itens > 0 else 0

    st.progress(progresso)
    st.write(f'{concluidos} de {total_itens} itens conferidos.')

    # Geração da planilha
    if concluidos == total_itens and total_itens > 0:
        st.success('Todos os itens foram conferidos!')

        col_gerar, col_baixar, col_finalizar = st.columns(3)

        with col_gerar:
            if st.button('Gerar Planilha'):
                st.session_state.planilha_gerada = True
                st.rerun(scope="fragment")

        if st.session_state.planilha_gerada:
            df_final = funcoes.gerar_planilha(df_limpo, st.session_state.conferencias)
            arquivo_excel = funcoes.gerar_excel(df_final)

            with col_baixar:
                st.download_button(
                    label='Baixar',
                    data=arquivo_excel,
                    file_name=f'conferencia-{st.session_state.arquivo_carregado}',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            with col_finalizar:
                if st.session_state.status_conferencia == 'em_andamento':
                    if st.button('Finalizar'):
                        confirmar_finalizacao(st.session_state.arquivo_carregado)

    # Itens ainda não conferidos
    itens_pendentes = df_limpo[
        ~df_limpo['Códg Mestre'].isin(
            st.session_state.conferencias
        )]

    # Itens já conferidos
    itens_conferidos = df_limpo[
        df_limpo['Códg Mestre'].isin(
            st.session_state.conferencias
        )]

    # Primeiro os pendentes
    itens_ordenados = pd.concat([itens_pendentes, itens_conferidos])

    # SELEÇÃO DOS ITENS
    for _, item in itens_ordenados.iterrows():

        # Geração das colunas
        coluna1, coluna2 = st.columns([3, 1], vertical_alignment='center')

        codigo = item['Códg Mestre']
        descricao = item['Descrição']
        locacao = item['Locações']


        # ITEM CONFERIDO
        if codigo in st.session_state.conferencias:
            with coluna1:
                st.success(f'✓ {codigo} - {descricao}')

            # Botão editar ou indicação de finalizado
            with coluna2:
                if st.session_state.status_conferencia == 'em_andamento':
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
                if st.session_state.status_conferencia == 'em_andamento':
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
                st.write(f"Código: {item['Códg Mestre']}")
                st.write(f"Descrição: {item['Descrição']}")
                st.write(f"Locação: {item['Locações']}")


                # CONFIRMAÇÃO DO CÓDIGO
                if not st.session_state.modo_edicao:
                    codigo_digitado = st.text_input('Confirme o código: ', key=f'codigo_digitado_{codigo}')

                    if st.button('Confirmar código', key=f'confirmar_{codigo}'):
                        if codigo_digitado == codigo:
                            st.session_state.codigo_confirmado = True

                            st.rerun(scope="fragment")
                        else:
                            st.session_state.codigo_confirmado = False
                            st.error('Código incorreto.')

            # CONFERÊNCIA
            if st.session_state.codigo_confirmado:
                with st.container(border=True):
                    conferencia_existente = (st.session_state.conferencias.get(codigo))

                    # Valores iniciais
                    if conferencia_existente:
                        conferencia_inicial = (conferencia_existente['conferente'])

                        contagem_inicial = (conferencia_existente['contagem'])

                    else:
                        conferencia_inicial = 'Selecione'
                        contagem_inicial = 0


                    funcionarios = ['Selecione', 'Ana Clara', 'André']

                    indice_conferente = (funcionarios.index(conferencia_inicial))

                    # Seleção do funcionário
                    conferente = st.selectbox(
                        'Usuário',
                        funcionarios,
                        index=indice_conferente,
                        key=f'usuario_{codigo}'
                    )

                    # Contagem física
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
                            # Salva a conferência
                            funcoes.salvar_contagem(
                                st.session_state.conferencia_id,
                                codigo,
                                conferente,
                                int(contagem)
                            )

                            st.session_state.conferencias[codigo] = {
                                'conferente': conferente,
                                'contagem': int(contagem),
                                'data_contagem': funcoes.horario_atual()
                            }


                            # Limpa a seleção
                            st.session_state.codigo_selecionado = None
                            st.session_state.codigo_confirmado = False
                            st.session_state.modo_edicao = False


                            st.rerun(scope="fragment")
        st.divider()
if importar_arquivo:
    atualizar_contagem()