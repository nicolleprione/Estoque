import streamlit as st
import pandas as pd

st.set_page_config(page_title='Omnis')

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

# Título
st.header("Bem-Vindo(a) ao Omnis!")

# Importação dos dados
importar_arquivo = st.file_uploader(label='Importe',type=['xlsx'])

# Verifica se foi importado algo
if importar_arquivo:

    # Leitura dos dados
    df = pd.read_excel(importar_arquivo, dtype={'Códg Mestre': str})
    
    # Remoção das duplicatas
    df_limpo = df.drop_duplicates(subset='Códg Mestre')

    # Informações da planilha
    total_itens = len(df_limpo)
    concluidos = len(st.session_state.conferencias)

    if total_itens > 0:
        progresso = concluidos / total_itens
    else:
        progresso = 0

    st.progress(progresso)
    st.write(f'{concluidos} de {total_itens} intens conferidos.')

    st.subheader('Lista de Conferência')

    # Botão de geração de planilha
    if concluidos == total_itens:
        st.success('Todos os itens foram conferidos!')

        if st.button('Gerar planilha'):
            st.write('Gerando planilha ...')

    # Separação de itens não conferidos
    itens_pendentes = df_limpo[~df_limpo['Códg Mestre'].isin(st.session_state.conferencias)]

    # Separação itens conferidos
    itens_conferidos = df_limpo[df_limpo['Códg Mestre'].isin(st.session_state.conferencias)]

    #Primeiro os pendentes
    itens_ordenados = pd.concat([itens_pendentes, itens_conferidos])

    # Seleção de itens
    for _, item in itens_ordenados.iterrows():

        codigo = item['Códg Mestre']
        descricao = item['Descrição']
        locacao = item['Locações']

        # Item conferido
        if codigo in st.session_state.conferencias:
            st.success(f'✓ {codigo} - {descricao}')

            # Botão editar
            if st.button('Editar', key=f'editar_{codigo}'):
                st.session_state.codigo_selecionado = codigo
                st.session_state.codigo_confirmado = True
                st.session_state.modo_edicao = True

                st.rerun()

        # Item não conferido
        else:
            st.write(f'{codigo} - {descricao}')

            if st.button('Conferir', key=codigo):
                st.session_state.codigo_selecionado = codigo
                st.session_state.codigo_confirmado = False
                st.session_state.modo_edicao = False

                st.rerun()

        # Se o item foi selecionado
        if st.session_state.codigo_selecionado == codigo:
            st.subheader('Item Selecionado')
            st.write(f"Código: {item['Códg Mestre']}")
            st.write(f"Descrição: {item['Descrição']}")
            st.write(f"Locação: {item['Locações']}")

            # Confirmação do Item
            if not st.session_state.modo_edicao:
                st.subheader('Confirmação do código')

                codigo_digitado = st.text_input('Digite o código: ', key=f'codigo_digitado_{codigo}')
            
                if st.button('Confirmar código', key=f'confirmar_{codigo}'):
                    if codigo_digitado == codigo:
                        st.session_state.codigo_confirmado = True
                        st.rerun()
                    else:
                        st.session_state.codigo_confirmado = False
                        st.error('Código incorreto.')

             # Conferencia
            if st.session_state.codigo_confirmado:
                st.subheader('Dados de conferência')
            
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
            
                conferente = st.selectbox('Usuário', funcionarios, index=indice_conferente)
            
                contagem = st.number_input('Quantidade física', min_value=0, step=1, value=int(contagem_inicial))
            
                if st.button('Salvar'):
                    if conferente == 'Selecione':
                        st.error('Selecione um usuário')
                    else:
                        st.session_state.conferencias[codigo] = {'conferente':conferente, 'contagem': contagem}

                        st.session_state.codigo_selecionado = None
                        st.session_state.codigo_confirmado = False
                        st.session_state.modo_edicao = False
            
                        st.rerun()

        st.divider() # linha separadora