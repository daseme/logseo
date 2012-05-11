{% include "header.py" %}

    </head>
<body id="dt_example">
	<div id="header">

<ul id="list-nav">
<li><a href="/">Home</a></li>
<li><a href="ranks.html">Ranks</a></li>
<li><a href="query_table.html">Queries</a></li>
<li><a href="#">Products</a></li>
<li><a href="#">Contact</a></li>
</ul>
</div>


<div id="container">
{% block content %}
{% for dict in phrase_name %}
<h1>{{ dict.phrase }}</h1>
{% endfor %}
<br>
<div style="width:50px;">
<span class="inlinesparkline" style="width:40px;">
{% for dict in rankings %}
    -{{ dict.position }}{% if not forloop.last %}, {% endif %}
{% endfor %}
</span>
</div>

{% regroup pages by page_id__page as rank_list %}

<ul>
{% for page_id__page in rank_list %}

    <li>{{ page_id__page.grouper }}
        <span class="inlinesparkline" style="width:40px;">
        {% for item in page_id__page.list %}
        -{{ item.position }}{% if not forloop.last %}, {% endif %}
        {% endfor %}
        </span>
    </li>
{% endfor %}
</ul>
{% endblock %}

{% include "footer.py" %}

