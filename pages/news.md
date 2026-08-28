---
layout: news
title: News and Events
subtitle: Recent news from the PAMI Research Group, University of Macau
permalink: /news
---

<h1>News and Events</h1>

{% assign items = site.data.news %}
{% if items and items.size > 0 %}
<ul class="news-list">
  {% for n in items %}
  <li class="news-item">
    <span class="news-date">{{ n.date }}</span>
    {% if n.tag %}<span class="news-tag news-tag-{{ n.tag }}">{{ n.tag }}</span>{% endif %}
    <span class="news-text">{{ n.text | markdownify | remove: '<p>' | remove: '</p>' }}</span>
  </li>
  {% endfor %}
</ul>
{% else %}
<p>No news yet.</p>
{% endif %}
