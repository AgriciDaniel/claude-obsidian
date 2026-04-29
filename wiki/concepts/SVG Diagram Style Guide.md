---
type: concept
title: "SVG 図表スタイルガイド"
created: 2026-04-14
updated: 2026-04-14
tags:
  - design
  - svg
  - brand
  - diagrams
status: evergreen
aliases:
  - "SVG Diagram Style Guide"
  - "SVG 図表スタイルガイド"
related:
  - "[[index]]"
sources:
  - "claude-ads/assets/diagrams/ (17 SVGs, v1.5.0)"
---

# SVG 図表スタイルガイド

agricidaniel の Claude Code スキルリポジトリ群すべてにまたがる、図表の規範的ビジュアルスタイル。claude-ads にある本番 17 SVG から抽出した。任意のスキルリポジトリで図を作成・更新する際のリファレンスとして用いる。

## フォント

```
font-family: 'Space Grotesk', system-ui, -apple-system, sans-serif
```

唯一の書体は Space Grotesk。serif や monospace へのフォールバックはなし。

## カラーパレット

### コア(すべての図で使う)

| トークン | 16 進 | 役割 |
|-------|-----|------|
| bg | #0A0A0A | キャンバス背景(ほぼ黒) |
| card | #111111 | カード/コンテナの塗り |
| card-inner | #1A1A1A | ネストした要素の塗り |
| border | #2D2D2D | カード境界、区切り線 |
| text-primary | #F5F5F0 | 見出し、ラベル(オフホワイト) |
| text-secondary | #888888 | 説明、キャプション |
| text-tertiary | #6a6a6a | 弱められたメタデータ |
| accent | #E07850 | 主アクセント、矢印、ハイライト(暖色のラスト・オレンジ) |
| accent-bright | #FF6B35 | 副アクセント、ホバー状態(より明るいオレンジ) |

### プラットフォーム/カテゴリ色(図中の変化に使う)

| トークン | 16 進 | 典型的用途 |
|-------|-----|-------------|
| blue | #60A5FA | Google、データ、情報 |
| purple | #8b5cf6 | Meta、戦略、クリエイティブ |
| cyan | #06b6d4 | LinkedIn、ネットワーキング |
| green | #4ADE80 | 成功、検証、TikTok |
| rose | #F43F5E | YouTube、警報 |
| orange | #FF6B35 | Microsoft、副アクセント |
| gray | #888888 | ニュートラル、汎用プラットフォーム |

### ステータス色(pass/warn/fail インジケータ用)

| トークン | 16 進 | 役割 |
|-------|-----|------|
| pass | #16a34a | 合格、成功 |
| warn | #f59e0b | 警告、注意 |
| fail | #dc2626 | 不合格、重大 |

## タイポグラフィスケール

| 要素 | サイズ | ウェイト | 色 | 追加 |
|---------|------|--------|-------|-------|
| 図のタイトル | 16-17px | 700 | #F5F5F0 | text-anchor: middle |
| サブタイトル | 11px | 400 | #888888 | text-anchor: middle |
| セクションラベル | 13px | 700 | アクセント色 | letter-spacing: 2 |
| カード見出し | 12-15px | 600-700 | #F5F5F0 | text-anchor: middle |
| カード補助文 | 9-11px | 400 | アクセント色 | スキル/エージェント名 |
| 本文 | 10px | 400 | #888888 | 説明 |
| 極小ラベル | 9px | 400 | #6a6a6a | メタデータ、件数 |

## レイアウトプリミティブ

### アウターコンテナ
```xml
<rect width="800" height="500" fill="#0A0A0A"/>
```
標準キャンバスは 800x500。コンテンツに応じて 900x250 や 900x350 を使う図もある。

### カード
```xml
<rect x="40" y="20" width="720" height="120" rx="16" fill="#111111" stroke="#2D2D2D" stroke-width="1.5"/>
```
- 角丸: アウターコンテナは `rx="16"`
- 境界: `#2D2D2D`、`stroke-width="1.5"`

### カラー付きトップバー(カードアクセント)
```xml
<rect x="40" y="20" width="720" height="4" rx="2" fill="#E07850"/>
```
高さ 4px、カードの上端に配置。色はカテゴリを示す。

### インナーカード(ネスト要素)
```xml
<rect x="60" y="230" width="105" height="60" rx="6" fill="#1A1A1A" stroke="#2D2D2D" stroke-width="1"/>
```
- 角丸: 小さなインナーカードは `rx="6"`、中サイズは `rx="9"`
- 塗り: `#1A1A1A`(親カードよりわずかに明るい)

### 番号付き円(順序用)
```xml
<circle cx="138" cy="60" r="14" fill="#0A0A0A" stroke="#60A5FA" stroke-width="1.5"/>
<text x="138" y="60" font-size="12" fill="#60A5FA" text-anchor="middle" font-weight="bold" dominant-baseline="central">1</text>
```
円の境界色はそのステップのカテゴリ色に合わせる。

### 矢印コネクタ
```xml
<line x1="400" y1="140" x2="400" y2="170" stroke="#E07850" stroke-width="1.5"/>
<polygon points="394,167 400,177 406,167" fill="#E07850"/>
```
常に `#E07850`。下向きフローには縦、左から右のパイプラインには横を使う。

### 水平区切り線(タイトル下線)
```xml
<line x1="380" y1="36" x2="520" y2="36" stroke="#E07850" stroke-width="2.5" stroke-linecap="round"/>
```
図のタイトル下に置く短い中央線。常にアクセント色。

## 図表タイプ(claude-ads より)

| # | 名称 | レイアウト | サイズ |
|---|------|--------|------|
| 01 | Architecture | 縦 3 層スタック | 800x500 |
| 02 | Parallel Audit | フロー付きエージェントグリッド | 800x500 |
| 04 | Platform Checks | チェックリスト列 | 800x500 |
| 05 | Quality Gates | ルールカード | 800x500 |
| 06 | How It Works | ステップ列 | 900x250 |
| 07 | Data Flow | 横方向パイプライン | 900x250 |
| 08 | Industry Templates | カードグリッド | 900x350 |
| 10 | MCP Integration | 接続図 | 800x500 |
| 12 | Privacy Flow | 縦フロー | 800x500 |
| 13 | Scoring Algorithm | 数式分解 | 800x500 |
| 14 | Creative Pipeline | 5 ステップ横方向 | 900x250 |
| 15 | Platform Grid | 2 行カードグリッド | 900x350 |
| 16 | PDF Pipeline | プロセスフロー | 900x250 |
| 17 | A/B Testing | 分割比較 | 800x500 |
| 18 | PPC Calculators | ツールカード | 900x350 |
| 19 | Audit Lifecycle | 円環フロー | 800x500 |
| 20 | Install Methods | オプションカード | 900x250 |

## ルール

1. 常にダークテーマ。白や明色背景は使わない。
2. Space Grotesk のみ。他のフォントは使わない。
3. `#E07850` がシグネチャアクセント。矢印、ハイライト、主要ビジュアル要素に使う。
4. カードには常に `#2D2D2D` の境界。境界なしカードは使わない。
5. カラー付きトップバー(4px)はカテゴリを示す。1 カテゴリ 1 色、図中で一貫させる。
6. テキストは常に左揃えか中央揃え。右揃えは使わない。
7. グラデーション、影、ぼかしフィルタは使わない。フラットデザインのみ。
8. 順次ステップには番号付き円を使う。色はカテゴリに合わせる。
9. 矢印コネクタは常に `#E07850`、三角形の先端を持つ。
10. ファイル命名: ゼロ埋めの番号プレフィックス(`01-`、`02-` など)+ ケバブケースの説明。
