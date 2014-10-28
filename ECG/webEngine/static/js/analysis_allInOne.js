
$(function () {
	
	//ajax call urls
	var fileHandlerUrl = 'ecgAllInOne';
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
    var yTickHeight = document.ontouchstart === undefined ? 20 : 30;
    var xTickHeight = document.ontouchstart === undefined ? 20 : 30;
    
    var yAxisOptionsTemplate = {
    		
        	lineColor: 'rgb(245, 149, 154)',
        	gridLineColor: 'rgb(245, 149, 154)', 
        	gridLineWidth: document.ontouchstart === undefined ? 0.5 : 2,
        	minorGridLineColor: 'rgb(245, 149, 154)',
        	minorGridLineWidth: document.ontouchstart === undefined ? 0.2 : 1,
        	
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
                zoomType: document.ontouchstart === undefined ? 'x': '',
                alignTicks: false,
                marginRight: 50,
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
                text: 'ECG Viewer (Maximum time slot: 10 seconds)'
            },
            exporting:{
            	enabled: false, //disable exporting due to bug on invoking destroying chart object for now
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
                enabled: false,
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
        	        	hour: '%H:%M:%S',
        	        	day: '%H:%M:%S',
        	        	week: '%H:%M:%S',
        	        	month: '%H:%M:%S',
        	        	year: '%H:%M:%S'
        	        },
        	        startOnTick: true,
        	        endOnTick: true
            	}
            },
            scrollbar: {
            	enabled: true,
    			liveRedraw: false
            },
            rangeSelector:{
            	enabled: true,
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
                		enabled: document.ontouchstart === undefined ? false : true
                	},
                	allowPointSelect: false,
                	animation: false,
                	color: 'black',	
                	lineWidth: 0.7,
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
				
				//minRange: 1000,
                minRange: 1000,
                //setting the scrollbar's position to the left
                min: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                max: document.ontouchstart === undefined ? Date.UTC(0, 0, 0, 0, 0, 0, 0) + 10* 1000 
                		: Date.UTC(0, 0, 0, 0, 0, 0, 0) + 5 * 1000,
                events: {
					afterSetExtremes : afterSetExtremes,
                	setExtremes: setExtremes
                },
            	
            	lineColor: 'rgb(245, 149, 154)',
            	gridLineColor: 'rgb(245, 149, 154)',
            	gridLineWidth: document.ontouchstart === undefined ? 0.5 : 2,
            	minorGridLineColor: 'rgb(245, 149, 154)',
            	minorGridLineWidth: document.ontouchstart === undefined ? 0.2 : 1,
            	
            	minorTickInterval: xGridInterval/5, //5 minor tick by default, exactlly what we want
    	        minorTickWidth: 1,
    	        minorTickLength: 0,
    	        minorTickPosition: 'inside',
    	        minorTickColor: 'rgb(245, 149, 154)',
    	
    	        //tickPixelInterval: 30,
    	        tickInterval: xGridInterval, //0.2 second
    	        tickWidth: 2,
    	        tickPosition: 'inside',
    	        tickLength: 0,
    	        tickColor: 'rgb(245, 149, 154)',
    	        
        		dateTimeLabelFormats: {
        			millisecond: '%H:%M:%S',
    	        	second: '%H:%M:%S',
    	        	minute: '%H:%M:%S',
    	        	hour: '%H:%M:%S',
    	        	day: '%H:%M:%S',
    	        	week: '%H:%M:%S',
    	        	month: '%H:%M:%S',
    	        	year: '%H:%M:%S'
    	        },
    	        
    	        labels: {
    	        	enabled: true,
    	        	step: 10,
    	        	overflow: false
    	        },
    	        startOnTick: false,
    	        endOnTick: false
            },
            tooltip: {
            	enabled: document.ontouchstart === undefined ? true : false,
            	backgroundColor: 'rgba(255, 255, 255, 0.1)'
            },
            yAxis: [],
            series: []
    };
    
    function setExtremes(e){
        var maxDistance = document.ontouchstart === undefined ? 10 * 1000 : 5 * 1000; //10 seconds
        var xaxis = this;
        if ((e.max - e.min) > maxDistance) {
            var min = e.max - maxDistance;
            var max = e.max;
            window.setTimeout(function() {
                xaxis.setExtremes(min, max);
            }, 1);
            return false;
        }  
        var minDistance = 1000; // 1 second
        if ((e.max - e.min) < minDistance) { //less than minrange
            var min = e.max - minDistance;
            var max = e.max;
            if(min < Date.UTC(0, 0, 0, 0, 0, 0, 0)){
            	min = Date.UTC(0, 0, 0, 0, 0, 0, 0);
            	max = e.min + 1000;
            }
            
            window.setTimeout(function() {
                xaxis.setExtremes(min, max);
            }, 1);
        	return false;
        }
    }
    
    function afterSetExtremes(e){
    	plot.showLoading('Loading data from server...');
    	
    	var min = Math.round((e.min-Date.UTC(0, 0, 0, 0, 0, 0, 0))/(1000/frequency));
    	var max = Math.round((e.max-Date.UTC(0, 0, 0, 0, 0, 0, 0))/(1000/frequency));
    	var tmpDatasets = [];
		$.ajax({
			type: 'GET',
			url: dataUrl,
			dataType: 'json',
			cache: false,
			data: {"min":min, "max": max},			
			error: function() {plot.hideLoading();/*alert("Server Error!");*/},
			success: function(data){
				tmpDatasets = data.data;
				
				// remove original series
				//console.log(plot.series.length, tmpDatasets.length);
				for(var i=0; i<tmpDatasets.length; i++){
					//console.log(plot.series[i].name);
					//plot.series[0].remove(false);
					var dataWithTime = [];
					for(var j=0; j<tmpDatasets[i].data.length; j++){
						dataWithTime.push([e.min + j*1000/frequency, tmpDatasets[i].data[j]]);
					}
					
					plot.series[i].setData(dataWithTime, false);
					
					// adjust min and max according on every y axis
					var minVal = tmpDatasets[i].min;
					var maxVal = minVal + 11 * yGridInterval; //tmpDatasets[i].max;
					plot.series[i].yAxis.setExtremes(minVal, maxVal, false);
				}
				
				plot.redraw();				
				plot.hideLoading();
			},
		});
    }

	/* issue ajax call and further process the data on sucess */
	function getAndProcessData() { 
    	getDicomList();
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
	
	var dicomList;
	var dicomListMenu;
	function getDicomList() {
		$.ajax({
			url: '/dicomList',
			cache: false,
			type: 'GET',
			async: false,
			dataType: 'json',
			success: function(data) {
				dicomList = data.fileList;
			}
		});
    	
    	dicomListMenu = $('<ul>').css({
    		zIndex: '2000'
    	}).appendTo('body');
    	$.each(dicomList, function(key, val) {
    		var lnk = $('<li><a href="#">' + val + '</a></li>').click(function() {
    			$.ajax({
					url: fileHandlerUrl,
					cache: false,
					type: 'POST',
					dataType: 'json',
					data: {"filename": val},
					beforeSend: function() {
						showSpinner();
						$('#fileChooser').dialog( "destroy" );
						dicomListMenu.hide();						
					},
					success: onDataReceived
				});
    		});
    		lnk.appendTo(dicomListMenu);
    	});
    	dicomListMenu.hide().menu();
	}
	
	function chooseFileSource(){
    	var popUpDiv = $('<div id="fileChooser"/>');
    	$('<p>Please choose choose a dicom file: </p>')
    		.appendTo(popUpDiv);
    	var fileListButton = $('<button>Select Recorded Files</button>').css({
    		float: 'left',
    		fontSize: 'small',
    	});

    	fileListButton.button({
            icons: {
                primary: "ui-icon-triangle-1-s"
              }
    	});
    	//fileListButton.click(chooseTestFile);
    	popUpDiv.append(fileListButton);

    	fileListButton.click(function(event){    		
    		dicomListMenu.show().position({
                my: "left top",
                at: "left bottom",
                of: this
              });           
            $( document ).one( "click", function() {
            	dicomListMenu.hide();
              });
            return false;
    	});
    	
    	var fileInput = $('<div class="file-wrapper">\
						<span>Submit your own Dicom file</span>\
		        		<input style="width:100%" type="file" \
						name="uploaded_files" ></div>')
		    			.css({
				    		float: 'right',
				            marginLeft: '5px',
				    		fontSize: 'small',
				    	});
    	
    	fileInput.button();
    	fileInput.fileupload({
    		url: fileHandlerUrl,
            dataType: 'json',
            send: function (e, data) {
            	showSpinner();
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
            modal: false,
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
		plotEverything();  //generate main plot div
		//addOverview(); // generate overview plot div	
	}

    var pointInterval, base;
	function extractDatasets(data) {
		datasets = data.dspData;
		pointInterval = data.pointInterval;
		base = data.base;
	}
    var resizer, innerResizer;
	function addResizer(diagramLength) {
		if(diagramLength == null)
			diagramLength = '100%';
		else
			diagramLength = diagramLength.toString() + 'px';
    	resizer = $('<div id="resizer" />').css( {
            //width: diagramLength,
            width: '100%',
            minHeight: '400px',
            margin: 'auto',
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
                <input style="width:100%" type="file" name="uploaded_files" >\
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
            	//plot.destroy();
            	plot = null;
            	diagram.remove();
            	resizer.remove();
            	fileInput.remove();
            	//overViewButton.remove();
            	generateButton.remove();
            	//console.log(data);
            },
            done: function (e, data) {
            	//console.log(data.result);
            	//choice.remove()

            	//histogram.remove();
            	//console.log(plot);
            	onDataReceived(data.result);
            },
            fail: function (e, data) {
            	alert('invalid file');
            	hideSpinner();
            }
        });
    	fileInput.appendTo(innerResizer);
    }
    /*
    var overViewButton;
    function addOverViewButton(){
    	var minCount = parseInt(datasets[0].data.length*pointInterval/1000/60);
    	var secCount = (datasets[0].data.length*pointInterval/1000) % 60;
    	overViewButton = $('<button>CLICK TO SEE ALL ' + minCount + ' minutes and ' + secCount + ' seconds</button>').css({
    		float: 'left',
    		fontSize: 'small',
    	});   	

    	overViewButton.button();
    	overViewButton.click(plotLarge);
    	overViewButton.appendTo(innerResizer);
    	
    }
    */
    function plotLarge(){
    	window.open('plotLarge', '_blank', false);
    	return false;
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
        			align: 'middle',
        			rotation: 0,
        			//y: 15
        	};   	
        	//yAxisOptions.min = datasets[i].min-0.5;
        	//yAxisOptions.max = datasets[i].max+0.5;
        	//add checker to handler rambled value from any channel, 
        	
        	var min = datasets[i].min;
        	var max = datasets[i].max;
        	yAxisOptions.min = min;
        	yAxisOptions.max = min + 11 * yGridInterval
        	yAxisOptions.height = yTickHeight*(Math.ceil(yAxisOptions.max/yGridInterval)-Math.floor(yAxisOptions.min/yGridInterval));
        	/*
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
        	*/
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
        	//console.log("min of ", datasets[i].label, " is ", tempMin);
        	//console.log("max of ", datasets[i].label, " is ", tempMax);
        	//console.log("height of ", datasets[i].label, " is ", yAxisOptions.height);
        	yAxisOptions.top = yTop;
        	yTop += yAxisOptions.height; //!!!!adjust the distance to the top
        	diagramHeight += yAxisOptions.height;
        	chartOptions.yAxis.push(yAxisOptions);
        	chartOptions.series.push({
        		name: datasets[i].label,
                data: datasets[i].data,
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                yAxis: i, //use the index of dataset as the index of yAxis
                pointInterval: /*pointInterval*/ 1000/frequency // 5 millisecond<--wrong! should be 1000/frequency. in this case 1000/250 = 4
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
        /*
        chartOptions.tooltip.positioner = function () {
        	return { x: 200, y: 20 };
        }
        */
        
        chartOptions.navigator.series = {
        		type: 'areaspline',
        		color: '#4572A7',
        		fillOpacity: 0.4,
        		dataGrouping: {
        			smoothed: true
        		},
        		lineWidth: 1,
        		marker: {
        			enabled: false
        		},
        		shadow: false,
                data: base[0],
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                pointInterval: pointInterval
        		};
        
		diagramHeight += document.ontouchstart === undefined ? 93 : 100;//93; //93 is bottom padding
		var diagramLength; //= datasets[0].data.length * pointInterval * xTickHeight / xGridInterval;
		console.log(diagramLength);
	    addResizer(diagramLength);
		addFileUploadDiv();
		//addOverViewButton();
		addGenerateButton();
    	//plot all channels on one plot
    	diagram = $('<div id="diagram" ></div>').css( {
            height: diagramHeight.toString() + 'px',
        });
		
    	diagram.appendTo(innerResizer);

    	plot = new Highcharts.StockChart(chartOptions);     
    	hideSpinner();
    }
    
    var generateButton;
    function addGenerateButton(){
    	var minCount = parseInt(datasets[0].data.length*pointInterval/1000/60);
    	var secCount = (datasets[0].data.length*pointInterval/1000) % 60;
    	generateButton = $('<button>GENERATE IMAGE FILE FOR ALL ' + minCount + ' minutes and ' + secCount + ' seconds</button>').css({
    		float: 'left',
    		fontSize: 'small',
    	});   	

    	generateButton.button();
    	generateButton.click(generateSVG);
    	generateButton.appendTo(innerResizer);
    	
    }
    
    function onDataReceivedForOutputFile(data){
		datasets = data.data;
		pointInterval = data.pointInterval;
		constructChartOptionsForOutput();
		
		//send options back to server
		$.ajax({
			url: dataUrl,
			cache: true,
			type: 'PUT',
			dataType: 'json',
			data: {'data': JSON.stringify(largeChartOptions)},
			beforeSend: showSpinner,
			success: function(data){
				hideSpinner();
				if(data.url != null){
					console.log(data.url);
					generateButton.remove();
					generateButton = $("<a target='_blank'>GENERATION DONE, CLICK TO VIEW/DOWNLOAD</a>")
									.attr('href', data.url)
									.button().css({
										fontSize: 'small',
									}).insertBefore(diagram);
					//window.open(data.url);				
				}
				else{// failure
					alert(data.message);
					
				}
			},
			error: function(data){
				hideSpinner();
				alert("Sever failure!");
			}
		});

    }
    var largeChartOptions = {
            chart: {
                alignTicks: false,
                marginRight: 50,
                //backgroundColor: "transparent",
                //plotBackgroundImage: "/static/Uploads/svg/chart1_20130316223730.png",
                //spacingLeft: 0,
                //spacingRight: 0

            },            
            credits: {
            	href: "http://cps.eng.uci.edu:8000/analysis",
            	text: "UCI Embedded Lab",
            },
            title: {
                text: 'ECG Viewer (All Samples)'
            },
            legend: {
                enabled: false,
            },
            navigator: {
            	enabled: false,
            },
            scrollbar: {
            	enabled: false
            },
            rangeSelector:{
            	enabled: false,
            },
            plotOptions: {
                line: {
                	dataGrouping: {
                		enabled: false
                	},
                	color: 'black',	
                	lineWidth: 0.7,
                    dataLabels: {
                        enabled: false
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
    	        
        		dateTimeLabelFormats: {
        			millisecond: '%H:%M:%S',
    	        	second: '%H:%M:%S',
    	        	minute: '%H:%M:%S',
    	        	hour: '%H:%M:%S',
    	        	day: '%H:%M:%S',
    	        	week: '%H:%M:%S',
    	        	month: '%H:%M:%S',
    	        	year: '%H:%M:%S'
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
    
    var lyAxisOptionsTemplate = {
    		
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
    		//gridLineWidth: 0,
        	labels: {
        		enabled: false,
        		align: 'right'
        	},
        	offset: 0,
        	//height: yAxisHeight,
        };
    function constructChartOptionsForOutput(){
    	//largeChartOptions = $.extend(true, {}, chartOptions);
        var yTop = 40; // top padding
        largeChartOptions.series = [];
        largeChartOptions.yAxis = [];
        //loop to fill in yAxis and data series
        var diagramHeight = 40; //calculate the diagram height!!!!!65 is the top padding of chart,
        for(var i=0; i<datasets.length;i++) {
        	var yAxisOptions = $.extend(true, {}, lyAxisOptionsTemplate); //!!!deep copy JSON object
        	yAxisOptions.title = {
        			text: datasets[i].label,
        			align: 'middle',
        			rotation: 0,
        			//y: 15
        	};   	
        	var min = datasets[i].min;
        	var max = datasets[i].max;
        	yAxisOptions.min = min;
        	yAxisOptions.max = min + 11 * yGridInterval
        	yAxisOptions.height = yTickHeight*(Math.ceil(yAxisOptions.max/yGridInterval)-Math.floor(yAxisOptions.min/yGridInterval));

        	yAxisOptions.top = yTop;
        	yTop += yAxisOptions.height; //!!!!adjust the distance to the top
        	diagramHeight += yAxisOptions.height;
        	largeChartOptions.yAxis.push(yAxisOptions);
        	largeChartOptions.series.push({
        		name: datasets[i].label,
                data: datasets[i].data,
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                yAxis: i, //use the index of dataset as the index of yAxis
                pointInterval: pointInterval //1000/frequency // 5 millisecond<--wrong! should be 1000/frequency. in this case 1000/250 = 4
        	});
        }        
		diagramHeight += 29; //29 is bottom padding
		var chartWidth = datasets[0].data.length * pointInterval * xTickHeight / xGridInterval;
	    largeChartOptions.chart.width = chartWidth;
	    largeChartOptions.chart.height = diagramHeight;
    }
    
    function generateSVG() {
		$.ajax({
			url: dataUrl,
			cache: true,
			type: 'GET',
			dataType: 'json',
			beforeSend: showSpinner,
			success: onDataReceivedForOutputFile
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