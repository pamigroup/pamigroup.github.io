#!/usr/bin/env python3
"""把 Google Scholar 上有、_data/publications.yml 里没有的论文补进来。

作者名从 CrossRef 取全名（Scholar 只给缩写，混排会与站内风格不一致）。
CrossRef 查不到的条目保留 Scholar 原始信息并在报告里标出，不猜。
通讯作者星号不自动加：CrossRef 不提供该信息，需人工补。
"""
import json, re, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher

UA = 'pami-site/1.0 (mailto:boom985426@gmail.com)'
PREPRINT = re.compile(r'arxiv|biorxiv|medrxiv|preprint|ssrn|techrxiv', re.I)
GROUP = ('Bob Zhang', 'Yibo Bob Zhang', 'Yi-Bo Zhang')


def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', (s or '').lower())).strip()


def crossref(title, year):
    u = ('https://api.crossref.org/works?rows=5&select=DOI,title,container-title,issued,type,author'
         '&query.bibliographic=' + urllib.parse.quote(title))
    try:
        r = urllib.request.Request(u, headers={'User-Agent': UA})
        items = json.load(urllib.request.urlopen(r, timeout=30))['message']['items']
    except Exception:
        return None
    best, br = 0, None
    tn = norm(title)
    for it in items:
        t = (it.get('title') or [''])[0]
        if not t:
            continue
        s = SequenceMatcher(None, tn, norm(t)).ratio()
        if s > best:
            best, br = s, it
    if not br or best < 0.92:
        return None
    y = (br.get('issued', {}).get('date-parts') or [[None]])[0][0]
    if year and y and abs(int(y) - int(year)) > 1:
        return None
    return br


def fmt_authors(cr_authors):
    out = []
    for a in cr_authors or []:
        g, f = a.get('given', ''), a.get('family', '')
        name = (g + ' ' + f).strip()
        if not name:
            continue
        out.append(f'<strong>{name}</strong>' if name in GROUP else name)
    return ', '.join(out)


def classify(venue, cr_type):
    if PREPRINT.search(venue or ''):
        return 'preprint'
    if cr_type in ('proceedings-article',):
        return 'conference'
    if cr_type in ('book-chapter', 'book-part'):
        return 'chapter'
    if cr_type in ('book', 'monograph'):
        return 'book'
    v = (venue or '').lower()
    if re.search(r'conference|proceedings|symposium|workshop|iccv|cvpr|neurips|iclr|icml|aaai|ijcai', v):
        return 'conference'
    return 'journal'


def clean_venue(v):
    v = re.sub(r',?\s*(19|20)\d{2}\s*$', '', v or '').strip()          # 尾部年份
    v = re.sub(r',\s*\d+(\s*\(\d+\))?,\s*[\d\-–]+$', '', v).strip()     # 卷,页
    v = re.sub(r',\s*[\d\-–]+$', '', v).strip()
    return v.rstrip(',').strip()


def main():
    adds = json.load(open(sys.argv[1]))
    def work(x):
        cr = crossref(x['title'], x['year'])
        return x, cr
    out = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        for x, cr in ex.map(work, adds):
            rec = {
                'title': x['title'],
                'year': x['year'],
                'venue': clean_venue(x['venue']),
                'scholar_authors': x['authors'],
            }
            if cr:
                rec['doi'] = cr['DOI']
                rec['authors'] = fmt_authors(cr.get('author'))
                cv = (cr.get('container-title') or [''])[0]
                if cv:
                    rec['venue'] = cv
                cy = (cr.get('issued', {}).get('date-parts') or [[None]])[0][0]
                if cy and not rec['year']:
                    rec['year'] = int(cy)
                rec['type'] = classify(x['venue'], cr.get('type'))
                rec['source'] = 'crossref'
            else:
                rec['authors'] = ''
                rec['type'] = classify(x['venue'], None)
                rec['source'] = 'scholar-only'
            out.append(rec)
    json.dump(out, open('/tmp/additions.json', 'w'), ensure_ascii=False, indent=1)
    ok = sum(1 for r in out if r['source'] == 'crossref')
    print(f'{len(out)} 条待添加: CrossRef 补全 {ok} 条, 仅 Scholar 信息 {len(out)-ok} 条')
    for r in out:
        mark = ' ' if r['source'] == 'crossref' else '!'
        print(f"{mark} [{r['year']}/{r['type']:<10}] {r['title'][:62]}")
        print(f"    venue: {r['venue'][:76]}")
        print(f"    doi  : {r.get('doi','(无)')}")
        print(f"    作者 : {(r['authors'] or '(CrossRef 无, Scholar 缩写: '+r['scholar_authors']+')')[:110]}")


if __name__ == '__main__':
    main()
