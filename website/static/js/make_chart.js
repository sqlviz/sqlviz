function percent_formatter(str) {
		return str + '%';
}
function currency_formatter(str) {
		return '$' + str ;
}
function url_formatter(str) {
		// Truncate link after 50 characters
		return '<a href="' + str + '">' + str.substring(0,50) + '</a>';
}
function img_formatter(str) {
		return '<img src="' + str + '"></img>';
}
function colname_to_type(colname){
	//return colname;
	var d = {
			'currency': {
					re: /^(\w)*_usd$/i,
					type: 'currency',
					formatter: currency_formatter
			},
					'percent': {
					re: /^(\w)*_pct$/i,
					type: 'percent',
					formatter: percent_formatter
			},
					'img': {
					re: /^(\w)*_img$/i,
					type: 'img',
					formatter: img_formatter
			},
					'url': {
					re: /^(\w)*_url$/i,
					type: 'url',
					formatter: url_formatter
			},
	};
	var return_val = false;
	$.each(d, function (type, re_info) {
			re = re_info['re'];
			if (re.test(colname)) {
				return_val = re_info;
			}
	});
	return return_val;
}

function make_table(columns, data, target){
		var table_name = 'table_' +  target;
		var div_name  = '#div_table_' + target;
		var pct_array = [];
		var cur_array = [];
		html = "<table class='table table-striped' id='" + table_name + "'>\n";
		html  +='<thead><tr>';
		var col_formatter_dict = {};
		$.each( columns, function( key, val ) {
			html += "<td>" + val  + "</td>";
			col_data =  colname_to_type(val);
			if (col_data){
				col_formatter_dict[key] = col_data['formatter'];
				type  = col_data['type'];
				if (type == 'percent'){
					pct_array.push(key - 1);
				}
				if (type == 'currency'){
					cur_array.push(key - 1);
				}
			}
		});
		html += "</tr></thead><tbody>\n";
		$.each( data, function( key, val ) {
			html += "<tr>";
			$.each(val, function(key2, val2) {
				//console.log(key2);
				if (key2 in col_formatter_dict) {
					//console.log('formatted!');
					val2 = col_formatter_dict[key2](val2);
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
					"sSwfPath": "/static/DataTables-1.10.7/extensions/TableTools/swf/copy_csv_xls.swf"
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
					options.xAxis.labels = {'step' : Math.max(Math.round(options.xAxis.categories.length / 7),1)};
				}
			}
			options.series = series;
			//console.log(options)
			if (stacked == 'True'){
				options.plotOptions = {};
				options.plotOptions[chart_type] = {'stacking' :'normal'};
			}
			if (yAxis_log == 'True'){
				options.yAxis.type = 'logarithmic';
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
