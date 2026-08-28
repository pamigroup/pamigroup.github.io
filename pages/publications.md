---
layout: news
title: Publications
subtitle: Publications of the PAMI Research Group, University of Macau
permalink: /publications
---

<h1>Publications</h1>

<p>
  {{ site.data.publications.papers | size }} entries. See
  <a href="https://scholar.google.com/citations?hl=en&user=dlZuABAAAAAJ&view_op=list_works&sortby=pubdate">Google Scholar</a>
  for citation counts. <span class="text-muted">An asterisk marks the corresponding author.</span>
</p>

{% assign selected = site.data.publications.papers | where: "selected", true %}
{% if selected.size > 0 %}
<section class="pub-selected">
  <h2 class="people-section-title">Selected Publications</h2>
  <ol class="pub-list">
    {% for p in selected %}{% include publication.html paper=p %}{% endfor %}
  </ol>
</section>
{% endif %}

<section>
  <h2 class="people-section-title">All Publications</h2>

  {% assign papers = site.data.publications.papers %}
  {% assign n_journal = papers | where: "type", "journal" | size %}
  {% assign n_conf    = papers | where: "type", "conference" | size %}
  {% assign n_book    = papers | where: "type", "book" | size %}
  {% assign n_chap    = papers | where: "type", "chapter" | size %}

  <div class="pub-controls" hidden>
    <div class="pub-filters" role="group" aria-label="Filter publications by type">
      <button type="button" class="pub-filter is-active" data-filter="all" aria-pressed="true">All <span>{{ papers | size }}</span></button>
      <button type="button" class="pub-filter" data-filter="journal" aria-pressed="false">Journal <span>{{ n_journal }}</span></button>
      <button type="button" class="pub-filter" data-filter="conference" aria-pressed="false">Conference <span>{{ n_conf }}</span></button>
      <button type="button" class="pub-filter" data-filter="book" aria-pressed="false">Books <span>{{ n_book }}</span></button>
      <button type="button" class="pub-filter" data-filter="chapter" aria-pressed="false">Chapters <span>{{ n_chap }}</span></button>
    </div>
    <label class="sr-only" for="pub-search">Search publications</label>
    <input type="search" id="pub-search" class="pub-search" placeholder="Filter by title, author or venue…" autocomplete="off">
    <p class="pub-count" id="pub-count" aria-live="polite"></p>
  </div>

  {% assign by_year = papers | group_by: "year" | sort: "name" | reverse %}

  <nav class="pub-years" aria-label="Jump to year">
    {% for g in by_year %}<a href="#y{{ g.name }}">{{ g.name }}</a>{% endfor %}
  </nav>

  {% for g in by_year %}
  <div class="pub-year-block" data-year="{{ g.name }}">
    <h3 id="y{{ g.name }}" class="pub-year">{{ g.name }}</h3>
    <ol class="pub-list">
      {% assign ordered = g.items | sort: "type" %}
      {% for p in ordered %}{% include publication.html paper=p %}{% endfor %}
    </ol>
  </div>
  {% endfor %}
</section>

<script src="{{ '/assets/js/publications.js' | relative_url }}"></script>
