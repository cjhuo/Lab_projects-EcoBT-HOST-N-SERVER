
$(function () {
	
	/*
	 * Highcharts plugin for adding an axis after render time. Works with Highcharts >= 2.2.4.
	 * As of Highcharts 3.0, the contents of this plugin will be part of the Highcharts
	 * core.
	 * Author: Torstein Hønsi
	 * License: MIT License
	 * Last revision: 2013-02-14
	 */
	(function (Highcharts) {
	    
	    var each = Highcharts.each,
	        UNDEFINED;
	    
	    /**
	     * Utility function to remove last occurence of an item from an array
	     * @param {Array} arr
	     * @param {Mixed} item
	     */
	    function erase(arr, item) {
	        var i = arr.length;
	        while (i--) {
	            if (arr[i] === item) {
	                arr.splice(i, 1);
	                break;
	            }
	        }
	        return i;
	    }
	    /**
	     * Add an axis to the chart
	     * @param {Object} options The axis option
	     * @param {Boolean} isX Whether it is an X axis or a value axis
	     */
	    Highcharts.StockChart.prototype.addAxis = function (options, isX) {
	        var key = isX ? 'xAxis' : 'yAxis',
	            axis = new Highcharts.Axis(this, Highcharts.merge(options, {
	                index: plot[key].length
	            }));
	        
	        // Push the new axis options to the chart options
	        plot.options[key] = Highcharts.splat(plot.options[key] || {});
	        plot.options[key].push(options);
	    };
	    
	    /**
	     * Remove an axis from the chart
	     */
	    Highcharts.Axis.prototype.remove = function () {
	        if (this.series.length) {
	            console.error('Highcharts error: Cannot remove an axis that has connected series');
	        } else {
	            var key = this.isXAxis ? 'xAxis' : 'yAxis';

	            // clean up chart options
	            var axisIndex = this.options.index;
	            plot.options[key].splice(axisIndex, 1);
	            
	            erase(plot.axes, this);
	            var index = erase(plot[key], this);
	            
	            // clean up following axis options (indices)
	            for (var i = index; i < plot[key].length; i++) {
	              plot[key][i].options.index--;
	            }
	            
	            this.destroy();
	            plot.isDirtyBox = true;
	            plot.redraw();
	        }
	    };
	    
	    /** 
	     * The improved version of Series.bindAxes uses axis.id
	     */
	    /**
		 * Set the xAxis and yAxis properties of cartesian series, and register the series
		 * in the axis.series array
		 */
		Highcharts.Series.prototype.bindAxes = function () {
			var series = this,
				seriesOptions = series.options,
				chart = series.chart,
				axisOptions;
				
			if (series.isCartesian) {
				
				each(['xAxis', 'yAxis'], function (AXIS) { // repeat for xAxis and yAxis
					
					each(chart[AXIS], function (axis) { // loop through the chart's axis objects
						
						axisOptions = axis.options;
						
						// apply if the series xAxis or yAxis option mathches the number of the 
						// axis, or if undefined, use the first axis
						if ((seriesOptions[AXIS] === axisOptions.index) ||
								(seriesOptions[AXIS] !== UNDEFINED && seriesOptions[AXIS] === axisOptions.id) || // docs: series.xAxis and series.yAxis can point to axis.id
								(seriesOptions[AXIS] === UNDEFINED && axisOptions.index === 0)) {
							
							// register this series in the axis.series lookup
							axis.series.push(series);
							
							// set this series.xAxis or series.yAxis reference
							series[AXIS] = axis;
							
							// mark dirty for redraw
							axis.isDirty = true;
						}
					});

					// The series needs an X and an Y axis
					if (!series[AXIS]) {
						error(17, true);
					}

				});
			}
		};
	}(Highcharts));
	// End plugin
	
	
	
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
    var yTickHeight = 20;
    
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
        	height: yAxisHeight,
        };
    
    chartOptions = {
            chart: {
                renderTo: 'diagram',
                /*zoomType: 'x',
                animation: {
                    duration: 1000
                },*/
                type: 'line',
                zoomType: 'x',
                alignTicks: false
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
                text: 'ECG Viewer'
            },
            exporting:{
                buttons: {
                    exportButton: {
                        menuItems: [{
                            text: 'Export to PNG',
                            onclick: function() {
                                this.exportChart({
                                    width: 2000
                                });
                            }
                        }, 
                        /*{
                            text: 'Export to PDF',
                            onclick: function() {
                                this.exportChart({
                                	type: "application/pdf"
                                });
                            }
                        },
                        */
                        {
                            text: 'Export to SVG',
                            onclick: function() {
                                this.exportChart({
                                	type: "image/svg+xml"
                                });
                            }
                        },
                        null,
                        null
                        ]
                    }
                }
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
            	adaptToUpdatedData: false,
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
                    /*
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
                    */
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
                    /*
                    point: {
                    	events: {
                    		click: function(event){
                    			this.select(true, true);
                    			//alert(this.series);
                    			return false;
                    		}
                    	}
                    }
                    */
                }
            },
            xAxis: {
            	/*
				events : {
					afterSetExtremes : afterSetExtremes
				},
				*/
				//minRange: 1000,
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
    
    function afterSetExtremes(e){
    	plot.showLoading('Loading data from server...');
    	
    	min = Math.round((e.min-Date.UTC(0, 0, 0, 0, 0, 0, 0))/(1000/frequency));
    	max = Math.round((e.max-Date.UTC(0, 0, 0, 0, 0, 0, 0))/(1000/frequency));
    	var newData = [];
    	var minVal = datasets[0].data[min];
    	var maxVal = datasets[0].data[min];
    	for(var j=min; j<=max; j++){
    		newData.push([e.min+(j-min)*4, datasets[0].data[j]]);
    		if(datasets[0].data[j]<minVal)
    			minVal = datasets[0].data[j]
    		if(datasets[0].data[j]>maxVal)
    			maxVal = datasets[0].data[j]
    	}
    	
    	plot.series[0].yAxis.setExtremes(minVal, maxVal);
    	console.log(minVal, maxVal);
		plot.series[0].setData(newData);

    	/*
    	for(var i=0; i<datasets.length; i++){
    		var newData = [];
        	for(var j=min; j<=max; j++){
        		newData.push(datasets[i].data[j]);
        	}
        	console.log(newData);
    		plot.series[i].setData(newData);
    	}
    	*/
    	//plot.redraw();
    	plot.hideLoading();
    }
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
    		position: {
    			my: "top",
    			at: "bottom",
    			of: $("#spinner")[0]
    		},
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
		plotEverything();  //generate main plot div
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
			padding: '0px 10px 0px 0px'
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
            	plot.destroy();
            	plot = null;
            	diagram.remove();
            	resizer.remove();
            	fileInput.remove();
            	//console.log(data);
            },
            done: function (e, data) {
            	//console.log(data.result);
            	//choice.remove()

            	//histogram.remove();
            	console.log(plot);
            	onDataReceived(data.result);
            },
            fail: function (e, data) {
            	alert('invalid file');
            	hideSpinner();
            }
        });
    	fileInput.appendTo(innerResizer);
    }
    
    function plotEverything() {
        var yTop = 65;
        chartOptions.series = [];
        chartOptions.yAxis = [];
        //loop to fill in yAxis and data series
        var diagramHeight = 65 //calculate the diagram height!!!!!65 is the top padding of chart,
        for(var i=0; i<datasets.length;i++) {
        	var yAxisOptions = $.extend(true, {}, yAxisOptionsTemplate); //!!!deep copy JSON object
        	yAxisOptions.title = {
        			text: datasets[i].label,
        			rotation: 0
        	};   	
        	//yAxisOptions.min = datasets[i].min-0.5;
        	//yAxisOptions.max = datasets[i].max+0.5;
        	//add checker to handler rambled value from any channel, 
        	var min = datasets[i].min;
        	var max = datasets[i].max;
        	var tempMin, tempMax;
        	if((max-min) > (50*yGridInterval)) {//greater than 10 blocks, only add 10 blocks based on max
        		//yAxisOptions.min = min;
        		//yAxisOptions.max = min + 49 * yGridInterval;  //draw 20 times of yGridInterval
        		//yAxisOptions.height = yTickHeight*(Math.ceil(yAxisOptions.max/yGridInterval)-Math.floor(yAxisOptions.min/yGridInterval));
        		tempMin = min;
        		tempMax = min + 49 * yGridInterval;
        		yAxisOptions.range = 50 * yGridInterval;
        		yAxisOptions.height = yTickHeight*(Math.ceil(tempMax/yGridInterval)-Math.floor(tempMin/yGridInterval));
        	}
        	else if((max-min) < (yGridInterval/100)){ //min and max are too close
        		yAxisOptions.max = max + yGridInterval;
        		yAxisOptions.min = max;
        		yAxisOptions.height = yTickHeight*(Math.ceil(yAxisOptions.max/yGridInterval)-Math.floor(yAxisOptions.min/yGridInterval));
        		//tempMax = max;
        		//tempMin = max - yGridInterval;
        		//yAxisOptions.range = 2 * yGridInterval;
        		//yAxisOptions.height = yTickHeight*(Math.ceil(tempMax/yGridInterval)-Math.floor(tempMin/yGridInterval));
        	}
        	else{
        		//yAxisOptions.max = max;
        		//yAxisOptions.min = min;
        		//yAxisOptions.height = yTickHeight*(Math.ceil(yAxisOptions.max/yGridInterval)-Math.floor(yAxisOptions.min/yGridInterval));
        		tempMax = max;
        		tempMin = min;
        		yAxisOptions.range = max - min;
        		yAxisOptions.height = yTickHeight*(Math.ceil(tempMax/yGridInterval)-Math.floor(tempMin/yGridInterval));
        	}
        	/*
    		yAxisOptions.max = max;
    		yAxisOptions.min = min;
    		yAxisOptions.height = yTickHeight*(Math.ceil(max/yGridInterval)-Math.floor(min/yGridInterval));
    		if(yAxisOptions.height > 500){
    			yAxisOptions.height = 500
    			yAxisOptions.max = min + 499;
    		}
    		*/
        	//console.log("min of ", datasets[i].label, " is ", yAxisOptions.min);
        	//console.log("max of ", datasets[i].label, " is ", yAxisOptions.max);
        	console.log("min of ", datasets[i].label, " is ", tempMin);
        	console.log("max of ", datasets[i].label, " is ", tempMax);
        	console.log("height of ", datasets[i].label, " is ", yAxisOptions.height);
        	yAxisOptions.top = yTop;
        	yTop += yAxisOptions.height; //!!!!adjust the distance to the top
        	diagramHeight += yAxisOptions.height;
        	chartOptions.yAxis.push(yAxisOptions);
        	chartOptions.series.push({
        		name: datasets[i].label,
                data: datasets[i].data,
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                yAxis: i, //use the index of dataset as the index of yAxis
                pointInterval: 1000/frequency // 5 millisecond<--wrong! should be 1000/frequency. in this case 1000/250 = 4
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
        
		diagramHeight += 93; //93 is bottom padding
		
    	//plot all channels on one plot
    	diagram = $('<div id="diagram" ></div>').css( {
            height: diagramHeight.toString() + 'px',
        });
		
    	diagram.appendTo(innerResizer);

    	plot = new Highcharts.StockChart(chartOptions, function() {
    		hideSpinner();
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