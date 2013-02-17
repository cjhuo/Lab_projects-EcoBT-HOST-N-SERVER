/* Main script for analysis.html page.
 *
 *   <p>1. Choose a radio button to pick the channel you want to analyze
 *   <br>
 *      2. Zoom to the range where you feel comfortable to pick start and end peak points
 *   <br>
 *      3. Pick 2 peak points and hit submit for further analysis in range between those 2 peak points
 *   <br>
 *      <b>Note:</b> <br>
 *      a) Click a point you picked will de-select the point <br>
 *      b) You can always go back to the original state by choose any of the radio buttons</p>
 *
 */

$(function () {
	var url = $('#serverAddr').val(); 	//push url, need to change this to server's url, 
	var name =  $('#name').text();
    var ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'];
	
    /**
	    Data received should have the structure as below:
	    data.from = "node"
	    data.type = "ecg"
	    data.name = node's MAC
	    data.data = [
	                    {
	                        'channelName': value,
	                        'data': value,
	                    },
	                    {
	                        'label': "channel2",
	                        'data': value
	                    }
	                    ...
	                ]    
	*/
	var datasets; //store datasets
	function onDataReceived(data) { //setup plot after retrieving data
		console.log(data);
		if( data.from == 'node')
			if(name.trim() == data.data.address.trim())
				if(data.data.type == 'ecg'){
					extractDatasets(data.data.data);
					addResizer();
					addPlot();
				}
	}
	
	/* issue ajax call and further process the data on sucess */
	function getAndProcessData() { 
		showSpinner();
		$.ajax({
			url: url,
			cache: false,
			type: 'POST',
			dataType: 'json',
			data: {"address":JSON.stringify(name.trim())},
			success: onDataReceived
		});
	}
	
	function extractDatasets(data) {
		datasets = data.data;
	}
	
	var init = function() {
		getAndProcessData();
	}
	

	var diagram; //store DOM object of plot div
    var plot;  //store main plot object will be returned by
    var chartOptions; //chartOptions settings for main plot
        
    var xGridInterval = 200; //0.2 second
    var yGridInterval = 500; //0.5 mV, assuming the unit of ECG output is micro volt
    var yAxisHeight = 100;
    
    var yAxisOptionsTemplate = {
        	lineColor: 'rgb(245, 149, 154)',
        	gridLineColor: 'rgb(245, 149, 154)', 
        	gridLineWidth: 0.5,
        	minorGridLineColor: 'rgb(245, 149, 154)',
        	minorGridLineWidth: 0.2,
        	
        	minorTickInterval: 'auto',
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
	    	plotLines: [{
	    		value: 0,
	    		width: 1,
	    		label: {
	    			text: '0',
	    			align: 'left',
	    			y: 0,
	    			x: -10
	    		}
	    	}],
        	labels: {
        		enabled: true,
        	},
        	offset: 0,
        	height: yAxisHeight,
        	min: -1000,
        	max: 1000
        };
    
    chartOptions = {
            chart: {
                renderTo: 'diagram',
                /*zoomType: 'x',
                animation: {
                    duration: 1000
                },*/
                type: 'line',
            },
            credits: {
            	href: "http://cps.eng.uci.edu:8000/analysis",
            	text: "UCI Embedded Lab"
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
                text: '10 seconds ECG Data'
            },
            
            legend: {
                enabled: true,
                align: 'right',
                backgroundColor: '#FCFFC5',
                borderColor: 'black',
                borderWidth: 2,
                layout: 'vertical',
                verticalAlign: 'top',
                //x: -10,
                y: 55,
                //floating: true,
                shadow: true
            },
            navigator: {
            	enabled: true
            },
            scrollbar: {
            	enabled: true
            },
            rangeSelector:{
            	enabled: true,
            	inputEnabled: false,
            	
            	buttons: [{
            		type: 'millisecond',
            		count: 2500,
            		text: '2.5s'
            	}, {
            		type: 'all',
            		text: 'All'
            	}],
            	selected: 1
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
                	allowPointSelect: true,
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
                    enableMouseTracking: true
                },
                series: {
                	allowPointSelect: true,  
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
                    point: {
                    	events: {
                    		click: function(event){
                    			this.select(true, true);
                    			//alert(this.series);
                    			return false;
                    		}
                    	}
                    }
                }
            },
            xAxis: {
            	reversed: true,
            	lineColor: 'rgb(245, 149, 154)',
            	gridLineColor: 'rgb(245, 149, 154)',
            	gridLineWidth: 0.5,
            	minorGridLineColor: 'rgb(245, 149, 154)',
            	minorGridLineWidth: 0.2,
            	
            	minorTickInterval: 'auto', //5 minor tick by default, exactlly what we want
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
    	        
    	        labels: {
    	        	enabled: false,
    	        	//step: 2
    	        },
    	        startOnTick: true,
    	        endOnTick: true
            },
            tooltip: {},
            yAxis: [],
            series: []
    };
    
    // plot related
    var resizer, innerResizer;
	function addResizer() {
    	resizer = $('<div id="resizer" />').css( {
            width: '100%',
            minHeight: '400px',
            //border: '1px solid silver'

        });	
		resizer.appendTo("body");
    	
		innerResizer = $('<div id="innerResizer" />').css( {
			padding: '10px'
        });	
		innerResizer.appendTo(resizer);
	}
	
    function addPlot() { 
    	/*//generate one plot for each channel
    	var diagram = $('<div id="channel'+ index +'"/>').css( {
            position: 'relative',
            width: '500px',
            height: '200px',
            margin: 'auto',
            padding: '2px'
        });
    	*/
		
		//calculate the diagram height
		
		var diagramHeight = 65 + yAxisHeight*datasets.length + 93; //!!!!!65 is the top padding of chart,
															//93 is bottom padding
		
    	//plot all channels on one plot
    	diagram = $('<div id="diagram" ></div>').css( {
            height: diagramHeight.toString() + 'px',
        });
		

    	diagram.appendTo(innerResizer);
    	
    	//resizable
    	/*
		resizer.resizable({
		    // On resize, set the chart size to that of the 
		    // resizer minus padding. If your chart has a lot of data or other
		    // content, the redrawing might be slow. In that case, we recommend 
		    // that you use the 'stop' event instead of 'resize'.
		    resize: function() {
		    	plot.setSize(
		            this.offsetWidth - 20, 
		            this.offsetHeight - 20,
		            false
			       );
			   }
		});
		*/
		plotEverything(); //plot diagram on generated div and generate overview
    }
    
    function plotEverything() {
        var yTop = 65;
        chartOptions.series = [];
        //loop to fill in yAxis and data series
        for(var i=0; i<datasets.length;i++) {
        	var yAxisOptions = $.extend(true, {}, yAxisOptionsTemplate); //!!!deep copy JSON object
        	yAxisOptions.title = {
        			text: datasets[i].label,
        			rotation: 0
        	};   	
        	yAxisOptions.top = yTop;
        	yTop += yAxisHeight; //!!!!adjust the distance to the top
        	
        	chartOptions.yAxis.push(yAxisOptions);        	
        	chartOptions.series.push({
        		name: datasets[i].label,
                data: datasets[i].data,
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                yAxis: i, //use the index of dataset as the index of yAxis
                pointInterval: 5 // 5 millisecond<--wrong! should be 1000/frequency. in this case 1000/250 = 5
        	});
        }
        //format tooltip
        chartOptions.tooltip.formatter = function() {
        	var s = '';
        	$.each(this.points, function(key, val) {
        		s += '<b>'+ val.series.name +'</b>'+
                val.y + '<br/>';
        	});
            return s;
        };

    	plot = new Highcharts.StockChart(chartOptions, function() {
    		hideSpinner();
    	});      
    }
    
	var spinner; //spinner
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
	var spinTarget = $('<div id="spinner" ></div>').css( {
        position: 'relative',
        width: '50px',
        height: '50px',
        margin: 'auto'
	});    
	spinTarget.appendTo("body");
	var spinner = new Spinner(spinnerOpts);
	
    /* show loading spinner, stopped when chart is fully loaded */
    function showSpinner(){
    	spinTarget.show();
		spinner.spin(spinTarget[0]);
    }
    
    function hideSpinner(){
		spinTarget.hide();
		spinner.stop();
    }
    
    //getAndProcessData();
    
    init();
});