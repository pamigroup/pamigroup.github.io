---
layout: news
title: Software
subtitle: Code released by the PAMI Research Group, University of Macau
permalink: /software/
---

<h1>Software and Code</h1>

<p>Open-source code released by current and former members of the group, from their own
GitHub accounts. Entries marked <em>before joining</em> are work done at a previous
affiliation and are listed here because the author is now with the group.</p>

{% assign items = site.data.software %}
{% if items and items.size > 0 %}
<ul class="sw-list">
  {% for s in items %}
  <li class="sw-item">
    <a class="sw-name" href="{{ s.repo }}">{{ s.name }}</a>
    {% if s.paper %}<span class="sw-paper">{{ s.paper }}{% if s.doi %} &middot; <a href="https://doi.org/{{ s.doi }}">DOI</a>{% endif %}</span>{% endif %}
    {%- if s.prior %}<span class="sw-prior">before joining</span>{% endif %}
    <p class="sw-desc">{{ s.desc }}{% if s.by %} <span class="text-muted">Maintained by {{ s.by }}.</span>{% endif %}</p>
  </li>
  {% endfor %}
</ul>
{% else %}
<p>Nothing released yet.</p>
{% endif %}
