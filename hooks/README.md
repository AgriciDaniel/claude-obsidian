# Hooks Claude Code

`hooks.json` é um adaptador Claude Code fino em torno do núcleo portátil.

Hooks exigem uma release atual do Claude Code: o shape `command`/`args` do
hook exec-form e o matcher `compact` `SessionStart` usado abaixo precisam
disso (veja o [contrato de hooks do Claude Code](https://code.claude.com/docs/en/hooks)).
Ambos os hooks também precisam de um interpretador alcançável como `python3` no
`PATH`; veja o [guia Windows e WSL](../docs/windows-wsl.md#claude-code-hooks-and-python3-on-windows)
para configuração no Windows nativo.

| Evento | Matcher | Comportamento |
|---|---|---|
| `SessionStart` | `startup\|resume\|clear\|compact` | Silencioso por padrão. Com `CLAUDE_OBSIDIAN_SESSION_CONTEXT=1`, resolve um vault real de usuário e emite um bloco de dados `wiki/hot.md` limitado e sanitizado. Um vault configurado fora do projeto também exige um path exato `CLAUDE_OBSIDIAN_SESSION_CONTEXT_VAULT`. |
| `Stop` | unsupported/omitido | Emite um JSON `systemMessage` limitado e agregado quando a recuperação for necessária. Omite identificadores de operação, paths e conteúdo de notas; do contrário, é silencioso. |

Ambos são hooks `command` usando um executável mais um array de argumentos e
`${CLAUDE_PLUGIN_ROOT}` apenas para localizar o código do plugin. Eles não usam
o cache de plugin como vault.

Os shapes de resposta seguem o [contrato de hooks do Claude Code](https://code.claude.com/docs/en/hooks)
atual: um `SessionStart` opt-in pode adicionar contexto via stdout, enquanto
avisos do `Stop` usam o campo `systemMessage` de nível superior suportado. O
`Stop` não tem matcher porque esse evento não suporta um. Ambos os leitores
rejeitam paths symlink e limitam sua contagem de varredura e bytes de saída.

Hooks nunca escrevem conhecimento, atualizam `wiki/hot.md`, preparam arquivos,
commitam no Git, executam chamadas remotas ou contornam a aprovação de
transações. Os mesmos fluxos de trabalho permanecem utilizáveis em hosts que
não suportam hooks Claude.
