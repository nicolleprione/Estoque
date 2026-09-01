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

        else:
            st.write(f'{codigo} - {descricao}')

            if st.button('Conferir', key=codigo):
                st.session_state.codigo_selecionado = codigo
                st.session_state.codigo_confirmado = False

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
            conferente = st.selectbox('Usuário', ['Ana Clara', 'André'])

            contagem = st.number_input('Quantidade física', min_value=0, step=1)

            if st.button('Salvar'):
                st.session_state.conferencias[codigo] = {'conferente':conferente, 'contagem': contagem}

                st.session_state.codigo_selecionado = None
                st.session_state.codigo_confirmado = False

                st.success('Salvo com Sucesso.')