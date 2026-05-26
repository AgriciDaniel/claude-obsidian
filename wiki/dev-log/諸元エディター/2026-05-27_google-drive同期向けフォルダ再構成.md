---
type: log
title: Google Drive 同期向けにプロジェクトを src/ サブフォルダ構造へ再編
created: 2026-05-27
updated: 2026-05-27
tags:
  - dev-log
  - 諸元エディター
status: developing
---

## 背景・理由

外出先のスマホ ↔ 社内 PC ↔ 他の Windows PC でプログラムを共有するため、プロジェクトフォルダごと Google Drive for desktop（ミラーリング）で同期していた。以下の不満点があった:

- `.venv/` `__pycache__/` `.DS_Store` `.tmp.drivedownload/` `.tmp.driveupload/` など、共有不要なファイルまで同期されていた
- Google Drive for desktop には `.gitignore` 相当の除外機能が公式に存在しない
- スマホから `.py` をメール添付すると Gmail に実行可能ファイル扱いで削除されるため、毎回 zip 圧縮していた

## 変更前の構造

```
~/諸元エディター/  ← Drive 同期対象
├── .venv/
├── __pycache__/
├── .DS_Store
├── .claude/
├── .tmp.drivedownload/ / .tmp.driveupload/
├── shogen_editor_v0_3_0_qt.py
├── shogen_editor_v0_3_1_qt.py
├── 諸元文言作成ツール_v0_2_7.py
├── 編集項目一覧.jpeg / 編集項目詳細.jpg
├── editorについて.md / editorのUIについて.md
└── 諸元文言作成ツール_v0_2_7_要件定義.md
```

## 変更後の構造

```
~/諸元エディター/                       ← Drive 同期から外す（ローカル専用）
├── .venv/
├── .claude/
├── editorについて.md
├── editorのUIについて.md
├── 編集項目一覧.jpeg / 編集項目詳細.jpg
├── 諸元文言作成ツール_v0_2_7_要件定義.md
└── src/                                ★ ここだけ Google Drive にミラーリング
    ├── shogen_editor_v0_3_0_qt.py
    ├── shogen_editor_v0_3_1_qt.py
    ├── 諸元文言作成ツール_v0_2_7.py
    └── share/                          ← スマホ → メール送信用の .py.txt コピー置き場
        └── shogen_editor_v0_3_1_qt.py.txt
```

## share/ 運用ルール

- `share/` には開発中の最新版を `.py` → `.py.txt` にリネームしてコピー配置する
- 目的: スマホから Drive 経由で取得 → そのままメール添付して社内 PC へ送信。Gmail の `.py` ブロックを回避するため拡張子を `.txt` にしている
- 編集本体は `src/*.py`、`share/*.py.txt` はあくまでコピー
- **更新ごとの手動コピーが必要**。自動化したい場合はシェルスクリプト or fswatch ベースの監視を検討（未実装）

**設計思想:** Drive 同期から除外したいものを `.gitignore` で除外するのではなく、「Drive に同期したいものだけをサブフォルダに集約して、そのサブフォルダだけを同期対象に指定する」という発想。除外機能のない Drive 同期では、これが唯一の確実な方法。

## 実施した作業

1. `~/諸元エディター/src/` を新規作成
2. `.py` 3ファイルを `src/` 配下に移動
3. `__pycache__/` を削除（Drive 同期止めた状態だったので安全）
4. `.tmp.drivedownload/` `.tmp.driveupload/` は同期停止に伴い自動消滅

## 関連ファイル

- 移動した `.py`: `~/諸元エディター/src/shogen_editor_v0_3_*.py`、`~/諸元エディター/src/諸元文言作成ツール_v0_2_7.py`
- 影響評価: 両 `.py` 内のファイル I/O を確認。旧版 `諸元文言作成ツール_v0_2_7.py` は `_app_base_dir()` で `__file__` 基準にデータ JSON を保存するが、サブフォルダ移動後は `src/` 配下に設定/履歴 JSON が作られるだけで動作上の問題なし

## 残作業（ユーザー操作）

1. Google Drive for desktop の設定:
   - 「マイ MacBook」配下で、旧 `諸元エディター` フォルダの同期を **解除**（ローカルファイルは残す）
   - 「フォルダを追加」→ `~/諸元エディター/src` を選択 → 「Google ドライブにミラーリング」
2. Windows 側でも同様に、Drive 上の `src/` をミラーリング対象に設定
3. スマホからのメール送信時は `.py` → `.py.txt` にリネームして送信、受信側で `.py` に戻す

## 未解決事項・将来の検討

- `src/__pycache__/` は src 内に生成されると同期対象に入る。実害は小さいので現状放置。将来気になったら `PYTHONDONTWRITEBYTECODE=1` または `PYTHONPYCACHEPREFIX=$HOME/.pycache` を環境変数に設定
- `src/.DS_Store` も同様。`defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true` は Drive のローカルミラーには効かない可能性があるため、実害が出てから対策
- 長期的には Git + GitHub Private への移行が本来の解決策（`.gitignore` で完全制御、スマホからは Working Copy 等で push）。社内 PC が GitHub にアクセスできる場合は検討の価値あり
