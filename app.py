# IMPORTAÇÕES
import hashlib
import math
import time
from io import BytesIO

import pandas as pd
import streamlit as st

import funcoes


# CONFIGURAÇÕES
st.set_page_config(page_title="Omnis")
st.header("Bem-Vindo(a) ao Omnis!")

ITENS_POR_PAGINA = 20
INTERVALO_SYNC = 30

FUNCIONARIOS = ["Selecione", "Ana Clara", "André"]


# LEITURA DA PLANILHA
@st.cache_data(show_spinner=False)
def carregar_planilha(conteudo_arquivo):
    df = pd.read_excel(
        BytesIO(conteudo_arquivo),
        dtype={"Códg Mestre": str},
    )

    # Verifica se as colunas necessárias existem
    colunas_necessarias = [
        "Códg Mestre",
        "Descrição",
        "Locações",
    ]

    colunas_ausentes = [
        coluna
        for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    if colunas_ausentes:
        raise ValueError(
            "Colunas não encontradas na planilha: "
            + ", ".join(colunas_ausentes)
        )

    # Limpa os códigos
    df["Códg Mestre"] = df["Códg Mestre"].str.strip()

    # Remove códigos vazios e duplicados
    df = df.dropna(subset=["Códg Mestre"])
    df = df[df["Códg Mestre"] != ""]
    df = df.drop_duplicates(subset="Códg Mestre").copy()

    return df.reset_index(drop=True)


# SESSION STATE
padroes = {
    "codigo_selecionado": None,
    "codigo_confirmado": False,
    "conferencias": {},
    "modo_edicao": False,
    "arquivo_carregado": None,
    "hash_arquivo": None,
    "df_limpo": None,
    "conferencia_id": None,
    "status_conferencia": None,
    "arquivo_excel": None,
    "ultima_sync": 0.0,
    "pagina": 0,
    "busca_anterior": "",
}

for chave, valor in padroes.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


# SINCRONIZAÇÃO COM O SUPABASE
def sincronizar(forcar=False):
    agora = time.time()

    if (
        not forcar
        and agora - st.session_state.ultima_sync < INTERVALO_SYNC
    ):
        return

    nome_arquivo = st.session_state.arquivo_carregado

    if not nome_arquivo:
        return

    conferencia = funcoes.localizar_ou_criar_conferencia(
        nome_arquivo
    )

    contagens = funcoes.buscar_contagens(
        conferencia["id"]
    )

    st.session_state.conferencia_id = conferencia["id"]
    st.session_state.status_conferencia = conferencia["status"]
    st.session_state.conferencias = contagens
    st.session_state.ultima_sync = time.time()


# DIÁLOGO DE FINALIZAÇÃO
@st.dialog("Finalizar Conferência")
def confirmar_finalizacao():
    st.write(
        "Deseja finalizar esta conferência? "
        "Os dados serão preservados, mas não poderão ser alterados."
    )

    coluna01, coluna02 = st.columns(2)

    with coluna01:
        if st.button(
            "SIM",
            type="primary",
            use_container_width=True,
        ):
            try:
                funcoes.finalizar_conferencia(
                    st.session_state.conferencia_id
                )

                st.session_state.status_conferencia = "finalizada"
                st.session_state.codigo_selecionado = None
                st.session_state.codigo_confirmado = False
                st.session_state.modo_edicao = False
                st.session_state.arquivo_excel = None

                st.rerun()

            except Exception as erro:
                st.error(
                    f"Erro ao finalizar a conferência: {erro}"
                )

    with coluna02:
        if st.button(
            "NÃO",
            use_container_width=True,
        ):
            st.rerun()


# LISTA DE CONFERÊNCIA
@st.fragment
def lista_conferencia():

    sincronizar()

    df_limpo = st.session_state.df_limpo

    if df_limpo is None or df_limpo.empty:
        st.warning("A planilha não contém itens válidos.")
        return

    st.subheader("Lista de Conferência")

    # ATUALIZAÇÃO MANUAL
    if st.button(
        "Atualizar",
        key="atualizar_conferencia",
    ):
        try:
            with st.spinner("Atualizando dados..."):
                sincronizar(forcar=True)

            st.session_state.arquivo_excel = None

            st.rerun(scope="fragment")

        except Exception as erro:
            st.error(f"Erro ao atualizar os dados: {erro}")

    conferencias = st.session_state.conferencias

    em_andamento = (
        st.session_state.status_conferencia == "em_andamento"
    )

    # PROGRESSO
    total_itens = len(df_limpo)

    concluidos = sum(
        codigo in conferencias
        for codigo in df_limpo["Códg Mestre"]
    )

    progresso = (
        min(concluidos / total_itens, 1.0)
        if total_itens > 0
        else 0
    )

    st.progress(progresso)
    st.write(
        f"{concluidos} de {total_itens} itens conferidos."
    )

    # GERAÇÃO DA PLANILHA
    if concluidos == total_itens and total_itens > 0:

        st.success("Todos os itens foram conferidos!")

        col_gerar, col_baixar, col_finalizar = st.columns(3)

        with col_gerar:
            if st.button(
                "Gerar Planilha",
                key="gerar_planilha",
                use_container_width=True,
            ):
                try:
                    with st.spinner("Gerando planilha..."):
                        df_final = funcoes.gerar_planilha(
                            df_limpo,
                            conferencias,
                        )

                        st.session_state.arquivo_excel = (
                            funcoes.gerar_excel(df_final)
                        )

                except Exception as erro:
                    st.error(
                        f"Erro ao gerar a planilha: {erro}"
                    )

        if st.session_state.arquivo_excel is not None:

            with col_baixar:
                st.download_button(
                    label="Baixar",
                    data=st.session_state.arquivo_excel,
                    file_name=(
                        f"conferencia-"
                        f"{st.session_state.arquivo_carregado}"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )

            with col_finalizar:
                if em_andamento:
                    if st.button(
                        "Finalizar",
                        key="finalizar_conferencia",
                        use_container_width=True,
                    ):
                        confirmar_finalizacao()

    # BUSCA
    busca = st.text_input(
        "Buscar por código ou descrição",
        key="busca",
    ).strip()

    mostrar_conferidos = st.checkbox(
        "Mostrar itens já conferidos",
        value=True,
        key="mostrar_conferidos",
    )

    if busca != st.session_state.busca_anterior:
        st.session_state.busca_anterior = busca
        st.session_state.pagina = 0

    # SEPARAÇÃO DOS ITENS
    codigos = df_limpo["Códg Mestre"]

    ja_conferido = codigos.isin(conferencias.keys())

    itens_pendentes = df_limpo.loc[~ja_conferido]

    if mostrar_conferidos:
        itens_conferidos = df_limpo.loc[ja_conferido]

        itens_ordenados = pd.concat(
            [itens_pendentes, itens_conferidos],
            ignore_index=True,
        )
    else:
        itens_ordenados = itens_pendentes

    # FILTRO
    if busca:

        filtro_codigo = itens_ordenados[
            "Códg Mestre"
        ].str.contains(
            busca,
            case=False,
            regex=False,
            na=False,
        )

        filtro_descricao = itens_ordenados[
            "Descrição"
        ].astype(str).str.contains(
            busca,
            case=False,
            regex=False,
            na=False,
        )

        itens_ordenados = itens_ordenados.loc[
            filtro_codigo | filtro_descricao
        ]

    # PAGINAÇÃO
    quantidade_itens = len(itens_ordenados)

    total_paginas = max(
        1,
        math.ceil(quantidade_itens / ITENS_POR_PAGINA),
    )

    pagina = min(
        st.session_state.pagina,
        total_paginas - 1,
    )

    col_ant, col_info, col_prox = st.columns(
        [1, 2, 1],
        vertical_alignment="center",
    )

    with col_ant:
        if st.button(
            "◀",
            key="pagina_anterior",
            disabled=pagina == 0,
            use_container_width=True,
        ):
            pagina -= 1

    with col_prox:
        if st.button(
            "▶",
            key="pagina_proxima",
            disabled=pagina >= total_paginas - 1,
            use_container_width=True,
        ):
            pagina += 1

    with col_info:
        st.caption(
            f"Página {pagina + 1} de {total_paginas} "
            f"({quantidade_itens} itens)"
        )

    st.session_state.pagina = pagina

    inicio = pagina * ITENS_POR_PAGINA

    itens_da_pagina = itens_ordenados.iloc[
        inicio:inicio + ITENS_POR_PAGINA
    ]

    # RENDERIZAÇÃO DOS ITENS
    for _, item in itens_da_pagina.iterrows():

        # ACESSO PELO NOME DA COLUNA
        codigo = item["Códg Mestre"]
        descricao = item["Descrição"]
        locacao = item["Locações"]

        coluna1, coluna2 = st.columns(
            [3, 1],
            vertical_alignment="center",
        )

        # ITEM CONFERIDO
        if codigo in conferencias:

            with coluna1:
                st.success(f"✓ {codigo} - {descricao}")

            with coluna2:
                if em_andamento:

                    if st.button(
                        "Editar",
                        key=f"editar_{codigo}",
                        use_container_width=True,
                    ):
                        st.session_state.codigo_selecionado = codigo
                        st.session_state.codigo_confirmado = True
                        st.session_state.modo_edicao = True

                        st.rerun(scope="fragment")

                else:
                    st.button(
                        "Finalizado",
                        key=f"finalizado_{codigo}",
                        disabled=True,
                        use_container_width=True,
                    )

        # ITEM PENDENTE
        else:

            with coluna1:
                st.write(f"{codigo} - {descricao}")

            with coluna2:
                if em_andamento:

                    if st.button(
                        "Conferir",
                        key=f"conferir_{codigo}",
                        use_container_width=True,
                    ):
                        st.session_state.codigo_selecionado = codigo
                        st.session_state.codigo_confirmado = False
                        st.session_state.modo_edicao = False

                        st.rerun(scope="fragment")

                else:
                    st.button(
                        "Finalizado",
                        key=f"pendente_finalizado_{codigo}",
                        disabled=True,
                        use_container_width=True,
                    )

        # FORMULÁRIO DO ITEM SELECIONADO
        if st.session_state.codigo_selecionado == codigo:

            with st.container(border=True):

                st.write(f"Código: {codigo}")
                st.write(f"Descrição: {descricao}")
                st.write(f"Locação: {locacao}")

                # CONFIRMAÇÃO DO CÓDIGO
                if not st.session_state.modo_edicao:

                    codigo_digitado = st.text_input(
                        "Confirme o código:",
                        key=f"codigo_digitado_{codigo}",
                    )

                    if st.button(
                        "Confirmar código",
                        key=f"confirmar_{codigo}",
                    ):

                        if codigo_digitado.strip() == str(codigo):
                            st.session_state.codigo_confirmado = True
                            st.rerun(scope="fragment")

                        else:
                            st.session_state.codigo_confirmado = False
                            st.error("Código incorreto.")

            # FORMULÁRIO DE CONTAGEM
            if st.session_state.codigo_confirmado:

                with st.container(border=True):

                    conferencia_existente = conferencias.get(codigo)

                    if conferencia_existente:
                        conferencia_inicial = (
                            conferencia_existente["conferente"]
                        )

                        contagem_inicial = (
                            conferencia_existente["contagem"]
                        )

                    else:
                        conferencia_inicial = "Selecione"
                        contagem_inicial = 0

                    indice_conferente = (
                        FUNCIONARIOS.index(conferencia_inicial)
                        if conferencia_inicial in FUNCIONARIOS
                        else 0
                    )

                    conferente = st.selectbox(
                        "Usuário",
                        FUNCIONARIOS,
                        index=indice_conferente,
                        key=f"usuario_{codigo}",
                    )

                    contagem = st.number_input(
                        "Quantidade física",
                        min_value=0,
                        step=1,
                        value=int(contagem_inicial),
                        key=f"contagem_{codigo}",
                    )

                    # SALVAR
                    if st.button(
                        "Salvar",
                        key=f"salvar_{codigo}",
                        type="primary",
                        use_container_width=True,
                    ):

                        if conferente == "Selecione":
                            st.error("Selecione um usuário.")

                        else:
                            try:
                                with st.spinner("Salvando..."):

                                    funcoes.salvar_contagem(
                                        st.session_state.conferencia_id,
                                        codigo,
                                        conferente,
                                        int(contagem),
                                    )

                                # ATUALIZA O ESTADO LOCAL
                                st.session_state.conferencias[codigo] = {
                                    "conferente": conferente,
                                    "contagem": int(contagem),
                                    "data_contagem": (
                                        funcoes.horario_atual()
                                    ),
                                }

                                st.session_state.arquivo_excel = None

                                st.session_state.codigo_selecionado = None
                                st.session_state.codigo_confirmado = False
                                st.session_state.modo_edicao = False

                                st.rerun(scope="fragment")

                            except Exception as erro:
                                st.error(
                                    f"Erro ao salvar a contagem: {erro}"
                                )

        st.divider()


# IMPORTAÇÃO DO ARQUIVO
importar_arquivo = st.file_uploader(
    label="Importe",
    type=["xlsx"],
)

if importar_arquivo:

    nome_arquivo = importar_arquivo.name
    conteudo_arquivo = importar_arquivo.getvalue()

    hash_arquivo = hashlib.sha256(
        conteudo_arquivo
    ).hexdigest()

    # IDENTIFICA MUDANÇAS NO CONTEÚDO
    if st.session_state.hash_arquivo != hash_arquivo:

        try:
            with st.spinner("Lendo planilha..."):
                df_novo = carregar_planilha(conteudo_arquivo)

            st.session_state.df_limpo = df_novo
            st.session_state.arquivo_carregado = nome_arquivo
            st.session_state.hash_arquivo = hash_arquivo

            st.session_state.arquivo_excel = None
            st.session_state.codigo_selecionado = None
            st.session_state.codigo_confirmado = False
            st.session_state.modo_edicao = False
            st.session_state.pagina = 0
            st.session_state.ultima_sync = 0.0

            with st.spinner("Carregando conferência..."):
                sincronizar(forcar=True)

        except Exception as erro:
            st.error(f"Erro ao carregar a planilha: {erro}")
            st.stop()

    lista_conferencia()