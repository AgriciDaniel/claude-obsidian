# Modos de instalação suportados

Resolva a raiz do produto instalado a partir da própria localização da skill
invocadora, e não a partir do diretório de trabalho do vault do usuário:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

## Plugin do marketplace do Claude

Instale o plugin pelo seu marketplace e invoque skills namespaced como
`/claude-obsidian:wiki`. Os assets do plugin vivem em um cache efêmero. O estado
mutável do vault deve ser resolvido a partir do projeto, de `--vault` ou da
configuração de workspace, nunca de `${CLAUDE_PLUGIN_ROOT}`.

## Desenvolvimento local de plugin do Claude

```bash
claude --plugin-dir /path/to/claude-obsidian
```

As skills permanecem namespaced. Rode o Claude a partir do vault do usuário, e não
do diretório-fonte do plugin, ou configure o vault explicitamente.

## Agent Skills portáteis

Use `scripts/setup-multi-agent.sh` ou faça link de cada diretório
`skills/<name>/` no caminho de descoberta direto `<skill-root>/<name>/SKILL.md`
do host. Hosts de Agent Skills como Codex, OpenCode e outros consomem os mesmos
arquivos `SKILL.md`. Hooks exclusivos do Claude são adaptadores, não lógica central
do workflow.

## Clone do produto

Um clone-fonte é código de produto/desenvolvimento, não um plugin instalado
automaticamente nem o vault de usuário recomendado. Crie um vault separado:

```bash
python3 "$CORE" init /path/to/vault \
  --generated-at <ISO-UTC> --operation-id init-reviewed
python3 "$CORE" init /path/to/vault \
  --generated-at <ISO-UTC> --operation-id init-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Adote um vault Obsidian existente de forma não destrutiva:

```bash
python3 "$CORE" adopt /path/to/vault \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed
python3 "$CORE" adopt /path/to/vault \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Ambos os comandos têm dry-run como padrão. Novos vaults de usuário não recebem
remote de produto upstream.