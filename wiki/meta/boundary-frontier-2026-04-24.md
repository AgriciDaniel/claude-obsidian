---
type: meta
title: "境界フロンティアスナップショット (2026-04-24)"
updated: 2026-04-24
aliases:
  - boundary-frontier-2026-04-24
  - "境界フロンティアスナップショット 2026-04-24"
tags:
  - meta
  - dragonscale
  - mechanism-4
status: snapshot
related:
  - "[[DragonScale Memory]]"
  - "[[log]]"
  - "[[hot]]"
---

# 境界フロンティアスナップショット (2026-04-24)

ナビゲーション: [[index]] | [[log]] | [[DragonScale Memory]]

DragonScaleメカニズム4(`scripts/boundary-score.py`)を本vaultに対して初めてエンドツーエンドで実行した結果。`./scripts/boundary-score.py --json --top 7`から2026-04-24T08:49:16Zに生成。

## このページの位置づけ

これはスコアリングのスナップショットであり、処方箋ではない。境界スコアのヒューリスティックは、外向きにリンクし最近触られたページを`/autoresearch`が拡張する候補として浮上させる。`[[DragonScale Memory]]`仕様v0.4のメカニズム4の通り、これは明示的にアジェンダ制御である。ランキングはエージェントが次に研究する対象を形作るが、ユーザーは候補を受け入れる、上書きする、却下するのいずれかを行うべきである。

数式: `boundary_score(p) = (out_degree(p) - in_degree(p)) * exp(-age_days / 30)`。

recencyの下限は無い。約90日より古いページは設計上ゼロ重みに近づくため、古いハブがフロンティアを支配することはない。

## フロンティア (上位7、score > 0)

| # | score | out | in | age_d | title | path |
|---|---|---|---|---|---|---|
| 1 | 4.693 | 8 | 0 | 16 | Claude + Obsidian Ecosystem Research | wiki/sources/claude-obsidian-ecosystem-research.md |
| 2 | 4.000 | 4 | 0 | 0 | DragonScale Memory | wiki/concepts/DragonScale Memory.md |
| 3 | 1.702 | 3 | 0 | 17 | How does the LLM Wiki pattern work? | wiki/questions/How does the LLM Wiki pattern work.md |
| 4 | 1.135 | 2 | 0 | 17 | Wiki vs RAG | wiki/comparisons/Wiki vs RAG.md |
| 5 | 0.717 | 1 | 0 | 10 | SEO Drift Monitoring | wiki/concepts/SEO Drift Monitoring.md |
| 6 | 0.717 | 1 | 0 | 10 | Search Experience Optimization (SXO) | wiki/concepts/Search Experience Optimization.md |
| 7 | 0.717 | 1 | 0 | 10 | Semantic Topic Clustering | wiki/concepts/Semantic Topic Clustering.md |

スコアリング対象は合計22ページ(meta、fold、indexのページは除外)。

## 結果の読み方

- 行1はエコシステム研究の情報源。8つのエンティティページに外向きリンクし、被リンクは無い。raw sourceとしては想定通り:被参照ではなくグラフのシードを果たす。スコアは正しく、この候補を辿れば情報源そのものを再検討するのではなく、その8エンティティのいずれかを拡張することになる。
- 行2(DragonScale Memory)はage_days=0かつin-degreeが0。まだどの議論からもリンクされていない新しい概念ページ。正当なフロンティア信号。
- 行3〜7はやや古いページ(約10〜17日)で、out-degreeはほどほど。recency減衰により新しいページに対して適切に減衰されている。
- out-degreeがゼロでrecencyだけのページは順位に上がらない。数式が次数差にrecencyを掛けるためである。

## キャリブレーションに関する注

30日のhalflifeはチューニング値ではなくデフォルトとして選んだ。このvaultが約100ページを超えてout-degreeパターンが変わる場合、halflifeを次数とrecency間の重み付けと併せて見直すべきである。`[[DragonScale Memory]]`仕様はこれらをシード値であり、文献に裏付けられた値ではないと明示的にタグ付けしている。

## 再現方法

```
./scripts/boundary-score.py --json --top 7
```

読み取り専用。python3のみ必要。スコアラー自体を実行するためのDragonScaleセットアップは不要。

## 関連リンク

- [[DragonScale Memory]]: 仕様、メカニズム4
- [[log]]: 操作ログ
- [[hot]]: 最近のコンテキスト
