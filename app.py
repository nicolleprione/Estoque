import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Data e hora atual
data_hora = datetime.now()

# Geração de colunas
coluna1, coluna2 = st.columns([3,1], vertical_alignment='center')

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

# Preencher planilha
def gerar_planilha(df, conferencias):

    # Copia da planilha já limpa
    df_final = df_limpo.copy()

    # Preenche a contagem
    for codigo, dados in st.session_state.conferencias.items():
        df_final.loc[df_final['Códg Mestre'] == codigo, 'Contagem'] = dados['contagem']

    # Cria e prenche a coluna Conferente
    df_final['Conferente'] = ''
    for codigo, dados in st.session_state.conferencias.items():
        df_final.loc[df_final['Códg Mestre'] == codigo, 'Conferente'] = dados['conferente']

    # Data e hora da conferência
    df_final['Data da Contagem'] = data_hora

    return df_final

# Gerar excel
def gerar_excel(df_final):
    arquivo = BytesIO()

    with pd.ExcelWriter(arquivo, engine='openpyxl') as write:
        df_final.to_excel(write, index=False, sheet_name='Estoque')

        arquivo.seek(0)

        return arquivo

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
    st.write(f'{concluidos} de {total_itens} itens conferidos.')

    # Botão de geração de planilha
    if concluidos == total_itens:
        while coluna1:
            st.success('Todos os itens foram conferidos!')
        with coluna2:    
            if st.button('Gerar planilha'):
                df_final = gerar_planilha(df_limpo, st.session_state.conferencias)
                arquivo_excel = gerar_excel(df_final)
        
                st.download_button(label='Baixar planilha', data=arquivo_excel, file_name='conferencia.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

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
                            st.session_state.conferencias[codigo] = {'conferente':conferente, 'contagem': contagem}

                            st.session_state.codigo_selecionado = None
                            st.session_state.codigo_confirmado = False
                            st.session_state.modo_edicao = False
                
                            st.rerun()

        st.divider() # linha separadora

        

       