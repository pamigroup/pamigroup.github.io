#!/usr/bin/env python3
"""用 CrossRef 为解析后的出版物回填 DOI。

匹配判据（必须全部满足，否则不写入 DOI）：
  1. 归一化标题相似度 >= 0.90
  2. 年份差 <= 2（期刊 early access 与正刊年常差 1 到 2）
宁可留空也不错配：错误 DOI 会把读者引到别人的论文。
同时报告 CrossRef 与本地记录的 venue/year 不一致，供人工复核。
"""
import json, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher

MAILTO = 'boom985426@gmail.com'
UA = f'pami-site-doi-backfill/1.0 (mailto:{MAILTO})'
TITLE_MIN = 0.90
YEAR_TOL = 2


def norm(s):
    s = re.sub(r'&[a-z]+;', ' ', s.lower())
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def surname(authors):
    first = authors.split(',')[0].strip().rstrip('*')
    return first.split()[-1].lower() if first.split() else ''


def query(rec):
    if rec.get('doi'):
        return rec, None, 'already-has-doi'
    q = f"{rec['title']} {surname(rec['authors'])}"
    url = ('https://api.crossref.org/works?rows=5&select=DOI,title,container-title,issued,type'
           '&query.bibliographic=' + urllib.parse.quote(q))
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            items = json.load(urllib.request.urlopen(req, timeout=30))['message']['items']
            break
        except Exception:
            if attempt == 2:
                return rec, None, 'query-failed'
            time.sleep(1.5 * (attempt + 1))
    best, best_r = 0.0, None
    tn = norm(rec['title'])
    for it in items:
        t = (it.get('title') or [''])[0]
        if not t:
            continue
        r = SequenceMatcher(None, tn, norm(t)).ratio()
        if r > best:
            best, best_r = r, it
    if best_r is None or best < TITLE_MIN:
        return rec, None, f'no-match(best={best:.2f})'
    yr = (best_r.get('issued', {}).get('date-parts') or [[None]])[0][0]
    if yr is None or abs(int(yr) - rec['year']) > YEAR_TOL:
        return rec, None, f'year-mismatch(local={rec["year"]},crossref={yr})'

    # 类型一致性守卫。本组多本专著的章节与期刊论文同名，仅靠标题相似度会把
    # 期刊论文错配到自家书的章节 DOI（已实际发生一次）。
    ct = best_r.get('type', '')
    ALLOWED = {
        'journal':    {'journal-article'},
        'conference': {'proceedings-article', 'book-chapter', 'book-part', 'journal-article'},
        'chapter':    {'book-chapter', 'book-part'},
        'book':       {'book', 'monograph', 'edited-book', 'reference-book'},
    }
    if ct not in ALLOWED.get(rec['type'], set()):
        return rec, None, f'type-mismatch(local={rec["type"]},crossref={ct})'

    return rec, {
        'doi': best_r['DOI'],
        'cr_venue': (best_r.get('container-title') or [''])[0],
        'cr_year': int(yr),
        'cr_type': ct,
        'sim': round(best, 3),
    }, 'ok'


def main():
    recs = json.load(open('/tmp/pubs.json'))
    out, stats, disc = [], {}, []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, (rec, hit, why) in enumerate(ex.map(query, recs), 1):
            key = why.split('(')[0]
            stats[key] = stats.get(key, 0) + 1
            if hit:
                rec['doi'] = hit['doi']
                rec['_sim'] = hit['sim']
                if abs(hit['cr_year'] - rec['year']) >= 1:
                    disc.append(('year', rec['title'][:64], rec['year'], hit['cr_year'], hit['doi']))
                lv, cv = norm(rec.get('venue', '')), norm(hit['cr_venue'])
                if cv and lv and SequenceMatcher(None, lv, cv).ratio() < 0.55:
                    disc.append(('venue', rec['title'][:64], rec.get('venue', '')[:52], hit['cr_venue'][:52], hit['doi']))
            else:
                rec['_nodoi'] = why
            out.append(rec)
            if i % 50 == 0:
                print(f'  ... {i}/{len(recs)}', file=sys.stderr)
    json.dump(out, open('/tmp/pubs_doi.json', 'w'), ensure_ascii=False, indent=1)
    print('\n匹配统计:', file=sys.stderr)
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'  {k:28} {v}', file=sys.stderr)
    got = sum(1 for r in out if r.get('doi'))
    print(f'\n已获得 DOI: {got}/{len(out)}  ({got*100//len(out)}%)', file=sys.stderr)
    json.dump(disc, open('/tmp/pubs_disc.json', 'w'), ensure_ascii=False, indent=1)
    print(f'需人工复核的 venue/year 不一致: {len(disc)} 条 -> /tmp/pubs_disc.json', file=sys.stderr)


if __name__ == '__main__':
    main()
