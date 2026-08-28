#!/usr/bin/env python3
"""把 pages/publications.md 的编号列表解析为结构化记录。

只做解析，不改写任何文字。解析失败的条目会被报告而不是静默丢弃。
"""
import re, sys, json

SECTION_TYPE = {
    'Monographs': 'book',
    'Journal Publications': 'journal',
    'Conference Publications': 'conference',
    'Book Chapters': 'chapter',
}

ITEM_RE = re.compile(r'^\s*(\d+)\.\s+(.*)$')


def strip_md(s: str) -> str:
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'_(.*?)_', r'\1', s)
    return s.strip().strip(',').strip()


def parse_entry(raw: str, ptype: str):
    e = {'type': ptype, 'raw': raw}

    # 备注，例如 **(Highly Cited)**
    m = re.search(r'\*\*\((.*?)\)\*\*', raw)
    if m:
        e['note'] = m.group(1).strip()
        raw = (raw[:m.start()] + raw[m.end():]).strip()

    # 内联 doi
    m = re.search(r'doi:\s*(10\.\S+?)[,.]?(?:\s|$)', raw)
    if m:
        e['doi'] = m.group(1).rstrip('.,')
        raw = (raw[:m.start()] + raw[m.end():]).strip()

    # 年份 = 条目中最后出现的四位年
    yrs = re.findall(r'\b(19\d{2}|20\d{2})\b', raw)
    if not yrs:
        return None
    e['year'] = int(yrs[-1])

    qm = re.search(r'["\u201c](.+?),?["\u201d]\s*,?\s*', raw)
    if qm:
        # 有引号标题：作者, "标题," _venue_, 其余
        e['authors_md'] = raw[:qm.start()].strip().rstrip(',').strip()
        e['title'] = qm.group(1).strip().rstrip(',').strip()
        rest = raw[qm.end():].strip()
    else:
        # 专著：作者, _标题_, 出版社, 年份
        im = re.search(r'_(.+?)_', raw)
        if not im:
            return None
        e['authors_md'] = raw[:im.start()].strip().rstrip(',').strip()
        e['title'] = im.group(1).strip()
        rest = raw[im.end():].strip().lstrip(',').strip()
        e['venue'] = re.sub(r',?\s*(19|20)\d{2}\.?$', '', rest).strip().strip(',')
        e['authors'] = strip_md(e['authors_md'])
        e['corresponding'] = '**Bob Zhang***' in e['authors_md'] or '**B. Zhang***' in e['authors_md']
        return e

    vm = re.search(r'_(.+?)_', rest)
    if vm:
        e['venue'] = vm.group(1).strip()
        e['detail'] = rest[vm.end():].strip().lstrip(',').strip().rstrip('.')
    else:
        e['venue'] = re.sub(r',?\s*(19|20)\d{2}\.?$', '', rest).strip().strip(',')
        e['detail'] = ''

    e['authors'] = strip_md(e['authors_md'])
    e['corresponding'] = '**Bob Zhang***' in e['authors_md'] or '**B. Zhang***' in e['authors_md']

    # 自洽性校验：作者段不该含引号或下划线，标题/venue 不该为空
    if '"' in e['authors'] or '_' in e['authors_md']:
        return None
    if not e['title'] or not e.get('venue'):
        return None
    if len(e['authors']) > 400 or len(e['title']) > 400:
        return None
    return e


def parse(path='pages/publications.md'):
    out, bad = [], []
    ptype = None
    for line in open(path, encoding='utf-8'):
        h = re.match(r'^#\s+(.*)$', line.strip())
        if h:
            ptype = SECTION_TYPE.get(h.group(1).strip())
            continue
        m = ITEM_RE.match(line)
        if not m or not ptype:
            continue
        e = parse_entry(m.group(2).strip(), ptype)
        if e is None:
            bad.append((ptype, m.group(0).strip()))
        else:
            out.append(e)
    return out, bad


if __name__ == '__main__':
    recs, bad = parse()
    print(f'解析成功 {len(recs)} 条, 失败 {len(bad)} 条', file=sys.stderr)
    for t, b in bad:
        print(f'  FAIL [{t}] {b[:130]}', file=sys.stderr)
    json.dump(recs, open('/tmp/pubs.json', 'w'), ensure_ascii=False, indent=1)
