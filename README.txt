# Omnis Industrial — arquivos de estilo

## Arquivos
- `style.py`: CSS e componentes visuais reutilizáveis.
- `.streamlit/config.toml`: tema global do Streamlit.

## Instalação
1. Copie `style.py` para a mesma pasta do `app.py`.
2. Copie a pasta `.streamlit` para a raiz do projeto.
3. No começo do `app.py`, depois de `st.set_page_config(...)`, adicione:

```python
import style
style.aplicar_estilo()
style.exibir_cabecalho()
```

4. Remova ou substitua o `st.header("Bem-Vindo(a) ao Omnis!")` antigo para não mostrar dois cabeçalhos.

## Componentes opcionais
Depois de calcular os totais, você pode chamar:

```python
style.exibir_resumo(
    total=total_itens,
    conferidos=concluidos,
    pendentes=total_itens - concluidos,
)
```

Dentro do laço de itens, o cartão visual pode ser exibido assim:

```python
style.exibir_cartao_item(
    codigo=codigo,
    descricao=descricao,
    locacao=locacao,
    conferido=(codigo in st.session_state.conferencias),
)
```

Importante: o cartão visual não substitui os botões funcionais `Conferir` e `Editar`.
Mantenha a lógica dos botões e do salvamento no `app.py`. Primeiro teste o tema;
depois integre os cartões com cuidado para evitar duplicar texto na interface.
