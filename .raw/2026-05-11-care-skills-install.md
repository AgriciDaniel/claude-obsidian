---
source: claude-conversation
date: 2026-05-11
topic: テンダーヒルズ向け3スキル（care-user-info-excel / admission-script / admission-assessment）をClaude Codeにインストール
---

# 特養スキル3種 Claude Codeインストール

## Summary
テンダーヒルズ（秋田県大仙市のユニット型個室特養）向けに作成された3つのSKILL.mdファイルをGoogleドライブの進藤榮子フォルダから発見し、~/.claude/skills/へインストールした。次のセッションからスラッシュコマンドで呼び出せる状態になった。

## Key Points
- `care-user-info-excel`: 複数資料（相談メモMD・PDF・服薬表）から利用者基本情報Excelを下書き入力し、確認リスト付き修正版を生成するスキル
- `admission-script`: 入所調整委員会で司会者が読み上げる台本（MS明朝・A4縦1ページ）をWord(.docx)で生成するスキル
- `admission-assessment`: 入所調整委員会向け入所判定資料（7セクション構成・青ヘッダーカラーテーブル）をWord(.docx)で生成するスキル
- ソース: `/Users/suzuki/Library/CloudStorage/GoogleDrive-miya2300@gmail.com/マイドライブ/022_利用者フェースシート/進藤榮子/`
- インストール先: `~/.claude/skills/{care-user-info-excel,admission-script,admission-assessment}/`
- SKILL.mdにはMac/Windowsクロスプラットフォーム対応（フォント自動切り替え、Pathlib使用）が記述済み

## Details

### スキル詳細

#### care-user-info-excel
- 依存: `openpyxl`, `pdfplumber`
- ワークフロー: ソース読込 → 下書き入力 → 確認リスト作成 → ユーザー修正反映 → 最終化
- カラールール: 緑=確認済み、黄=要確認
- 命名規則: `[氏名]_利用者基本情報_修正版.xlsx` → `_反映版.xlsx`
- テンプレートのシート構成: 確認リスト / 基本情報 / 緊急連絡先

#### admission-script
- 依存: `python-docx`
- 台本テンプレート: 開会宣言→待機番号→生活歴→介護経過→ADL→収入→医療方針→各職種意見→判定→閉会
- 不明項目は全角スペースで空白確保
- 命名規則: `[氏名]_入所調整委員会台本_[YYYYMMDD].docx`

#### admission-assessment
- 依存: `python-docx`
- カラー: ヘッダー青(`2E6DA4`)、ラベル薄青(`DAE3F3`)、判定注記茶(`843C0C`)
- テーブル構成: 4列テーブル（基本情報・病歴・ADL）＋2列テーブル（生活歴・認知等）
- 命名規則: `[氏名]_入所判定資料_[YYYYMMDD].docx`
- 関連スキル: `admission-script`（台本単体）、`admission-committee`（台本＋判定資料一式）

### 施設情報
- 施設名: テンダーヒルズ
- 種別: ユニット型個室特養（115床）＋ショートステイ（12床）
- 所在地: 秋田県大仙市
- 協力医療機関: 大曲厚生医療センター
