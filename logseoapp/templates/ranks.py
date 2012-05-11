{% include "header.py" %}

 <table>
		 <tr>
		<form name='greForm'>
<td>Date Range:</td><td><select id="date1">
<?php
$date_display = "<option value=''>Any Date</option>";
while($row3 = mysql_fetch_array($qry_result3)){
	$date_display .= "<option value='$row3[refdate]'>$row3[refdate]</option>";
}

echo $date_display;
?>
</select>
 TO
<select id="date2">
<?php
echo $date_display;
mysql_close();
?>
</select></td>
</tr><tr>
<td>&nbsp;</td><td><input type='button' onclick='ajaxFunction()' value='Query Logseo' /></td>
</tr>
</form>
	 </table>
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
		<tr>
    {% for object in objects %}
             <td></td>
			<td>{{ object.phrase }}</td>
            {% for tag in object.tags.all %}
            <td>{{ tag.name }}</td>

           <td></td><td></td><td></td><td></td><td></td><td></td>
		</tr>
         {% endfor %}
     {% endfor %}
        </tbody>
			</table>

{% include "footer.py" %}

