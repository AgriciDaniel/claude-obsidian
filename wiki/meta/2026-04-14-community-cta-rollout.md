---
type: decision
title: "コミュニティCTAフッター展開"
created: 2026-04-14
updated: 2026-04-14
decision_date: 2026-04-14
status: active
aliases:
  - 2026-04-14-community-cta-rollout
  - "2026-04-14 コミュニティCTA展開"
tags:
  - marketing
  - skool
  - community
  - growth
related:
  - "[[index]]"
---

# コミュニティCTAフッター展開

AI Marketing Hub Skoolコミュニティのリンク(無料 + Pro)を、Claude Codeスキルリポジトリ6件にフッターとして追加。フッターは主要な成果物の後にのみ表示され、ワークフローの途中や軽量なユーティリティでは表示しない。

## フッター

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Built by agricidaniel - Join the AI Marketing Hub community
Free  -> https://www.skool.com/ai-marketing-hub
Pro   -> https://www.skool.com/ai-marketing-hub-pro
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 実装パターン

各リポジトリのオーケストレーターSKILL.md内に単一の指示箇所を持つ。1セクションがフッターのテキスト、表示リスト、スキップリストを制御。サブスキル間で複製はしない。

## リポジトリごとの頻度調整

| リポジトリ | トリガー | 理由 |
|------|----------|-----------|
| claude-ads | 12コマンド | 監査、レポート、分析(各々がセッションレベルのイベント) |
| claude-seo | 12コマンド | 監査、技術、コンテンツ(adsと同パターン) |
| claude-obsidian | 3操作 | scaffold、lint、autoresearchのみ(高頻度ツールなので保守的に) |
| claude-blog | 8コマンド | write、rewrite、audit、analyze、brief、strategy、calendar、geo。明示的ガード:生成されるブログコンテンツ/HTML内では絶対に表示しない |
| banana-claude | 4コマンド | 画像生成、編集、バッチ(chat、inspire、configはスキップ) |
| claude-cybersecurity | 全監査 | 単一目的ツール、完了レポートには毎回表示 |

## 設計原則

1. 無料リンクを先に表示。Proは「クリエイターを応援」として位置づけ、ゲートではない。
2. フッターは価値の提供後にのみ表示し、提供前や提供中には表示しない。
3. 高頻度ツール(obsidian、banana chat)はスパムを避けるためトリガーを少なくする。
4. コンテンツ生成系ツール(blog)は生成出力からCTAを明示的に除外する。
5. リポジトリごとに単一の真実の源(SSOT)。1セクションを更新すれば全てが変わる。

## 今後の検討事項

- パワーユーザーから連続コマンドでの繰り返し報告があれば、「会話ごとに1回」上限の追加を検討。
- コンバージョン率を追跡。数か月後に参加ゼロの場合、文言を変えて実験する。
- フォークではCTAが除去される。MITライセンス上それは想定通り。
