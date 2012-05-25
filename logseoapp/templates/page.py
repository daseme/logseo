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
{% for dict in page_name %}
<h1>{{ dict.page }}</h1>
{% endfor %}
<br>
<div style="width:50px;">
<span class="inlinesparkline" style="width:40px;">
{% for dict in rankings %}
    -{{ dict.position }}{% if not forloop.last %}, {% endif %}
{% endfor %}
</span>
</div>

<div>
<h1>Kws that sent folks to this page</h1>
{{ kws }}
{% regroup kws by phrase_id__phrase as rank_list %}

<table class="pretty">
		<thead>
		<tr>
			<th>phrase</th>
            <th>ipcount</th>
			<th>rankings</th>
      </tr>
      </thead>
	    <tbody>
{% for phrase_id__phrase in rank_list %}
<tr>
    <td>
    {{ phrase_id__phrase.grouper }}
    </td>
    <td></td>
    <td>
        <span class="inlinesparkline" style="width:40px;">
        {% for item in phrase_id__phrase.list %}
        -{{ item.position }}{% if not forloop.last %}, {% endif %}
        {% endfor %}
        </span>{{item.num_google}}
    </td>

    </tr>
{% endfor %}
</tbody>
</table>
{% endblock %}
</div>
{% include "footer.py" %}


