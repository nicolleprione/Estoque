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
    total_original = len(df)
    total_unicos = len(df_limpo)
    st.text(f"Total de registros: {total_original}")
    st.text(f"Códigos únicos: {total_unicos}")

    st.subheader('Lista de Conferência')

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

        if codigo in st.session_state.conferencias:
            st.success(f'✓ {codigo} - {descricao}')

            if st.button('Editar', key=f'editar_{codigo}'):
                st.session_state.codigo_selecionado = codigo
                st.session_state.codigo_confirmado = True
                st.session_state.modo_edicao = True

        else:
            st.write(f'{codigo} - {descricao}')

            if st.button('Conferir', key=codigo):
                st.session_state.codigo_selecionado = codigo
                st.session_state.codigo_confirmado = False
                st.session_state.modo_edicao = False

        st.divider() # linha separadora

    # Exibindo o Item
    if st.session_state.codigo_selecionado:
        codigo = st.session_state.codigo_selecionado
        item = df_limpo[df_limpo['Códg Mestre'] == codigo].iloc[0]

        st.subheader('Item Selecionado')
        st.write(f"Código: {item['Códg Mestre']}")
        st.write(f"Descrição: {item['Descrição']}")
        st.write(f"Locação: {item['Locações']}")

        # Confirmação do Item
        if not st.session_state.modo_edicao:
            st.subheader('Confirmação do código')
            codigo_digitado = st.text_input('Digite o código: ')

            if st.button('Confirmar código'):
                if codigo_digitado == codigo:
                    st.session_state.codigo_confirmado = True
                else:
                    st.session_state.codigo_confirmado = False
                    st.error('Código incorreto.')

        # Conferencia
        if st.session_state.codigo_confirmado:
            st.subheader('Dados de conferência')

            conferencia_existente = st.session_state.conferencias.get(codigo)
            if conferencia_existente:
                conferencia_inicial = conferencia_existente['conferente']
                contagem_inicial = conferencia_existente['contagem']
            else:
                conferencia_inicial = 'Selecione'
                contagem_inicial = 0

            funcionarios = ['Ana Clara', 'André']
            indice_conferente = funcionarios.index(conferencia_inicial)

            conferente = st.selectbox('Usuário', funcionarios, index=indice_conferente)

            contagem = st.number_input('Quantidade física', min_value=0, step=1, value=int(contagem_inicial))

            if st.button('Salvar'):
                st.session_state.conferencias[codigo] = {'conferente':conferente, 'contagem': contagem}

                st.session_state.codigo_selecionado = None
                st.session_state.codigo_confirmado = False
                st.session_state.modo_edicao = False

                st.success('Salvo com Sucesso.')