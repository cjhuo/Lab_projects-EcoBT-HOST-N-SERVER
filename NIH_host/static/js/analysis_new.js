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
            	enabled: false
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
            	selected: 0
            },
            subtitle: {
            	/*
                text: document.ontouchstart === undefined ?
                      'Click and drag in the plot area to zoom in' :
                      'Drag your finger over the plot to zoom in'
                */
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
    	        //startOnTick: true,
    	        //endOnTick: true
            },
            yAxis: {
            	lineColor: 'rgb(245, 149, 154)',
            	gridLineColor: 'rgb(245, 149, 154)', 
            	gridLineWidth: 1,
            	minorGridLineColor: 'rgb(245, 149, 154)',
            	minorGridLineWidth: 0.5,
            	
            	minorTickInterval: 'auto',
    	        minorTickWidth: 2,
    	        minorTickLength: 0,
    	        minorTickPosition: 'inside',
    	        minorTickColor: 'red',
    	
    	        //tickPixelInterval: 30,
    	        tickInterval: yGridInterval,
    	        tickWidth: 2,
    	        tickPosition: 'inside',
    	        tickLength: 0,
    	        tickColor: 'red',
            	title: {
            		text: ""
            	},
            	labels: {
            		enabled: false
            	}

            },
            tooltip: {
                enabled: true,
                crosshairs: true,
                formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+
                        /*this.x +', '+ */this.y;
                }
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
		addChoices(); //add channel radio buttons
		addPlot();  //generate main plot div
		//addOverview(); // generate overview plot div
		plotAccordingToChoices(); //plot diagram on generated div and generate overview

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
    		
    	//plot all channels on one plot
    	diagram = $('<div id="diagram" ></div>').css( {
            position: 'right',
            width: '50%',
            height: '400px',
            margin: 'auto',
            padding: '2px'
        });
    	diagram.appendTo("body");
    }

    
    function addChoices() {
        var i = 1;
        choice = $('<div id="choices">Show:</div>').css( {
            position: 'relative',
            width: '10%',
            cssFloat: 'left',
			fontWeight: 'bold',
			margin: '10px 0px 0px 10px'
            //textAlign: 'center'
        });
        var checked = 0;
        $.each(datasets, function(key, val){
			
        	//generate radiobox for each channel 
        	var domStr = '<br><input type="radio" name="channel" id="' + val.label 
        	+ '" value="' + key + '"' + (checked==0?' checked':'') + '>' 
        	+'<label for="' + val.label + '">'+ val.label + '</label>';
        	
        	choice.append(domStr);
        	
        	++i;
        });
        choice.appendTo("body");
		
		choice.find("input").click(plotAccordingToChoices);
    }
    
    function plotAccordingToChoices() {
        var data = [];
        var peakSeries = {};
        var key;
        var label;

        choice.find("input:checked").each(function () {
        	key = $(this).attr("value");
        	label = $(this).attr("id");

            if (key && datasets[key])
                data = datasets[key].data;
            
        });
    
        if (data.length > 0)
	        if(diagram) {//just in case the plot div is not yet generated when user starts to click radio buttons
	        	/* re-initialize every parameter */
	        	//diagram.unbind();

				/* re-plot everything */
	        	options.series = [];
	        	options.series.push({
	        		name: label,
                    data: data,
                    pointStart: Date.UTC(0, 0, 0),
                    pointInterval: 5 // 5 millisecond
	        	});
	        	plot = new Highcharts.StockChart(options, function() {
	        		spinner.stop();
	        		spinTarget.hide();
	        	});
	        	
	        	//end loading data
	            //plot = $.plot(diagram, data, options);
	            //addHoverEvent();
	           	//plotOverview(data);
	           	//addSelectionEvent(data);
	            //addClickEvent();
	        }
	        else {
	        	alert('plot div has not been generated!');
	        }        
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