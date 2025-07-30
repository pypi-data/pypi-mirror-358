# Exemplo de Conversão Markdown para PDF

Este documento demonstra todas as funcionalidades avançadas do conversor de Markdown para PDF.

## Introdução

O conversor suporta uma ampla gama de elementos Markdown, incluindo:

- Formatação de texto avançada
- Syntax highlighting para código
- Tabelas responsivas
- Imagens otimizadas
- Índice automático
- Múltiplos temas visuais

## Formatação de Texto

### Texto Básico

Este é um parágrafo normal com **texto em negrito**, _texto em itálico_, e `código inline`.

### Citações

> Esta é uma citação em bloco que demonstra como o texto é formatado
> de forma elegante com bordas coloridas e fundo diferenciado.
>
> — Autor da Citação

### Listas

#### Lista Não Ordenada

- Item principal 1
  - Subitem 1.1
  - Subitem 1.2
- Item principal 2
- Item principal 3

#### Lista Ordenada

1. Primeiro passo
2. Segundo passo
   1. Subpasso 2.1
   2. Subpasso 2.2
3. Terceiro passo

## Código e Syntax Highlighting

### Python

```python
def fibonacci(n):
    """Calcula a sequência de Fibonacci até n."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Exemplo de uso
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript

```javascript
// Função para calcular fatorial
function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}

// Arrow function moderna
const factorialArrow = (n) => (n <= 1 ? 1 : n * factorialArrow(n - 1));

console.log("5! =", factorial(5));
```

### SQL

```sql
-- Consulta complexa com JOIN
SELECT
    u.nome,
    u.email,
    COUNT(p.id) as total_pedidos,
    SUM(p.valor) as valor_total
FROM usuarios u
LEFT JOIN pedidos p ON u.id = p.usuario_id
WHERE u.ativo = 1
GROUP BY u.id, u.nome, u.email
HAVING COUNT(p.id) > 0
ORDER BY valor_total DESC;
```

## Tabelas

### Tabela Simples

| Nome  | Idade | Cidade         |
| ----- | ----- | -------------- |
| João  | 25    | São Paulo      |
| Maria | 30    | Rio de Janeiro |
| Pedro | 35    | Belo Horizonte |

### Tabela Complexa

| Recurso              | Tema Modern  | Tema Dark  | Tema Minimal | Tema Academic |
| -------------------- | ------------ | ---------- | ------------ | ------------- |
| Cores Primárias      | Azul Moderno | Azul Claro | Preto        | Azul Escuro   |
| Tipografia           | Sans-serif   | Sans-serif | Serif        | Serif         |
| Syntax Highlighting  | ✅           | ✅         | ✅           | ✅            |
| Índice Automático    | ✅           | ✅         | ✅           | ✅            |
| Numeração de Páginas | ✅           | ✅         | ✅           | ✅            |

## Elementos Matemáticos

Embora este conversor não inclua suporte nativo para LaTeX, você pode usar notação matemática básica:

- Fórmula quadrática: x = (-b ± √(b² - 4ac)) / 2a
- Teorema de Pitágoras: a² + b² = c²
- Euler: e^(iπ) + 1 = 0

## Links e Referências

- [GitHub do Projeto](https://github.com/exemplo/markdown-html-pdf)
- [Documentação do Markdown](https://daringfireball.net/projects/markdown/)
- [WeasyPrint Documentation](https://weasyprint.org/)

## Separadores

---

## Notas de Rodapé

Este texto tem uma nota de rodapé[^1] que aparece no final da página.

Aqui temos outra referência[^nota-importante] com um nome mais descritivo.

[^1]: Esta é a primeira nota de rodapé.
[^nota-importante]: Esta nota explica algo muito importante sobre o documento.

## Definições

Markdown
: Uma linguagem de marcação leve para formatação de texto.

PDF
: Portable Document Format, um formato de arquivo desenvolvido pela Adobe.

WeasyPrint
: Uma biblioteca Python para converter HTML/CSS em PDF.

## Checklist de Funcionalidades

- [x] Suporte a múltiplos temas
- [x] Syntax highlighting
- [x] Tabelas responsivas
- [x] Índice automático
- [x] Numeração de páginas
- [x] Headers e footers customizáveis
- [ ] Suporte a LaTeX (planejado)
- [ ] Gráficos interativos (planejado)

## Conclusão

Este conversor de Markdown para PDF oferece uma solução completa e profissional para gerar documentos de alta qualidade. Com seus quatro temas distintos e amplo suporte a elementos Markdown, é ideal para:

1. **Documentação técnica** - Com syntax highlighting e formatação limpa
2. **Relatórios acadêmicos** - Com tipografia serif e layout formal
3. **Apresentações** - Com tema escuro para projeção
4. **Documentos minimalistas** - Com foco no conteúdo

### Comandos de Exemplo

```bash
# Conversão básica
python markdown_html_pdf.py exemplo.md

# Com tema específico
python markdown_html_pdf.py exemplo.md -t dark -o exemplo_dark.pdf

# Sem índice
python markdown_html_pdf.py exemplo.md --no-toc

# Conversão em lote
python markdown_html_pdf.py -d ./documentos/ -o ./pdfs/
```

---

**Nota**: Este documento foi criado para demonstrar todas as funcionalidades do conversor. Para usar o script, certifique-se de ter todas as dependências instaladas conforme especificado no `pyproject.toml`.
