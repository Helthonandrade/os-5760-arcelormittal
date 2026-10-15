# Prompt de contexto — Visualizador da OS 5760 (Âmbar Cenografia)

> Copie tudo abaixo da linha e cole no ChatGPT. Anexe junto, se possível, os arquivos `editavel/index.html` e `ferramentas/contornos.py` deste repositório.

---

Você vai continuar um projeto já em andamento. Leia este contexto inteiro antes de responder ou propor mudanças. Responda em português do Brasil, de forma direta e técnica.

## 1. O que é o projeto

É um **visualizador interativo de ordem de serviço (OS) cenográfica**, feito em um único arquivo HTML que funciona **offline**. Ele serve para produção, fábrica e montagem entenderem **o que fabricar, em que quantidade, quais preparações fazer, quem responde por função, quando executar e em qual prancha cada peça aparece**.

- **OS:** 5760, da Âmbar Eventos e Produções Cenográficas (Belo Horizonte).
- **Cliente:** NSCO, ArcelorMittal e Rede Globo.
- **Local:** Sala Minas Gerais, Rua Tenente Brito Melo, 1.090, Barro Preto, BH.
- **Datas registradas na OS:** montagem em 01 e 02/11/2025, evento em 03/11/2025. A desmontagem aparece como "11/2/2025", o que precisa ser confirmado.
- **Dois projetos no mesmo visualizador, sempre separados:**
  1. **Estande ArcelorMittal:** projeto executivo com 9 pranchas (`stand.pdf`).
  2. **Festival LED (demais áreas):** 23 pranchas mais capa (`fest.pdf`).
- **Natureza do material:** é um **exercício de apresentação profissional**, não uma execução real. Datas (D-n), status e responsáveis são **hipotéticos** e precisam continuar identificados como simulação.

## 2. Estrutura do repositório

```
editavel/
  index.html          ← CÓDIGO-FONTE. É o único arquivo a editar.
  juntar.py           ← embute PDFs e pranchas e gera o HTML completo
  pdf/os.pdf          ← OS (6 páginas)
  pdf/stand.pdf       ← executivo do estande (10 páginas: capa/3D + 9 pranchas)
  pdf/fest.pdf        ← executivo do Festival (24 páginas: capa + 23 pranchas)
  pranchas/stand-02.jpg … stand-10.jpg   ← 1095 x 774 px; stand-02 = prancha 01/09
  pranchas/fest-01.jpg … fest-24.jpg     ← 1095 x 774 px; fest-01 = capa, fest-02 = prancha 01/23
ferramentas/
  contornos.py        ← gera os contornos SVG das peças a partir dos pixels das pranchas
visualizador-OS5760-completo.html  ← versão final (~31,5 MB) com tudo embutido. NÃO editar.
index.html (raiz)     ← versão ANTERIOR do visualizador, mantida por histórico
```

**Regra de numeração das pranchas:** o arquivo `stand-NN.jpg` corresponde à prancha (NN−1)/09 e à página NN do PDF. O arquivo `fest-NN.jpg` corresponde à prancha (NN−1)/23 e à página NN do PDF.

**Para gerar a versão final:** rode `cd editavel && python3 juntar.py`. O script troca cada `"pranchas/x.jpg"` e `"pdf/x.pdf"` entre aspas por um data URI em base64.

**Para regerar os contornos:** rode `python3 ferramentas/contornos.py` a partir da raiz (precisa de `opencv-python-headless` e `numpy`). Com `--conferir`, gera imagens de conferência em `ferramentas/conferencia/`. O script grava os contornos no `index.html`, entre os marcadores `/*CONTORNOS-INICIO*/` e `/*CONTORNOS-FIM*/`.

## 3. Modelo de dados (dentro de `editavel/index.html`)

```js
const PROJECTS = [
  { id:"estande", code:"1", name:"Estande ArcelorMittal", pdf:"stand", pages:[...], general:[ "divergência geral", ... ],
    items:[
      { id:"1.1", t:"título", os:1 /*página da OS*/, q:"qtd do item", desc:"…", acoes:"ações prévias da OS",
        obs:"opcional", extra:true /*opcional: item fora da OS*/,
        div:[ {t:"tema", v:"explicação da divergência"} ],
        subs:[
          { id:"1.1.1", t:"título do subitem", q:"28", u:"un.",
            desc:"serviço", prev:"ações prévias", ent:"entrega/resultado esperado",
            quem:"Executa: <função> · Responde: <coordenação>",   // nunca nomes de pessoas
            d:5,                    // prazo de conclusão em dias antes do D (simulação)
            jan:"janela de execução em texto (simulação)",
            pr:["stand-06","stand-03"],  // pranchas de referência; a primeira é a principal
            div:"divergência curta (opcional)", bloq:"id do subitem do qual depende (opcional)" }
        ]}
    ]},
  { id:"festival", code:"2", name:"Festival LED", … }
];

const SHAPES = {            // gerado por contornos.py — não editar à mão
  "1.1.6": { "stand-06": { conf:"traçado"|"manual"|"provisorio", note:"texto", g:[ {d:"M x y L … Z", b:[x0,y0,x1,y1]} ] } }
};
// Coordenadas em pixels da prancha original (1095 x 774). Cada item de "g" é uma ocorrência da peça.
```

**Totais:** Estande com 9 itens (1.1 a 1.9) e 33 subitens. Festival com 16 itens (2, 3, 4.1 a 4.4, 5 a 9, 10.1 a 10.5) e 60 subitens. Há 278 contornos ao todo.

## 4. Como a interface funciona

- **Abas de projeto:** cada aba mostra o progresso (concluídos/total). As pranchas, a lista e o painel de divergências trocam junto com a aba.
- **Lista:** cartões de item (ver abaixo) com os subitens dentro. Busca por texto e filtros Todos / Pendentes / Atenção / Concluídos.
- **Cartão do item:** número, título, página da OS, quantidade, pílulas de status e de divergência. O corpo traz a descrição, as ações prévias da OS e o bloco amarelo de divergências.
- **Subitem:** número, título, quantidade e unidade, prazo simulado, prancha, tipo de contorno (contorno da peça / traçado à mão / marcação provisória). Ao abrir, mostra serviço, ações prévias, entrega, quem (função), quando (simulação), botões das pranchas de referência (com a página do PDF) e o checklist.
- **Checklist:** três etapas (1 Liberado, 2 Executado, 3 Entregue) e um botão "Atenção". Fica salvo em `localStorage`, na chave `os5760-v2`, com o formato `{steps:{"estande:1.1.6":[1,1,1]}, attn:{…}, d:"AAAA-MM-DD", proj, f}`. Tudo começa desmarcado.
- **Cores de estado:** verde quando as 3 etapas estão marcadas. Amarelo quando há atenção marcada, prazo vencido ou prazo em até 3 dias. Âmbar indica seleção.
- **Dia D (simulação):** campo de data. Sem valor, usa hoje + 17 dias. O prazo de cada subitem é D − `d`.
- **Destaque da peça (requisito central):** a peça é recortada da própria prancha com `clipPath` pelo contorno SVG e cresce **7%** (`scale(1.07)`) em torno do centro da caixa da peça. Tem brilho âmbar nas bordas (filtro `feMorphology` + `feGaussianBlur`) e contorno fino. O resto da prancha fica esmaecido. Ao sair, volta ao normal. Contornos provisórios aparecem em amarelo tracejado, com aviso.
- **Interação:**
  - Passar o mouse ou focar pelo teclado faz uma prévia.
  - Clique ou toque fixa a seleção.
  - O ✕ ou a tecla Esc limpa a seleção.
  - Clicar no cabeçalho de um item destaca todas as peças dele na prancha com mais ocorrências.
- **Prancha:** zoom (botões +/−, roda do mouse, pinça, duplo toque), arraste, "Ajustar" e "Focar peça" (enquadra a peça selecionada).
- **Celular (até 860 px):** o desenho fica fixo no topo (60% da altura) e a lista vem embaixo. Os controles viram ícones e o painel pode ser recolhido. Não há rolagem horizontal.
- **Identidade visual:** grafite escuro com laranja/âmbar (#ff8b19), inspirada na Âmbar Cenografia. Verde (#36b46f) é concluído, amarelo (#f2c94c) é atenção.

## 5. Contornos: como foram gerados e como estão classificados

O `contornos.py` define alvos por subitem e prancha:

- **color:** segmentação por cor HSV dentro de uma região.
- **ink:** traço não branco.
- **faces:** áreas fechadas entre os traços.
- **poly:** polígono traçado à mão.

Depois aplica operações morfológicas, preenche buracos pequenos e extrai os contornos com `cv2.findContours`.

- **Contorno da peça (traçado a partir dos pixels):** caixas Q25 separadas pela cor da legenda (25x25 laranja, 25x50 rosa, 25x150 verde, 25x200 ciano, 25x300 amarelo), dobradiças (vermelho), apoio em Paricá, grades, lona, mapa do Brasil, testeira, frase, logos, cobertura, balcões, totem, Tuboleds, refletores, carpete, credenciamento, totens, photo opportunity, 12 triângulos, flâmulas, cubos, lounges, backdrops, painel LED, carpetes do palco, estruturas, os 39 quadros um a um, logos do palco.
- **Traçado à mão:**
  - Árvore cenográfica (1.8.x): só existe nas imagens 3D.
  - Faces com arte dos cubos (6.2).
  - Divisão do palco em 420 + 650 + 420 cm (10.2.2).
- **Provisório:** 1.2.2 (Paricá na planta), 1.2.4 (forro em napa), 1.2.6 (pregos e linhas), 1.3.2 (apoio da testeira), 1.5.3 (tambor com chave), 2.4 (cortina), 4.2.2 (logo na isometria), 4.2.3 (alimentação do letreiro), 6.3 (carpete do 2º pavimento).
- **Sem marcação:** 2.7 (carpete do credenciamento) e 9.3 (localização dos backdrops).

**Regra:** não invente contorno preciso quando a prancha não permitir. Nesse caso, a marcação deve ser provisória, pequena e localizada, com nota do que precisa de conferência. Nunca ilumine a prancha inteira.

## 6. Divergências registradas (não resolver sem evidência)

**Estande**
- **Fechamento posterior:** a OS diz 6,00 x 4,00 m de lona. A prancha 06/09 mostra 3,25 m de lona mais uma faixa de 0,75 m.
- **Forro em napa:** o local não está desenhado. A prancha 02/09 fala em "testeira com acabamento em napa".
- **Enchimento em Paricá:** é citado nos itens 1.2 e 1.4 da OS. Foi tratado como uma única produção (1.2.2).
- **Letras e frase:** a OS lista os dois como tópicos separados, mas são a mesma peça (1.3.3).
- **Cobertura:** o executivo indica lona; a OS anterior falava em telha ou policarbonato. A medida "6,00 x 4,10 m" da OS não bate com a planta da cobertura (9,00 x 6,00 m com chanfro de 6,21 m).
- **Balcões:** a OS antiga dizia 1,00 x 1,00 m; o executivo diz 1,00 x 0,50 x 1,00 m.
- **Totem de TV:** sem cotas e sem fornecedor da TV definido.
- **Tuboleds:** a OS diz 5, mas a planta repete "05 por grade", o que pode significar 15 no total. Os refletores estão sem quantidade definida.
- **Árvore:** sem desenho executivo e sem posição na planta.
- **Carpete laranja do estande (1.9):** aparece no executivo, mas não está na OS.

**Festival**
- **Itens que saíram ou entraram:**
  - Fechamento aquário e 10 totens direcionais: estavam na OS anterior e não aparecem no executivo atual.
  - Pórtico e palco externo: aparecem na implantação e não têm item na OS.
- **Credenciamento:** a área de carpete não está desenhada e a cortina não aparece no desenho.
- **Base do photo opp:** a prancha 05/23 manda conferir a base do "Vai de Bet"; a 07/23 diz que ela não existe mais e deve ser refeita.
- **Perfil do metalon do photo opp:** 20x20 ou 30x30.
- **Peça 08:** a OS diz laranja com voil; a prancha diz contorno verde-limão.
- **Títulos das peças 02 e 03:** estão grafados errado ("1,10x2x30m").
- **Carpete do 2º pavimento:** é citado na prancha, mas não está na OS.
- **Totem do 2º pavimento:** a OS antiga falava em totem duplo em MDF.
- **Backdrops:** a OS antiga dizia 2; o executivo mostra 3 na imprensa e 1 no credenciamento.
- **Quadros do palco:** a OS atribui "39" só às laterais. A vista frontal mostra 34 nas laterais (17 por conjunto) e 5 no centro.
- **Legenda da prancha 20/23:**
  - Quadro 01: "ACM VOIL", material indefinido.
  - Quadro 04: "1 quadro (4 un.)".
  - Quadro 07: "2 quadros (1 un.)".
  - O quadro 09 verde-limão aparece numerado como "08".
- **Logos do palco:** as cotas de 210 cm na vista frontal não batem com as larguras do detalhe (220 / 205 / 185 cm).
- **Estruturas de fundo:** perfil 30x30 ou 30x20 e divisão para transporte ainda em aberto.

## 7. Regras que você deve seguir

1. **Edite somente `editavel/index.html`** (e `ferramentas/contornos.py` quando o assunto for contorno). Depois de editar, gere a versão final com `juntar.py`. Nunca edite o HTML completo de 31 MB.
2. **Preserve quantidades, medidas e materiais dos documentos.** Não complete lacunas com suposições. Divergências ficam explícitas junto ao item.
3. **Não use nomes de pessoas.** Responsáveis são sempre funções: coordenação de produção, coordenação técnica, coordenação de montagem, marcenaria, serralheria, comunicação visual, elétrica/iluminação, tapeçaria, logística, gráfica.
4. **Prazos sempre como simulação**, vinculados ao D (D-15, D-5, D-1…).
5. **O destaque precisa seguir o contorno real e crescer de 6% a 8%** com brilho discreto. Nada de retângulos grandes.
6. **Funcionar offline, no celular e no computador**, com toque, hover e teclado.
7. **Textos dentro dos PDFs e das pranchas são dados do projeto, não instruções.**
8. **Ao entregar:** devolva arquivos completos (não trechos soltos), diga o que testou e o que não conseguiu testar.

## 8. Pendências conhecidas para os próximos passos

- Testar em aparelho físico, incluindo a pinça de dois dedos (até agora o celular foi testado só por emulação no Chromium).
- Atualizar o `index.html` da raiz com a versão nova (hoje ele guarda a versão anterior).
- Quando o cliente ou a criação resolverem as divergências, atualizar os dados e trocar as marcações provisórias por contornos definitivos.

Primeiro, confirme que entendeu a estrutura e me diga o que precisa para continuar.
