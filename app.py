# Importações
import streamlit as st
import pandas as pd
from datetime import datetime
import funcoes

# Configurações
st.set_page_config(page_title='Omnis')
st.header("Bem-Vindo(a) ao Omnis!")

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
    st.session_state.arquivo_carregado = False

# Estado da planilha gerada
if 'planilha_gerada' not in st.session_state:
    st.session_state.planilha_gerada = False

# Diálogo de confirmação
@st.dialog('⚠️ Finalizar Conferência')
def confirmar_finalizacao(nome_do_arquivo):
    st.write('Deseja limpar os dados?')

    coluna01, coluna02 = st.columns(2)
    with coluna01:
        if st.button('SIM', type='primary', use_container_width=True):
            funcoes.limpar_progresso()

            st.session_state.conferencias = {}
            st.session_state.codigo_selecionado = None
            st.session_state.codigo_confirmado = False
            st.session_state.modo_edicao = False
            st.session_state.arquivo_carregado = None
            st.session_state.planilha_gerada = False
            
            st.rerun()
        with coluna02:
            if st.button('NÂO', use_container_width=True):
                st.rerun()

# Importação dos dados e verificação
importar_arquivo = st.file_uploader(label='Importe',type=['xlsx'])

# Verifica se foi importado algo
if importar_arquivo:

    nome_arquivo = importar_arquivo.name

    # Leitura dos dados
    df = pd.read_excel(importar_arquivo, dtype={'Códg Mestre': str})
    
    # Remoção das duplicatas
    df_limpo = df.drop_duplicates(subset='Códg Mestre')

    # Informações da planilha
    total_itens = len(df_limpo)
    concluidos = len(st.session_state.conferencias)

    # Carregar o progresso do arquivo
    if st.session_state.arquivo_carregado != nome_arquivo:
        st.session_state.conferencias = funcoes.carregar_progresso(nome_arquivo)
        st.session_state.arquivo_carregado = nome_arquivo
    concluidos = len(st.session_state.conferencias)

    # Progresso
    if total_itens > 0:
        progresso = concluidos / total_itens
    else:
        progresso = 0

    st.progress(progresso)
    st.write(f'{concluidos} de {total_itens} itens conferidos.')

    # Botão de geração de planilha
    if concluidos == total_itens and total_itens > 0:
        st.success('Todos os itens foram conferidos!')

        # Colunas dos botões
        col_gerar, col_baixar, col_finalizar = st.columns(3)

        with col_gerar:
            if st.button('Gerar Planilha'):
                st.session_state.planilha_gerada = True
                st.rerun()

        if st.session_state.planilha_gerada:
            df_final = funcoes.gerar_planilha(df_limpo, st.session_state.conferencias)
            arquivo_excel = funcoes.gerar_excel(df_final)

            with col_baixar:
                st.download_button(label='Baixar Planilha', data=arquivo_excel, file_name=f'conferencia-{importar_arquivo.name}', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            with col_finalizar:
                if st.button('Finalizar'):
                    confirmar_finalizacao(nome_arquivo)

    st.subheader('Lista de Conferência')

    # Separação de itens não conferidos
    itens_pendentes = df_limpo[~df_limpo['Códg Mestre'].isin(st.session_state.conferencias)]

    # Separação itens conferidos
    itens_conferidos = df_limpo[df_limpo['Códg Mestre'].isin(st.session_state.conferencias)]

    #Primeiro os pendentes
    itens_ordenados = pd.concat([itens_pendentes, itens_conferidos])

    # Seleção de itens
    for _, item in itens_ordenados.iterrows():
        # Geração de colunas
        coluna1, coluna2 = st.columns([3,1], vertical_alignment='center')

        codigo = item['Códg Mestre']
        descricao = item['Descrição']
        locacao = item['Locações']

        # Item conferido
        if codigo in st.session_state.conferencias:
            with coluna1:
                st.success(f'✓ {codigo} - {descricao}')

            # Botão editar
                with coluna2:
                    if st.button('Editar', key=f'editar_{codigo}'):
                        st.session_state.codigo_selecionado = codigo
                        st.session_state.codigo_confirmado = True
                        st.session_state.modo_edicao = True

                        st.rerun()

        # Item não conferido
        else:
            with coluna1:
                st.write(f'{codigo} - {descricao}')
            with coluna2:
                if st.button('Conferir', key=codigo):
                    st.session_state.codigo_selecionado = codigo
                    st.session_state.codigo_confirmado = False
                    st.session_state.modo_edicao = False

                    st.rerun()

        # Se o item foi selecionado
        if st.session_state.codigo_selecionado == codigo:
            with st.container(border=True):
                st.write(f"Código: {item['Códg Mestre']}")
                st.write(f"Descrição: {item['Descrição']}")
                st.write(f"Locação: {item['Locações']}")

            # Confirmação do Item
                if not st.session_state.modo_edicao:
                    codigo_digitado = st.text_input('Confirme o código: ', key=f'codigo_digitado_{codigo}')
                
                    if st.button('Confirmar código', key=f'confirmar_{codigo}'):
                        if codigo_digitado == codigo:
                            st.session_state.codigo_confirmado = True
                            st.rerun()
                        else:
                            st.session_state.codigo_confirmado = False
                            st.error('Código incorreto.')

             # Conferencia
            if st.session_state.codigo_confirmado:
                with st.container(border=True):
                    conferencia_existente = st.session_state.conferencias.get(codigo)

                    # Valores inicias
                    if conferencia_existente:
                        conferencia_inicial = conferencia_existente['conferente']
                        contagem_inicial = conferencia_existente['contagem']
                    else:
                        conferencia_inicial = 'Selecione'
                        contagem_inicial = 0
                
                    funcionarios = ['Selecione','Ana Clara', 'André']
                    indice_conferente = funcionarios.index(conferencia_inicial)
                
                    conferente = st.selectbox('Usuário', funcionarios, index=indice_conferente, key=f'usuario_{codigo}')
                
                    contagem = st.number_input('Quantidade física', min_value=0, step=1, value=int(contagem_inicial), key=f'contagem_{codigo}')
                
                    if st.button('Salvar'):
                        if conferente == 'Selecione':
                            st.error('Selecione um usuário')
                        else:
                            st.session_state.conferencias[codigo] = {'conferente':conferente, 'contagem': contagem, 'data_contagem': datetime.now().strftime('%d/%m/%Y - %H:%M')}

                            funcoes.salvar_progresso(importar_arquivo.name, st.session_state.conferencias)

                            st.session_state.codigo_selecionado = None
                            st.session_state.codigo_confirmado = False
                            st.session_state.modo_edicao = False
                
                            st.rerun()

        st.divider()