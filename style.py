import base64
from pathlib import Path

import streamlit as st


# ============================================================
# OMNIS INDUSTRIAL — identidade visual mobile-first
# ============================================================
# Este arquivo cuida apenas da aparência.
# Não altera a lógica de conferência, banco de dados ou planilhas.
#
# Uso no app.py:
#   import style
#   style.aplicar_estilo()
#
# Opcional:
#   style.exibir_cabecalho()
#   style.exibir_cartao_item(codigo, descricao, locacao, conferido)
#
# Observação:
# Os cartões visuais abaixo são componentes de apresentação.
# Os botões funcionais "Conferir" e "Editar" devem continuar no app.py,
# para manter a lógica de seleção e salvamento já existente.
# ============================================================


# Paleta Omnis Industrial
FUNDO = "#171B20"
SUPERFICIE = "#242A31"
SUPERFICIE_ELEVADA = "#2D343D"
BORDA = "#3D4651"
TEXTO = "#F3F4F6"
TEXTO_SECUNDARIO = "#AAB3BE"
LARANJA = "#E69200"
LARANJA_CLARO = "#FFBA0D"
CINZA_CONFERIDO = "#343B43"
CINZA_BORDA = "#4B5561"
VERDE = "#22C55E"


def _imagem_em_base64(caminho: Path) -> str | None:
    """Lê uma imagem local e retorna seu conteúdo em Base64."""
    try:
        extensao = caminho.suffix.lower()
        tipos = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        tipo = tipos.get(extensao)
        if not tipo or not caminho.is_file():
            return None

        conteudo = base64.b64encode(caminho.read_bytes()).decode("utf-8")
        return f"data:{tipo};base64,{conteudo}"
    except OSError:
        return None


def aplicar_estilo():
    """Aplica o tema visual industrial à aplicação Streamlit."""
    st.markdown(
        f"""
        <style>
        /* ---------- Base da página ---------- */
        :root {{
            color-scheme: dark;
            --omnis-bg: {FUNDO};
            --omnis-surface: {SUPERFICIE};
            --omnis-surface-raised: {SUPERFICIE_ELEVADA};
            --omnis-border: {BORDA};
            --omnis-text: {TEXTO};
            --omnis-muted: {TEXTO_SECUNDARIO};
            --omnis-orange: {LARANJA};
            --omnis-orange-light: {LARANJA_CLARO};
            --omnis-complete: {CINZA_CONFERIDO};
            --omnis-green: {VERDE};
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background: var(--omnis-bg);
            color: var(--omnis-text);
        }}

        [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(ellipse at top right, rgba(245, 158, 11, 0.055), transparent 36%),
                var(--omnis-bg);
        }}

        [data-testid="stHeader"] {{
            background: rgba(23, 27, 32, 0.94);
        }}

        [data-testid="stMainBlockContainer"] {{
            max-width: 760px;
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }}

        /* Tipografia e títulos */
        html, body, [class*="css"], input, button, textarea {{
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        h1, h2, h3 {{
            color: var(--omnis-text) !important;
            letter-spacing: -0.025em;
        }}

        h1 {{
            font-size: clamp(1.55rem, 6vw, 2.05rem) !important;
            font-weight: 800 !important;
        }}

        h2 {{
            font-size: 1.25rem !important;
            font-weight: 750 !important;
        }}

        p, label, [data-testid="stMarkdownContainer"] {{
            color: var(--omnis-text);
        }}

        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p {{
            color: var(--omnis-muted) !important;
        }}

        /* ---------- Botões gerais ---------- */
        .stButton > button,
        .stDownloadButton > button {{
            min-height: 46px;
            width: 100%;
            border-radius: 11px;
            border: 1px solid var(--omnis-border);
            background: var(--omnis-surface-raised);
            color: var(--omnis-text);
            font-weight: 700;
            transition: background-color 120ms ease, border-color 120ms ease;
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            border-color: var(--omnis-orange);
            color: var(--omnis-orange-light);
            background: #353C45;
        }}

        .stButton > button:focus,
        .stDownloadButton > button:focus {{
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.28);
            border-color: var(--omnis-orange);
        }}

        /* Botões primários Streamlit */
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {{
            background: var(--omnis-orange);
            color: #171B20;
            border-color: var(--omnis-orange);
        }}

        .stButton > button[kind="primary"]:hover,
        .stDownloadButton > button[kind="primary"]:hover {{
            background: #D97706;
            border-color: #D97706;
            color: #171B20;
        }}

        /* ---------- Campos de entrada ---------- */
        [data-baseweb="input"],
        [data-baseweb="select"],
        [data-baseweb="textarea"] {{
            background: var(--omnis-surface) !important;
            border-color: var(--omnis-border) !important;
            border-radius: 10px !important;
        }}

        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea {{
            color: var(--omnis-text) !important;
        }}

        [data-baseweb="select"] > div {{
            background: var(--omnis-surface) !important;
            border-color: var(--omnis-border) !important;
            color: var(--omnis-text) !important;
        }}

        [data-testid="stNumberInput"] button {{
            color: var(--omnis-text) !important;
            background: var(--omnis-surface-raised) !important;
            border-color: var(--omnis-border) !important;
        }}

        /* ---------- Cartões e containers ---------- */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(36, 42, 49, 0.78);
            border-color: var(--omnis-border) !important;
            border-radius: 14px !important;
        }}

        [data-testid="stAlert"] {{
            border-radius: 12px;
        }}

        hr {{
            border-color: var(--omnis-border) !important;
        }}

        /* Barra de progresso */
        [data-testid="stProgressBar"] > div {{
            background: #3A424C;
            border-radius: 999px;
            overflow: hidden;
            height: 9px;
        }}

        [data-testid="stProgressBar"] > div > div {{
            background: var(--omnis-orange) !important;
            border-radius: 999px;
        }}

        /* Upload de arquivo */
        [data-testid="stFileUploader"] section {{
            background: var(--omnis-surface);
            border: 1px dashed #59636F;
            border-radius: 13px;
        }}

        [data-testid="stFileUploader"] button {{
            border-radius: 9px;
        }}

        /* Dialog/modal */
        [data-testid="stDialog"] > div > div {{
            background: var(--omnis-bg);
            border: 1px solid var(--omnis-border);
            border-radius: 16px;
        }}

        /* Rodapé e menus sem decoração extra */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}

        /* ---------- Componentes HTML próprios ---------- */
        .omnis-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 24px 0 18px 0;
            margin-bottom: 14px;
            border-bottom: 1px solid var(--omnis-border);
        }}

        .omnis-logo-mark {{
            display: flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 46px;
            width: 46px;
            height: 46px;
            border-radius: 12px;
            background: var(--omnis-orange);
            color: #171B20;
            font-size: 25px;
            font-weight: 900;
        }}

        .omnis-brand {{
            margin: 0;
            color: var(--omnis-text);
            font-size: 1.55rem;
            line-height: 1.1;
            font-weight: 900;
            letter-spacing: 0.075em;
        }}

        .omnis-tagline {{
            margin-top: 5px;
            color: var(--omnis-muted);
            font-size: 0.67rem;
            font-weight: 700;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }}

        .omnis-section-title {{
            margin: 18px 0 10px;
            color: var(--omnis-text);
            font-size: 1.1rem;
            font-weight: 800;
        }}

        .omnis-summary {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 8px;
            margin: 12px 0 18px;
        }}

        .omnis-stat {{
            min-width: 0;
            padding: 13px 8px;
            border: 1px solid var(--omnis-border);
            border-radius: 12px;
            background: var(--omnis-surface);
            text-align: center;
        }}

        .omnis-stat-value {{
            color: var(--omnis-text);
            font-size: clamp(1.15rem, 5vw, 1.55rem);
            line-height: 1.2;
            font-weight: 850;
            overflow-wrap: anywhere;
        }}

        .omnis-stat-label {{
            margin-top: 5px;
            color: var(--omnis-muted);
            font-size: 0.68rem;
            line-height: 1.2;
            font-weight: 700;
        }}

        .omnis-item {{
            margin: 10px 0;
            padding: 15px;
            border: 1px solid var(--omnis-border);
            border-left: 5px solid var(--omnis-orange);
            border-radius: 13px;
            background: var(--omnis-surface);
        }}

        .omnis-item.is-pending {{
            border-left-color: var(--omnis-orange);
            background: linear-gradient(110deg, rgba(245, 158, 11, 0.10), transparent 65%), var(--omnis-surface);
        }}

        .omnis-item.is-complete {{
            border-left-color: #7D8792;
            border-color: var(--omnis-cool-border);
            background: var(--omnis-complete);
            --omnis-cool-border: #4B5561;
        }}

        .omnis-item-code {{
            color: var(--omnis-orange-light);
            font-size: 0.9rem;
            font-weight: 800;
            overflow-wrap: anywhere;
        }}

        .omnis-item.is-complete .omnis-item-code {{
            color: #D1D5DB;
        }}

        .omnis-item-description {{
            margin-top: 7px;
            color: var(--omnis-text);
            font-size: 1rem;
            line-height: 1.4;
            font-weight: 700;
            overflow-wrap: anywhere;
        }}

        .omnis-item-location {{
            margin-top: 7px;
            color: var(--omnis-muted);
            font-size: 0.82rem;
            overflow-wrap: anywhere;
        }}

        .omnis-status {{
            display: inline-block;
            margin-top: 10px;
            padding: 5px 8px;
            border-radius: 6px;
            background: rgba(245, 158, 11, 0.14);
            color: var(--omnis-orange-light);
            font-size: 0.66rem;
            font-weight: 850;
            letter-spacing: 0.06em;
        }}

        .omnis-item.is-complete .omnis-status {{
            background: rgba(209, 213, 219, 0.10);
            color: #D1D5DB;
        }}

        .omnis-detail-card {{
            margin: 10px 0;
            padding: 15px;
            border: 1px solid var(--omnis-border);
            border-radius: 13px;
            background: var(--omnis-surface);
        }}

        @media (max-width: 480px) {{
            [data-testid="stMainBlockContainer"] {{
                padding-left: 0.75rem;
                padding-right: 0.75rem;
                padding-top: 0.6rem;
            }}

            .omnis-header {{
                padding-top: 8px;
                padding-bottom: 13px;
                margin-bottom: 10px;
            }}

            .omnis-logo-mark {{
                width: 42px;
                height: 42px;
                flex-basis: 42px;
            }}

            .omnis-brand {{
                font-size: 1.4rem;
            }}

            .omnis-item {{
                padding: 13px;
            }}

            .stButton > button,
            .stDownloadButton > button {{
                min-height: 48px;
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                transition-duration: 0.01ms !important;
                animation-duration: 0.01ms !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def exibir_cabecalho(subtitulo: str = "Conferência de estoque"):
    """Exibe o cabeçalho OMNIS compacto."""
    st.markdown(
        f"""
        <div class="omnis-header">
            <div class="omnis-logo-mark">O</div>
            <div>
                <div class="omnis-brand">OMNIS 2.0</div>
                <div class="omnis-tagline">{subtitulo}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def exibir_resumo(total: int, conferidos: int, pendentes: int):
    """Exibe três cartões de resumo."""
    st.markdown(
        f"""
        <div class="omnis-summary">
            <div class="omnis-stat">
                <div class="omnis-stat-value">{total}</div>
                <div class="omnis-stat-label">TOTAL</div>
            </div>
            <div class="omnis-stat">
                <div class="omnis-stat-value">{conferidos}</div>
                <div class="omnis-stat-label">CONFERIDOS</div>
            </div>
            <div class="omnis-stat">
                <div class="omnis-stat-value" style="color:{LARANJA_CLARO}">{pendentes}</div>
                <div class="omnis-stat-label">PENDENTES</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def exibir_cartao_item(
    codigo,
    descricao,
    locacao=None,
    conferido: bool = False,
):
    """
    Exibe somente a parte visual de um cartão de peça.

    Os botões funcionais devem ser desenhados no app.py abaixo ou ao lado
    deste cartão, usando st.button com as chaves já existentes.
    """
    estado = "is-complete" if conferido else "is-pending"
    status = "CONFERIDO" if conferido else "PENDENTE"
    locacao_html = (
        f'<div class="omnis-item-location">Locação: {locacao}</div>'
        if locacao is not None and str(locacao).strip()
        else ""
    )

    st.markdown(
        f"""
        <div class="omnis-item {estado}">
            <div class="omnis-item-code">{codigo}</div>
            <div class="omnis-item-description">{descricao}</div>
            {locacao_html}
            <div class="omnis-status">{status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def exibir_cartao_detalhes(titulo: str = "Detalhes da peça"):
    """Abre um container visual para os campos detalhados."""
    st.markdown(
        f'<div class="omnis-detail-card"><strong>{titulo}</strong></div>',
        unsafe_allow_html=True,
    )
