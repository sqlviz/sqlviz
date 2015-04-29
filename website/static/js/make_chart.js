function determine_type(colname){
	/*
	Check against regex and return string for datatype for
	Datatables or None
	*/
	var re = /^(\w)*_usd$/i;
	//var found = ;
	if (re.test(colname)){
		return 'currency';
	}
	var re2 = /^(\w)*_pct$/i;
	if (re2.test(colname)){
		return 'percent';
	}
}

function make_table(columns, data, target){
		var table_name = 'table_' +  target;
		var div_name  = '#div_table_' + target;
		var pct_array = [];
		var cur_array = [];
		html = "<table class='table table-striped' id='" + table_name + "'>\n";
		html  +='<thead><tr>';
		$.each( columns, function( key, val ) {
			html += "<td>" + val  + "</td>";
			var type = determine_type(val);
			console.log(val);
			console.log(key);
			console.log(type);
			if (type){
				if (type == 'percent'){
					pct_array.push(key-1);
				}
				if (type == 'currency'){
					cur_array.push(key-1	);
				}
			}
		});
		//console.log(pct_array);
		//console.log(cur_array);
		html += "</tr></thead><tbody>\n";
		$.each( data, function( key, val ) {
			html += "<tr>";
			$.each(val, function(key2, val2) {
				if (pct_array.indexOf(key2) != -1){
					val2 = val2.toString() + '%';
				}
				if (cur_array.indexOf(key2) != -1){
					val2 = '$' + val2.toString() ;
				}
				html += "<td>" + val2 +"</td>";
			});
			html += "</tr>\n";
		});
		html += "</tbody></table>\n";
		//console.log(html);
		$(div_name).html(html);
		//console.log('#' + table_name);
		//console.log(div_name);
		$(document).ready(function() {
			$('#' + table_name).dataTable({
				"bAutoWidth": false,
				"bScrollCollapse": true,
				"dom": 'T<"clear">lfrtip',
				"tableTools": {
					"aButtons": [ "copy", "csv" ],
					"sSwfPath": "/static/DataTables-1.10.2/extensions/TableTools/swf/copy_csv_xls.swf"
				},
				'columnDefs': [
					{ 'type': 'percent', 'targets': pct_array },
					{ 'type': 'currency', 'targets': cur_array },
				]
			});
		});
	//console.log(html);
	return html;
}

function make_chart_country(columns, data, title, map_name){
	map_name = 'custom/world-highres';
	/* Assume data is array of arrays with first column being country
	and second value being numeric for chloropleth color */
	map_data = [];
		$.each( data, function( index, val ) {
		map_data.push({"hc-key":val[0],"value":val[1]});
	});
	options = {
				title : {
						text : title
				},
				mapNavigation: {
						enabled: true,
						buttonOptions: {
								verticalAlign: 'bottom'
						}
				},
				series : [{
						data : map_data,
						mapData: Highcharts.maps[map_name],
						joinBy: 'hc-key',
						name: columns[1],
						states: {
								hover: {
										color: '#BADA55'
								}
						},
						dataLabels: {
								enabled: true,
								format: '{point.name}'
						}
					}],
					colorAxis: {
							type: 'linear'
					},
		};
		return options;
}

function make_chart(columns, data, target, stacked, chart_type, title, xAxis, yAxis, yAxis_log, graph_extra){
	if (chart_type == 'country') {
		return make_chart_country(columns,data,title,map_name);
	} else {
		options = {
					chart: {
						type : chart_type,
						renderTo: target,
						zoomType: 'xy'
					},
					title: {
							text: title,
							x: -20 //center
					},
					xAxis: {
							categories: [],
							title: {
								text: columns[0]
							}
					},
					yAxis: {
							title: {
									text: columns[1]
							},
							plotLines: [{
									value: 0,
									width: 1,
									color: '#808080'
							}]
					},
					/*tooltip: {
							valueSuffix: '%',
							valuePrefix: '$'
					},*/
					legend: {
							layout: 'vertical',
							align: 'right',
							verticalAlign: 'middle',
							borderWidth: 0
					},
					series: [],
					credits: {'enabled':false},
					exporting: {'enabled':true},
			}
			var series = [];
			var cur_array = [];
			var pct_array = [];
			$.each( columns, function( index, val ) {
				if (index > 0){
					series.push({"name":val,"data":[]});
				}
			});
			// Check that the first column is a date
			//console.log(is_date(data));
			if (is_date(data)){
				//console.log('is a date');
				$.each(data, function( key, row ) {
					$.each(row, function( index, value ) {
						if (index !== 0){
							series[index -1].data.push([Date.parse(row[0]),value]);
						}
					});
				});
				delete options.xAxis.categories;
				options.xAxis.type = 'datetime';
			} else {
				//console.log('is NOT a date');
				$.each(data, function( key, row ) {
					$.each(row, function( index, value ) {
						if (index == 0){
							options.xAxis.categories.push(value)
						} else {
							series[index -1].data.push(value)
						}
					});
				});
				if (options.xAxis.categories.length > 14){
					options.xAxis.labels = {'step' : Math.max(Math.round(options.xAxis.categories.length / 7),1)}
				}
			}
			options.series = series; 
			//console.log(options)
			if (stacked == 'True'){
				options.plotOptions = {};
				options.plotOptions[chart_type] = {'stacking' :'normal'};
			}
			if (yAxis_log == 'True'){
				options.yAxis.type = 'logarithmic'
			}
			$.extend(options, graph_extra); // MUNGE GRAPH SETTINGS
			//var chart = new Highcharts.Chart(options);
			return options;    
	}
}
function is_date(data) {
	return_flag = true;
	$.each( data, function( key, row ) {
		if (isNaN(Date.parse(row[0]))) {
			//console.log('not a date!');
			return_flag = false;
			return false;
		}
	});
	return return_flag;
}
