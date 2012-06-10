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
<style>
#chart_container {
        position: relative;
        font-family: Arial, Helvetica, sans-serif;
}
#chart {
        position: relative;
        left: 40px;
}
#y_axis {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 40px;
}
		.rickshaw_graph .detail .x_label { display: none }
		.rickshaw_graph .detail .item { line-height: 1.4; padding: 0.5em }
		.detail_swatch { float: right; display: inline-block; width: 10px; height: 10px; margin: 0 4px 0 0 }
		.rickshaw_graph .detail .date { color: #a0a0a0 }
</style>

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
<br><br>

			<div id="container">
<div id="chart_container">
        <div id="y_axis"></div>
        <div id="chart"></div>
</div>
<br><br>
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


<script>

var graph = new Rickshaw.Graph( {
        element: document.querySelector("#chart"),
        width: 540,
        height: 240,
        series: [{
                name: 'rank phrase',
                data: {{rank_phrase|safe}},
                color: '#E9967A'
            },
            {
                name:'all phrase',
                data: {{all_phrase|safe}},
                color: 'steelblue'
            }

            ]
} );

var x_axis = new Rickshaw.Graph.Axis.Time( { graph: graph } );

var y_axis = new Rickshaw.Graph.Axis.Y( {
        graph: graph,
        orientation: 'left',
        tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
        element: document.getElementById('y_axis'),
} );

graph.render();
var hoverDetail = new Rickshaw.Graph.HoverDetail( {
	graph: graph,
	formatter: function(series, x, y) {
		var date = '<span class="date">' + new Date(x * 1000).toUTCString() + '</span>';
		var swatch = '<span class="detail_swatch" style="background-color: ' + series.color + '"></span>';
		var content = swatch + series.name + ": " + parseInt(y) + '<br>' + date;
		return content;
	}
} );
</script>


</body>
{% include "footer.py" %}

