---
layout: default
title: home
---

<div class="row">
  <div class="column">
  <div class="img-container">
  <img src="{{site.url}}/assets/images/heart-brain.png">
  </div>
  </div>
  <div class="column">
  <h2> Discover </h2>
  </div>
  <div class="column">
  {% for item in site.contribution_types %}
  <p> 🧠 <a href="{{site.url}}/contributions#{{ item | slugify }}" target="_blank">{{item}}</a></p>
  {% endfor %}
  </div>
</div>
