---
name: save
description: >
  現在の会話、回答、気づきを Obsidian ウィキ Vault に構造化ノートとして保存する。
  チャットを解析し、適切なノートタイプを判定、frontmatter を作成し、正しい wiki フォルダに
  ファイリングして、index、log、ホットキャッシュを更新。本文は日本語で書く
  (プロジェクト CLAUDE.md の言語ポリシー参照)。トリガー(日本語): これを保存、その回答を保存、
  /save、これをファイル化、wiki に保存、このセッションを保存、この会話をファイル、これを残す、
  この分析を保存、これをウィキに追加。Triggers (English): "save this", "save that answer",
  "/save", "file this", "save to wiki", "save this session", "file this conversation",
  "keep this", "save this analysis", "add this to the wiki".
allowed-tools: Read Write Edit Glob Grep
---

# save: 会話をウィキにファイリングする

良い回答や気づきをチャット履歴に消えさせない。このスキルは直前の議論を取り、永続的な wiki ページとしてファイリングする。

ウィキは複利で積み上がる。こまめに保存する。

> **言語ルール**: ノート本文・見出し・log エントリは日本語。frontmatter のキー名と列挙値、ファイル名、wikilink ターゲットは英語のまま。`aliases:` には英語のファイル名と日本語表示名の両方を入れる。

---

## ノートタイプの決定

会話内容から最適なタイプを判定:

| タイプ | フォルダ | 適用 |
|------|--------|---------|
| synthesis | wiki/questions/ | 複数ステップの分析、比較、特定質問への回答 |
| concept | wiki/concepts/ | アイデア、パターン、フレームワークの説明や定義 |
| source | wiki/sources/ | セッションで議論された外部資料の要約 |
| decision | wiki/meta/ | 行われたアーキテクチャ・プロジェクト・戦略上の決定 |
| session | wiki/meta/ | フルセッション要約: 議論されたすべてを捕捉 |

ユーザーがタイプを指定したらそれに従う。指定が無ければ内容から最適を選ぶ。迷ったら `synthesis`。

---

## 保存ワークフロー

1. 現在の会話を **スキャン**。残す価値がある最重要部分を特定。
2. **質問**(まだ命名されていなければ): 「このノートに何という名前を付けますか?」短く説明的に。
3. 上の表からノートタイプを **判定**。
4. 会話から関連内容をすべて **抽出**。平叙の現在形で書き直す(「ユーザーが聞いた」ではなく実際の内容そのもの)。
5. 完全な frontmatter 付きで正しいフォルダに **ノートを作成**。
6. **リンク収集**: 会話で言及された wiki ページを特定。frontmatter の `related` に追加。
7. `wiki/index.md` を **更新**。新エントリを該当セクションの先頭に追加。
8. `wiki/log.md` に **追記**。新エントリは TOP に:
   ```
   ## [YYYY-MM-DD] save | ノートタイトル
   - タイプ: [ノートタイプ]
   - 場所: wiki/[folder]/Note Title.md
   - 出典: [簡単なトピック説明] についての会話
   ```
9. 新規追加を反映するよう `wiki/hot.md` を **更新**。
10. **確認**: 「[[Note Title]] として wiki/[folder]/ に保存しました。」

---

## frontmatter テンプレート

```yaml
---
type: <synthesis|concept|source|decision|session>
title: "ノートタイトル(日本語可)"
aliases: ["English Filename Slug", "日本語表示名"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:
  - <関連タグ>
status: developing
related:
  - "[[言及された Wiki ページ]]"
sources:
  - "[[.raw/source-if-applicable.md]]"
---
```

`question` タイプには追加:
```yaml
question: "聞かれた元のクエリ"
answer_quality: solid
```

`decision` タイプには追加:
```yaml
decision_date: YYYY-MM-DD
status: active
```

---

## 文体

- 平叙、現在形で日本語で書く。会話ではなく知識を書く。
- NG: 「ユーザーが X について尋ね、Claude が説明した...」
- OK: 「X は Y することで動作する。重要な気づきは Z。」
- 関連コンテキストをすべて含める。未来のセッションがコールドでこのページを読めるように。
- 言及された概念・エンティティ・wiki ページすべてに wikilink を張る。
- 該当する場合は出典を引用: `(出典: [[Page]])`。

---

## 保存すべきもの vs スキップすべきもの

保存:
- 自明でない気づき・合成
- 根拠付きの決定
- 大きな労力をかけた分析
- 再参照される可能性が高い比較
- リサーチで得た発見

スキップ:
- 機械的な Q&A(明らかな答えのある検索質問)
- 他で文書化済みのセットアップ手順
- 持続的な気づきの無い一時的なデバッグセッション
- 既に wiki にあるもの

すでに wiki にある場合、重複を作らず既存ページを更新する。
