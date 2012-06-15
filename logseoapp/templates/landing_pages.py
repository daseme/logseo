{% include "header.py" %}
<script language="javascript" type="text/javascript">
$(document).ready(function() {
    $.extend( $.fn.dataTableExt.oStdClasses, {
    "sWrapper": "dataTables_wrapper form-inline"
} );

$.fn.dataTableExt.oApi.fnPagingInfo = function ( oSettings )
{
	return {
		"iStart":         oSettings._iDisplayStart,
		"iEnd":           oSettings.fnDisplayEnd(),
		"iLength":        oSettings._iDisplayLength,
		"iTotal":         oSettings.fnRecordsTotal(),
		"iFilteredTotal": oSettings.fnRecordsDisplay(),
		"iPage":          Math.ceil( oSettings._iDisplayStart / oSettings._iDisplayLength ),
		"iTotalPages":    Math.ceil( oSettings.fnRecordsDisplay() / oSettings._iDisplayLength )
	};
}
$.extend( $.fn.dataTableExt.oPagination, {
	"bootstrap": {
		"fnInit": function( oSettings, nPaging, fnDraw ) {
			var oLang = oSettings.oLanguage.oPaginate;
			var fnClickHandler = function ( e ) {
				e.preventDefault();
				if ( oSettings.oApi._fnPageChange(oSettings, e.data.action) ) {
					fnDraw( oSettings );
				}
			};

			$(nPaging).addClass('pagination').append(
				'<ul>'+
					'<li class="prev disabled"><a href="#">&larr; '+oLang.sPrevious+'</a></li>'+
					'<li class="next disabled"><a href="#">'+oLang.sNext+' &rarr; </a></li>'+
				'</ul>'
			);
			var els = $('a', nPaging);
			$(els[0]).bind( 'click.DT', { action: "previous" }, fnClickHandler );
			$(els[1]).bind( 'click.DT', { action: "next" }, fnClickHandler );
		},

		"fnUpdate": function ( oSettings, fnDraw ) {
			var iListLength = 5;
			var oPaging = oSettings.oInstance.fnPagingInfo();
			var an = oSettings.aanFeatures.p;
			var i, j, sClass, iStart, iEnd, iHalf=Math.floor(iListLength/2);

			if ( oPaging.iTotalPages < iListLength) {
				iStart = 1;
				iEnd = oPaging.iTotalPages;
			}
			else if ( oPaging.iPage <= iHalf ) {
				iStart = 1;
				iEnd = iListLength;
			} else if ( oPaging.iPage >= (oPaging.iTotalPages-iHalf) ) {
				iStart = oPaging.iTotalPages - iListLength + 1;
				iEnd = oPaging.iTotalPages;
			} else {
				iStart = oPaging.iPage - iHalf + 1;
				iEnd = iStart + iListLength - 1;
			}

			for ( i=0, iLen=an.length ; i<iLen ; i++ ) {
				// Remove the middle elements
				$('li:gt(0)', an[i]).filter(':not(:last)').remove();

				// Add the new list items and their event handlers
				for ( j=iStart ; j<=iEnd ; j++ ) {
					sClass = (j==oPaging.iPage+1) ? 'class="active"' : '';
					$('<li '+sClass+'><a href="#">'+j+'</a></li>')
						.insertBefore( $('li:last', an[i])[0] )
						.bind('click', function (e) {
							e.preventDefault();
							oSettings._iDisplayStart = (parseInt($('a', this).text(),10)-1) * oPaging.iLength;
							fnDraw( oSettings );
						} );
				}

				// Add / remove disabled classes from the static elements
				if ( oPaging.iPage === 0 ) {
					$('li:first', an[i]).addClass('disabled');
				} else {
					$('li:first', an[i]).removeClass('disabled');
				}

				if ( oPaging.iPage === oPaging.iTotalPages-1 || oPaging.iTotalPages === 0 ) {
					$('li:last', an[i]).addClass('disabled');
				} else {
					$('li:last', an[i]).removeClass('disabled');
				}
			}
		}
	}
} );
    var oTable = $('#example').dataTable( {
        "sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
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
        font-size:6px;
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
    <div class="row-fluid">
        <div class="span12">
            <div id="chart_container">
                <div id="y_axis"></div>
                <div id="chart"></div>
            </div>
        </div>
    </div>

<div class="row-fluid">
    <div class="span12">
        <br><br>
        {% include "date_form.html" %}


     <table cellpadding="0" cellspacing="0" border="0" class="table table-striped table-bordered" id="example">
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
            </div></div>
<script>

var graph = new Rickshaw.Graph( {
        element: document.querySelector("#chart"),
        width: 440,
        height: 250,
        series: [{
            data: {{t_series|safe}},
            color: '#E9967A'
            }]
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
		var content = swatch + "distinct landing pages" + ": " + parseInt(y) + '<br>' + date;
		return content;
	}
} );
</script>

</body>
{% include "footer.py" %}


