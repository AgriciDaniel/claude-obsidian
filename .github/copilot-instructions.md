# Instruções do Copilot para claude-obsidian

Leia `AGENTS.md` antes de propor mudanças. O repositório é um pacote de Agent
Skills, um adaptador de Claude Code, um núcleo Python de biblioteca padrão e um
template de vault determinístico — não o vault de usuário ativo padrão.

Ao editar:

- Mantenha o frontmatter da skill em exatamente `name` e `description` de linha
  única.
- Use Obsidian Flavored Markdown, propriedades YAML planas e datas no formato
  `YYYY-MM-DD`.
- Nunca modifique payloads de fonte bruta existentes.
- Encaminhe todas as mutações lógicas de conhecimento através de um único
  bundle de operação inspecionado.
- Mantenha trabalhadores somente para rascunhos e lint/query somente-leitura.
- Preserve a contenção de paths do vault e a separação produto/vault.
- Adicione testes de regressão herméticos para mudanças de comportamento e
  execute `make test`.
- Não adicione segredos, paths privados, alegações de capacidade sem suporte
  nem wrappers de comando duplicados.

Public canonical: https://github.com/AgriciDaniel/claude-obsidian
