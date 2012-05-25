{% include "header.py" %}
<script language="javascript" type="text/javascript">
$(document).ready(function() {
    var oTable = $('#example').dataTable( {
        "bPaginate": true,
		"sPaginationType": "full_numbers",
        "aaSorting": [[ 3, "desc" ]]
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

<form method="GET">
<select name="start_date">
{% for date in dates %}
    <option value="{{ date.refdate }}" {% if start_date =  date.refdate %} selected {% endif %}>{{ date.refdate }}</option>
{% endfor %}

</select>

<select name="end_date">
{% for date in dates %}
    <option value="{{ date.refdate }}"  {% if end_date =  date.refdate %} selected {% endif %}>{{ date.refdate }}</option>
{% endfor %}
</select>
<input type="submit" name="submit" class="submit" value="filter dates" />
</form>


      <table id="example"  border="0" cellpadding="0" cellspacing="0" class="pretty">
		<thead>
		<tr>
			<th width="4%" rowspan="2"></th>
			<th rowspan="2" width="280px">Page</th>
			<th colspan="8">Metrics for Pages</th>
		</tr>
		<tr>
			<th>gcount</th>
			<th>bcount</th>
            <th>ycount</th>
            <th>phrase count</th>
            <th>ip count</th>
            <th>ip per q</th>

      </tr>
      </thead>
	    <tbody>




 {% block content %}

     {% for dict in combo %}

		<tr>


             <td>placeholder</td>


           <td style="text-align:left;">
           <a href="/landing_pages/page/{{dict.page_id}}/" style="text-decoration:none;">{{dict.page_id__page}}</a></td>
           <td>{{ dict.num_google}} </td><td>{{dict.num_bing}}</td><td>{{dict.num_yahoo}}</td>
           <td>{{dict.num_phrase}}</td><td>{{dict.num_ip}}</td><td>{{dict.ip_per_q}}</td>

		</tr>
    {% endfor %}
{{ gcount }}

{% endblock %}

        </tbody>
			</table>

</body>
{% include "footer.py" %}


