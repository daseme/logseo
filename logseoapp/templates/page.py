{% include "header.py" %}
<script language="javascript" type="text/javascript">
$(document).ready(function() {
    var oTable = $('#example').dataTable( {
        "bPaginate": true,
		"sPaginationType": "full_numbers",
        "aaSorting": [[ 2, "desc" ]]
        });
} );

</script>
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

{% regroup kws by phrase_id__phrase as rank_list %}

<table id="example" class="pretty">
		<thead>
		<tr>
			<th>phrase</th>
            <th>ipcount</th>
			<th>gcount</th>
            <th>bing</th>
            <th>yahoo</th>
      </tr>
      </thead>
	    <tbody>

{% for phrase_id__phrase in rank_list %}
<tr>
     <td style="text-align:left;">
    {{ phrase_id__phrase.grouper }}
    </td>

    {% for item in phrase_id__phrase.list %}
    <td>
     {{ item.num_ip }}
    </td>
    <td>
     {{item.num_google}}
    </td>
        <td>
     {{item.num_bing}}
    </td>
        <td>
     {{item.num_yahoo}}
    </td>
        {% endfor %}
    </tr>
{% endfor %}
</tbody>
</table>
{% endblock %}
</div>
{% include "footer.py" %}


