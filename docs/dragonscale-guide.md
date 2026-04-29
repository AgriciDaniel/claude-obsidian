# DragonScale Memory ガイド

> 🇯🇵 **日本語ローカライズ版。** 上流の英語ドキュメントを日本語化したもの。コード・コマンド・ファイル名は英語のまま。

DragonScale Memory は `claude-obsidian` のオプション拡張です。ログのロールアップ、安定したページアドレス、重複ページの lint、フロンティアトピックの提案について、控えめなヘルパー群を追加します。まずは [docs/install-guide.md](./install-guide.md) から始めてください。設計仕様と背景については [wiki/concepts/DragonScale Memory.md](../wiki/concepts/DragonScale%20Memory.md) を参照してください。

このページは `v1.6.0` で出荷された挙動に近い内容に保たれています。セットアップが何を作成するか、各メカニズムが実際に何をするか、何を必要とするか、リポジトリをアンインストールせずに安全に無効化する方法を説明します。

## DragonScale とは何か

### スコープとオプトイン状態

DragonScale は wiki 向けのメモリレイヤー拡張です。ロールアップ、決定論的なページ ID、重複検出、`/autoresearch` 用のオプトイントピック選択パスを 1 つカバーします。ベースの vault では必須ではありません。

`bash bin/setup-dragonscale.sh` を一度も実行しなければ、ベースインストールと元のスキル挙動はそのまま残ります。リポジトリは特徴検出を使うため、DragonScale はハード依存ではなくオプションのままにできます。

コンセプトページはこのガイドより範囲が広いです。このガイドは運用向けです。仕様と実装が細部で異なる場合は、日々の挙動については出荷されたスクリプトとスキルを優先してください。

### 1.6.0 で出荷されるもの

バージョン `1.6.0` では、4 つの DragonScale メカニズムすべてがオプトイン機能として出荷されます。

- メカニズム 1、Fold Operator: `skills/wiki-fold/`
- メカニズム 2、決定論的ページアドレス: `scripts/allocate-address.sh` および `wiki-ingest` と `wiki-lint` の統合
- メカニズム 3、Semantic Tiling Lint: `scripts/tiling-check.py` および `wiki-lint` の統合
- メカニズム 4、Boundary-First Autoresearch: `scripts/boundary-score.py` および `skills/autoresearch/SKILL.md` の Topic Selection ロジック

リリース履歴は `CHANGELOG.md`、クイックスタート視点は [docs/install-guide.md](./install-guide.md)、完全な設計コンテキストは [wiki/concepts/DragonScale Memory.md](../wiki/concepts/DragonScale%20Memory.md) を参照してください。

## 有効化する前に

### ベースインストールの要件

DragonScale はアドオンであり、ベースセットアップの代替ではありません。まず [docs/install-guide.md](./install-guide.md) に従って通常の vault インストールを行ってください。

最低限必要なもの:

- リポジトリをクローンするか、プラグインをインストールする
- `bash bin/setup-vault.sh` を実行する
- フォルダを Obsidian vault として開く
- `/wiki` を使ってスキャフォルドするか、セットアップを続行する

DragonScale セットアップスクリプトは、vault パスというオプション引数を 1 つ受け取ります。

```bash
bash bin/setup-dragonscale.sh
```

```bash
bash bin/setup-dragonscale.sh /path/to/vault
```

パスを省略すると、`bin/` から推論されたリポジトリルートを使用します。

### 共通の前提条件: flock

`flock` は共通の前提条件です。メカニズム 2 は `scripts/allocate-address.sh` の中で `.vault-meta/.address.lock` を保護するために直接使用します。メカニズム 3 はキャッシュ I/O 前後で `.vault-meta/.tiling.lock` を保護するために、Python から flock を使用します。

クイックチェック:

```bash
command -v flock
```

何も出力されない場合、DragonScale に依存する前に `flock` をインストールしてください。Linux では通常すでに存在します。macOS では `util-linux` から取得することが多いです。

`flock` がない場合、セットアップはファイルを作成できますが、アドレスアロケーターと tiling キャッシュのパスは信頼できません。これはブロッカーとして扱ってください。

### メカニズム 3 の追加前提条件: python3、ollama、nomic-embed-text

メカニズム 3 はローカル埋め込みスタック全体を必要とする唯一のメカニズムです。`python3`、`ollama`、そして ollama に取り込んだ `nomic-embed-text` モデルが必要です。

便利なチェック:

```bash
command -v python3
```

```bash
curl -sS http://127.0.0.1:11434/api/version
```

```bash
ollama pull nomic-embed-text
```

セットアップスクリプトはこれらをインストールしません。チェックして状態を報告するだけです。メカニズム 4 は `python3` を必要としますが、ollama は不要です。メカニズム 1 と 2 はどちらも不要です。

### オプション依存が欠けている場合の挙動

DragonScale はクリーンに失敗するか、no-op で動作するように設計されています。

`python3` がない場合:

- メカニズム 3 は実行できない
- メカニズム 4 は実行できない
- メカニズム 1 と 2 は引き続き動作する

ollama に到達できない場合、`scripts/tiling-check.py` は `10` で終了します。ollama には到達できるが `nomic-embed-text` がインストールされていない場合、`11` で終了します。`wiki-lint` はこれらを semantic tiling のスキップ条件として扱い、lint フローの残りを壊す理由とはしないことが期待されます。

boundary ヘルパーが失敗した場合、`/autoresearch` は通常のユーザーへトピックを尋ねるパスにフォールバックします。候補リストを強制せず、トピックを即興で作ることもしません。

DragonScale セットアップが一度も実行されていない場合、`wiki-ingest` と `wiki-lint` は DragonScale 非対応の挙動を維持します。

## セットアップ

### bin/setup-dragonscale.sh の実行

実行:

```bash
bash bin/setup-dragonscale.sh
```

このスクリプトは冪等です。再実行しても安全で、すでに作成したランタイムファイルを上書きしません。

状態をプロビジョニングする前に、以下を検証します:

- `scripts/allocate-address.sh`
- `scripts/tiling-check.py`
- `skills/wiki-fold/SKILL.md`

これらのいずれかが欠けている場合、セットアップは停止し、プラグインを再インストールするように指示します。

セットアップが行うこと:

- `scripts/allocate-address.sh` を実行可能にする
- `scripts/tiling-check.py` を実行可能にする
- 必要に応じて `.vault-meta/` を作成する
- アドレス、tiling、レガシーベースラインの状態ファイルが欠けていれば作成する
- `.raw/.manifest.json` がなければ作成する
- 最後にサニティチェックを実行する

セットアップが行わないこと:

- ollama のインストール
- `nomic-embed-text` の取得
- 古いページへのアドレスのバックフィル
- fold の実行
- semantic tiling の実行
- 既存の wiki ページの書き換え

### 作成されるファイルと状態

セットアップは少量のランタイム状態をプロビジョニングします。

`.vault-meta/` には次が作成されます:

- `address-counter.txt`
- `tiling-thresholds.json`
- `legacy-pages.txt`

`.raw/` には次が作成されます:

- `.manifest.json`

`address-counter.txt` は `1` から始まるので、まっさらな vault で次に予約されるページアドレスは `c-000001` になります。

`tiling-thresholds.json` は `error: 0.90`、`review: 0.80`、`calibrated: false` でシードされます。これらは控えめなシードバンドであり、あなたの vault に対してキャリブレートされた真実ではありません。

`legacy-pages.txt` にはロールアウトマーカーのコメントが付きます:

```text
# rollout: YYYY-MM-DD
```

`wiki-lint` はそのベースラインを使い、アドレス強制のためにレガシーページとロールアウト後ページを区別します。

`.raw/.manifest.json` は空の `sources` と `address_map` オブジェクトで始まります。ingest スキルがそのファイルを保守します。`.raw/` 配下のソースドキュメントは不変のままです。

### セットアップの検証方法

セットアップスクリプトはすでにサニティチェックを行いますが、いくつかを自分で確認しておくと有用です。

予約せずに次のアドレスを確認:

```bash
./scripts/allocate-address.sh --peek
```

ランタイム状態が存在することを確認:

```bash
ls -1 .vault-meta
```

埋め込みを計算せずに tiling の準備状況を確認:

```bash
python3 ./scripts/tiling-check.py --peek
```

boundary ヘルパーを確認:

```bash
python3 ./scripts/boundary-score.py --top 5
```

vault が小さい、もしくは密に統合されている場合、boundary ヘルパーはポジティブスコアのフロンティアページを 1 つも報告しないかもしれません。それでも妥当な実行結果です。

## メカニズム 1: Fold Operator

### 何をするか

fold オペレーターはログのロールアップです。`wiki/log.md` から最新の `2^k` 件のエントリを読み、`wiki/folds/` 配下に extractive な fold ページを生成します。

fold は加算的です。子エントリを削除、移動、書き換えしません。fold は extractive です。出力中のすべての成果やテーマは、子のログエントリにトレース可能でなければなりません。

現在出荷されているスキルは意図的に狭く設計されています。生のログエントリに対するフラットな fold をサポートします。コンセプト仕様には積み重ねた fold についての記述がありますが、階層的な fold-of-folds の挙動は現スキルのスコープ外です。

特定のレンジに対する fold ID は決定論的です:

```text
fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}
```

これは構造的冪等性を与えます。完全に同じ fold がすでに存在する場合、スキルは重複書き込みではなく停止することが期待されます。

### いつ使うか

ログにまとまった作業バッチが蓄積し、生のエントリ列よりスキャンしやすいチェックポイントページが欲しいときに fold を使います。

典型的なケース:

- 1 つのテーマで複数回 ingest した後
- 集中的な研究セッションを終えた後
- 平坦な `wiki/log.md` が長くなりすぎて使いにくくなる前

fold をガベージコレクションとして扱わないでください。要約はしますが、削除によるコンパクションはしません。

コマンド例:

```text
fold the log, dry-run k=3
```

これは `2^3 = 8` 件のエントリに対する dry-run を要求します。

### Dry-run と commit モード

dry-run はデフォルトで stdout のみです。これはリポジトリに書き込み用の PostToolUse フックがあるため重要です。

dry-run モードでは:

- ファイルは書き込まれない
- 自動コミットフックは発火しない
- 提案された fold の内容が端末出力で得られる

commit モードでは:

- fold ページが `wiki/folds/` に書き込まれる
- `wiki/index.md` が更新される
- `wiki/log.md` に新しい fold エントリが追加される

スキルドキュメントは commit モードで 3 つの別々の書き込み操作を想定しているため、フックからの 3 回の自動コミットは正常です。

commit コマンド例:

```text
fold the log, commit k=3
```

まず dry-run を実行してください。fold の内容が正しそうな場合のみ commit してください。

DragonScale をアンインストールせずにメカニズム 1 を無効化するには、`wiki-fold` の呼び出しをやめてください。既存の fold ページは vault に残しても、もう不要であれば手動で削除しても構いません。

## メカニズム 2: 決定論的ページアドレス

### アドレス形式とロールアウトポリシー

メカニズム 2 は安定した frontmatter アドレスを割り当てます。出荷形式は次の通り:

```yaml
address: c-000042
```

`c-` は creation-order カウンターを意味します。数値部分は 6 桁にゼロパディングされます。これはコンテンツハッシュではありません。仕様は明示的に、出荷されるアドレスは決定論的かつ安定しているが、content-addressable ではないと述べています。

ロールアウトベースラインは `2026-04-23` です。DragonScale 採用後、ロールアウト後の非メタページにはアドレスが付くことが期待されます。レガシーページは、意図的なバックフィルを行うまで除外されます。

ヘルパーには 3 つの実モードがあります:

```bash
./scripts/allocate-address.sh
```

```bash
./scripts/allocate-address.sh --peek
```

```bash
./scripts/allocate-address.sh --rebuild
```

デフォルトモードは次のアドレスを予約して出力します。`--peek` は読み取り専用です。`--rebuild` は観測された最大の `c-NNNNNN` からカウンターを再計算します。

コマンド例:

```bash
./scripts/allocate-address.sh --peek
```

### ingest と lint の使い方

`wiki-ingest` は `./scripts/allocate-address.sh` が実行可能で、かつ `./.vault-meta` が存在する場合にのみアドレス割り当てを有効にします。両方の条件が真であれば、新しい非メタページの frontmatter に `address:` が付きます。そうでない場合、ingest はアドレスなしで進行します。

`wiki-lint` は `./scripts/allocate-address.sh` が実行可能で、かつ `./.vault-meta/address-counter.txt` が存在する場合にのみアドレス検証を有効にします。これらの条件が満たされている場合、lint はアドレス形式、一意性、`--peek` に対するカウンター整合性、ロールアウト後ページのアドレス欠落、`.raw/.manifest.json` の `address_map` 整合性をチェックします。

ここでは single-writer ルールが重要です。アロケーターは `flock` を使いますが、ingest スキルは依然として Phase 2 が single-writer 専用と述べています。アドレスを割り当てる複数のセッションやサブエージェントから並行 ingest を実行しないでください。

スキルドキュメントの厳格なルールを 1 つ繰り返す価値があります。`.vault-meta/address-counter.txt` を直接編集しないでください。`scripts/allocate-address.sh` を通してのみ変更してください。

アンインストールせずにメカニズム 2 を無効化する方法:

1. アドレス割り当てに依存する ingest の実行をやめる
2. 機能検出をオフにしたい場合は `.vault-meta/` を削除する
3. `./scripts/allocate-address.sh` の使用をやめる

既存の `address:` フィールドはページに残せます。機能を無効化すると、不活性なメタデータになります。

## メカニズム 3: Semantic Tiling Lint

### 何をチェックするか

メカニズム 3 は埋め込みベースの重複ページ検出器です。`wiki/` 配下の markdown ファイルをスキャンし、次を除外します:

- `wiki/folds/`
- `wiki/meta/`
- `index.md`、`log.md`、`hot.md`、`overview.md`、`dashboard.md`、`Wiki Map.md`、`getting-started.md` などの一般的なメタファイル名
- `type: meta` のファイル
- `type: fold` のファイル
- vault ルートを抜け出すシンボリックリンクやパス

含まれる各ページに対して 1 つの埋め込みを計算し、コサイン類似度でペアを比較し、候補のオーバーラップをバンドで出力します。

デフォルトのバンド:

- `>= 0.90` を error とする
- `0.80 - 0.90` を review とする
- `< 0.80` を pass とする

ヘルパーが自動でページをマージすることはありません。レビュー候補を報告するだけです。

コマンド例:

```bash
python3 ./scripts/tiling-check.py --peek
```

これは埋め込みを計算せずに構造化された診断結果を返します。

### ローカル埋め込みの要件

デフォルトでは、ヘルパーは `http://127.0.0.1:11434` のローカル ollama エンドポイントだけを信頼します。リモート ollama エンドポイントは、ページ本文が埋め込み入力として送信されるため、明示的なオーバーライドフラグが必要です。

リモートオーバーライドの例:

```bash
python3 ./scripts/tiling-check.py --allow-remote-ollama --peek
```

通常の準備完了パスはローカルです:

1. `python3` がインストールされている
2. ollama がローカルホストで到達可能
3. ollama に `nomic-embed-text` がインストールされている

重要な終了コード:

- `0` 成功
- `10` ollama に到達不可
- `11` モデル欠落

`wiki-lint` はこれらをスキップ条件として扱うように書かれています。

### キャリブレーションと no-op の挙動

出荷されるしきい値は控えめなシードであり、キャリブレートされた真実ではありません。スキルドキュメントは vault ごとに 1 度の手動キャリブレーションパスを推奨しています。それを行うまでは、偽陰性と偽陽性の両方が出ることを想定してください。

ヘルパーには意図的な no-op 挙動もあります。ollama かモデルが欠けている場合、スキップコードで終了します。結果を捏造することはありません。

便利なコマンド:

```bash
python3 ./scripts/tiling-check.py --peek
```

```bash
python3 ./scripts/tiling-check.py --rebuild-cache
```

```bash
python3 ./scripts/tiling-check.py --report wiki/meta/tiling-report-YYYY-MM-DD.md
```

`--report` は実装済みで、vault 内にパスが限定されます。保存されたレポートが欲しいときに使ってください。準備状況と診断だけが欲しいときは `--peek` を使ってください。

アンインストールせずにメカニズム 3 を無効化する方法:

1. `python3 ./scripts/tiling-check.py` の実行をやめる
2. `wiki-lint` の semantic-tiling パスの使用をやめる
3. 不要であれば ollama やモデルをプロビジョニングしない

`.vault-meta/` はメカニズム 2、3、4 の共有ゲートです。メカニズム 3 だけを無効化するために削除しないでください。アドレス割り当てと boundary-first autoresearch も同時に無効になってしまいます。tiling キャッシュは `.vault-meta/` 配下にありますが、ヘルパーが呼ばれない限り不活性です。

## メカニズム 4: Boundary-First Autoresearch

### 何をするか

メカニズム 4 は wiki グラフのフロンティアページにスコアを付けます。出荷される計算式は次の通り:

```text
boundary_score(p) = (out_degree(p) - in_degree(p)) * recency_weight(p)
```

実際には、高スコアのページはスコア対象の多くのページに外向きにリンクし、流入リンクは比較的少なく、フロンティアらしさを保つ程度に最近更新されています。

ヘルパーは `wiki/**/*.md` を読み、wikilink グラフを構築し、ランク付けされた結果を stdout または JSON で出力します。意図的に stdout 専用です。tiling ヘルパーと違い、`--report PATH` モードはありません。

コマンド例:

```bash
python3 ./scripts/boundary-score.py --json --top 5
```

これは autoresearch スキルが候補生成のために使う、まさにそのコマンドです。

### Agenda コントロールの注意点

この注意点は仕様とスキルドキュメントの両方で明示されています。

これは agenda コントロールであり、純粋なメモリではありません。

メカニズム 4 は単に vault を記述するだけではありません。エージェントが次に何を調査する可能性が高いかに影響を与えます。これはメモリと計画の境界をまたいでいます。

プロジェクトはこれをオプトインに保ち、正直にラベル付けしています。厳密にメモリレイヤーのサブセットだけが欲しい場合、このパスを省略してください。トピックなしで `/autoresearch` を使わない、もしくは boundary scorer をセットアップして呼び出さないでください。

### メカニズム 4 の有無による /autoresearch の挙動

メカニズム 4 が利用可能で、かつ `/autoresearch` がトピックなしで呼ばれた場合のみ、スキルは:

1. `scripts/boundary-score.py` の存在を確認する
2. `./.vault-meta` の存在を確認する
3. `python3` の存在を確認する
4. `./scripts/boundary-score.py --json --top 5` を実行する
5. 上位のフロンティアページを候補トピックとして提示する
6. ユーザーが選ぶ、フリーテキストで上書きする、辞退する、のいずれかを選択させる

ヘルパーが非ゼロで終了したり、無効な JSON を返したり、空の `results` 配列を返したりすると、スキルはフォールバックします。

メカニズム 4 がない場合、もしくはフォールバック後、`/autoresearch` は単に次を尋ねます:

```text
What topic should I research?
```

ヘルパーは提案するだけです。決めるのは依然としてユーザーです。

アンインストールせずにメカニズム 4 を無効化する方法:

1. `python3 ./scripts/boundary-score.py` の実行をやめる
2. 明示的なトピックを付けて `/autoresearch [topic]` を使う
3. フロンティア提案が不要であれば、トピックなしの `/autoresearch` パスを避ける

`.vault-meta/` はメカニズム 2、3、4 の共有ゲートです。メカニズム 4 だけを無効化するために削除しないでください。スコアラー自体は読み取り専用で共有状態を使いません。無効化とは呼び出さないことを意味します。

## 運用ポリシー

### Single-writer ルール

DragonScale はアドレス割り当てパスについて単一の書き手を仮定します。アロケーターは flock で保護されており、これがカウンターを単純な競合から守ります。wiki 全体を安全な複数書き手システムに変えるわけではありません。

ingest スキルはここで明示的です。アドレスを割り当てる複数の Claude セッションやサブエージェントから並行 ingest を実行しないでください。

安全な運用ポリシー:

- 一度に有効な ingest 書き手は 1 つ
- 一度に有効なアドレスアロケーターパスは 1 つ
- カウンター状態への直接の手動編集は行わない

メカニズム 1 は人間が起動するもので、直列化が容易です。メカニズム 3 はキャッシュ I/O のためにロックを使います。メカニズム 4 は読み取り専用です。

### 機能検出と graceful フォールバック

DragonScale は仮定するのではなく、機能検出されることを意図しています。

`wiki-ingest` はアロケーターが実行可能で `.vault-meta/` が存在する場合のみアドレスを割り当てます。
`wiki-lint` はアロケーターが存在し `.vault-meta/address-counter.txt` が存在する場合のみアドレスを検証します。
`wiki-lint` はヘルパーが存在し `python3` が利用可能な場合のみ semantic tiling を実行し、`--peek` から準備状況を解釈します。
`autoresearch` はヘルパーが存在し、`.vault-meta/` が存在し、`python3` が存在する場合のみ boundary-first 選択を使います。

これらの条件が満たされない場合、リポジトリは以前の挙動にフォールバックします。これが意図された運用姿勢です。

## トラブルシューティング

### flock の欠落

`flock` がない場合、まずそれを修正してください。症状にはアドレス割り当てパスの不安全化や、tiling キャッシュパスのロック失敗などが含まれます。

確認:

```bash
command -v flock
```

存在しない場合、システム上で flock を提供するパッケージをインストールし、再実行:

```bash
bash bin/setup-dragonscale.sh
```

`.vault-meta/address-counter.txt` を直接編集して回避しないでください。

### ollama またはモデルの欠落

これはメカニズム 3 のみをブロックします。DragonScale の他の部分はブロックしません。

ollama の到達可能性を確認:

```bash
curl -sS http://127.0.0.1:11434/api/version
```

tiling の準備状況を確認:

```bash
python3 ./scripts/tiling-check.py --peek
```

ヘルパーが `10` で終了したら、ollama に到達できません。`11` で終了したら、モデルを取得:

```bash
ollama pull nomic-embed-text
```

その後再実行:

```bash
python3 ./scripts/tiling-check.py --peek
```

メカニズム 4 は ollama を必要としません。boundary-first autoresearch だけが欲しい場合は `python3` で十分です。

### 安全なロールバック / 無効化パス

DragonScale をオフにするためにリポジトリをアンインストールする必要はありません。やりたいことに合った最小のロールバックを使ってください:

- メカニズム 1: `wiki-fold` の呼び出しをやめる。共有状態は使わない。
- メカニズム 2: `./scripts/allocate-address.sh` の使用をやめる。既存の `address:` frontmatter フィールドはプレーンなコンテンツとして残る。
- メカニズム 3: `python3 ./scripts/tiling-check.py` の実行をやめ、`wiki-lint` の semantic-tiling パスの呼び出しをやめる。`.vault-meta/` 配下のキャッシュは未使用なら不活性。
- メカニズム 4: `python3 ./scripts/boundary-score.py` の実行をやめ、トピックなしの `/autoresearch` パスを避ける。スコアラーは読み取り専用で、無効化は呼び出さないこと。

`.vault-meta/` はメカニズム 2、3、4 の共有ゲートです。これを削除するとひとつではなく 3 つすべてが同時に無効になります。

セットアップベースのメカニズム全体に対する DragonScale 機能検出を一度に無効化したい場合、`.vault-meta/` を削除します:

```bash
rm -rf .vault-meta
```

その後、DragonScale 固有のヘルパーやスキルの呼び出しをやめてください。これは通常の wiki コンテンツをそのまま残します。fold ページは削除されず、frontmatter から既存の `address:` フィールドも除去されません。手動でクリーンアップしない限り、これらはプレーンなコンテンツとして残ります。

後で DragonScale を戻したくなったら、再実行してください:

```bash
bash bin/setup-dragonscale.sh
```
