---
type: concept
title: "ScrumFlow"
created: 2026-05-25
updated: 2026-05-25
tags:
  - scrumflow
  - next-js
  - scrum
  - agile
  - project-management
  - typescript
status: developing
related:
  - "[[Definition of Ready Framework]]"
  - "[[2026-05-25-scrumflow-dor-session]]"
---

# ScrumFlow

PdM / PM / PO 向けのスクラム管理 Web アプリ。スクラムの全フェーズをガイド形式で進行できる。プロジェクト立ち上げからスプリントレビュー・レトロスペクティブまでを 1 ツールでカバーし、各フェーズの必須項目が揃わないと次に進めないゲート制御を持つ。

- **リポジトリ**: `C:\Users\clover\Desktop\Workspace\scrum-tool`
- **ローカルサーバー**: `http://localhost:3000`
- **コミット**: `e769ac5`（初回コミット、全作業を一括収録）

---

## 技術スタック

| 分類 | 採用技術 |
|---|---|
| フレームワーク | Next.js 16.2.6（App Router、Turbopack） |
| 言語 | TypeScript 5 |
| スタイリング | Tailwind CSS v4 |
| UIコンポーネント | shadcn/ui（base-ui ベース、`asChild` prop 非対応） |
| 状態管理 | Zustand 5 + persist ミドルウェア（localStorage） |
| D&D | dnd-kit（カンバンボード） |
| チャート | Recharts（バーンダウンチャート） |
| 日時 | date-fns + ja ロケール |
| アイコン | lucide-react |
| トースト | sonner |

### ストア構成（localStorage）

| キー | 管理対象 |
|---|---|
| `scrum-projects` | Project, TeamMember, Stakeholder |
| `scrum-backlog` | Epic, UserStory, Task |
| `scrum-sprints` | Sprint, DailyScrum, SprintReview, Retrospective |

---

## 7フェーズ構成

フェーズは順番にアンロックされる。前フェーズの完了条件を満たさないと次に進めない（`canAccessPhase()` によるゲート制御）。

| # | フェーズ名 | URL | 主な画面内容 |
|---|---|---|---|
| P1 | プロジェクト立ち上げ（setup） | `/projects/[id]/setup` | エレベーターピッチ・DoD/DoR・チームルール・ベロシティ設定 |
| P2 | バックログ作成（backlog） | `/projects/[id]/backlog` | ユーザーストーリー + エピック管理、準備完了ゲート |
| P3 | スプリント計画（sprint_plan） | `/sprints/[id]/plan` | ストーリーをスプリントに割り当て、ベロシティチェック |
| P4 | スプリント実行（sprint_exec） | `/sprints/[id]/board` | カンバンボード（Todo/進行中/レビュー/完了）、バーンダウン |
| P5 | スプリントレビュー（sprint_review） | `/sprints/[id]/review` | 完了ストーリー確認、ステークホルダーフィードバック |
| P6 | レトロスペクティブ（retrospective） | `/sprints/[id]/retro` | KPT（Keep/Problem/Try）形式 |
| P7 | バックログリファインメント（refinement） | `/backlog?refinement=1` | 次スプリントに向けたバックログ整備（P2 画面を再利用） |

フェーズループ：`P7(refinement)` → `P3(sprint_plan)` に戻る。

---

## 画面一覧

```
/                          プロジェクト一覧（ホーム）
/projects/new              プロジェクト新規作成
/projects/[id]             ダッシュボード
/projects/[id]/setup       P1: プロジェクト立ち上げ
/projects/[id]/backlog     P2/P7: バックログ管理
/projects/[id]/sprints     スプリント一覧
/projects/[id]/sprints/[sprintId]/plan    P3: スプリント計画
/projects/[id]/sprints/[sprintId]/board   P4: カンバンボード
/projects/[id]/sprints/[sprintId]/daily   デイリースクラム記録
/projects/[id]/sprints/[sprintId]/review  P5: スプリントレビュー
/projects/[id]/sprints/[sprintId]/retro   P6: レトロスペクティブ
/projects/[id]/members     チームメンバー・ステークホルダー管理
/projects/[id]/reports     レポート（バーンダウンチャート等）
```

---

## データモデル概要

### Project

エレベーターピッチは 7 フィールド構造化テンプレートで入力し、`buildElevatorPitch()` で 1 文に組み立てる。

```
elevatorPitch: string          // 組み立て済み（表示用・後方互換）
elevatorPitchFields: {         // テンプレートフィールド（入力用）
  needs, target, productName, category, benefits, alternative, differentiation
}
definitionOfDone: string[]     // プロジェクト共通 DoD（チップ選択 + カスタム入力）
definitionOfReady: string[]    // プロジェクト共通 DoR（チップ選択 + カスタム入力）
currentPhase: Phase
currentSprintId: string | null
initialVelocity: number
sprintDurationWeeks: number
```

### UserStory

```
asA / iWantTo / soThat        // ユーザーストーリー形式（〜として/〜したい/なぜなら）
epicId: string | null         // エピックに紐付け（任意）
status: 'backlog' | 'ready' | 'in_sprint' | 'done'
priority: 'must' | 'should' | 'could' | 'wont'   // MoSCoW
roughEstimate: 'S' | 'M' | 'L' | 'XL' | null
acceptanceCriteria: string[]  // 受け入れ条件
readinessCheck?: ReadinessCheck  // 準備完了チェック結果（DoR 詳細）
```

`status === 'in_sprint'` でスプリント所属を表現（`sprintId` フィールドは UserStory に持たない）。

### Epic

色コード付き（Tailwind bg クラス 8色）のユーザーストーリーグループ。

### Task

```
estimatePoints: 1|2|3|5|8|13|21 | null   // フィボナッチポイント
status: 'todo' | 'in_progress' | 'review' | 'done'
sprintId: string | null   // スプリントへの割り当てはタスク側が持つ
```

スプリント所属はタスクの `sprintId` で管理。ストーリーのスプリント帰属は `status === 'in_sprint'` で判定。

---

## 主要な実装方針と判断記録

### shadcn/ui の `sm:` prefix 問題

`DialogContent` のベーススタイルに `sm:max-w-sm` が含まれるため、`max-w-*` で上書きしても sm ブレークポイント以上では効かない。すべての幅指定は `sm:max-w-*` 形式で記述する必要がある。

```tsx
// NG: max-w-2xl が sm 以上で無効になる
<DialogContent className="max-w-2xl">

// OK
<DialogContent className="sm:max-w-[65vw]">
```

### エレベーターピッチのテンプレート形式

自由記述ではなく、7 フィールドの穴埋め形式を採用。以下テンプレートをそのまま組み立てる：

```
「{needs}したい {target}向けの {productName}というプロダクトは
 {category}です。これは{benefits}ができ、
 {alternative}とは違って {differentiation}が備わっている。」
```

### DoD/DoR のテンプレートチップ選択

セットアップ画面でカテゴリ別チップから典型的な項目を選択できる。選択済み項目は `×` ボタンで削除、独自項目を自由入力で追加可能。プロジェクト共通の DoD/DoR として保存される。

### バックログカードの 2 カード構成

ユーザーストーリー（左）とエピック（右）を `・・・` コネクターでつなぐデザイン。

```
[ストーリーカード (flex-1)]  ・・・  [エピックカード (w-44)]
```

- ステータス変更・編集・削除ボタンはストーリーカードの右端カラムに配置（`justify-center` で上下中央揃え）
- エピックカードは色ドット + タイトル + 説明の表示のみ

### スプリントのストーリー所属判定

`status === 'in_sprint'` のみで判定し、タスクの `sprintId` によるフィルターは使わない。タスクが 0 件のストーリーも追加できる。

```ts
// NG: タスクが 0 件だと in_sprint になれない
const sprintStories = allStories.filter(s =>
  s.status === 'in_sprint' && s.tasks.some(t => t.sprintId === sprintId))

// OK
const sprintStories = allStories.filter(s => s.status === 'in_sprint')
```

### 準備完了チェック（DoR ゲート）

詳細は [[Definition of Ready Framework]] と [[2026-05-25-scrumflow-dor-session]] を参照。

- バックログカード上の「準備完了にする」ボタン（グラジエント）押下で `ReadinessCheckDialog` を起動
- 19/19 チェック完了まで「準備完了に変更」ボタンは disabled
- `StoryDialog`（編集モーダル）からは `ready` に直接変更不可。バックログに戻す操作のみ可能
- `readinessCheck` データは `backlog` に戻しても保持される（再度 `ready` にする際に再入力不要）

---

## フェーズ完了チェック（`checkPhaseComplete`）

各フェーズの必須条件を定義。満たさないと次フェーズへの「完了」ボタンが機能しない。

| フェーズ | 必須条件 |
|---|---|
| setup | プロジェクト名・エレベーターピッチ・WhyWeAreHere・チームルール・開始/終了日・DoD 1件以上・DoR 1件以上・初回ベロシティ |
| backlog | `status === 'ready'` のストーリー 1件以上・全 ready ストーリーに roughEstimate |
| sprint_plan | スプリントゴール・期間・レビュー/レトロ日時・スプリントにストーリー 1件以上 |
| sprint_review | フィードバック入力済み |
| retrospective | Keep / Problem / Try それぞれ 1件以上 |
| refinement | `ready` ストーリー 1件以上 |
