#!/usr/bin/env python3
"""站点自检。加完新人 / 改完数据后跑一次，能挡住最容易犯的错。

    python3 tools/check_site.py

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
REQUIRED = ('title', 'pname', 'layout', 'permalink', 'status', 'position', 'eml', 'desp')
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

        perma = str(fm.get('permalink') or '')
        if perma in seen_perma:
            errors.append(f'{f}: permalink 与 {seen_perma[perma]} 重复')
        seen_perma[perma] = f

        base = os.path.basename(f)[:-3]
        if perma and perma.split('/')[-1] != base:
            warnings.append(f'{f}: 文件名 {base} 与 permalink 末段 {perma.split("/")[-1]} 不一致，容易混淆')

        photo = 'assets/img' + perma + '.jpg'
        if not os.path.isfile(photo):
            errors.append(f'{f}: 找不到照片 {photo}（布局按 permalink 拼路径且写死 .jpg）')
        else:
            check_photo(f, photo)

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
    for name in ('publications', 'news', 'software', 'alumni'):
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
        for i, x in enumerate(d.get('papers', []), 1):
            for k in ('title', 'authors', 'venue', 'year', 'type'):
                if not x.get(k):
                    errors.append(f'{p} 第 {i} 条: 缺少 {k}')
            if x.get('type') not in ('book', 'journal', 'conference', 'chapter'):
                errors.append(f'{p} 第 {i} 条: type={x.get("type")} 非法')
            doi = str(x.get('doi') or '')
            if doi and not doi.startswith('10.'):
                errors.append(f'{p} 第 {i} 条: doi 应以 10. 开头，实际 {doi}')


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

    # 头像由布局用 {{ p.permalink }} 拼出来，源码里搜不到文件名，需单独登记
    liquid_used = set()
    for f in glob.glob('_people/*.md'):
        fm = front_matter(f) or {}
        perma = str(fm.get('permalink') or '')
        if perma:
            liquid_used.add(os.path.basename(perma) + '.jpg')

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


check_people()
check_data()
check_assets()

for w in warnings:
    print(f'WARN  {w}')
for e in errors:
    print(f'ERROR {e}')
print(f'\n{len(errors)} 个错误, {len(warnings)} 个警告')
sys.exit(1 if errors else 0)
