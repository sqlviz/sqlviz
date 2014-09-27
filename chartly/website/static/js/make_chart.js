function make_table(columns, data, target){
    html  ='<thead><tr>';
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
    html += "</tbody>"
    $(target).html(html);
    $(document).ready(function() {
      $(target).dataTable({
        "bAutoWidth": false,
        "bScrollCollapse": true,
      });
    });      
};

function make_chart(columns, data, target, stacked, graph_type, title, xAxis, yAxis, yAxis_log, defaults){
  options = {
        chart: {
          type : graph_type,
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
                text: yAxis
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
    series = []
    $.each( columns, function( index, val ) {
      if (index > 0){
        series.push({"name":val,"data":[]})  
      }
    });
    $.each(data, function( key, row ) {
      $.each(row, function( index, value ) {
        if (index == 0){
          options.xAxis.categories.push(value)
        } else {
          series[index -1].data.push(value)  
        }
      });
    });
    options.series = series;
    console.log(options)
    if (stacked == 'True'){
      options.plotOptions = {};
      options.plotOptions [graph_type] = {'stacking' :'normal'};
    }
    if (options.xAxis.categories.length > 14){
      options.xAxis.labels = {'step' :Math.max(Math.round(options.xAxis.categories.length / 7),1)}
    }
    if (yAxis_log == 'True'){
      options.yAxis.type = 'logarithmic'
    }
    $.extend(options, defaults); // MUNGE GRAPH SETTINGS
    var chart = new Highcharts.Chart(options);
}