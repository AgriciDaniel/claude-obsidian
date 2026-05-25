---
type: session
title: "ScrumFlow — DoR実装セ��ション"
created: 2026-05-25
updated: 2026-05-25
tags:
  - scrumflow
  - scrum
  - definition-of-ready
  - next-js
  - typescript
  - implementation
status: complete
related:
  - "[[Definition of Ready Framework]]"
---

# ScrumFlow — DoR実装セッション（2026-05-25）

## セッション概要

ScrumFlowのバックログ管理画面に「準備完了チェック（Definition of Ready）」機能を実装した。バックログアイテムが5カテゴリ19項目すべてを満たさないと「準備完了」ステータスに変更できないゲート制御を導入。

---

## 実装した機能

### 1. ReadinessCheck 型定義（`src/lib/types/index.ts`）

`UserStory` に `readinessCheck?: ReadinessCheck` を追加。5セクションの入れ子構造：

```typescript
interface ReadinessCheck {
  spec: {
    specUrl: string              // 仕様ドキュメントURL（任意）
    functionalSpecDecided: boolean
    uiDesignReady: boolean
    businessRulesDefined: boolean
    edgeCasesDefined: boolean
    stakeholderApproved: boolean
  }
  completion: {
    acceptanceCriteriaWritten: boolean
    testScenariosOutlined: boolean
    dodUnderstood: boolean
  }
  scope: {
    storyPointsEstimated: boolean
    fitsInSprint: boolean
    prioritySet: boolean
  }
  technical: {
    apiSpecsDefined: boolean
    dataModelDefined: boolean
    dependenciesConfirmed: boolean
    environmentReady: boolean
    accessGranted: boolean
  }
  teamAlignment: {
    teamUnderstandsStory: boolean
    assigneeReady: boolean
    noOpenQuestions: boolean
  }
}
```

### 2. ReadinessCheckDialog（`src/app/projects/[id]/backlog/ReadinessCheckDialog.tsx`）

- 単一スクロールページに5セクションを展開表示
- 各セクションヘッダーに完了数バッジ（例：`3/5`）
- 上部プログレスバーで全体進捗を表示（`totalCount/19`）
- 「機能仕様が決まっている」項目の下に折りたたみ式記載例（商品検索・ユーザー登録）
- 仕様ドキュメントURL入力欄（Notion等への外部リンク対応）
- 技術前提5項目は「該当なし場合もチェック」のヒント付き
- **19/19 チェックが完了するまで「準備完了に変更」ボタンは `disabled`**

### 3. バックログカード UI（`src/app/projects/[id]/backlog/page.tsx`）

**ステータス変更 UI の変更：**
- 変更前：`<select>` ドロップダウン
- 変更後：グラジエントボタン「✓ 準備完了にする」

```
backlog状態：[✓ 準備完了にする]  [編集]  [削除]
ready状態：  [バックログに戻す]   [編集]  [削除]
```

「準備完了にする」ボタンのスタイル：
- `bg-gradient-to-r from-emerald-500 to-green-500`
- `shadow-sm hover:shadow-md`
- `active:scale-95` でプレス感

**ボタン配置の改善：**
- 変更前：バッジ行に `ml-auto` で埋め込み（カード上部固定）
- 変更後：右端独立カラム `flex-col justify-center`（上下中央揃え）

カード内部の3カラム構造：
```
[▶展開] [バッジ+ストーリー文+タスク数 (flex-1)] [ボタン列 (flex-shrink-0, justify-center)]
```

**展開セクションのチェック済みサマリー：**
`ready` ステータスのカードを展開すると、5セクションの完了バッジと仕様書リンクを表示。「確認・編集」ボタンで再度ダイアログを開ける。

**StoryDialog のステータス欄：**
- `ready` オプションをドロップダウンから削除
- `backlog` 時：静的表示 + 「「準備完了」への変更は一覧画面のカードから行えます」注記
- `ready` 時：緑バッジ + 「バックログに戻す」リンクボタン

---

## 設計上の判断

### 受け入れ条件フィールドは残す

StoryDialog の受け入れ条件（`acceptanceCriteria: string[]`）と ReadinessCheck の「受け入れ条件が書かれている」チェックは**役割が異なる**：

| 場所 | 役割 |
|---|---|
| StoryDialog の受け入れ条件入力欄 | **内容を書く** — 完了基準の本文 |
| ReadinessCheck のチェックボックス | **確認する** — 書かれているかのゲートチェック |

削除すると ReadinessCheck チェックの参照先がなくなるため、両者は補完関係として維持する。

---

## ファイル一覧

| ファイル | 変更内容 |
|---|---|
| `src/lib/types/index.ts` | `ReadinessCheck` 型追加、`UserStory` に `readinessCheck?` 追加 |
| `src/app/projects/[id]/backlog/ReadinessCheckDialog.tsx` | 新規作成（19項目チェックダイアログ） |
| `src/app/projects/[id]/backlog/page.tsx` | ボタン化、上下中央揃え、ReadinessCheckDialog 統合 |

コミット: `e769ac5` — feat: build ScrumFlow scrum management tool（全作業を初回コミットとして一括収録）
