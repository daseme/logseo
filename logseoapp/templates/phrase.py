{% include "header.py" %}

    </head>
<body id="dt_example">

{% include "navigation.html" %}
{% include "subpage-sidenav.html" %}
<div class="span10">
{% include "date_form.html" %}
    <div class="row-fluid">
        <div class="span12">
            <br><br>

            {% block content %}

                    {% for dict in phrase_name %}
                    <h1>{{ dict.phrase }}</h1>
                    {% endfor %}


                    <span class="inlinesparkline">
                        {% for dict in rankings %}
                        -{{ dict.position }}{% if not forloop.last %}, {% endif %}
                        {% endfor %}
                    </span>

<h2>Pages accessed by this search term</h2>
{% regroup pages by page_id__page as rank_list %}
<table cellpadding="0" cellspacing="0" border="0" class="table table-striped table-bordered" id="example">
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

