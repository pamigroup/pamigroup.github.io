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

不会为成员单独生成页面：卡片上的姓名直接链到本人主页（`website`），没填主页就是纯文本。

```yaml
---
# ---------- 必填 ----------
title: Firstname Lastname 中文名        # 浏览器标签页 / og:title
pname: Firstname Lastname 中文名        # 页面上显示的姓名，用本人惯用写法即可
photo: /assets/img/people/Firstname_Lastname.jpg
status: PhD                             # Director | Postdoc | PhD | MSc | Visiting | RA
eml: ycXXXXX@um.edu.mo
desp: >-
  三到五句英文第三人称简介，用本人给的原文，不要替他补写。

# ---------- 选填, 留空即可 ----------
joined: 2026-08                         # 入组时间，YYYY 或 YYYY-MM，只用于显示
um_id: mcXXXXX                          # UM 学号，决定组内排序（学号本身按入学先后递增）
position:                               # 只在职称不能由分组标题表达时才填（例如 Associate Professor）
office:
website:                                # 个人主页；填了姓名就会链到这里
google_scholar:
orcid:                                  # 公开链接 https://orcid.org/0000-XXXX-XXXX-XXXX
github:
linkedin:
twitter:
cv:
---
```

两个容易出错的地方：

- `status` 决定此人出现在 People 页的哪一组，**拼错就整个人不显示且不报错**。
- `um_id` 决定组内顺序，学号越小排越前。**不填的会掉到该组最后**。
  `joined` 只显示不排序，因为只有部分人填了 `joined` 时会把顺序搞乱。

成员没有提供的信息就留空，不要替他推断补写。

### 3. Add the photo

路径写在 `photo` 字段里，习惯放 `assets/img/people/`。必须是**真正的 JPEG**、**正方形**。

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

如果本地构建过，再核对一次构建产物：

```bash
jekyll build && python3 tools/check_site.py --site _site
```

这一步专门挡"构建成功但页面是空的"：Liquid 里写错一个变量名不会报错，
只会安静地渲染出零个人，Jekyll 照样返回成功。

### When a member graduates

1. 删掉 `_people/<name>.md` 和 `assets/img/people/<name>.jpg`。
2. 在 `_data/alumni.yml` 对应分类（`postdoc` / `phd` / `msc`）的**顶部**加一条：

```yaml
  - name: Firstname Lastname
    years: '2024-2026'      # 在组年份
    now: Ph.D.              # 选填，毕业去向
    where: Some University  # 选填
    note: XXX Award         # 选填
    url: https://...        # 选填，个人主页；填了姓名就会链过去
```

---

## Where the content lives

| 内容 | 文件 | 说明 |
|---|---|---|
| 首页 | `index.html` | 研究方向段落、Join Us、Contact |
| 动态 | `_data/news.yml` | 首页取最新 5 条，`/news` 显示全部，也驱动 `feed.xml` |
| 成员 | `_people/*.md` + `assets/img/people/*.jpg` | 一人一文件 |
| 校友 | `_data/alumni.yml` | |
| 出版物 | `_data/publications.yml` | **唯一数据源**，页面自动按年份分组 |
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
    type: journal            # book | journal | conference | chapter | preprint
    detail: "vol. 35, pp. 1-12"
    doi: 10.1109/TIP.2026.xxxxxxx
    url:                     # 没有 DOI 时填官方链接
    code:                    # 代码仓库
```

`<strong>` 标出本组作者，`*` 表示通讯作者。年份分组、锚点、DOI 徽章、
类型筛选和搜索都是自动的，不用改页面。

**收录标准：Bob Zhang 必须是作者之一。** 他不在作者列表里的论文不算本组论文，
即使合作者是本组成员。`tools/check_site.py` 会强制这一条，加错了会直接报错。

数据与 [Bob Zhang 的 Google Scholar](https://scholar.google.com/citations?hl=en&user=dlZuABAAAAAJ&sortby=pubdate)
对齐。文件里两个待人工处理的标记，处理完把该行删掉：

- `_needs_full_authors: true` 作者名来自 Scholar 缩写（CrossRef 尚无记录），待补全名和通讯作者星号。
- `_doi_unresolved: ...` DOI 存疑，原因写在值里。

## Tools

| 脚本 | 用途 |
|---|---|
| `tools/check_site.py` | 站点自检，改完数据跑一次；加 `--site _site` 还会核对构建产物条目数 |
| `tools/parse_publications.py` | 从旧的 Markdown 出版物列表解析出结构化记录（一次性迁移用） |
| `tools/backfill_dois.py` | 用 CrossRef 严格回填 DOI，匹配不确定时宁可留空 |
| `tools/gen_publications_yml.py` | 由上面两步的结果生成 `_data/publications.yml` |
| `tools/add_from_scholar.py` | 把 Google Scholar 上有、数据文件里没有的论文补进来 |

## Building locally (optional)

不是必须的，推 `main` 就会自动部署。想本地预览：

```bash
gem install jekyll jekyll-sitemap
jekyll serve
```
