---
type: concept
title: "SEO ドリフト監視"
created: 2026-04-14
updated: 2026-04-14
tags:
  - concept
  - seo
  - monitoring
  - change-detection
status: evergreen
aliases:
  - "SEO Drift Monitoring"
  - "SEO ドリフト監視"
related:
  - "[[Claude SEO]]"
  - "[[Pro Hub Challenge]]"
---

# SEO ドリフト監視

「SEO のための Git」。SEO に重要なページ要素のベースラインをキャプチャし、現在の状態と差分を取って退行を検出する。Dan Colta により [[Claude SEO]] v1.9.0 へ貢献された。

## 追跡対象

3 つの重要度レベルにわたる 17 の比較ルール。

| 重要度 | 例 |
|----------|----------|
| CRITICAL | スキーマ削除、canonical 変更、noindex 追加、H1 削除 |
| WARNING | タイトル変更、CWV の 20% 超退行、メタディスクリプション変更 |
| INFO | H2 構造変更、コンテンツハッシュ変更、画像数変更 |

## アーキテクチャ

- **SQLite 永続化**: `~/.cache/claude-seo/drift/baselines.db`
- **4 つの Python スクリプト**: `drift_baseline.py`(キャプチャ)、`drift_compare.py`(差分)、`drift_report.py`(HTML レポート)、`drift_history.py`(タイムライン)
- **セキュリティ強化**: URL 取得には `fetch_page.py` のみを使用(SSRF 保護)。元の応募には SSRF 保護を回避する curl フォールバックがあり、統合時に完全に削除した。

## コマンド

```
/seo drift baseline <url>    # 現在の状態をキャプチャ
/seo drift compare <url>     # ベースラインと比較
/seo drift history <url>     # 全チェックを時系列で表示
```
