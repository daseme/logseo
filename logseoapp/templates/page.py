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


