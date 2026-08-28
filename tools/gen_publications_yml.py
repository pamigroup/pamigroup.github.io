#!/usr/bin/env python3
"""由 /tmp/pubs_doi.json 生成 _data/publications.yml。"""
import json, re, sys

SELECT_VENUE = re.compile(
    r'Nature|IEEE Transactions on Pattern Analysis', re.I)

def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

def authors_html(md):
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md)
    return s

def is_selected(r):
    if r.get('note'):                       # 高被引 / 最佳论文奖
        return True
    if SELECT_VENUE.search(r.get('venue', '')):
        return True
    return False

recs = json.load(open('/tmp/pubs_doi.json'))
recs.sort(key=lambda r: (-r['year'], r['type'], r['title'].lower()))

lines = [
 "# PAMI Research Group 出版物数据（唯一数据源）。",
 "# 由 tools/parse_publications.py + tools/backfill_dois.py 从旧的 pages/publications.md 生成。",
 "# 新增论文：在本文件顶部按同样字段加一条即可，页面会自动按年份分组渲染。",
 "#",
 "# 字段说明:",
 "#   title / authors / venue / year / type(book|journal|conference|chapter)  必填",
 "#   detail    卷期页码等",
 "#   doi       仅在能确认指向本文时填；宁可留空也不要填错",
 "#   url       没有 DOI 时的官方链接（例如 IJCAI proceedings）",
 "#   code      代码仓库；project 项目主页；pdf 本地或外部 PDF",
 "#   note      奖项 / 高被引等",
 "#   selected  true 时会出现在页面顶部的 Selected Publications",
 "",
 "papers:",
]
nsel = 0
for r in recs:
    lines.append(f'  - title: "{esc(r["title"])}"')
    lines.append(f'    authors: "{esc(authors_html(r["authors_md"]))}"')
    lines.append(f'    venue: "{esc(r.get("venue",""))}"')
    lines.append(f'    year: {r["year"]}')
    lines.append(f'    type: {r["type"]}')
    d = re.sub(r',?\s*(19|20)\d{2}\.?$', '', r.get('detail','')).strip().strip(',')
    if d:              lines.append(f'    detail: "{esc(d)}"')
    if r.get('doi'):   lines.append(f'    doi: {r["doi"]}')
    if r.get('note'):  lines.append(f'    note: "{esc(r["note"])}"')
    if is_selected(r):
        lines.append('    selected: true'); nsel += 1
    lines.append('    url:')
    lines.append('    code:')
open('_data/publications.yml','w',encoding='utf-8').write('\n'.join(lines) + '\n')
print(f'写入 _data/publications.yml: {len(recs)} 条, selected {nsel} 条', file=sys.stderr)
