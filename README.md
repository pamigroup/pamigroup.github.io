# PAMI Research Group Website

Public site of the Pattern Analysis and Machine Intelligence (PAMI) Research Group,
University of Macau. Built with [Jekyll](https://jekyllrb.com/) and the
[Beautiful Jekyll](https://github.com/daattali/beautiful-jekyll) theme, deployed by
GitHub Pages at <https://pamigroup.github.io>.

Push to `main` and GitHub Pages rebuilds automatically. There is nothing to run by hand.

---

## Adding a new member

Two files, then one check. Nothing else needs editing.

### 1. Collect this information from the new member

```
1.  英文姓名（用本人惯用的写法即可，不必照护照）+ 中文姓名
      例: Carina Zhao 赵彩杰
2.  身份: Ph.D. Student / M.Sc. Student / Post-doctoral Fellow /
          Research Assistant / Visiting Student
3.  入组年月, 例 2026-09
4.  UM 邮箱
5.  办公室房号, 例 E11-2039
6.  教育背景: 本科学校 + 专业 + 毕业年份; 硕士学校 + 专业 + 毕业年份
7.  导师（联合培养请写清共同导师及其单位）
8.  研究方向 2-3 个关键词, 以及 3-5 句英文第三人称简介
9.  个人主页 / Google Scholar / GitHub / ORCID / LinkedIn（有就给）
10. 获奖、审稿经历（可选）
11. 一张照片: 正方形, 短边 >= 600px, 正面清晰, 背景干净
```

### 2. Create `_people/Firstname_Lastname.md`

The filename decides the URL and the photo path, so keep it stable even if the person
later changes how their name is displayed. `pname` is the display name and can be
anything; `permalink` is the identity.

```yaml
---
# ---------- 必填 ----------
title: Firstname Lastname 中文名        # 浏览器标签页 / og:title / 搜索结果标题
pname: Firstname Lastname 中文名        # 页面上显示的姓名，可用惯用英文名
layout: people
permalink: /people/Firstname_Lastname   # 照片路径 = /assets/img + 这个 + .jpg
status: PhD                             # Director | Postdoc | PhD | MSc | Visiting | RA
position: Ph.D. Student                 # 卡片上显示的身份文字
eml: ycXXXXX@um.edu.mo
desp: >-
  Firstname Lastname received the B.Eng. degree from XXX University in 20XX.
  They are currently pursuing the Ph.D. degree in Computer Science at the PAMI
  Group, Faculty of Science and Technology, University of Macau, under the
  supervision of Prof. Bob Zhang. Their research interests include A, B, and C.

# ---------- 选填, 留空即可 ----------
joined: 2026                            # 入组年份, 用于组内排序; 留空的排在有值的后面
office:
website:
google_scholar:
orcid:                                  # 用公开链接 https://orcid.org/0000-XXXX-XXXX-XXXX
github:
linkedin:
twitter:
cv:
---
```

`status` 决定此人出现在 People 页的哪一组，**拼错就整个人不显示且不报错**，
所以改完一定要跑第 4 步的自检。

### 3. Add the photo

必须是 `assets/img/people/<permalink 末段>.jpg`，**真正的 JPEG**，**正方形**。
布局按 permalink 拼路径并写死了 `.jpg`。

```bash
python3 - <<'PY'
from PIL import Image, ImageOps
src, dst = 'input.jpg', 'assets/img/people/Firstname_Lastname.jpg'
im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
ImageOps.fit(im, (400, 400), Image.LANCZOS, centering=(0.5, 0.35)) \
        .save(dst, 'JPEG', quality=82, optimize=True, progressive=True)
PY
```

### 4. Check

```bash
python3 tools/check_site.py
```

会检查必填字段、`status` 合法性、照片是否存在 / 是否真 JPEG / 是否正方形、
是否把同一个链接错挂到两个人身上。

### When a member graduates

把 `_people/<name>.md` 删掉，然后在 `_data/alumni.yml` 里加一条。

---

## Where the content lives

| 内容 | 文件 | 说明 |
|---|---|---|
| 首页 | `index.html` | 研究方向段落、Join Us、Contact |
| 动态 | `_data/news.yml` | 首页取最新 5 条，`/news` 显示全部，也驱动 `feed.xml` |
| 成员 | `_people/*.md` + `assets/img/people/*.jpg` | 一人一文件 |
| 校友 | `_data/alumni.yml` | |
| 出版物 | `_data/publications.yml` | **唯一数据源**，页面自动按年份分组 |
| 代码 | `_data/software.yml` | |
| 招生 | `pages/positions.md` | 记得同步更新页首的 `last-updated` |
| 样式 | `assets/css/lab.css` | 自定义样式都放这里，不要改主题的 `main.css` |

页面模板在 `pages/`，可复用片段在 `_includes/`（`person-card.html`、
`person-group.html`、`publication.html`、`structured-data.html`）。

## Adding a publication

在 `_data/publications.yml` 的 `papers:` 顶部加一条：

```yaml
  - title: "论文标题"
    authors: "First Author, <strong>Bob Zhang</strong>*, Third Author"
    venue: "IEEE Transactions on Image Processing"
    year: 2026
    type: journal            # book | journal | conference | chapter
    detail: "vol. 35, pp. 1-12"
    doi: 10.1109/TIP.2026.xxxxxxx
    url:                     # 没有 DOI 时填官方链接
    code:                    # 代码仓库
    selected: true           # 出现在页面顶部的 Selected Publications
```

`<strong>` 标出本组作者，`*` 表示通讯作者。年份分组、锚点、DOI 徽章、
类型筛选和搜索都是自动的，不用改页面。

## Tools

| 脚本 | 用途 |
|---|---|
| `tools/check_site.py` | 站点自检，改完数据跑一次 |
| `tools/parse_publications.py` | 从旧的 Markdown 出版物列表解析出结构化记录（一次性迁移用） |
| `tools/backfill_dois.py` | 用 CrossRef 严格回填 DOI，匹配不确定时宁可留空 |
| `tools/gen_publications_yml.py` | 由上面两步的结果生成 `_data/publications.yml` |

## Building locally (optional)

不是必须的，推 `main` 就会自动部署。想本地预览：

```bash
gem install jekyll jekyll-sitemap
jekyll serve
```
