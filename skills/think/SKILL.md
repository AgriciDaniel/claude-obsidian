---
name: think
description: Aplique o loop Fable derivado de 10 etapas OBSERVE, OBSERVE, LISTEN, THINK, CONNECT, CONNECT, FEEL, ACCEPT, CREATE, GROW a raciocínios e decisões consequentes ou ambíguos. Use para pensar bem nisso, pensar profundamente, revisão de arquitetura, postmortem, análise de tradeoffs, ou questionar premissas. Esta é uma revisão de raciocínio, não uma verificação de saúde determinística do vault nem um workflow de reparo.
---

# Think

Use as dez etapas como um loop de atenção, não como uma transcrição
cerimonial. Ajuste a profundidade à novidade, ao risco, à incerteza e à
irreversibilidade. Mantenha o resumo final do raciocínio conciso e ancorado em
evidências.

Esta skill é somente leitura. Ela pode inspecionar evidências disponíveis, mas
não edita arquivos, não executa mutações no vault, não faz commit no Git e não
publica nada. Se a etapa CREATE recomendar uma mudança, componha com a skill de
mutação apropriada depois que o usuário autorizar essa operação.

## Estabelecer um enquadramento de evidências

Antes do loop, separe:

- **Observado:** diretamente sustentado por uma entrada, fonte, teste ou
  medição.
- **Inferido:** uma conclusão tirada das observações; declare a ponte.
- **Desconhecido:** evidência ausente que poderia mudar a decisão.
- **Preferência:** uma escolha do usuário ou do projetista, não um claim factual.

Anexe citações ou localizadores concretos quando houver fontes. Nunca fabrique
uma citação, um localizador, um resultado de teste, um consenso ou um nível de
confiança.

## As dez etapas

### 1. OBSERVE — externo

Leia as entradas reais, o estado atual, as restrições, as falhas e o trabalho
anterior. Distinga o que foi inspecionado por completo do que foi amostrado ou
assumido.

### 2. OBSERVE — interno

Nomeie os vieses mais prováveis de distorcer esta decisão: ancoragem, posse,
novidade, familiaridade, urgência, custo afundado, confirmação, ou um veredicto
desejado. Recalibre a confiança à evidência disponível.

### 3. LISTEN

Recupere a intenção do usuário, a condição de sucesso, as restrições e as
participações não declaradas. Esteja atento a mensagens de erro, dissenso, casos
de borda e vozes afetadas. Faça apenas perguntas cujas respostas possam mudar
materialmente o resultado.

### 4. THINK

Reduza o problema a invariantes, alternativas, tradeoffs e modos de falha.
Prefira o menor teste reversível que possa refutar a hipótese principal. Trate o
comportamento de falha como parte da especificação.

### 5. CONNECT — lateral

Procure a mesma estrutura em componentes adjacentes ou em outro domínio. Use uma
analogia apenas quando suas similaridades e limites mapeados forem explícitos.

### 6. CONNECT — sistema

Rastreie entradas a montante, consumidores a jusante, posse, limites de estado,
interfaces e caminhos de recuperação. Verifique se uma decisão localmente
sólida cria uma falha de integração em outro lugar.

### 7. FEEL

Considere a carga cognitiva, o estado emocional, a acessibilidade, a confiança e
a experiência de recuperação de erro do usuário. Trate a intuição como um sinal
a investigar, nunca como substituto de evidência.

### 8. ACCEPT

Declare de forma direta restrições, incerteza, evidências contraditórias e
achados desfavoráveis. Não infle uma pontuação, não suavize um risco material
para agradar o usuário e não confunda concordância com correção. Apresente o
contraargumento mais forte e razoável contra a conclusão preferida.

### 9. CREATE

Produza o menor artefato útil: uma recomendação, um registro de decisão, um
experimento, um rascunho, uma revisão ou um handoff. Marque as premissas e os
riscos não resolvidos. Não mute estado nesta skill.

### 10. GROW

Defina qual feedback ou medição deve atualizar a decisão, quando revisitá-la e
qual lição é reutilizável. Salvar a lição é uma operação explícita separada,
composta com `save`.

## Disciplina de verificação

Antes de chamar o trabalho de concluído:

1. Teste o claim de maior risco ou declare claramente por que ele segue não
   testado.
2. Busque evidências que desconfirmem, não apenas exemplos de apoio.
3. Ajuste o esforço de verificação ao raio de impacto e à reversibilidade.
4. Reporte os comandos, fontes, artefatos ou observações realmente usados.
5. Separe uma verificação aprovada de uma correção mais ampla que ela não
   estabelece.
6. Dê a confiança como um julgamento qualitativo calibrado com razões, não como
   uma porcentagem decorativa.

## Formato da saída

Adapte os headings à tarefa, mas preserve estes resultados:

```markdown
## Decision
<recommendation or artifact>

## Evidence
<observed facts and important inferences>

## Counterargument and risks
<strongest alternative, contradictions, unknowns>

## Verification
<checks performed and checks still needed>

## Growth loop
<feedback signal, revisit condition, reusable lesson>
```

Para uma busca trivial e reversível ou para um erro de digitação, pule o loop
formal. Para uma decisão consequente, volte ao loop sempre que uma etapa
posterior expor uma observação ausente ou um requisito mal compreendido.