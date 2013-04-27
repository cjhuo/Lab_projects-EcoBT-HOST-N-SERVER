
$(function () {
	
	//ajax call urls
	var dataUrl = 'ecgAllInOne';
	
	var datasets; //store datasets
	var diagram; //store DOM object of plot div
    var plot;  //store main plot object will be returned by flot
    var options; //options settings for main plot
    
    var spinTarget; //store DOM object used to show loading spinner
    var spinner; //spinner
    
    var frequency = parseInt($('#frequency').val());

    var xGridInterval = 200; //0.2 second
    var yGridInterval = 500; //0.5 mV, assuming the unit of ECG output is microvolt
    //var yAxisHeight = 100;
    var yTickHeight = 20;
    var xTickHeight = 20;
    var chartWidth;
    
    var yAxisOptionsTemplate = {
        	lineColor: 'rgb(245, 149, 154)',
        	gridLineColor: 'rgb(245, 149, 154)', 
        	gridLineWidth: 0.5,
        	minorGridLineColor: 'rgb(245, 149, 154)',
        	minorGridLineWidth: 0.2,
        	
        	minorTickInterval: yGridInterval/5,
	        //minorTickWidth: 2,
	        minorTickLength: 0,
	        //minorTickPosition: 'inside',
	        //minorTickColor: 'red',
	
	        //tickPixelInterval: 30,
	        tickInterval: yGridInterval,
	        //tickWidth: 2,
	        //tickPosition: 'inside',
	        tickLength: 0,
	        //tickColor: 'red',
        	/*
        	 * title: {
        		text: "AAA"
        	},
        	*/
        	labels: {
        		enabled: false,
        		align: 'right'
        	},
        	offset: 0,
        	//height: yAxisHeight,
        };
    
    chartOptions = {
            chart: {
                renderTo: 'diagram',
                /*zoomType: 'x',
                animation: {
                    duration: 1000
                },*/
                type: 'line',
                //zoomType: 'x',
                panning: false, // does not allow click and drag event
                alignTicks: false,
                marginRight: 50
            },
            credits: {
            	href: "http://cps.eng.uci.edu:8000/analysis",
            	text: "UCI Embedded Lab",
            },
            loading: {
                labelStyle: {
                    color: 'white'
                },
                style: {
                    backgroundColor: 'gray'
                }
            },
            title: {
                text: 'ECG Viewer (All Samples)'
            },
            exporting:{
                buttons: {
                    exportButton: {
                        menuItems: [
                        /*{
                            text: 'Export to PNG',
                            onclick: function() {
                            	alert(chartWidth);
                                this.exportChart({
                                    width: chartWidth
                                });
                            }
                        }, 
                        {
                            text: 'Export to PDF',
                            onclick: function() {
                                this.exportChart({
                                	type: "application/pdf"
                                });
                            }
                        },*/
                        {
                            text: 'Export to SVG',
                            onclick: function() {
                                this.exportChart({
                                	type: "image/svg+xml"
                                });
                            }
                        },
                        null,
                        null,
                        null
                        ]
                    }
                }
            },
            legend: {
                enabled: false,
            },
            navigator: {
            	enabled: false,
            	adaptToUpdatedData: false,
            	series: {},
            	xAxis:{
            		labels:{
            			enabled: true,
            			//step: 3,
            			overflow: false
            		},
            		//tickInterval: 1000,
            		dateTimeLabelFormats: {
            			millisecond: '%H:%M:%S',
        	        	second: '%H:%M:%S',
        	        	minute: '%H:%M:%S',
        	        	hour: '%H:%M',
        	        	day: '%e. %b',
        	        	week: '%e. %b',
        	        	month: '%b \'%y',
        	        	year: '%Y'
        	        },
        	        startOnTick: true,
        	        endOnTick: true
            	}
            },
            scrollbar: {
            	enabled: false
            },
            rangeSelector:{
            	enabled: false,
            	inputEnabled: false,     
    	    	buttonTheme: { // styles for the buttons
    	    		fill: 'none',
    	    		stroke: 'none',
    	    		style: {
    	    			//color: '#039',
    	    			fontWeight: 'bold'
    	    		},
    	    		states: {
    	    			hover: {
    	    				fill: 'white'
    	    			},
    	    			select: {
    	    				style: {
    	    					color: 'white'
    	    				}
    	    			}
    	    		}
    	    	},
            	buttons: [{
            		type: 'millisecond',
            		count: 10000,
            		text: '10s'
            	}/*, {
            		type: 'all',
            		text: 'All'
            	}*/],
            	selected: 0
            },
            subtitle: {
            	/*
                text: document.ontouchstart === undefined ?
                      'Click and drag in the plot area to zoom in' :
                      'Drag your finger over the plot to zoom in'
                */
            },
            plotOptions: {
                line: {
                	dataGrouping: {
                		enabled: false
                	},
                	allowPointSelect: false,
                	animation: false,
                	color: 'black',	
                	lineWidth: 0.7,
                	marker: {
                		enabled: false,
                		states: {
                			hover: {
                				radius: 4
                			},
                			select: {
                				radius: 10 //!!! not working!!!!!
                			}
                		}
                	},
                    dataLabels: {
                        enabled: false
                    },
                    states: {                 
                    	hover: {
                    		lineWidth: 0.7 //gotta be same value as line.lineWidth 
                    					//so that when hovered plot won't look weird
                    	}
                    },
                    shadow: false,
                    enableMouseTracking: false,
                },
                series: {
                	//allowPointSelect: true,  
                    marker: {
                    	radius: 0.1,
                        states: {
                			hover: {
                				radius: 4
                			},
                            select: {
                                radius: 4
                            }
                        }
                    },
                }
            },
            xAxis: {           	
            	lineColor: 'rgb(245, 149, 154)',
            	gridLineColor: 'rgb(245, 149, 154)',
            	gridLineWidth: 0.5,
            	minorGridLineColor: 'rgb(245, 149, 154)',
            	minorGridLineWidth: 0.2,
            	
            	minorTickInterval: xGridInterval/5, //5 minor tick by default, exactlly what we want
    	        minorTickWidth: 1,
    	        minorTickLength: 0,
    	        minorTickPosition: 'inside',
    	        minorTickColor: 'red',
    	
    	        //tickPixelInterval: 30,
    	        tickInterval: xGridInterval, //0.2 second
    	        tickWidth: 2,
    	        tickPosition: 'inside',
    	        tickLength: 0,
    	        tickColor: 'red',
    	        
        		dateTimeLabelFormats: {
        			millisecond: '%H:%M:%S',
    	        	second: '%H:%M:%S',
    	        	minute: '%H:%M:%S',
    	        	hour: '%H:%M',
    	        	day: '%e. %b',
    	        	week: '%e. %b',
    	        	month: '%b \'%y',
    	        	year: '%Y'
    	        },
    	        
    	        labels: {
    	        	enabled: true,
    	        	step: 10,
    	        	overflow: false
    	        },
    	        startOnTick: true,
    	        endOnTick: true
            },
            tooltip: {},
            yAxis: [],
            series: []
    };

	/* issue ajax call and further process the data on sucess */
	function getAndProcessData() { 
		showSpinner();

		$.ajax({
			url: dataUrl,
			cache: true,
			type: 'GET',
			dataType: 'json',
			success: onDataReceived
		});

		//checkFinishFlag();
	}
	
	function init(){
		getAndProcessData();
	}
	
    var overViewButton;
    function addOverViewButton(){
   	overViewButton = $('<button>START GENERATING LARGE ECG PAPER</button>').css({
    		float: 'left',
    		fontSize: 'small',
    	});   	

    	overViewButton.button();
    	overViewButton.click(getAndProcessData);
    	overViewButton.appendTo("body");
    	
    }

	function checkFinishFlag(){
		if(finishFlag != false)
			plotEverything();  //generate main plot div
		else //set a timeout to check it again
			setTimeout(checkFinishFlag, 200);
	}

	function onDataReceived(data) { //setup plot after retrieving data
		document.close();
		console.log(data);
	    extractDatasets(data); //JSON {'dspData': datasets, 'peaks': indice of peak points}
	    plotEverything(); 
	}

    var pointInterval, finishFlag=false;
	function extractDatasets(data) {
		datasets = data.data;
		pointInterval = data.pointInterval;
		finishFlag = true;
	}
	
    var resizer, innerResizer;
	function addResizer(chartWidth) {
		var tmpWidth;
		if(chartWidth == null)
			tmpWidth = '100%';
		else
			tmpWidth = chartWidth.toString() + 'px';
    	resizer = $('<div id="resizer" />').css( {
            width: tmpWidth,
            minHeight: '400px',
            //border: '1px solid silver'

        });	
		resizer.appendTo("body");
    	
		innerResizer = $('<div id="innerResizer" />').css( {
			padding: '0px 10px 0px 0px'
        });	
		innerResizer.appendTo(resizer);
	}
    
    function plotEverything() {
        var yTop = 40; // top padding
        chartOptions.series = [];
        chartOptions.yAxis = [];
        //loop to fill in yAxis and data series
        var diagramHeight = 65 //calculate the diagram height!!!!!65 is the top padding of chart,
        for(var i=0; i<datasets.length;i++) {
        	var yAxisOptions = $.extend(true, {}, yAxisOptionsTemplate); //!!!deep copy JSON object
        	yAxisOptions.title = {
        			text: datasets[i].label,
        			align: 'high',
        			rotation: 0,
        			y: 15
        	};   	
        	//yAxisOptions.min = datasets[i].min-0.5;
        	//yAxisOptions.max = datasets[i].max+0.5;
        	//add checker to handler rambled value from any channel, 
        	
        	var min = datasets[i].min;
        	var max = datasets[i].max;
        	yAxisOptions.min = min;
        	yAxisOptions.max = min + 11 * yGridInterval
        	yAxisOptions.height = yTickHeight*(Math.ceil(yAxisOptions.max/yGridInterval)-Math.floor(yAxisOptions.min/yGridInterval));

        	yAxisOptions.top = yTop;
        	yTop += yAxisOptions.height; //!!!!adjust the distance to the top
        	diagramHeight += yAxisOptions.height;
        	chartOptions.yAxis.push(yAxisOptions);
        	chartOptions.series.push({
        		name: datasets[i].label,
                data: datasets[i].data,
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                yAxis: i, //use the index of dataset as the index of yAxis
                pointInterval: pointInterval //1000/frequency // 5 millisecond<--wrong! should be 1000/frequency. in this case 1000/250 = 4
        	});
        }
        //format tooltip
        chartOptions.tooltip.formatter = function() {
        	var s = '';
        	$.each(this.points, function(key, val) {
        		s += '<b>'+ val.series.name +'</b>'+
                val.y + ' ';
        		if(key == 5)
        			s +='<br/>'; 
        	});
            return s;
        };
        
        chartOptions.tooltip.positioner = function () {
        	return { x: 200, y: 20 };
        }
        
		diagramHeight += 4; //4 is bottom padding
		chartWidth = datasets[0].data.length * pointInterval * xTickHeight / xGridInterval;
		console.log(chartWidth);
	    addResizer(chartWidth);
	    chartOptions.chart.width = chartWidth;
	    chartOptions.chart.height = diagramHeight;
    	//plot all channels on one plot
    	diagram = $('<div id="diagram" ></div>').css( {
            height: diagramHeight.toString() + 'px',
        });
    	/*
    	$('#options').val(JSON.stringify(chartOptions));
    	$('#type').val("image/svg+xml");
    	$('#filename').val("test");
    	$('#constr').val("StockChart");
		
    	$('#exportForm').submit();
    	*/
    	diagram.appendTo(innerResizer);
    	plot = new Highcharts.StockChart(chartOptions);     
    	hideSpinner();
    }
    
    /* show loading spinner, stopped when chart is fully loaded */
    function showSpinner(){
    	spinTarget.show();
		spinner.spin(spinTarget[0]);
    }
    
    function hideSpinner(){
		spinTarget.hide();
		spinner.stop();
    }
    
    //show loading spinner, stopped when chart is fully loaded
	var spinnerOpts = { //options settings for spinner
			  lines: 13, // The number of lines to draw
			  length: 7, // The length of each line
			  width: 4, // The line thickness
			  radius: 10, // The radius of the inner circle
			  corners: 1, // Corner roundness (0..1)
			  rotate: 0, // The rotation offset
			  color: '#000', // #rgb or #rrggbb
			  speed: 1, // Rounds per second
			  trail: 60, // Afterglow percentage
			  shadow: false, // Whether to render a shadow
			  hwaccel: false, // Whether to use hardware acceleration
			  className: 'spinner', // The CSS class to assign to the spinner
			  zIndex: 2e9, // The z-index (defaults to 2000000000)
			  top: 'auto', // Top position relative to parent in px
			  left: 'auto' // Left position relative to parent in px
			};
	spinTarget = $('<div id="spinner" ></div>').css( {
	            position: 'relative',
	            width: '50px',
	            height: '50px',
	            margin: 'auto'
	});
	spinTarget.appendTo("body");
	
	spinner = new Spinner(spinnerOpts);
    
	init();
});