from conftest import load_fixture
from mcp_dof.markdown import html_to_markdown, slice_text, tidy


def test_banxico_note_becomes_clean_markdown() -> None:
    html = load_fixture("notas/nota/5803775")["Nota"]["cadenaContenido"]
    markdown = html_to_markdown(html)
    assert "<span" not in markdown
    assert "<div" not in markdown
    assert markdown.startswith("## TIPO de cambio")  # H1 demoted: the tool owns the H1
    assert "$18.6188 M.N." in markdown
    assert "**Pilar María Figueredo Díaz**" in markdown  # bold from inline style
    assert "font-family" not in markdown


def test_inline_styles_tables_and_links() -> None:
    html = """
    <html><head><style>.x{color:red}</style></head><body>
    <h1>DECRETO</h1>
    <p><span style="font-style:italic">Artículo&nbsp;1o.</span>
       <span style="font-weight:bold">Se expide</span> la ley.</p>
    <table><tr><td>Concepto</td><td>Monto</td></tr><tr><td>ISR</td><td>3,288,975.3</td></tr></table>
    <p><a href="/nota_detalle.php?codigo=1&fecha=01/01/2026">ver</a></p>
    </body></html>
    """
    markdown = html_to_markdown(html)
    assert "## DECRETO" in markdown
    assert "*Artículo 1o.*" in markdown
    assert "**Se expide**" in markdown
    assert "| Concepto | Monto |" in markdown
    assert "| ISR | 3,288,975.3 |" in markdown
    assert "(https://dof.gob.mx/nota_detalle.php?codigo=1&fecha=01/01/2026)" in markdown
    assert ".x{color:red}" not in markdown


def test_tidy_collapses_blank_lines_and_nbsp() -> None:
    assert tidy("a b  \n\n\n\nc") == "a b\n\nc\n"


def test_slice_text_cuts_at_paragraph_boundaries() -> None:
    text = "\n\n".join(f"Párrafo {i} " + "x" * 80 for i in range(50))
    first, next_start = slice_text(text, 0, 1000)
    assert next_start is not None
    assert first.endswith("x\n")
    assert len(first) <= 1000
    second, _ = slice_text(text, next_start, 1000)
    assert second.lstrip().startswith("Párrafo")


def test_slice_text_end_of_text() -> None:
    assert slice_text("short", 0, 1000) == ("short", None)
    assert slice_text("short", 10, 1000) == ("", None)
