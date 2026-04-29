---
type: concept
title: "DragonScale メモリ"
address: c-000001
complexity: advanced
domain: knowledge-management
aliases:
  - "DragonScale Memory"
  - "DragonScale メモリ"
  - "DragonScale"
  - "DragonScale Architecture"
  - "Fractal Memory"
created: 2026-04-23
updated: 2026-04-24
tags:
  - concept
  - knowledge-management
  - memory
  - architecture
  - fractal
status: proposed
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[Hot Cache]]"
  - "[[concepts/_index]]"
sources:
---

# DragonScale メモリ

LLM Wiki vault のためのメモリ層設計。Heighway ドラゴン曲線に着想を得ている。4 つのメカニズム(fold オペレータ、決定論的ページアドレス、セマンティックタイリング、境界優先 autoresearch)が、LLM が維持する Wiki に成長・コンパクト化・整合性維持の原則を与える。ドラゴン曲線は設計の正当化装置であり、推論アーキテクチャではない。

> **ステータス: v0.4 2026-04-24。** 4 つのメカニズムすべてがオプトイン機能として出荷された。Phase 0(仕様)+ Phase 1(wiki-fold スキル、ドライラン検証済み)+ Phase 2(アドレス MVP)+ Phase 3(セマンティックタイリング)+ Phase 3.5/3.6(堅牢化)+ Phase 4(境界優先 autoresearch)。経過は Review History を参照。

---

## スコープ

DragonScale は **メモリアーキテクチャ** である。Wiki がどう成長し、どうコンパクト化され、ページにどう番地を振り、重複をどう確認するかを規定する。**検索、計画、推論アルゴリズムではない。** エージェントの推論は既存パターンを使う(Tree of Thoughts と BFS/DFS/ビーム探索、Yao et al. 2023)。

**正直な免責**: メモリ層の選択は推論に対して中立ではあり得ない。vault が何をどの順で表に出すかが、モデルが見るものを形作る。長文コンテキスト性能は位置依存があり(Liu et al. 2023, *Lost in the Middle*)、MemGPT の前提はページングポリシーがタスク成功率に影響することにある(Packer et al. 2023)。下記 4 メカニズムのうち 1 つ(境界優先 autoresearch)はアジェンダ制御へ明示的に踏み込む。意図的に含めており、その旨を明記する。

---

## 中核アナロジー

ドラゴン曲線の 4 つの性質を、隣接領域ですでに検証されているメモリシステムのパターンに対応付ける。これは *アナロジー* であって *同一性* ではない。

| ドラゴン曲線の性質 | メモリ上の類似物 | アナロジーの強さ |
|---|---|---|
| 紙折り再帰: `D_{n+1} = D_n · R · swap(reverse(D_n))` | 階層的ロールアップ/指数的ファンアウトを伴う実体化要約 | 弱い。指数的バッチ構造を共有するが、コンパクションのセマンティクスは共有しない。 |
| `n` のビットからターンが導出可能(正則紙折り列、OEIS A014577) | 組織的慣習としての決定論的ページアドレス(MVP は作成順カウンタであって真のコンテンツハッシュではない) | 弱い。決定論的アドレッシングはドラゴンとは独立に有用。 |
| タイリング/自己交差なし | 正規ホームの被覆: 1 概念、1 ページ | 中程度。重複検出 lint が機械的に強制する。 |
| 境界次元 ≈ 1.523627 対 内部次元 2 | エージェントの注意をフロンティアページに重み付け | 美的。フラクタル次元の数値そのものは荷重を担っていない。 |

ドラゴン曲線は「どのつまみをどう締めるか、なぜか」を決めるのに有用であり、特定のメカニズムが最適だと数学的に証明する道具ではない。

---

## メカニズム 1: fold オペレータ

ingest のバッチが終わった後に fold を実行する。バッチを要約するメタページを生成し、子をリンクし、index を更新する。fold はスタックする。レベル `k` の fold が十分蓄積すると、レベル `k+1` の fold がスーパーサマリーを生成する。

これは **階層的ロールアップ** であり、LSM ツリーのコンパクションに緩く似ているが、重要な違いがある。

**LSM コンパクションと共有する点:**
- レベルをまたいだ指数的バッチファンアウト(LevelDB の固定レベルサイズ比のように、leveled モードでは典型的にレベルあたり 10 倍)
- 書き込みごとの作業ではなく、定期的な統合

**LSM から継承しない点:**
- ソート済みキーのセマンティクスはない(ページはキー順ではなくセマンティックなアイデンティティを持つ)
- SSTable/memtable の区別なし、トゥームストーンなし、Bloom フィルタなし
- 書き込み増幅の算術なし、読み出し経路の高速化なし
- **fold は加法的**: 子はその場に残る。LSM コンパクションは書き直して削除する。DragonScale の fold はコンパクションよりも実体化ビューに近い。

**トリガオプション:**
- `2^k` エントリ数(k=4 なら 16 ログエントリごと)。実装が簡単。レベル算術が直截。ただしページサイズや新規性は無視。
- **適応的トリガ(本番では推奨)**: トークン予算(例: 未 fold バッチが N トークンを超えたら fold する)、新規性スコア(既存サマリーからの平均埋め込み距離)、または陳腐化年齢(直近 fold が T 日以上前)。Phase 1 では MVP としてエントリ数方式を実装する。適応的トリガは追走で導入する。

**不変条件:**
- 同一範囲に対して冪等(再実行は no-op)。
- 可逆(子は残る。fold は加法的)。
- レベル有界: エントリ数トリガ `2^k` のとき、fold 深度はリーフページの上に高々 `⌈log₂(N)⌉`。導出値であって経験値ではない。

---

## メカニズム 2: 決定論的ページアドレス

新しいページごとにフロントマターに安定した `address` フィールドを与える。Phase 2 MVP は単純な作成順カウンタを使う。

```yaml
address: c-000042
```

形式: `c-<6-digit-counter>`。`c-` は「creation-order counter(作成順カウンタ)」を意味する。ゼロ埋め。

**将来拡張**(文書化のみ、Phase 2 では未出荷):
- fold 相対パス: fold が存在するようになれば `f1.2/c-000042` のようにし、`f1.2` は fold ツリーの系譜を符号化する。
- コンテンツハッシュ接尾辞: ハッシュローテーションポリシーが決まれば `c-000042:h7f3c2`。

**Phase 2 MVP が与えるもの:**
- 一意性: カウンタは単調増加。削除済みページのアドレスは引退して再利用しない。
- 安定性: コンテンツ編集をまたいで変わらない。
- 決定性: `.vault-meta/address-counter.txt` のカウンタ状態から導出可能。
- 順序: 作成順序を保つ。

**与えないもの**(v0.1 で「コンテンツアドレッシング可能パス」と呼んでいたが誤解を招くため改名):
- **MVP にコンテンツアドレッシング性はない。** Phase 2 のアドレスはシーケンスカウンタであってコンテンツハッシュではない。このメカニズムを「コンテンツアドレッシング可能パス」から「決定論的ページアドレス」に改名したのは、実際に出荷されるものに対してより誠実だからだ。
- **プロンプトキャッシュの便益はない**(v0.1 → v0.2 ですでに修正済み)。Anthropic のドキュメントによれば、キャッシュヒットにはバイト単位で同一のプレフィックスが必要だ。フロントマターのアドレスフィールドが助けになるのは、フロントマター自体がキャッシュブロックの中にあり、かつバイト単位で同一であり続ける場合だけ。キャッシュヒットを駆動するのはアドレスではなく安定したプレフィックスだ。

**Phase 2 の除外項目**(すべて延期):
- Phase 2 以前のレガシーページのバックフィル(`l-` プレフィックスと専用カウンタを使う予定)。
- fold 系譜のビットプレフィックス(将来の fold-of-folds スキルからのコミット済み fold が必要)。
- コンテンツハッシュ接尾辞(ローテーションポリシー未解決、limitations 参照)。

**実装**(Phase 2、出荷済み):
- `scripts/allocate-address.sh`: flock 保護のアトミックなアロケータ。すべてのカウンタ読み書きはこのスクリプトを通す。`.vault-meta/address-counter.txt` への直接 Write/Edit は禁止(PostToolUse フックが発火する)。
- `skills/wiki-ingest/SKILL.md` → Address Assignment セクション: オプトイン機能検出。アロケーションをヘルパーに委譲。再 ingest 安定性のためパス→アドレスマッピングを `.raw/.manifest.json` の `address_map` に記録。
- `skills/wiki-lint/SKILL.md` → Address Validation セクション: 形式チェック、一意性チェック、カウンタドリフトチェック、address-map 整合性チェック。

**Lint 重要度モデル**(`skills/wiki-lint/SKILL.md` の Address Validation 挙動と一致):
- ロールアウト後のページ(フロントマター `created:` >= 2026-04-23、もしくは DragonScale 採用後に新規作成された任意のページ)でアドレスが欠けているものは **エラー**。これがサイレント退行のガード。
- レガシーページ(`created:` < 2026-04-23)でアドレスがないものは **情報通知**。オプションの `.vault-meta/legacy-pages.txt` マニフェストで、`created:` メタデータが間違いまたは欠落のページを猶予できる。
- メタページ(`_index.md`、`index.md`、`log.md`、`hot.md` など)と fold ページは完全に除外する。

---

## メカニズム 3: セマンティックタイリング lint

タイリング性が言うのは、同じ概念は 1 つの正規ページに住むべきということだ。`wiki-lint` の埋め込みベース重複チェックでこれを強制する。

**手順(キャリブレーションあり、推測ではない):**
1. すべてのページに対して埋め込みを計算する。デフォルトモデル: `http://127.0.0.1:11434` で動くローカルの ollama 上の `nomic-embed-text`。コスト: ローカルハードウェアの時間のみ(API 料金なし)。スクリプトは `--allow-remote-ollama` でリモート上書きをサポートする。リモートエンドポイントはプロバイダの API 料金を発生させ得る。
2. すべてのページペアの間でコサイン類似度を計算する。
3. **キャリブレーション**(初回のみ、初使用前に): vault 内 50〜100 ペアを duplicate/near/distinct でラベル付けし、各バンドの目標精度を最適化する閾値を見つける。
4. **デフォルトバンド**(キャリブレーション前に使用、その後精緻化):
   - `≥ 0.90`: ニアデュプリケート、lint エラー
   - `0.80 – 0.90`: レビューバケット、lint 警告
   - `< 0.80`: 別物、フラグなし
5. 自動マージは決して行わない。レビューリストを出力する。

**なぜ固定の 0.85 ではないか?** v0.1 は根拠なく 0.85 を使っていた。埋め込み文献で公表されている閾値は広い範囲にわたる(Sentence Transformers の `community_detection` のデフォルトは 0.75、Quora 重複キャリブレーションは 0.77〜0.83 付近、スパースモデルのデフォルトはまた異なる)。閾値はモデル、コーパス、目的に依存するため、キャリブレーションが必須だ。

---

## メカニズム 4: 境界優先 autoresearch

> **ステータス: 出荷済み(Phase 4、オプトイン)** 2026-04-24 時点。実装: `scripts/boundary-score.py`。統合: `skills/autoresearch/SKILL.md` の Topic Selection セクション B。テスト: `tests/test_boundary_score.py`。

境界ページ(出次数が入次数に対して高く、recency 重み付き)は vault のフロンティアだ。トピックなしで起動された `/autoresearch` はトップ 5 の境界ページを読み、研究候補として提示する。ユーザーは 1 つを選ぶ(または自由テキストでトピックを指定するか、すべて拒否してオリジナルの ask-user モードへフォールバックする)。

**式(厳密)**:

```
out_degree(p) = body 内で scoreable ページに解決するファイル名 stem の wikilink の重複なし数
in_degree(p)  = body に p への wikilink を含む scoreable ページの重複なし数
recency_weight(p) = exp(-days_since_updated / 30)      # 床なし、古いページは 0 に近づく
boundary_score(p) = (out_degree - in_degree) * recency_weight
```

**リンク解決**: ファイル名 stem のみ。`[[Foo]]` は vault のどこかにある `Foo.md` に解決する。フロントマターの `aliases:` で宣言されたエイリアスはパースしない。フォルダ修飾リンク(例: `[[notes/Foo]]`)も stem のみで解決する。これは一意なファイル名に対する Obsidian のデフォルト挙動と一致するが、完全なエイリアス解決は実装しない。

**Scoreable** = 以下のいずれによっても除外されないページ:
- フロントマター `type: meta` または `type: fold`
- ファイル名が `{_index.md, index.md, log.md, hot.md, overview.md, dashboard.md, Wiki Map.md, getting-started.md}` のいずれか
- パスプレフィックスが `wiki/folds/` または `wiki/meta/`
- シンボリックリンクや、解決後の対象が vault ルートを脱出するパス(スキャン時に拒否)

**コードブロックフィルタリング**: トリプルバックティック AND トリプルチルダのフェンスドコードブロックをスキップする。CommonMark 風の長さ追跡を行い、より長い開始フェンスがより短い内側のフェンスで閉じられないようにする。インデントコードブロック(4+ スペース)はフィルタしない。Obsidian の箇条書きが 4 スペースのインデントを使い、本物の wikilink を含むからだ。唯一の調整可能定数は `scripts/boundary-score.py:RECENCY_HALFLIFE_DAYS` を参照。

**正直なラベリング**: このメカニズムは **アジェンダ制御** であり、純粋なメモリではない。エージェントが次に何を調べるかを形作る。DragonScale に含めているのは、これがドラゴン曲線の境界アナロジーの直接的な帰結であり、fold と自然に組むからだ(直近 fold されたページは出次数が低く、フロンティアページは fold 前)。だが「メモリのみ、推論ではない」という枠組みでは覆えない。厳密にメモリ層のサブセットを望むユーザーはこのメカニズムを省くこと(単に `/autoresearch` をトピックなしで起動しないか、`scripts/boundary-score.py` を導入しない)。

**含まれないもの**:
- 自動トリガなし。`/autoresearch` は依然としてユーザー起動。
- 境界スコアの永続キャッシュなし。スコアリングは O(N * avg_links) で、起動ごとに新鮮な wiki/ 状態から走る。
- fold やアドレスとの統合なし。wikilink グラフ上の純粋なグラフ解析。
- ユーザー確認なしの自動トピック選択なし。ヘルパーは選択肢を提示し、ユーザーが選ぶ。

---

## 運用ポリシー(実装前に必須)

敵対的レビューが v0.1 でこれらのギャップを指摘した。各項目は対応するフェーズの出荷前に決定する必要がある。

| ポリシー | Phase 0 の立場 | 決定ポイント |
|---|---|---|
| **保持/GC** | 自動削除なし。ページは恒久的。 | vault が約 5000 ページを超えたら再考。 |
| **トゥームストーン** | なし。削除済みページは git revert で除く。 | 削除イベントが頻発するようになったら再考。 |
| **バージョニング** | git 履歴に依存し、vault 内バージョニングは行わない。 | アドレスハッシュローテーションポリシーが粗いバージョン信号を兼ねる。 |
| **矛盾する fold の競合解決** | メタページは両ソースを引用し、明示的な「conflict」コールアウトを置く。自動解決なし。 | Phase 1 仕様で必須。 |
| **並行性/原子性** | 単一書き手前提(同時 1 Claude セッション)。PostToolUse 自動コミットが直列化する。 | 多書き手ケースは延期。 |
| **メタページの来歴** | すべての fold ページは子と fold レベルを記載するフロントマターを含む必要がある。 | Phase 1 で強制必須。 |
| **アクセス制御** | スコープ外。これは単一ユーザー vault。 | 共有時のみ再考。 |

---

## Claude-Obsidian へのマッピング

| メカニズム | ステータス | 新規 | 拡張 |
|---|---|---|---|
| fold オペレータ | 出荷済み(Phase 1、ドライラン検証済み) | `skills/wiki-fold/` | `log.md` を読み、`wiki/folds/` に書き、コミット時に `index.md` を更新 |
| アドレスアンカー | 出荷済み(Phase 2、オプトイン) | `scripts/allocate-address.sh`、新フロントマターフィールド | `wiki-ingest`(割り当て)、`wiki-lint`(検証) |
| セマンティックタイリング | 出荷済み(Phase 2/3、オプトイン) | `scripts/tiling-check.py`、`.vault-meta/tiling-thresholds.json` | バンド閾値付きの `wiki-lint`、文書化されたキャリブレーション手順 |
| 境界優先 | 出荷済み(Phase 4、オプトイン) | `scripts/boundary-score.py`、`tests/test_boundary_score.py` | `skills/autoresearch/SKILL.md` の Topic Selection セクション B、`commands/autoresearch.md` のトピックなし経路 |

既存の hot → index → ドメイン → ページの階層はすでにスケールをまたぐ自己相似性を実装している。DragonScale 以前にこの vault が持っていた唯一のドラゴン曲線的性質はそれだ。

---

## 代替案より優れる理由

| パターン | 提供物 | DragonScale が加えるもの |
|---|---|---|
| MemGPT の仮想コンテキスト(2 段ページング) | メインコンテキスト ↔ 外部コンテキストのスワップ | 2 階層を超えるレベル、明示的な fold トリガ、重複検出 lint |
| 純粋な LSM コンパクション | 指数的書き込みスループット | セマンティック層のメカニズム(タイリング、境界)、破壊的マージではなく加法的ロールアップ |
| アドホックな `/save` | 人手起動のファイリング | ルールベースの fold ケイデンス |
| ベクトルのみの RAG | 取得 | 正規ホーム構造、系譜アドレス |

DragonScale は隣接システムで検証されたパターンを構成する。LSM の *バッチング*(データベース)、MemGPT の *ページング*(エージェント)、Anthropic の *キャッシュ順序*(プロンプトエンジニアリング)、埋め込みの *重複検出*(ナレッジグラフ)。

---

## 既知の制約(v0.3)

- **スケールでは未検証。** 4 メカニズムすべて理論的、数千ページ vault でのテスト未実施。
- **fold ケイデンスはつまみであって定理ではない。** `k=4` は出発点の推測。適応的トリガの方が良い可能性が高い。
- **アドレス安定性は未解決。** 編集時のハッシュローテーションは既知問題、延期。
- **境界優先はスコープを越える。** 警告付きで含めており、こっそりではない。
- **キャリブレーション負荷。** タイリングは初回ラベリングパスを必要とする。それなしではデフォルトのみ。

---

## 一次ソース

2026-04-23 に一次ソースに対して検証済み。**タグ付けの範囲**: 下記の特定の数値、式、命名されたパターンは、直接引用可能なときに **[sourced]**、引用素材から導出可能なときに **[derived]**、特定のソースに依らない推論時に **[conjecture]** とタグ付けする。**タグなし**(読者は解釈的合成として扱うべき): 本文の枠組み的な文(「検証されたパターンを構成する」「自己相似性はすでに存在する」、4 メカニズムを結びつける設計理由)など。これらは編集的判断であってソースに裏付けられたものではない。

**ドラゴン曲線の数学 [sourced]**
- 境界次元 `2·log₂(λ)`、ここで `λ³ − λ² − 2 = 0`、結果 1.523627086: [Dragon curve, Wikipedia](https://en.wikipedia.org/wiki/Dragon_curve)
- 紙折り構成と OEIS A014577: [Regular paperfolding sequence, Wikipedia](https://en.wikipedia.org/wiki/Regular_paperfolding_sequence)、[OEIS A014577](https://oeis.org/A014577)
- タイリングと rep-tile: [Wolfram Demonstrations: Tiling Dragons and Rep-tiles of Order Two](https://demonstrations.wolfram.com/TilingDragonsAndRepTilesOfOrderTwo/)

**LSM ツリー [sourced]**
- レベルサイズ比とコンパクションのセマンティクス: [RocksDB Compaction wiki](https://github.com/facebook/rocksdb/wiki/Compaction)、[RocksDB Tuning Guide](https://github.com/facebook/rocksdb/wiki/RocksDB-Tuning-Guide)、[How to Grow an LSM-tree? (2025)](https://arxiv.org/abs/2504.17178)
- LevelDB の 10 倍レベル比: 上記 arXiv 論文で参照。*典型値* として扱い、必須ではない。

**LLM メモリアーキテクチャ [sourced]**
- OS 由来のページング: [MemGPT: Towards LLMs as Operating Systems (Packer et al. 2023)](https://arxiv.org/abs/2310.08560)
- 位置感受性: [Lost in the Middle (Liu et al. 2023)](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long)
- ノートベースのエージェント記憶: [A-Mem (2025)](https://arxiv.org/abs/2502.12110)

**プロンプトキャッシュ [sourced]**
- バイト単位同一プレフィックス要件、ブレークポイント機構、TTL オプション: [Anthropic Prompt Caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

**埋め込み閾値 [sourced]**
- Sentence Transformers のデフォルトとキャリブレーション例: [Sentence Transformers util](https://sbert.net/docs/package_reference/util.html)、[SBERT evaluation docs](https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html)

**推論探索(スコープ外、スコープ境界の正当化のためのみ引用)[sourced]**
- [Tree of Thoughts (Yao et al. 2023)](https://arxiv.org/abs/2305.10601)

**この文書中で [conjecture] とマークされる項目:**
- fold ケイデンスの開始値 `k=4`/`k=5`(経験的調整が必要)
- 全 vault 埋め込みパス時間 `~30s`(計測が必要)
- `boundary_score` 式の正確な重み付け(妥当な開始形だが、検索メトリクスでは未検証)

**[derived] とマークされる項目:**
- `⌈log₂(N)⌉` fold 深度上限(エントリ数トリガから自明に導出可能)
- キャリブレーション前のデフォルトタイリングバンド `{≥0.90, 0.80-0.90, <0.80}`(Sentence Transformers 例の引用範囲から内挿、構成上の最適性は保証されない)

---

## レビュー履歴

**v0.1(2026-04-23、初稿)**: Wikipedia、arXiv、Anthropic ドキュメントへの検証パスを経て執筆。4 メカニズムを提案。

**v0.4(2026-04-24、Phase 4 出荷)**: メカニズム 4(境界優先 autoresearch)を `scripts/boundary-score.py` として実装。`tests/test_boundary_score.py` でパース、recency 重み、wikilink 抽出(フェンス長 + チルダ + インデントブロックテスト付き)、グラフ構築(自己ループ/未解決/メタターゲット除外)、シンボリックリンク拒否、CLI 表面(`--top`、`--page`、`--json`)をカバー。`skills/autoresearch/SKILL.md` にオプトイン Topic Selection モードとして統合。明示的なヘルパー失敗フォールバック付き。仕様の "NOT IMPLEMENTED" マーカーを除去。厳密スコアリング式(recency 床なし)、ファイル名 stem のみ解決の開示、スコープ、「含まれないもの」セクションを追加。Phase 4 前堅牢化として Phase 3.6 を並行出荷(5 件の修正: `--report` パス封じ込め、ロールアウトベースライン、AGENTS.md 整合性、wiki-ingest .raw 矛盾、install-guide バージョン)。

**v0.3(2026-04-23、Phase 2 整合)**: メカニズム 2 を `wiki-ingest` と `wiki-lint` で実出荷された Phase 2 MVP に合わせて再執筆。「Content-Addressable Paths」から「Deterministic Page Addresses」に改名(MVP は作成順カウンタであってコンテンツハッシュではない)。fold 系譜ビットとコンテンツハッシュ接尾辞の拡張経路を文書化、両者とも明示的に延期。

**v0.2(2026-04-23、敵対的レビュー後)**: `codex exec` 敵対的レビュー後。7 件の批評をすべて受け入れた。

1. *LSM「構造的に同一」* → 「階層的ロールアップに緩く類似」に弱め、継承しない性質を明示列挙。
2. *プロンプトキャッシュのアドレス便益* → 強い主張を撤回し、組織的慣習に絞る。
3. *0.85 閾値* → キャリブレーション手順とバンド付きデフォルトに置き換え。
4. *2^k ケイデンス* → 実装の便宜として正当化、本番では適応的トリガを推奨と注記。
5. *スコープ境界の矛盾* → 認め、境界優先をアジェンダ制御として明示ラベル化。
6. *本番機構の欠如* → 運用ポリシーセクションを追加(保持、バージョニング、競合解決、並行性、来歴)。
7. *未検証の主張* → 特定の数値、式、命名されたパターンを [sourced]、[derived]、[conjecture] でタグ付け。本文の編集的合成は明示的にタグなしとし(Primary Sources のスコープ注を参照)。

---

## 関連

このパターンが拡張する広範な枠組みは [[LLM Wiki Pattern]] を参照。
DragonScale の前提となる永続状態の理由は [[Compounding Knowledge]] を参照。
レベル 0 の手動 fold である既存の 500 語セッションコンテキストは [[Hot Cache]] を参照。
知的系譜は [[Andrej Karpathy]] を参照。
