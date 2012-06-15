{% include "header.py" %}

    </head>
<body id="dt_example">
{% include "navigation.html" %}
{% include "subpage-sidenav.html" %}

    <div class="span10">
        <div id="chart_container">
            <div id="y_axis"></div>
            <div id="chart"></div>
        </div>
    </div>


<div class="span10">

<br><br>
{% include "date_form.html" %}
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

<div>
<h1>Pages accessed by this search term</h1>
{% regroup pages by page_id__page as rank_list %}
<table class="pretty">
		<thead>
		<tr>
			<th>page</th>
			<th>rankings</th>
      </tr>
      </thead>
	    <tbody>
{% for page_id__page in rank_list %}
<tr><td>{{ page_id__page.grouper }}</td><td>
        <span class="inlinesparkline" style="width:40px;">
        {% for item in page_id__page.list %}
        -{{ item.position }}{% if not forloop.last %}, {% endif %}
        {% endfor %}

    </td></tr>
{% endfor %}
</tbody>
</table>
{% endblock %}
</div>
{% include "footer.py" %}

