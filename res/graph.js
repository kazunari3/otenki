$(function () {
    var chart;
    var str;
    $(document).ready(function() {
    
        // define the options
        var options = {
    
            chart: {
                renderTo: 'container'
            },
    
            title: {
                text: '気温グラフ（平年値との比較）'
            },
    
            subtitle: {
                text: 'Source: 気象庁'
            },
    
            xAxis: {
                type: 'datetime',
                tickInterval: 7 * 24 * 3600 * 1000, // one week
                tickWidth: 0,
                gridLineWidth: 1,
                labels: {
                    align: 'left',
                    x: 3,
                    y: -3
                }
            },
    
            yAxis: [{ // left y axis
                title: {
                    text: null
                },
                labels: {
                    align: 'left',
                    x: 3,
                    y: 16,
                    formatter: function() {
                        return Highcharts.numberFormat(this.value, 0);
                    }
                },
                showFirstLabel: false
            }, { // right y axis
                linkedTo: 0,
                gridLineWidth: 0,
                opposite: true,
                title: {
                    text: null
                },
                labels: {
                    align: 'right',
                    x: -3,
                    y: 16,
                    formatter: function() {
                        return Highcharts.numberFormat(this.value, 0);
                    }
                },
                showFirstLabel: false
            }],
    
            legend: {
                align: 'left',
                verticalAlign: 'top',
                y: 20,
                floating: true,
                borderWidth: 0
            },
    
            tooltip: {
                shared: true,
                crosshairs: true
            },
    
            plotOptions: {
                series: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function() {
                                hs.htmlExpand(null, {
                                    pageOrigin: {
                                        x: this.pageX,
                                        y: this.pageY
                                    },
                                    headingText: this.series.name,
                                    maincontentText: Highcharts.dateFormat('%A, %b %e, %Y', this.x) +':<br/> '+
                                        this.y +' visits',
                                    width: 200
                                });
                            }
                        }
                    },
                    marker: {
                        lineWidth: 1
                    }
                }
            },
    
            series: [{
                name: '最高気温',
                lineWidth: 4,
                marker: {
                    radius: 4
                }
            }, {
                name: '最低気温'
            }, {
                name: '最高気温（実績）'
            }, {
                name: '最低気温（実績）'
            }, {
                name: '本日の最高気温（予報）'
            }, {
                name: '本日の最低気温（予報）'
            }, {
                name: '明日の最高気温（予報）'
            }, {
                name: '明日の最低気温（予報）'
            }]
        };
    

        // Load data asynchronously using jQuery. On success, add the data
        // to the options and initiate the chart.
        // This data is obtained by exporting a GA custom report to TSV.
        // http://api.jquery.com/jQuery.get/
        date=new Date();
         data = "res/" + (date.getMonth()+1) + ".json";
        //data= $("#yokohama_avg").html()
        jQuery.get(data, null, function(tsv, state, xhr) {
         options.series[0].data = tsv[0];
         options.series[1].data = tsv[1];
    
            chart = new Highcharts.Chart(options);
        });



        jQuery.get('getjson', null, function(tsv, state, xhr) {

         options.series[2].data = tsv[0];
         options.series[3].data = tsv[1];
         options.series[4].data = tsv[2];
         options.series[5].data = tsv[3];
         options.series[6].data = tsv[4];
         options.series[7].data = tsv[5];
            chart = new Highcharts.Chart(options);
        }, "json");

    });
    
});
