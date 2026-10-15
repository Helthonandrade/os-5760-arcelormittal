# Prompt — Projeto C · Fluxograma de Montagem Âmbar (modo simples + modo completo)

> Cole tudo abaixo da linha no ChatGPT, na mesma conversa em que estiver o **Projeto A** (a versão publicada no Render). Anexe o pacote `projeto-C.zip`. Se não puder anexar tudo, o mínimo é `projeto-C/index.html` e `projeto-C/dados.js`.

---

Você vai juntar duas versões do mesmo sistema. Leia este contexto inteiro antes de responder. Responda em português do Brasil, de forma direta.

## 1. O que são os projetos

- **Projeto A:** o visualizador de produção já publicado em https://ambarprocessoseletivo.onrender.com/. É a referência das funções que existem hoje. **Não altere o Render nem o GitHub do Projeto A sem aprovação explícita.**
- **Projeto C (este pacote):** uma nova versão do mesmo sistema, feita para ser **muito mais fácil**. A pessoa que mais vai usar trabalha na fábrica ou na montagem e pode ter pouca escolaridade. A regra de desenho é: **uma criança de 7 anos precisa conseguir usar.** O celular é o aparelho principal; tablet e computador vêm depois.
- **Objetivo desta conversa:** aplicar o Projeto C junto ao Projeto A. As funções do A precisam continuar existindo, mas a tela inicial e a tela da tarefa devem seguir a simplicidade do C.

Os dados vêm da **OS 5760** da Âmbar Cenografia, com dois projetos sempre separados:
- **Estande ArcelorMittal:** 9 itens e 33 subitens.
- **Festival LED:** 16 itens e 60 subitens.

Prazos (D-n), etapas e responsáveis são **hipotéticos (simulação)**. A OS registra montagem em 01–02/11/2025 e evento em 03/11/2025.

## 2. Arquivos do pacote `projeto-C.zip`

```
projeto-C/
  PROMPT-PROJETO-C.md        ← este texto
  index.html                 ← CÓDIGO-FONTE do app (HTML + CSS + JS, sem build, sem dependências)
  dados.js                   ← dados da OS: PROJECTS, SHAPES (contornos), PAGES, PAGE_NAMES, DOCS, R
  fluxograma-versao-b.html   ← versão pronta em arquivo único (5,3 MB, funciona offline). Não editar.
  juntar_b.py                ← gera o arquivo único a partir de index.html + dados.js + pranchas
  extrair_dados.py           ← regenera dados.js a partir do visualizador anterior (editavel/index.html)
  LEIA-ME.md                 ← como abrir e gerar
```

As 33 pranchas (`stand-02.jpg` … `stand-10.jpg`, `fest-01.jpg` … `fest-24.jpg`, 1095 × 774 px) e os PDFs (`os.pdf`, `stand.pdf`, `fest.pdf`) ficam na pasta do Drive **BAITA › AMBAR › OS 5760 - Pacote Claude**. Elas também estão embutidas em `fluxograma-versao-b.html`. No código-fonte, os caminhos esperados são `../editavel/pranchas/…` e `../editavel/pdf/…`.

**Numeração das pranchas:** o arquivo `stand-NN.jpg` corresponde à prancha (NN−1)/09 e à página NN do PDF. O arquivo `fest-NN.jpg` corresponde à prancha (NN−1)/23 e à página NN do PDF.

## 3. Os dois modos do Projeto C

### Modo simples (abre por padrão, para a equipe)

**Tela inicial: só três coisas**
1. **Fotos dos dois projetos** (imagens 3D). Tocar escolhe o projeto.
2. **Três botões grandes**, com ícone e número de tarefas:
   - ⌛ **Para fazer:** etapas "Aguardando" e "Liberado".
   - 🔨 **Fazendo:** etapas "Em produção" e "Executado".
   - ✔ **Pronto:** etapa "Entregue".
3. **Cartões das tarefas**, com:
   - foto da peça (recorte da prancha pelo contorno);
   - nome da peça;
   - quantidade em número grande;
   - faixa de cor à esquerda (cinza = para fazer, laranja = fazendo, verde = pronto);
   - etiqueta amarela **só** quando há problema marcado ou o prazo está perto ou vencido ("Faltam 2 dias", "Atrasado 1 dia", "É para hoje").

   As tarefas mais urgentes aparecem primeiro.

Além disso, um botão discreto "Procurar peça" no fim da lista e nada mais. Não há barra de progresso, filtros técnicos, códigos de item nem textos longos.

**Tela da tarefa, de cima para baixo**
1. **Desenho:** a peça aparece **já de perto** (zoom automático na peça), recortada pelo contorno real, **7% maior** e com brilho laranja nas bordas. O resto do desenho fica esmaecido. Botões: −, +, "Ver tudo" e "Ver peça".
2. **Número grande** da quantidade ("4 peças"), com quem faz (função, nunca nome de pessoa) e quando ("Faltam 12 dias").
3. **Aviso amarelo em palavras simples**, só quando existir:
   - "Confirme antes de fazer", se houver divergência ou o item estiver fora da OS;
   - "Espere antes de fazer", se a tarefa depender de outra.
4. **Um botão enorme só:**
   - **Começar** (leva para "Em produção");
   - depois **Terminei** (leva para "Entregue");
   - depois o estado **Pronto**.
5. **Dois botões:**
   - 🔊 **Ouvir:** lê a tarefa em voz alta em pt-BR com `speechSynthesis`; some se o aparelho não suportar.
   - ⚠ **Problema:** marca o aviso de atenção; o cartão fica com borda amarela.
6. **"Ler mais"** (fechado): o que fazer, antes de começar, como fica pronto, o que confirmar, divergências, responsável e prazo da simulação.
7. **"Ligar para fornecedor"**, só nos itens de box Q25 (Boxtruss):
   - Marcelo · Móvel Estrutura · (31) 9 8864-0265
   - Cobaia · Atual Estruturas · (31) 9 9243-1891
   - Reginaldo · Lighting · (31) 9 9671-2845

   Cada contato tem botões Ligar (`tel:`) e WhatsApp (`https://wa.me/55…`), e o número fica visível para copiar.
8. **"Desfazer"** pequeno, para voltar a etapa.

**Tour curto** de 6 passos, oferecido na primeira visita: "Quer aprender a usar?". Depois, fica em Menu ☰ › Como usar. O balão fica preso ao alvo ao rolar.

### Modo completo (no menu ☰, para a coordenação)

Tem as mesmas funções da versão publicada:
- **Projetos e visão do projeto:** abas dos projetos e ficha com progresso, tarefas em andamento, em atenção e a validar, e próximas tarefas.
- **Busca e filtros:** por peça, material, função ou número; filtros por situação e por quem executa.
- **Três visões sincronizadas:** **Produção** (lista agrupada por item, com divergências), **Kanban** (5 colunas, com botões ‹ › para mudar a etapa) e **Planilha** (descrição, qtd, ações prévias, entrega, responsável, prazo, etapa, atenção e prancha; item fixo à esquerda e rolagem lateral visível).
- **Ficha da tarefa:** etapa em 5 passos e atenção como aviso separado; detalhes; vistas da prancha; outras pranchas; zoom, ajustar, focar peça e recolher desenho.
- **Materiais e fornecedores:** cadastro de contato e de **alternativa de material "a validar pela equipe técnica"**. Uma alternativa nunca troca o material do projeto.
- **Menu:** tamanho do texto, Dia D da simulação, PDF da OS, divergências gerais e "Limpar dados deste aparelho" (pede um segundo toque).

**Estado:** compartilhado entre os dois modos e salvo em `localStorage`, na chave `ambar-fluxograma-b`. O formato é `{mode, proj, view, chip, resp, stage:{"estande:1.1.6":"pr"}, attn:{…}, sup:{…}, alt:{…}, d, fs, tourAsked, sq}`. **Não sincroniza entre pessoas.** A interface precisa dizer isso.

## 4. Modelo de dados (`dados.js`)

```js
const PROJECTS=[{id:"estande",code:"1",name:"Estande ArcelorMittal",pdf:"stand",pages:[…],general:["divergência geral",…],
  items:[{id:"1.1",t:"título",os:1,q:"qtd",desc:"…",acoes:"ações prévias da OS",extra:true?,div:[{t,v}]?,
    subs:[{id:"1.1.1",t:"título",q:"28",u:"un.",desc,prev,ent,quem:"Executa: <função> · Responde: <coordenação>",
           d:5 /*dias antes do D*/, jan:"janela (simulação)", pr:["stand-06"], div?:"…", bloq?:"id"}]}]}, {id:"festival",…}];
const SHAPES={"1.1.6":{"stand-06":{conf:"traçado"|"manual"|"provisorio",note:"…",g:[{d:"M x y L … Z",b:[x0,y0,x1,y1]}]}}};
// coordenadas em pixels da prancha 1095 x 774; cada item de g é uma ocorrência da peça
```

**Etapas:** ag (Aguardando), li (Liberado), pr (Em produção), ex (Executado), en (Entregue).

**Destaque da peça:** `<image>` da prancha recortada por `clipPath` com o contorno; grupo com `transform: scale(1.07)` e `transform-origin` no centro da caixa `b`; filtro SVG de brilho (`feMorphology` + `feGaussianBlur` + `feFlood` âmbar). Contorno provisório aparece em amarelo tracejado, com aviso.

## 5. Regras que não podem ser quebradas

1. **Sem IA:** nenhum botão, chat, chamada de API ou resposta simulada.
2. **Sem inventar dados:** nada de datas, preços, fornecedores, etapas concluídas ou medidas que não estejam nos dados. Divergências ficam visíveis. Os contatos de Boxtruss só aparecem nos itens de box Q25.
3. **Sem nomes de pessoas:** responsáveis são sempre funções. Os únicos nomes permitidos são os dos contatos de fornecedor acima.
4. **Prazos sempre como simulação** (D-n).
5. **Nenhuma tarefa marcada como pronta automaticamente.**
6. **Contorno honesto:** quando não houver contorno confiável, dizer isso; nunca usar retângulo genérico nem iluminar a prancha inteira.
7. **Linguagem do modo simples:** palavras curtas e do dia a dia, ícone junto do texto, botões com pelo menos 56 px de altura, um botão principal por tela, texto grande.
8. **Funcionar offline e no celular primeiro,** com toque, mouse e teclado. A tela nunca rola para os lados (só a planilha, dentro da própria caixa).
9. **Cores:** grafite escuro, laranja Âmbar (#f39a1d) para ação, verde (#3fb767) para pronto, amarelo (#f2c94c) para atenção.
10. **Cabeçalho e rodapé:** cabeçalho com a logo da Âmbar à esquerda e **FLUXOGRAMA DE MONTAGEM** centralizado; rodapé com "Concepção e desenho do produto: **BAITA, by Helthon Andrade.**"
11. **Publicação:** não publicar nem alterar o Render ou o GitHub sem aprovação.

## 6. O que fazer agora (aplicar C junto com A)

1. Compare as funções do Projeto A com as do Projeto C e devolva uma tabela com três colunas: função · onde está no A · onde fica no C.
2. Aponte qualquer função do A que **não** exista no C, para eu decidir se entra no modo simples, no modo completo ou em nenhum.
3. Proponha como unir: usar o C como base e trazer o que faltar do A, ou aplicar a interface do C sobre o código do A. Recomende uma das duas e explique em poucas linhas.
4. Só depois de eu aprovar, entregue os arquivos completos (nunca trechos soltos) e diga o que testou e o que não conseguiu testar.

## 7. Pendências conhecidas

- **Logomarca:** a logo branca da Âmbar não está no pacote; hoje há um símbolo provisório.
- **Decisões no modo simples:** tarefas que são decisões ou desenhos (ex.: 1.4.1 "Definição de material", 1.8.1 "Desenho da árvore") aparecem para a fábrica. Proposta em aberto: escondê-las do modo simples.
- **Testes:** feitos por emulação no Chromium; falta testar num celular de verdade, incluindo a pinça de dois dedos e a voz em pt-BR.
- **Comparação com o A:** a cópia publicada do Projeto A (31 MB) não foi comparada linha a linha com o C.
