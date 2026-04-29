---
name: obsidian-bases
description: "Obsidian Bases(`.base` ファイル)を作成・編集する: Vault ノートに対する動的テーブル、カードビュー、リストビュー、フィルタ、数式、サマリーを提供する Obsidian のネイティブデータベース層。応答は日本語(プロジェクト CLAUDE.md の言語ポリシー参照)。トリガー(日本語): base を作成、base ファイル追加、obsidian bases、ビュー作成、ノートをフィルタ、数式、データベースビュー、動的テーブル、タスクトラッカー base、読書リスト base。Triggers (English): create a base, add a base file, obsidian bases, base view, filter notes, formula, database view, dynamic table, task tracker base, reading list base."
allowed-tools: Read Write
---

# obsidian-bases: Obsidian のデータベース層

Obsidian Bases(2025 年公開)は Vault ノートをクエリ可能で動的なビュー(テーブル、カード、リスト、マップ)に変えます。`.base` ファイルで定義。プラグイン不要、Obsidian のコア機能。

> **言語ルール**: ビューの `name:`、`displayName:`、テーブル列ラベル、説明的テキストは日本語で書く。フィルタ式・数式・JSON キー・関数名・列挙値(`type: table` など)は英語のまま。

**正規リファレンス**: kepano/obsidian-skills プラグインがインストールされていれば、その正規 obsidian-bases スキルを優先。なければ下のリファレンスを使用。公式ドキュメント: https://help.obsidian.md/bases/syntax

---

## ファイル形式

`.base` ファイルは有効な YAML を含む。ルートキーは `filters`, `formulas`, `properties`, `summaries`, `views`。

```yaml
# グローバルフィルタ: すべてのビューに適用
filters:
  and:
    - file.hasTag("wiki")
    - 'status != "archived"'

# 計算プロパティ
formulas:
  age_days: '(now() - file.ctime).days.round(0)'
  status_icon: 'if(status == "mature", "✅", "🔄")'

# プロパティパネル用の表示名上書き
properties:
  status:
    displayName: "ステータス"
  formula.age_days:
    displayName: "経過日数"

# 1 つ以上のビュー
views:
  - type: table
    name: "全ページ"
    order:
      - file.name
      - type
      - status
      - updated
      - formula.age_days
```

---

## フィルタ

フィルタはどのノートを表示するかを選ぶ。グローバルまたはビュー単位で適用。

```yaml
# 単一文字列フィルタ
filters: 'status == "current"'

# AND: すべて真
filters:
  and:
    - 'status != "archived"'
    - file.hasTag("wiki")

# OR: いずれか真
filters:
  or:
    - file.hasTag("concept")
    - file.hasTag("entity")

# NOT: マッチを除外
filters:
  not:
    - file.inFolder("wiki/meta")

# ネスト
filters:
  and:
    - file.inFolder("wiki/")
    - or:
        - 'type == "concept"'
        - 'type == "entity"'
```

### フィルタ演算子

`==` `!=` `>` `<` `>=` `<=`

### 便利なフィルタ関数

| 関数 | 例 |
|----------|---------|
| `file.hasTag("x")` | タグ `x` を持つノート |
| `file.inFolder("path/")` | フォルダ内のノート |
| `file.hasLink("Note")` | Note にリンクしているノート |

---

## プロパティ

3 種類:
- **ノートプロパティ**: frontmatter から: `status`, `type`, `updated`
- **ファイルプロパティ**: メタデータ: `file.name`, `file.mtime`, `file.size`, `file.ctime`, `file.tags`, `file.folder`
- **数式プロパティ**: 計算: `formula.age_days`

---

## 数式

`formulas:` で定義。`order:` と `properties:` では `formula.name` で参照。

```yaml
formulas:
  # 作成からの日数
  age_days: '(now() - file.ctime).days.round(0)'

  # 日付プロパティまでの日数
  days_until: 'if(due_date, (date(due_date) - today()).days, "")'

  # 条件付きラベル
  status_icon: 'if(status == "mature", "✅", if(status == "developing", "🔄", "🌱"))'

  # 単語数推定
  word_est: '(file.size / 5).round(0)'
```

**重要ルール**: 2 つの日付の減算は `Duration` を返す。数値ではない。常に先に `.days` にアクセス:
```yaml
# 正しい
age: '(now() - file.ctime).days'

# 間違い: クラッシュ
age: '(now() - file.ctime).round(0)'
```

**null 可能なプロパティは常に `if()` でガード**:
```yaml
# 正しい
days_left: 'if(due_date, (date(due_date) - today()).days, "")'
```

---

## ビュータイプ

### テーブル
```yaml
views:
  - type: table
    name: "ウィキ索引"
    limit: 100
    order:
      - file.name
      - type
      - status
      - updated
    groupBy:
      property: type
      direction: ASC
```

### カード
```yaml
views:
  - type: cards
    name: "ギャラリー"
    order:
      - file.name
      - tags
      - status
```

### リスト
```yaml
views:
  - type: list
    name: "クイックリスト"
    order:
      - file.name
      - status
```

---

## ウィキ Vault テンプレート

### ウィキコンテンツダッシュボード(全非メタページ)

```yaml
filters:
  and:
    - file.inFolder("wiki/")
    - not:
        - file.inFolder("wiki/meta")

formulas:
  age: '(now() - file.ctime).days.round(0)'

properties:
  formula.age:
    displayName: "経過日数"

views:
  - type: table
    name: "全ウィキページ"
    order:
      - file.name
      - type
      - status
      - updated
      - formula.age
    groupBy:
      property: type
      direction: ASC
```

### エンティティ索引(人物、組織、リポジトリ)

```yaml
filters:
  and:
    - file.inFolder("wiki/entities/")
    - 'file.ext == "md"'

views:
  - type: table
    name: "エンティティ"
    order:
      - file.name
      - entity_type
      - status
      - updated
    groupBy:
      property: entity_type
      direction: ASC
```

### 最近の取り込み

```yaml
filters:
  and:
    - file.inFolder("wiki/sources/")

views:
  - type: table
    name: "ソース"
    order:
      - file.name
      - source_type
      - created
      - status
    groupBy:
      property: source_type
      direction: ASC
```

---

## ノートへの埋め込み

```markdown
![[MyBase.base]]

![[MyBase.base#ビュー名]]
```

---

## 保存場所

`.base` ファイルは Vault ダッシュボード用に `wiki/meta/` に置く:
- `wiki/meta/dashboard.base`: メインコンテンツビュー
- `wiki/meta/entities.base`: エンティティトラッカー
- `wiki/meta/sources.base`: 取り込みログ

---

## YAML クォートルール

- ダブルクォート付きの数式 → シングルクォートで囲む: `'if(done, "Yes", "No")'`
- コロンや特殊文字を含む文字列 → ダブルクォートで囲む: `"ステータス: Active"`
- クォートなしのコロン入り文字列は YAML パースを壊す

---

## 禁止事項

- `from:` や `where:` を使わない: それは Dataview 構文で Obsidian Bases ではない
- ルートレベルで `sort:` を使わない: ソートはビュー単位で `order:` と `groupBy:` 経由
- `.base` ファイルを Vault 外に置かない: Obsidian 内でのみレンダリング
- `formulas:` で `X` を定義せず `order:` で `formula.X` を参照しない
