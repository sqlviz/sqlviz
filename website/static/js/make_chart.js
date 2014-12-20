function make_table(columns, data, target){
    var table_name = 'table_' +  target; 
    var div_name  = '#div_table_' + target;
    html = "<table class='table table-striped' id='" + table_name + "'>\n";
    html  +='<thead><tr>';
    $.each( columns, function( key, val ) {
      html += "<td>" + val  +"</td>";
    });
    html += "</tr></thead><tbody>\n";
    $.each( data, function( key, val ) {
      html += "<tr>";
      $.each(val, function(key2, val2) {
        html += "<td>" + val2 +"</td>";
      });
      html += "</tr>\n";
    });
    html += "</tbody></table>\n"
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
        }
      });
    });    
    return html; 
};

function make_chart(columns, data, target, stacked, chart_type, title, xAxis, yAxis, yAxis_log, graph_extra){
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
        tooltip: {
            valueSuffix: ''
        },
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
    $.each( columns, function( index, val ) {
      if (index > 0){
        series.push({"name":val,"data":[]})  
      }
    });
    // Check that the first column is a date
    console.log(is_date(data));
    if (is_date(data)){
      console.log('is a date');
      $.each(data, function( key, row ) {
        $.each(row, function( index, value ) {
          if (index != 0){
            series[index -1].data.push([Date.parse(row[0]),value])  
          }
        });
      });
      delete options.xAxis.categories;
      options.xAxis.type = 'datetime';
    } else {
      console.log('is NOT a date');
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
    console.log(options)
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
function is_date(data) {
  return_flag = true;
  $.each( data, function( key, row ) {
    if (isNaN(Date.parse(row[0]))) {
      console.log('not a date!');
      return_flag = false;
      return false;
    }
  });
  return return_flag;
}