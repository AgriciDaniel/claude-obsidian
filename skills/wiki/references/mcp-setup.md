# Transportes externos de leitura

A baseline portátil lê arquivos do vault diretamente. O CLI oficial do Obsidian é
uma superfície de leitura opcional quando a sondagem de runtime reporta que é
utilizável. Servidores MCP e plugins REST são integrações opcionais de terceiros,
nunca pré-requisitos.

## Política de seleção

1. Prefira leituras diretas do filesystem por portabilidade e menor privilégio.
2. Use o CLI oficial do Obsidian somente leitura quando `detect-transport.sh --peek`
   reportar que ele é utilizável.
3. Considere um adaptador MCP ou REST somente quando o usuário precisar de uma
   capacidade que as duas primeiras escolhas não podem fornecer e aprovar
   explicitamente a instalação.
4. Mantenha todas as mutações do vault em uma transação de operação
   claude-obsidian. Um transporte externo não pode contornar hashes esperados,
   journaling ou recuperação.

## Revisão de terceiros

Receitas de instalação, nomes de pacotes, flags e permissões mudam. Consulte a
documentação primária atual do adaptador antes do uso, fixe uma versão revisada e
verifique publisher e origem. Não execute pacotes `latest` flutuantes, downloads
não verificados ou scripts de instalação opacos a partir desta referência.

Para qualquer adaptador:

- conceda acesso somente ao vault selecionado;
- vincule listeners de rede ao loopback, a menos que o usuário tenha projetado e
  aprovado acesso remoto autenticado;
- mantenha tokens fora de notas, histórico de shell, logs e arquivos do repositório;
- preserve a verificação TLS em vez de usar flags de ambiente de bypass global;
- use read-only como padrão e teste com dados não sensíveis;
- documente quais dados podem sair da máquina e como desabilitar o adaptador.

Vincular ao loopback reduz a exposição, mas não torna segura uma verificação de
certificado desabilitada nem um bearer token vazado.

## Verificação

Relate a prontidão do adaptador somente após uma sondagem de leitura inofensiva
ter sucesso. Apenas a presença do binário ou da configuração significa
`available`, não `verified`. Se uma sondagem falhar, volte a leituras do filesystem
sem mudar a semântica de mutação.