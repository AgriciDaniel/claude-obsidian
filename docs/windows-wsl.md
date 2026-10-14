# Guia Windows e WSL

O claude-obsidian suporta Windows nativo como plataforma somente-leitura e
WSL como plataforma de capacidade total. Este guia cobre o que funciona onde,
por que o limite existe e como destravar o WSL quando ele se comporta mal.

## Suporte de plataforma

| Capacidade | WSL / Linux / macOS | Windows nativo (incl. Git Bash) |
|---|---|---|
| Inspeção, previews de dry-run, recuperação | Sim | Sim |
| Escritas no vault (`transaction apply`, `init`, `adopt`, `migrate`, `capture apply`, `mode set`) | Sim | Não — recusado com `UNSUPPORTED_PLATFORM` |
| Comandos de fila de captura (incluindo `capture queue list` somente-leitura) | Sim | Não — atualmente recusado; rastreado em [#151](https://github.com/AgriciDaniel/claude-obsidian/issues/151) |
| Checkpoints Git (`checkpoint`) | Apenas Linux e macOS | Não |
| Scripts de setup Bash e suíte de testes shell | Sim | Não (somente POSIX) |
| Hooks Claude Code (`SessionStart`, `Stop`) | Sim (funciona out of the box) | Parcial: requer `python3` no `PATH`; veja [abaixo](#claude-code-hooks-and-python3-on-windows) |

Vaults devem ficar em um filesystem com identidade de arquivo estável: NTFS
funciona bem, mas volumes FAT/exFAT (pendrives USB típicos) e alguns
compartilhamentos de rede são recusados com `UNSAFE_VAULT_IDENTITY` — mova
o vault para NTFS ou trabalhe dentro do WSL.

## Hooks Claude Code e python3 no Windows

`hooks/hooks.json` spawna cada hook usando o [hook de comando exec-form do
Claude Code](https://code.claude.com/docs/en/hooks): `"command": "python3"`
com um array `args`. O Claude Code resolve `python3` como um executável no
`PATH` e o spawna diretamente; não há shell, então nenhum shim `.bat`,
função de alias ou perfil de shell é consultado.

WSL e a maioria das instalações Python no Linux e macOS fornecem um
`python3` no `PATH` por padrão, então os hooks funcionam lá sem configuração
extra. Windows nativo comumente não:

- instalador python.org: instala `python.exe`, não `python3.exe`. Adicione
  um shim `python3.exe` antes no `PATH` do que o interpretador, instale uma
  distribuição que forneça `python3.exe`, ou execute Claude Code a partir do
  WSL para que os hooks resolvam o `python3` do WSL.
- Microsoft Store Python: o alias de execução de app `python3` pode ser um
  stub que abre a Store em vez de executar Python. Desabilite o alias de
  execução de app `python3` nas Configurações do Windows, então instale
  Python do python.org ou do WSL e confirme que o interpretador real está
  no `PATH`.

Quando `python3` não pode ser resolvido, o Claude Code falha em spawnar o
processo do hook, então o código do claude-obsidian nunca executa e não pode
emitir um diagnóstico. O contexto de `SessionStart` e os avisos de recuperação
do `Stop` estão ambos silenciosamente ausentes nesse caso; o resto do
claude-obsidian (skills e CLI) é unaffected, já que apenas o caminho opcional
de hook depende de `python3`.

## Por que as escritas exigem WSL

A segurança de mutação está vinculada a descritores de diretório POSIX: a
raiz do vault e cada diretório de tempo de execução permanecem fixados
durante toda a escrita, então um symlink trocado concorrentemente ou uma pasta
substituída falha de forma segura em vez de redirecionar a escrita (veja o
[guia do Compound Vault](compound-vault-guide.md)). Windows nativo não pode
fornecer essas primitivas, então as escritas são recusadas de imediato em vez
de executar silenciosamente com garantias mais fracas.

Um modo degradado de escrita no Windows nativo — default-off, atrás de um
flag de garantias reduzidas explícito — está sob consideração em
[#151](https://github.com/AgriciDaniel/claude-obsidian/issues/151). Se o WSL
é um blocker para você, essa issue é o lugar para opinar.

## Troubleshooting de WSL

WSL estar "instalado" nem sempre significa que o WSL está funcionando.
Sintomas e verificações, aproximadamente na ordem valiosa para tentar:

| Sintoma | Verificação |
|---|---|
| `wsl --install` concluído mas `wsl --status` ou `wsl -l -v` trava indefinidamente | Este hang reportado em campo não tem causa confirmada. Siga o fluxo de diagnóstico e reporte de hang do WSL da Microsoft abaixo. |
| `wsl` reporta erro de kernel ou versão | Execute `wsl --update`, depois `wsl --shutdown`, depois tente novamente. |
| WSL funcionava antes e parou após uma atualização ou mudança de software | Não assuma uma causa. Atualize Windows e WSL, então siga o fluxo de troubleshooting de WSL da Microsoft. |
| Hash de aprovação de dry-run nativo falha dentro do WSL com `PLAN_CHANGED` | Por design: o hash de aprovação vincula a identidade de filesystem do ambiente de revisão. Execute a revisão do dry-run dentro do WSL quando o apply acontecerá lá; um `approved_plan_sha256` produzido nativamente não pode ser replayed a partir do WSL. |
| Escritas falham com `UNSAFE_VAULT_IDENTITY` mencionando identidade de arquivo estável | O vault está em FAT/exFAT ou em um compartilhamento de rede não suportado. Mova-o para NTFS, ou mantenha-o dentro do filesystem do WSL. |

Checklist de troubleshooting de WSL:

1. Comece com o [guia oficial de troubleshooting de WSL](https://learn.microsoft.com/en-us/windows/wsl/troubleshooting) da Microsoft.
2. Confirme que a virtualização está habilitada na BIOS/UEFI e que ambos
   "Virtual Machine Platform" e "Windows Subsystem for Linux" estão
   habilitados. Reinicie após habilitar qualquer funcionalidade.
3. Execute `wsl --update` a partir de um prompt elevado, depois
   `wsl --shutdown`, e tente `wsl --status` novamente.
4. Confirme que a configuração de launch do hypervisor está habilitada. Se
   um hypervisor de terceiros estiver instalado, use uma versão atual que
   suporte Hyper-V ou desligue-o temporariamente enquanto diagnostica o
   conflito.
5. Se o WSL ainda travar, siga os [passos de coleta de dados de hang de WSL](https://learn.microsoft.com/en-us/windows/wsl/troubleshooting-guide#wsl-hangs) da Microsoft
   e arquive o relatório resultante com o projeto WSL. Não atribua o hang a
   uma causa específica sem diagnósticos de suporte.

## Trabalhando através da fronteira

O fluxo de trabalho suportado no Windows nativo é: inspecione e revise
nativamente, mute dentro do WSL. Como os hashes de aprovação vinculam-se ao
ambiente que os produziu, faça o dry-run revisado no mesmo ambiente que
executará o apply. Manter o vault dentro do filesystem do WSL (em vez de em
unidade Windows montada) evita tanto as ressalvas de identidade acima quanto a
sobrecarga de performance da fronteira.
