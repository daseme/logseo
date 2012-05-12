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
			<th rowspan="2" width="280px">Phrase</th>
			<th colspan="8">Metrics for Ranked Phrases</th>
		</tr>
		<tr>
			<th>engine</th>
			<th>ipcount</th>
			<th>rcount</th>
			<th>ratio</th>
			<th>avgrank</th>
			<th>stdev</th>
			<th>chart2gohere</th>
      </tr>
      </thead>
	    <tbody>




 {% block content %}
     {% for dict in ip_cnts %}

		<tr>


             <td>placeholder</td>


           <td style="text-align:left;"><a href="/phrase/{{dict.phrase_id}}/" style="text-decoration:none;">{{dict.phrase_id__phrase}}</a></td>
           <td>G</td><td>{{dict.num_ips}}</td>
           <td>{{dict.num_rank}}</td>
           <td>{{ dict.ratio }}</td>
           <td>{{dict.avg_rank|floatformat:2}}</td>
           <td>{{dict.st_rank|floatformat:2}}</td>
           <td>{{dict.phrase_id__tags__name}}</td>
		</tr>
    {% endfor %}


{% endblock %}

        </tbody>
			</table>

{% include "footer.py" %}
