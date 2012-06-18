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
#Rickshaw
#chart_container {
        position: relative;
        font-family: Arial, Helvetica, sans-serif;
}
#chart {
        float:left;
}
#y_axis {
	float: left;
	width: 40px;
}
		.rickshaw_graph .detail .x_label { display: none }
		.rickshaw_graph .detail .item { line-height: 1.4; padding: 0.5em }
		.detail_swatch { float: right; display: inline-block; width: 10px; height: 10px; margin: 0 4px 0 0 }
		.rickshaw_graph .detail .date { color: #a0a0a0 }
</style>

</head>
<body id="dt_example">
{% include "navigation.html" %}
{% include "subpage-sidenav.html" %}

<div class="span10">
{% include "date_form.html" %}
    <div class="row-fluid">
        <div class="span5">
        <h2>Ranked/Unranked Kws per Week</h2>
        <hr>
            <div id="chart_container">
                <div id="y_axis"></div>
                <div id="chart"></div>
            </div>
        </div>
        <div class="span5">
            <h2>Search Engines per Week</h2>
            <p>like this</p>
        </div>
        <div class="span5">
            <div id="chart_container">
                <div id="y_axis"></div>
                <div id="chart"></div>
            </div>
        </div>

    <div>



<div class="row-fluid">
<div class="span10">
<br><br>



       <table cellpadding="0" cellspacing="0" border="0" class="table table-striped table-bordered" id="example">
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
        width: 440,
        height: 240,
        series: [{
                name: 'rank phrase',
                data: {{rank_phrase|safe}},
                color: '#E9967A'
            },
            {
                name:'all phrase',
                data: {{all_phrase|safe}},
                color: '#ADB7AB'
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

