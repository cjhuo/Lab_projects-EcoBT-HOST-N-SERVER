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
	var fileHandlerUrl = 'ecgAllInOne'
	
	var datasets; //store datasets
	var diagram; //store DOM object of plot div
    var plot;  //store main plot object will be returned by flot
    var options; //options settings for main plot
    
    var spinTarget; //store DOM object used to show loading spinner
    var spinner; //spinner
    
    var frequency = 250;
    var xGridInterval = 200; //0.2 second
    var yGridInterval = 500; //0.5 mV, assuming the unit of ECG output is microvolt
    var yAxisHeight = 100;
    
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
        		enabled: false
        	},
        	offset: 0,
        	height: yAxisHeight,
        	min: -500,
        	max: 2000
        };
    
    options = {
            chart: {
                renderTo: 'diagram',
                /*zoomType: 'x',
                animation: {
                    duration: 1000
                },*/
                type: 'line',
                zoomType: 'x'
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
                layout: 'vertical',
                verticalAlign: 'top',
                //x: -10,
                y: 55,
                //floating: true,
                shadow: true
            },
            navigator: {
            	enabled: true,
            	xAxis:{
            		dateTimeLabelFormats: {
        	        	second: '%H:%M:%S',
        	        	minute: '%H:%M:%S',
        	        	hour: '%H:%M',
        	        	day: '%e. %b',
        	        	week: '%e. %b',
        	        	month: '%b \'%y',
        	        	year: '%Y'
        	        }
            	}
    	        
            },
            scrollbar: {
            	enabled: true
            },
            rangeSelector:{
            	enabled: true,
            	inputEnabled: false,            	
            	buttons: [{
            		type: 'millisecond',
            		count: 10000,
            		text: '10s'
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
            plotOptions: {
                line: {
                	dataGrouping: {
                		enabled: false
                	},
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
                    enableMouseTracking: true,
                    point: {
                        events: {
                            click: function(event) {
    	    			    alert(this.name +' clicked\n'+
                        	    'Alt: '+ event.altKey +'\n'+
                            	'Control: '+ event.ctrlKey +'\n'+
                              	'Shift: '+ event.shiftKey +'\n');
                            }
                        }
                    }
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
    	        
    	        labels: {
    	        	enabled: false,
    	        	//step: 2
    	        },
    	        startOnTick: false,
    	        endOnTick: false
            },
            tooltip: {},
            yAxis: [],
            series: []
    };
    /*
	function getAndProcessData() { //issue ajax call and further process the data on sucess
		showSpinner();
		$.ajax({
			url: dataurl,
			cache: false,
			type: 'POST',
			dataType: 'json',
			success: onDataReceived
		});
	}
	*/

	/* issue ajax call and further process the data on sucess */
	function getAndProcessData() { 
		chooseFileSource();
	}
	
	function chooseTestFile() {
		showSpinner();
		$.ajax({
			url: fileHandlerUrl,
			cache: false,
			type: 'POST',
			dataType: 'json',
			success: onDataReceived
		});
		$('#fileChooser').dialog( "destroy" );
	}
	
	function chooseFileSource(){
    	var popUpDiv = $('<div id="fileChooser"/>');
    	$('<p>Please choose choose a dicom file: </p>').appendTo(popUpDiv);
    	var defButton = $('<button>Use sample dicom file</button>').css({
    		float: 'left',
    		fontSize: 'small',
    	});   	

    	defButton.button();
    	defButton.click(chooseTestFile);
    	popUpDiv.append(defButton);
    	
    	var fileInput = $('<span class="file-wrapper">\
    			<span>Submit your own Dicom file</span>\
                <input type="file" name="uploaded_files" >\
            </span>').css({
    		float: 'right',
    		fontSize: 'small',
    	});
    	fileInput.button();
    	fileInput.fileupload({
    		url: fileHandlerUrl,
            dataType: 'json',
            send: function (e, data) {
            	showSpinner();           	
            	//console.log(data);
            },
            done: function (e, data) {
            	//console.log(data.result);
            	$('#fileChooser').dialog( "destroy" );
            	onDataReceived(data.result);
            	$(this).fileupload('destroy');
            },
            fail: function (e, data) {
            	//console.log(data.textStatus);
            	alert('invalid file');
            	hideSpinner();
            	
            }
        });
    	
    	popUpDiv.append(fileInput);
    	
    	
    	//add two button, one for file input handler directed to jquery upload
    	//, one for default file handler
    	//TBD
    	
    	popUpDiv.dialog({
            //height: 200,
    		width: 500,
            modal: true,
            resizable: false,
            dialogClass: 'alert',
            closeOnEscape: false,
        });
    	$(".ui-dialog-titlebar").hide(); //remove dialog title bar
	}
	
    /** 
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
	/*
    function onDataReceived(data) { //setup plot after retrieving data
        extractDatasets(data); //JSON {'dspData': datasets, 'peaks': indice of peak points}         
		addPlot();  //generate main plot div
    }
    */
	function onDataReceived(data) { //setup plot after retrieving data
		console.log(data);
	    extractDatasets(data); //JSON {'dspData': datasets, 'peaks': indice of peak points}
	    addResizer();
		addFileUploadDiv();
		addPlot();  //generate main plot div
		//addOverview(); // generate overview plot div	
	}

	    
	function extractDatasets(data) {
		datasets = data.dspData;
	}
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
	
    function addFileUploadDiv() {
    	var fileInput = $('<span class="file-wrapper" title="Submit a different Dicom file">\
    			<span>File</span>\
                <input type="file" name="uploaded_files" >\
            </span>').css({
    		float: 'left',
    		fontSize: 'small',
    	});
    	fileInput.button();
    	fileInput.fileupload({
    		url: fileHandlerUrl,
            dataType: 'json',
            send: function (e, data) {
            	showSpinner();
            	//console.log(data);
            },
            done: function (e, data) {
            	//console.log(data.result);
            	//choice.remove()
            	diagram.remove();
            	resizer.remove();
            	fileInput.remove();
            	//histogram.remove();
            	onDataReceived(data.result);
            },
            fail: function (e, data) {
            	alert('invalid file');
            	hideSpinner();
            }
        });
    	fileInput.appendTo(innerResizer);
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
        options.series = [];
        //loop to fill in yAxis and data series
        for(var i=0; i<datasets.length;i++) {
        	var yAxisOptions = $.extend(true, {}, yAxisOptionsTemplate); //!!!deep copy JSON object
        	yAxisOptions.title = {
        			text: datasets[i].label,
        			rotation: 0
        	};   	
        	yAxisOptions.top = yTop;
        	yTop += yAxisHeight; //!!!!adjust the distance to the top
        	
        	options.yAxis.push(yAxisOptions);        	
        	options.series.push({
        		name: datasets[i].label,
                data: datasets[i].data,
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                yAxis: i, //use the index of dataset as the index of yAxis
                pointInterval: 1000/frequency // 5 millisecond<--wrong! should be 1000/frequency. in this case 1000/250 = 5
        	});
        }
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
    
    getAndProcessData();
});