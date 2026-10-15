# Âmbar · Fluxograma de Montagem — Versão B (local)

Versão B do visualizador da OS 5760, para revisão antes de qualquer publicação.
**Não foi publicada:** o Render e o GitHub publicados continuam intactos.

## Como abrir
- **Arquivo único (celular, tablet, computador, offline):** `fluxograma-versao-b.html`. Basta abrir no navegador.
- **Versão de edição:** `index.html` + `dados.js`. Abra `index.html` com a pasta `editavel/` ao lado (as pranchas e os PDFs vêm de lá).

## Como atualizar
1. Os dados da OS (itens, subitens, divergências, contornos) vêm de `editavel/index.html`. Depois de mudar algo lá, rode:
   `python3 versao-b/extrair_dados.py`
2. Para gerar o arquivo único: `python3 versao-b/juntar_b.py` (≈5 MB, com a OS em PDF).
   Para incluir também os PDFs executivos: `python3 versao-b/juntar_b.py --com-pdfs` (≈31 MB).

## O que tem
- Estande ArcelorMittal e Festival LED separados (93 subitens, 91 com contorno na prancha).
- Ficha do projeto, busca, filtros por situação e por função.
- Visões Produção, Kanban e Planilha com o mesmo estado; atenção separada da etapa.
- Prancha com a peça recortada pelo contorno real, aumento de 7% e brilho; vistas, zoom, ajustar, focar peça e recolher.
- Materiais e fornecedores: contatos reais de Boxtruss (Ligar e WhatsApp) nos itens de box Q25; cadastro de contato e de alternativa "a validar pela equipe técnica".
- Tour opcional na primeira visita, depois em Menu › Como usar.
- Sem IA. Dados salvos só no aparelho, sem sincronizar entre pessoas.
