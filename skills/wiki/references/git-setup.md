# Histórico Git opcional

O Git é opcional. A correção do vault vem das transações de operação, dos hashes
esperados, dos journals de recuperação e da validação determinística, e não de
commits em background.

## Inicialize apenas com aprovação

Não inicialize um repositório, não adicione um remote, não faça stage, commit ou
push só porque um vault foi scaffoldado. Se o usuário pedir histórico local,
primeiro mostre o vault selecionado e a ação planejada, e então inicialize o Git
nesse vault. Mantenha estado de workspace, caches, segredos e lixeira excluídos.

Uma política típica de ignore para o vault do usuário inclui:

```gitignore
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.trash/
.DS_Store
.vault-meta/
```

Transaction bundles, journals de recuperação, filas e chunks derivados podem conter
texto de nota, caminhos locais ou URLs de fonte, então mantenha todo `.vault-meta/`
ignorado por padrão. Se o usuário quiser deliberadamente versionar um arquivo de
configuração estável desse diretório, adicione a exceção revisada mais estreita
enquanto deixa as subárvores de runtime ignoradas. Ajuste as entradas restantes aos
plugins reais e às necessidades de privacidade. Não copie cegamente o arquivo de
ignore do repositório do produto.

Commits de `checkpoint` confirmam exatamente uma operação concluída e portanto
requerem um commit pai existente. Após `git init`, crie uma baseline revisada
separada antes de rodar qualquer operação que você pretenda fazer checkpoint:

```bash
git status --short
git add -- <reviewed-baseline-paths>
git diff --cached --stat
git diff --cached
git commit -m "vault: reviewed baseline"
```

Selecione os caminhos da baseline deliberadamente; não faça stage de estado de
runtime ignorado, segredos ou payloads brutos apenas para tornar o repositório não
vazio. O comando de checkpoint nunca cria essa baseline nem dobra arquivos
pré-existentes em silêncio dentro de um commit de operação.

## Checkpoints de operação exata

Após uma transação claude-obsidian bem-sucedida, um checkpoint explicitamente
solicitado é:

```bash
python3 "$CORE" checkpoint OPERATION_ID --vault "$VAULT"
```

O comando verifica os hashes registrados, recusa qualquer estado de stage
pré-existente, roda lint determinístico por padrão e exclui payloads brutos de
fonte a menos que o usuário aceite. Ele constrói e verifica o commit através de um
índice temporário e então avança a ref por compare-and-swap. Um registro pending
durável torna uma finalização interrompida segura para retentativa. Revise o commit
retornado com `git show`. Push ou adição de remote é uma ação externa separada que
exige autorização explícita do usuário.

Evite plugins de commit automático durante operações do agente porque eles podem
capturar estado parcial ou não relacionado e invalidar o histórico de operação exata.