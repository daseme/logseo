<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
	<link href="/static/css/complete.css" rel="stylesheet" />
<script src="http://code.jquery.com/jquery-1.7.2.min.js"></script>
<script src="/media/jquery.flot.min.js"></script>
<script type="text/javascript" charset="utf-8" src="/media/jquery.sparkline.min.js"></script>
<script type="text/javascript" charset="utf-8" src="/media/plugins/DataTables-1.9.1/media/js/jquery.dataTables.min.js"></script>
 <script type="text/javascript">
    $(function() {
        /** This code runs when everything has been loaded on the page */
        /* Inline sparklines take their values from the contents of the tag */
        $('.inlinesparkline').sparkline();

        /* Sparklines can also take their values from the first argument
        passed to the sparkline() function */
        var myvalues = [10,8,5,7,4,4,1];
        $('.dynamicsparkline').sparkline(myvalues);

        /* The second argument gives options such as chart type */
        $('.dynamicbar').sparkline(myvalues, {type: 'bar', barColor: 'green'} );

        /* Use 'html' instead of an array of values to pass options
        to a sparkline with data in the tag */
        $('.inlinebar').sparkline('html', {type: 'bar', barColor: 'red'} );
    });
    </script>


