# Integrações opcionais do Obsidian

O vault baseline do claude-obsidian usa Markdown, JSON e recursos nativos do
Obsidian. Nenhum plugin, tema ou executável baixado da comunidade é necessário.

## Instalar e abrir o Obsidian

Use as instruções de instalação atuais em
[Obsidian Help](https://help.obsidian.md/). Abra a pasta separada do vault do
usuário, e não o checkout do produto claude-obsidian.

As views nativas de Properties, Backlinks, Outline e Graph podem melhorar a
navegação. Use Bases somente quando a versão instalada do Obsidian suportar a
sintaxe `.base` de que você precisa. A skill `obsidian-bases` pode redigir um
arquivo, mas a renderização da aplicação ainda exige verificação no Obsidian.

## Plugins da comunidade

Plugins da comunidade são código opcional de terceiros. Antes de recomendar ou
instalar um:

1. Confirme a necessidade real do usuário e obtenha aprovação para a instalação.
2. Revise o publisher atual, o repositório-fonte, as permissões solicitadas, a
   proveniência da release e o estado de manutenção.
3. Instale pela interface suportada do Obsidian. Não copie um `main.js` não
   verificado nem baixe uma release flutuante a partir de um workflow de agente.
4. Faça backup do vault e teste em uma cópia não crítica quando o plugin puder
   reescrever notas ou propriedades.
5. Registre o plugin e a versão na documentação do vault do usuário, e não no
   código do produto.

Plugins de templates, calendário, captura rápida, Git, Dataview, busca semântica e
temas podem ser úteis, mas nenhum é incluso nem assumido pela baseline.

## Plugins de Git e sync

Um plugin de Git ou de sync do Obsidian é uma conveniência de backup, não o
mecanismo de transação ou de checkpoint do claude-obsidian. Commits em background
podem entrar em corrida com uma operação do agente e tornar ambíguos os
checkpoints de operação exata. Desabilite commits automáticos sobrepostos enquanto
aplica uma operação, ou use um método de backup separado. Rode `checkpoint` apenas
quando o usuário pedir explicitamente histórico Git.

## Web Clipper

Trate material capturado do navegador como entrada de fonte não confiável.
Capture-o na inbox configurada, preserve seu localizador e hash, e ingira-o pelo
workflow de proveniência normal. Um clip não é evidência de verdade apenas porque
foi importado com sucesso.