# Git セットアップ

Vault に git を初期化して完全な履歴を持ち、不正な書き込みから守る。

---

## 初期化

```bash
cd "$VAULT_PATH"
git init
git add -A
git commit -m "Initial vault scaffold"
```

---

## .gitignore

このリポジトリのルート `.gitignore` は適切な除外を既にカバー:

```
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.smart-connections/
.obsidian-git-data
.trash/
.DS_Store
```

`workspace.json` はペインを動かすたびに変わる。除外して diff をクリーンに保つ。

---

## Obsidian Git プラグイン

プラグインインストール後(`plugins.md` 参照):

設定 → Obsidian Git:
- Auto backup interval: **15 分**
- Auto backup after file change: on
- Push on backup: on(リモートがあれば)
- Commit message: `vault: auto backup {{date}}`

バックグラウンドで静かに動く。何も意識せずすべてのノートの完全な履歴が手に入る。

---

## リモート(任意)

GitHub にバックアップ:

```bash
git remote add origin https://github.com/yourname/your-vault
git push -u origin main
```

Vault に個人ノートが含まれるならリポジトリは private にする。
