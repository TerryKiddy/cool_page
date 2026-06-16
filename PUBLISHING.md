# 发布到 cool_page 的安全规则

> 这是一个**多人/多机/多会话**共同写入的静态发布仓（GitHub Pages）。
> 同一时间可能有别的会话也在加页面，所以**每次发布都必须走"先拉再推、非强推"的安全流程**，
> 否则可能覆盖别人刚加的页面或丢提交。

## TL;DR — 照抄这套命令

```bash
# 0. 确认在发布分支
git branch --show-current          # 必须是 gh-pages

# 1. 把你的 HTML 放进仓根目录，只 add 你自己那一个文件
git add your-page.html             # ❌ 绝不要 git add -A / git add .

# 2. 提交
git commit -m "add your-page: 一句话说明"

# 3. 先拉再推（= pull --rebase before push，安全关键的一步）
git fetch origin
git rebase origin/gh-pages         # 把你的提交垫到远端最新之上

# 4. 非强推
git push origin gh-pages           # 成功会显示 旧SHA..新SHA（".." = 快进）
```

## 五条规则

1. **分支 = `gh-pages`**。Pages 直接从该分支构建，这个仓平时就 checkout 在 gh-pages 上。
2. **只 `git add` 你自己的文件**。仓根常年躺着未跟踪文件（`feishu_boards/`、`gold_trend_3d.html` 等）——
   `git add -A` / `git add .` 会把它们误卷进你的提交。
3. **先拉再推**：push 前一定 `git fetch origin && git rebase origin/gh-pages`
   （等价 `git pull --rebase origin gh-pages`；用 rebase 而非 merge，保持线性历史、不产生 merge commit）。
4. **只用非强推** `git push origin gh-pages`。**永远不要** `push --force` / `push +`——那是唯一能丢别人提交的操作。
5. **新增页面不用手改 `index.html`**：它用 Jekyll 自动遍历所有 `.html` 生成目录列表，commit 上去就会出现。
   （本文件是 `.md`，不会出现在站点列表里，只在仓库里可见——正合适做流程文档。）

## 为什么这样就不会覆盖别人（两层保险）

- **快进推送只"叠加"**：push 显示 `旧SHA..新SHA`（非 `+ forced`）时，你的提交只是垫在历史最上面，
  **不改、不删**任何已有文件。别人的页面原封不动。
- **撞车会被拒、而非互相覆盖**：万一 fetch 之后、push 之前的一瞬别人抢先推了，你的非强推会被 GitHub
  以 *non-fast-forward* **拒绝**；你再 `git rebase origin/gh-pages` 一次重推即可，**没有任何人的提交被吞**。

## 一键自证"我没覆盖到别人"

```bash
git log --oneline -5                                   # 你的提交应叠在对方提交"之上"
git ls-tree origin/gh-pages --name-only | grep <对方文件>   # 对方页面仍在远端
curl -sI https://terrykiddy.github.io/cool_page/<对方页面>.html | head -1   # 仍 200
```

## 撤回一次发布

```bash
git revert <那条提交的SHA>
git push origin gh-pages
```

---
公开访问：`https://terrykiddy.github.io/cool_page/<文件名>.html` ·
首页：`https://terrykiddy.github.io/cool_page/` · push 后构建约 1–2 分钟。
**发布即公开**，可能被搜索引擎/缓存收录——放敏感内容前先想清楚。
