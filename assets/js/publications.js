/* 出版物页的类型筛选与关键词过滤。无外部依赖，纯前端。 */
(function () {
  var items   = Array.prototype.slice.call(document.querySelectorAll('.pub-year-block .pub-item'));
  var blocks  = Array.prototype.slice.call(document.querySelectorAll('.pub-year-block'));
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.pub-filter'));
  var search  = document.getElementById('pub-search');
  var counter = document.getElementById('pub-count');
  var controls= document.querySelector('.pub-controls');
  var selected= document.querySelector('.pub-selected');
  var yearNav = document.querySelector('.pub-years');
  if (!items.length) return;

  // 控件默认隐藏，脚本跑起来才显示，避免无 JS 时出现点不动的死控件
  if (controls) controls.hidden = false;

  var type = 'all';

  function apply() {
    var q = (search.value || '').trim().toLowerCase();
    var shown = 0;
    items.forEach(function (li) {
      var okType = type === 'all' || li.getAttribute('data-type') === type;
      var okText = !q || li.getAttribute('data-search').indexOf(q) !== -1;
      var vis = okType && okText;
      li.hidden = !vis;
      if (vis) shown++;
    });
    // 整年为空时连同年份标题一起隐藏
    blocks.forEach(function (b) {
      var any = Array.prototype.some.call(b.querySelectorAll('.pub-item'), function (li) { return !li.hidden; });
      b.hidden = !any;
    });
    // Selected Publications 不参与筛选逻辑，但筛选生效时整块隐藏，
    // 否则页面上会出现与计数不符的条目
    var filtering = type !== 'all' || !!q;
    if (selected) selected.hidden = filtering;
    // 年份导航跟随隐藏，避免锚点指向已隐藏的区块
    if (yearNav) {
      Array.prototype.forEach.call(yearNav.querySelectorAll('a'), function (a) {
        var b = document.querySelector('.pub-year-block[data-year="' + a.textContent.trim() + '"]');
        a.hidden = !!(b && b.hidden);
      });
    }
    counter.textContent = shown === items.length ? '' : 'Showing ' + shown + ' of ' + items.length;
  }

  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      buttons.forEach(function (o) { o.classList.remove('is-active'); o.setAttribute('aria-pressed', 'false'); });
      b.classList.add('is-active');
      b.setAttribute('aria-pressed', 'true');
      type = b.getAttribute('data-filter');
      apply();
    });
  });
  search.addEventListener('input', apply);
  apply();
})();
