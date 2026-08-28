#!/usr/bin/env python3
"""站点自检。加完新人 / 改完数据后跑一次，能挡住最容易犯的错。

    python3 tools/check_site.py                 只检查源文件
    python3 tools/check_site.py --site _site    额外核对构建产物的条目数

第二种用法能挡住"构建成功但页面是空的"这类静默故障：Liquid 里写错一个变量名
不会报错，只会安静地渲染出零个人。

退出码非 0 表示有问题。
"""
import glob, os, re, sys

try:
    import yaml
except ImportError:
    sys.exit('需要 PyYAML: pip install pyyaml')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

STATUSES = {'Director', 'Postdoc', 'PhD', 'MSc', 'Visiting', 'RA'}
REQUIRED = ('title', 'pname', 'photo', 'status', 'eml', 'desp')
MAX_IMG_KB = 150
MAX_AVATAR_KB = 60

errors, warnings = [], []


def front_matter(path):
    s = open(path, encoding='utf-8').read()
    m = re.match(r'^---\r?\n(.*?)\r?\n---', s, re.S)
    if not m:
        errors.append(f'{path}: 缺少 front matter')
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        errors.append(f'{path}: front matter 不是合法 YAML: {e}')
        return None


def check_people():
    seen_perma, seen_url = {}, {}
    files = sorted(glob.glob('_people/*.md'))
    if not files:
        errors.append('_people/ 下没有任何成员文件')
    for f in files:
        fm = front_matter(f)
        if fm is None:
            continue
        for k in REQUIRED:
            if not str(fm.get(k) or '').strip():
                errors.append(f'{f}: 缺少必填字段 {k}')
        st = fm.get('status')
        if st not in STATUSES:
            errors.append(f'{f}: status="{st}" 不在允许值 {sorted(STATUSES)} 中，此人不会显示在任何分组里')

        photo = str(fm.get('photo') or '').lstrip('/')
        if photo in seen_perma:
            errors.append(f'{f}: photo 与 {seen_perma[photo]} 重复')
        seen_perma[photo] = f

        if not photo:
            pass                                   # 上面的必填检查已经报过
        elif not os.path.isfile(photo):
            errors.append(f'{f}: 找不到照片 {photo}')
        else:
            check_photo(f, photo)

        j = fm.get('joined')
        if j and not re.fullmatch(r'(19|20)\d{2}(-(0[1-9]|1[0-2]))?', str(j)):
            errors.append(f'{f}: joined 应为 YYYY 或 YYYY-MM，实际 {j}')

        # 同一个外链挂在两个人身上，通常是复制粘贴错误
        for key in ('github', 'google_scholar', 'website', 'orcid', 'linkedin'):
            v = str(fm.get(key) or '').strip()
            if not v:
                continue
            if v in seen_url:
                errors.append(f'{f}: {key} 与 {seen_url[v]} 指向同一个 URL {v}')
            seen_url[v] = f
            if not v.startswith('http'):
                errors.append(f'{f}: {key} 不是完整 URL: {v}')
            if 'orcid.org/my-orcid' in v:
                errors.append(f'{f}: {key} 用了需要登录的 my-orcid 链接，应改为 https://orcid.org/0000-...')


def check_photo(src, photo):
    try:
        from PIL import Image
    except ImportError:
        warnings.append('未安装 Pillow，跳过照片尺寸检查')
        return
    kb = os.path.getsize(photo) / 1024
    if kb > MAX_AVATAR_KB:
        warnings.append(f'{src}: 照片 {kb:.0f} KB 超过 {MAX_AVATAR_KB} KB，建议压到 400x400 / q82')
    im = Image.open(photo)
    if im.format != 'JPEG':
        errors.append(f'{src}: {photo} 扩展名是 .jpg 但实际格式是 {im.format}，'
                      f'Content-Type 会发错，请真正转成 JPEG')
    w, h = im.size
    if w != h:
        errors.append(f'{src}: 照片 {w}x{h} 不是正方形，圆形头像会被裁切或留白')
    elif w < 400:
        warnings.append(f'{src}: 照片 {w}x{h} 小于 400x400，高分屏上会发糊')


def check_data():
    for name in ('publications', 'news', 'alumni'):
        p = f'_data/{name}.yml'
        if not os.path.isfile(p):
            warnings.append(f'{p} 不存在')
            continue
        try:
            yaml.safe_load(open(p, encoding='utf-8'))
        except yaml.YAMLError as e:
            errors.append(f'{p}: 不是合法 YAML: {e}')

    p = '_data/publications.yml'
    if os.path.isfile(p):
        d = yaml.safe_load(open(p, encoding='utf-8')) or {}
        # 收录标准：Bob Zhang 必须是作者之一，他不在的不算本组论文
        BOB = re.compile(r'\b(Bob\s+Zhang|Yi-?Bo\s+(Bob\s+)?Zhang|B\.\s*Zhang|B\s+Zhang'
                         r'|Y\.?\s*B\.?\s*Zhang)\b')
        seen_titles = {}
        for i, x in enumerate(d.get('papers', []), 1):
            for k in ('title', 'authors', 'venue', 'year', 'type'):
                if not x.get(k):
                    errors.append(f'{p} 第 {i} 条: 缺少 {k}')
            if x.get('type') not in ('book', 'journal', 'conference', 'chapter', 'preprint'):
                errors.append(f'{p} 第 {i} 条: type={x.get("type")} 非法')
            doi = str(x.get('doi') or '')
            if doi and not doi.startswith('10.'):
                errors.append(f'{p} 第 {i} 条: doi 应以 10. 开头，实际 {doi}')

            authors = re.sub(r'<[^>]*>', '', str(x.get('authors') or ''))
            title = str(x.get('title') or '')
            if authors and not BOB.search(authors):
                errors.append(f'{p} 第 {i} 条: 作者中没有 Bob Zhang，不属于本组论文 -> {title[:60]}')
            elif authors and '<strong>' not in str(x.get('authors') or ''):
                warnings.append(f'{p} 第 {i} 条: Bob Zhang 没有用 <strong> 标出 -> {title[:60]}')

            key = re.sub(r'[^a-z0-9]', '', title.lower())[:70]
            if key and key in seen_titles:
                warnings.append(f'{p} 第 {i} 条: 标题与第 {seen_titles[key]} 条高度重复 -> {title[:60]}')
            seen_titles[key] = i


def check_assets():
    # 先收集所有被引用的资源名，未被引用的图只是仓库负担，不影响访客
    referenced = set()
    for pat in ('*.html', '*.md', '*.yml', '*.css', '*.js',
                'pages/*', '_includes/*', '_layouts/*', '_data/*'):
        for src in glob.glob(pat) + glob.glob('**/' + pat, recursive=True):
            if not os.path.isfile(src) or src.startswith('assets/img'):
                continue
            try:
                referenced.add(open(src, encoding='utf-8', errors='ignore').read())
            except OSError:
                pass
    blob = '\n'.join(referenced)

    # 头像路径写在成员 front matter 的 photo 字段里，需单独登记
    liquid_used = set()
    for f in glob.glob('_people/*.md'):
        fm = front_matter(f) or {}
        ph = str(fm.get('photo') or '')
        if ph:
            liquid_used.add(os.path.basename(ph))

    for f in glob.glob('assets/img/**/*', recursive=True):
        if not os.path.isfile(f):
            continue
        kb = os.path.getsize(f) / 1024
        base = os.path.basename(f)
        used = base in blob or base in liquid_used
        limit = MAX_IMG_KB * 2 if '@2x' in f else MAX_IMG_KB   # 视网膜屏 2x 图允许翻倍
        if not used:
            warnings.append(f'{f}: {kb:.0f} KB，仓库中没有任何引用；'
                            f'不影响访客加载，但每次 clone 和部署都带着它')
        elif kb > limit:
            warnings.append(f'{f}: {kb:.0f} KB 超过 {limit:.0f} KB，会拖慢页面')


def check_built_site(site_dir):
    """核对构建产物里的条目数与源数据一致。"""
    people_page = os.path.join(site_dir, 'people.html')
    if not os.path.isfile(people_page):
        errors.append(f'{people_page} 不存在，构建产物路径给错了?')
        return
    html = open(people_page, encoding='utf-8').read()

    n_src = len(glob.glob('_people/*.md'))
    n_out = html.count('class="person-card"')
    if n_out != n_src:
        errors.append(f'people.html 渲染出 {n_out} 张人员卡片，_people/ 下有 {n_src} 个文件；'
                      f'通常是 _includes/person-group.html 里的变量名或 status 值对不上')

    alum = yaml.safe_load(open('_data/alumni.yml', encoding='utf-8')) or {}
    n_alum = sum(len(v) for v in alum.values())
    n_alum_out = html.count('class="alumni-name"')
    if n_alum_out != n_alum:
        errors.append(f'people.html 渲染出 {n_alum_out} 条校友，_data/alumni.yml 有 {n_alum} 条')

    pub_page = os.path.join(site_dir, 'publications.html')
    if os.path.isfile(pub_page):
        n_pub = len((yaml.safe_load(open('_data/publications.yml', encoding='utf-8')) or {}).get('papers', []))
        n_pub_out = open(pub_page, encoding='utf-8').read().count('class="pub-item"')
        if n_pub_out != n_pub:
            errors.append(f'publications.html 渲染出 {n_pub_out} 条，_data/publications.yml 有 {n_pub} 条')


check_people()
check_data()
check_assets()
if '--site' in sys.argv:
    check_built_site(sys.argv[sys.argv.index('--site') + 1])

for w in warnings:
    print(f'WARN  {w}')
for e in errors:
    print(f'ERROR {e}')
print(f'\n{len(errors)} 个错误, {len(warnings)} 个警告')
sys.exit(1 if errors else 0)
