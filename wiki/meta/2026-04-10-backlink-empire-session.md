---
type: session
title: "バックリンク帝国 - ブログ投稿、Karpathy Gist、GitHubクロスリンク"
created: 2026-04-10
updated: 2026-04-10
aliases:
  - 2026-04-10-backlink-empire-session
  - "2026-04-10 バックリンク帝国セッション"
tags:
  - session
  - backlinks
  - seo
  - github
  - blog
  - rankenstein
status: complete
related:
  - "[[Claude Obsidian]]"
  - "[[Claude Canvas]]"
  - "[[Rankenstein]]"
  - "[[Karpathy LLM Wiki Pattern]]"
decision_date: 2026-04-10
---

## 実施内容

### 作成したブログ投稿

2本のブログ投稿を執筆し、Vercelにデプロイ、Google Indexing API + Bing IndexNowに送信した。

1. **claude-obsidian-ai-second-brain** : 「Obsidianを自己組織化するAIブレインに変えた話」
   - フォーカスキーワード:「obsidian ai second brain」
   - 約2,800語、リポジトリ画像/GIF 5点、SVGチャート3点、出典付き統計8件
   - 画像はclaude-obsidianリポジトリの`wiki/meta/`から(グラフビュー、wikiマップ、welcomeキャンバスGIF)
   - 公開URL: agricidaniel.com/blog/claude-obsidian-ai-second-brain

2. **claude-canvas-ai-visual-production** : 「Claude CodeがObsidian CanvasをAIデザインスタジオに変えた」
   - フォーカスキーワード:「obsidian canvas ai」
   - 約2,500語、リポジトリのスクリーンショット5枚、SVGチャート2点、出典付き統計7件
   - 画像はclaude-canvasリポジトリの`assets/screenshots/`から
   - 公開URL: agricidaniel.com/blog/claude-canvas-ai-visual-production

### Karpathy Gistへのコメント

Andrej KarpathyのLLM Wiki gist(gist ID: 442a6bf555914893e9891c11519de94f)にコメントを投稿。claude-obsidian(358スター)、claude-canvas、ブログ投稿へリンクを設置。差別化要素として、ホットキャッシュ、矛盾フラグ機能、8カテゴリのlint、自律研究ループを取り上げた。

### GitHubバックリンク帝国(26リポジトリ更新)

**フェーズ1:API更新(README変更なし):**
- 10リポジトリにホームページURLを設定(on-page-seo, Keywordo-kun, claude-youtube, marketing-skill-pack, google-maps-scraper, claude-repurpose, claude-gif, claude-avatar, rankenstein-pro-latest, claude-canvas)
- 25リポジトリにトピック/タグを設定(カテゴリ別:SEO、コンテンツ、マーケティング、obsidian、メディア、開発ツール、n8n)

**フェーズ2-5:README更新:**
- 25リポジトリに標準化したAuthorセクションを追加し、以下にリンク設置:
  - agricidaniel.com/about
  - agricidaniel.com/blog
  - skool.com/ai-marketing-hub
  - youtube.com/@AgriciDaniel
  - github.com/AgriciDaniel

**Rankenstein.proへのバックリンク(SEO関連リポジトリ5件のみ):**
- claude-seo:「Publishing Pipeline」セクション
- claude-blog:「Publishing Platform」セクション
- on-page-seo:Authorの前にblockquote
- Keywordo-kun:Authorの前にblockquote
- marketing-skill-pack:Author内で言及

### 検証結果

64/65チェック合格。軽微な指摘1件:claude-obsidianは正式な`## Author`見出しの代わりにフッター形式の表記を採用(意図的:既に独自表記が存在)。

## 主要な意思決定

- **rankenstein.pro配置**:SEO関連リポジトリのみ(26中5件)。動画/画像/開発ツールに乱用しない。自然さを保つ。
- **Karpathy gistのトーン**:技術重視、価値先行。マーケティングではなく実装から入る。コメントスレッドの協調的なトーンに合わせる。
- **ブログのキーワード戦略**:「obsidian ai second brain」(トレンド、競合中程度)と「obsidian canvas ai」(競合低、検索数増加中)。両方とも競合の隙を突く狙い:既存記事で特定ツールを深掘りしているものは無い。
- **カバー画像**:ストック写真ではなく実際のリポジトリアセット(ピクセルアートカバー、スクリーンショット、GIF)を使用。コンバージョンが良く、より本物らしい。

## 数字

- github.com(DA 96)からagricidaniel.comへの新規バックリンク約87件
- rankenstein.proへのバックリンク約6件
- skool.com/ai-marketing-hubへのバックリンク約25件
- サイトマップの総ページ数22件(セッション開始時20件)
- ブログ投稿総数15件(従来13件)

## 今後のブログ投稿に向けたワークフロー

このセッションで再現可能なワークフローが確立された:
1. リポジトリを徹底調査(機能、画像、統計)
2. ウェブ検索によるキーワード調査+競合分析
3. HTMLコンテンツ、SVGチャート、リポジトリ画像を含むブログJSONを執筆
4. blogPosts.ts、sitemap.xml、llms.txtに追加
5. Vercelへビルド+プリレンダー+デプロイ
6. Google Indexing API + Bing IndexNowへ送信
7. リポジトリのホームページをブログURLに設定
8. リポジトリREADMEにブログのバックリンクを追加
9. READMEのAuthor/コミュニティセクションを更新
