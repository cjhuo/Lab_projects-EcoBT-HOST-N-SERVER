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
	//ajax call urls
	var dataurl = 'dsp'; 
	var submitUrl = 'submit'; 
	
	var datasets; //store datasets
	var peaks; //store indice of peak points for channels 
			   //only need 1-d array since peak indice for every channel are the same
	var diagram; //store DOM object of plot div
	var overview; //store DOM object of overview plot
	var choice;  //store DOM objects of checkbox of channels
    var plot;  //store main plot object will be returned by flot
    var options; //options settings for main plot
    var overviewPlot; ///store overview plot object will be returned by flot
    var peakText;// store DOM object of peak point
    var submit; //store DOM object of submit button
    
    var spinTarget; //store DOM object used to show loading spinner
    var spinner; //spinner
    
    var selectedPoints = [];
    var xGridInterval = 200; //0.2 second
    var yGridInterval = 500; //0.5 mV
    
    var yAxisOptionsTemplate = {
        	lineColor: 'rgb(245, 149, 154)',
        	gridLineColor: 'rgb(245, 149, 154)', 
        	gridLineWidth: 1,
        	minorGridLineColor: 'rgb(245, 149, 154)',
        	minorGridLineWidth: 0.5,
        	
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
        	labels: {
        		enabled: false
        	},
        	offset: 0,
        	height: 100,
        	min: -2000,
        	max: 2000
        };
    
    options = {
            chart: {
                renderTo: 'diagram',
                /*zoomType: 'x',
                animation: {
                    duration: 1000
                },*/
                type: 'line'
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
                text: 'QRS Wave data analysis'
            },
            legend: {
                enabled: true,
                align: 'right',
                backgroundColor: '#FCFFC5',
                borderColor: 'black',
                borderWidth: 2,
                //layout: 'vertical',
                verticalAlign: 'top',
                x: -10,
                y: 25,
                floating: true,
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
                	animation: false,
                	color: 'black',	
                	lineWidth: 0.7,
                	marker: {
                		enabled: false
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
                }
            },
            xAxis: {
            	lineColor: 'rgb(245, 149, 154)',
            	gridLineColor: 'rgb(245, 149, 154)',
            	gridLineWidth: 1,
            	minorGridLineColor: 'rgb(245, 149, 154)',
            	minorGridLineWidth: 0.5,
            	
            	minorTickInterval: 'auto', //5 minor tick by default, exactlly what we want
    	        minorTickWidth: 1,
    	        minorTickLength: 0,
    	        minorTickPosition: 'inside',
    	        minorTickColor: 'red',
    	
    	        //tickPixelInterval: 30,
    	        tickInterval: xGridInterval, //0.2 second
    	        //tickWidth: 2,
    	        //tickPosition: 'inside',
    	        tickLength: 0,
    	        //tickColor: 'red',
    	        
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

	function getAndProcessData() { //issue ajax call and further process the data on sucess
		showSpinner();
		$.ajax({
			url: dataurl,
			cache: false,
			type: 'GET',
			dataType: 'json',
			success: onDataReceived
		});
	}
	
    /* 
	    Data received should have the structure as below:
	    data.dspData = [
	                    {
	                        'label': "channel1",
	                        'data': [array of y]
	                    },
	                    {
	                        'label': "channel2",
	                        'data': [array of y]
	                    }
	                ]
	    data.peaks = [index of 1st peak, index of 2nd peak, ...]
	    
	    for fakePlot only:
	    	data retrieved from server for n channels with 100 data each, ranged from (-100, 100)
	    
    */
    function onDataReceived(data) { //setup plot after retrieving data
        extractDatasets(data); //JSON {'dspData': datasets, 'peaks': indice of peak points}         
		addPlot();  //generate main plot div
    }
	    
	function extractDatasets(data) {
		datasets = data.dspData;
		peaks = data.peaks;
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
    	var resizer = $('<div id="resizer" />').css( {
            width: '1000px',
            minHeight: '400px',
            //border: '1px solid silver'

        });	
		resizer.appendTo("body");
    	
		var innerResizer = $('<div id="innerResizer" />').css( {
			padding: '10px'
        });	
		innerResizer.appendTo(resizer);
		
		//calculate the diagram height
		
		var diagramHeight = 65 + 100*datasets.length + 93; //!!!!!65 is the top padding of chart,
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
        
        //loop to fill in yAxis and data series
        $.each(datasets, function(key, val) {
        	var yAxisOptions = $.extend(true, {}, yAxisOptionsTemplate); //!!!deep copy JSON object
        	yAxisOptions.title = {
        			text: val.label,
        			rotation: 0
        	};   	
        	yAxisOptions.top = yTop;
        	yTop += 100; //!!!!adjust the distance to the top
        	
        	options.yAxis.push(yAxisOptions);        	
        	options.series.push({
        		name: val.label,
                data: val.data,
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                yAxis: key, //use the index of dataset as the index of yAxis
                pointInterval: 5 // 5 millisecond
        	});
        });
    	
        //format tooltip
        options.tooltip.formatter = function() {
        	var s = '';
        	$.each(this.points, function(key, val) {
        		s += '<b>'+ val.series.name +'</b>'+
                val.y + '<br/>';
        	});
            return s;
        };

    	plot = new Highcharts.StockChart(options, function() {
    		spinner.stop();
    		spinTarget.hide();
    	});      
    }
    
    //show loading spinner, stopped when chart is fully loaded
    function showSpinner(){
    	var opts = {
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
    			spinner = new Spinner(opts).spin(spinTarget[0]);
    }
    
    getAndProcessData();
});