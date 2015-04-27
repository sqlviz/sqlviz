function send_data_ml_adhoc(query_id, destination_div){
	// TODO make sure that get parameters are used here!
	var model_type = $("#model_type_" + query_id + " option:selected").val();
	var target_column = $("#column_names_" + query_id + " option:selected").val();
	// TODO use http://api.jquery.com/serialize/
	var str = $( "#ml_adhoc_"+query_id ).serialize();
	data = {'query_id': query_id,
		'model_type' : model_type,
		'target_column' : target_column,
	};
	//console.log(data)
	//console.log(str)
	$.get('{% url "ml:build_model_adhoc" %}',data, function( json_data ) {
		return_str = ''
		$.each( json_data.data, function( key, value ) {
			return_str = return_str + '\n' +  key + ' \n' + value;
		});
		$("#ml_output_" + query_id).text(return_str);
		$("#ml_output_" + query_id).removeClass("hide");
	}).fail(function() {
			alert('oops');
	});
	;
};
function display_data(query_id, url, parameters, hide_table, chart_type, title, stacked, log_scale_y, graph_extra){
	$( "#error_"+query_id ).hide();
	$.getJSON(url, parameters, function( json_data ) {
		$( "#waiting_" + query_id).empty();
		if (json_data.error == false){
			if (hide_table ==  'False') {
				make_table(json_data.data.columns, json_data.data.data, query_id);  
			}
			if (chart_type == 'country'){
				options = make_chart_country(json_data.data.columns, json_data.data.data, title,'custom/world')
				$('#chart_' + query_id).highcharts('Map', options);
			}
			else if (chart_type != 'None'){
				options = make_chart(json_data.data.columns, json_data.data.data, 'chart_' + query_id, stacked, chart_type,title, 'Xaxis Title', 'yAxis Title' ,log_scale_y,graph_extra);
					var chart = new Highcharts.Chart(options);
			};
			$( "#execution_info_" + query_id).text("Cache Status : " + json_data.cached + " Run Time : " + json_data.time_elapsed + ' seconds');
			$('#ml_section').removeClass('hide');
			// Make drop downs in ML based on Columns
			//console.log(json_data.data.columns);
			var mySelect = $("#column_names_" + query_id);
			$.each(json_data.data.columns, function(idx, colname) {
					mySelect.append(
						$('<option></option>').val(colname).html(colname)
					);
			});
		} else {
			$( "#error_" + query_id ).show();
			$( "#error_" + query_id + " pre" ).text(json_data.data);
		}
	}).fail(function() {
		$( "#waiting_" + query_id ).empty();
		$( "#error_" + query_id ).show();
		$( "#error_" + query_id + " pre" ).text('Unknown Error Occured');
	});
}
jQuery.escapeSelector = function(str) {
	return str.replace(/[!"#$%&'()*+,./:;<=>?@\[\\\]^`{|}~]/g, "\\$&");
}
function make_date_picker(search_for){
	$(function(){
		$('#selector_' +  $.escapeSelector(search_for)).datepicker({ dateFormat: 'yy-mm-dd' });
	});              
} 
function make_adhoc_model(ml_id, url, json, query_id){
	$(document).ready(function() {
		$('#ml_' + ml_id).click(function() {
			$.getJSON(url, json, function( json_data ) {
					return_str = ''
					$.each( json_data.data, function( key, value ) {
						return_str = return_str + '\n' +  key + ' \n' + value;
					});
					$("#ml_output_" + query_id).text(return_str);
					$("#ml_output_" + query_id).removeClass("hide");
			}).fail(function() {
				alert('oops');
			})
		})
	})
} 
