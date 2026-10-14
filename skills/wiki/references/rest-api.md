# Contrato de segurança do adaptador REST

A Local REST API é um plugin opcional de terceiros do Obsidian. O claude-obsidian
não a instala, não a exige e não a usa como transporte de mutação.

## Antes do uso

- Confirme que o usuário instalou e habilitou o plugin intencionalmente.
- Leia a documentação primária atual do plugin e verifique a versão exata da API
  e os endpoints em vez de confiar em exemplos lembrados.
- Mantenha o listener no loopback por padrão e armazene sua credencial em um
  ambiente protegido ou gerenciador de segredos.
- Nunca imprima a credencial, embuta-a em uma nota, faça commit dela ou a coloque
  em uma transcrição de comando reutilizável.
- Exija a verificação TLS normal. Não use `curl -k`,
  `NODE_TLS_REJECT_UNAUTHORIZED=0` ou outro bypass de escopo de processo.

## Papel permitido

Use um adaptador REST configurado somente para operações de leitura e busca que o
usuário colocou em escopo. Valide os caminhos retornados e rejeite travessia de
diretórios ou escapes por symlink. Uma resposta HTTP bem-sucedida prova o
comportamento do transporte, e não a verdade do conteúdo retornado.

Requisições de create, replace, append, patch, move e delete estão fora deste
contrato de adaptador. Expresse toda mudança no vault como uma única operação
inspecionada `claude-obsidian.transaction.v1`, de modo que hashes esperados,
proveniência, journaling e recuperação continuem garantidos.

Se não for possível configurar TLS seguro ou acesso de menor privilégio, use
leituras diretas do filesystem ou a superfície de leitura do CLI oficial verificada.