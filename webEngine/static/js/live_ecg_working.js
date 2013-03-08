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
	var frequency = 250;
    var ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'];
    var TOTAL_POINTS = 2500;
	
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
		//console.log(data);
		if( data.from == 'node'){
			if(name.trim() == data.data.address.trim())
				if(data.data.type == 'ecg'){
					datasets = data.data.data;
					//console.log(datasets.length);
					/*
					removeProgressBar();
					addCountDownDiv();
					addCountDownButton();
					addStartButton();
					addStopButton();
					stopButton.hide();
					*/
					plotEverything();
				}
				else if(data.data.type == 'ECG'){ //state info
					if(data.data.value.type == 'state'){
						if(data.data.value.value == 0){
							// ready to start real recording
							if(startButton != null && redoButton != null){
								plot.hideLoading();
								startButton.button("enable");
								redoButton.button("enable");
							}
						}
					}
					else if(data.data.value.type == 'progress'){
						updateProgress(data.data.value.value);
					}
				}
		}
		else if(data.from == 'central') {
			if(data.data.type == 'message'){
				alert(data.data.value);
				open('/administration', '_self', true);
			}
		}
	}
	
	var init = function() {
		showProgressBar();
		
		addResizer();
		addRedoButton();
		redoButton.button("enable");
		/*
		addCountDownDiv()
		addCountDownButton();
		addStartButton();
		addStopButton();
		stopButton.hide();
		*/
	}
	

	var diagram; //store DOM object of plot div
    var plot;  //store main plot object will be returned by
    var chartOptions; //chartOptions settings for main plot
        
    var xGridInterval = 200; //0.2 second
    var yGridInterval = 500; // 0.5mV, assuming the unit of ECG output is micro volt
    var yAxisHeight = 200;
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
	        /*
	    	plotLines: [{
	    		value: 0,
	    		width: 1,
	    		label: {
	    			text: '0',
	    			align: 'left',
	    			y: 0,
	    			x: 0
	    		}
	    	}],
	    	*/
        	labels: {
        		enabled: false,
        		align: 'right'
        	},
        	offset: 0,
        	//height: yAxisHeight,
	    	startOnTick: true,
	    	endOnTick: true	
        };
    
    chartOptions = {
            chart: {
                renderTo: 'diagram',
                zoomType: 'x',
                
                /*
                animation: {
                    duration: 1000
                },*/
                type: 'line',
                /**
                 * When using multiple axis, the ticks of two or more opposite axes will automatically 
                 * be aligned by adding ticks to the axis or axes with the least ticks. This can be prevented
                 *  by setting alignTicks to false. If the grid lines look messy, it's a good idea to hide them 
                 *  for the secondary axis by setting gridLineWidth to 0. Defaults to true.
                 */
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
                text: '10 seconds ECG Data'
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
            	xAxis: {
            		labels:{
            			enabled: true
            		}
            	}
            	//adaptToUpdatedData: false
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
            	},
            	{
            		type: 'millisecond',
            		count: 5000,
            		text: '5s'
            	},
            	{
            		type: 'all',
            		text: 'All'
            	}],
            	selected: 2
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
    	var newData = [];
    	//console.log(e.min-Date.UTC(0, 0, 0, 0, 0, 0, 0), e.max-Date.UTC(0, 0, 0, 0, 0, 0, 0));
    	min = e.min-Date.UTC(0, 0, 0, 0, 0, 0, 0);
    	max = e.max-Date.UTC(0, 0, 0, 0, 0, 0, 0);
    	console.log(plot.series);
    	for(var i=0; i<datasets.length; i++){
        	for(var j=min/(1000/frequency); j<=max/(1000/frequency); j++){
        		newData.push(datasets[i].data[j]);
        	}
        	console.log(newData);
    		plot.series[i].setData(newData);
    	}
    	plot.hideLoading();
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
			padding: '0px 10px 0px 0px',
			//marginTop: '30px'
        });	
		innerResizer.appendTo(resizer);
    }
    
    function plotEverything() {
    	if(plot == null){ // init plot
	    	console.log(datasets);
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
	        	//var min = Math.min.apply(null, datasets[i].data);
	        	//var max = Math.max.apply(null, datasets[i].data);
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
	        	/*
	        	var tmpData = [];
	        	for(var j=0;j<TOTAL_POINTS;j++){
	        		if(j<TOTAL_POINTS-datasets[i].data.length)
	        			tmpData.push(yAxisOptions.min) // padding points
	        		else
	        			tmpData.push(datasets[i].data[j-(TOTAL_POINTS-datasets[i].data.length)]); //received points
	        	}
	        	*/
	        	
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
	
	    	plot = new Highcharts.StockChart(chartOptions);     
    		//showSpinner();
	    	plot.showLoading("RECEIVING DATA...");
    	}
    	else{ // update plot
    		console.log(datasets[0]);
    		for(var i=0; i<datasets.length;i++) {
    			plot.series[i].setData(datasets[i].data, false);
    			/*
	        	for(var j=0;j<datasets[i].data.length;j++){
	        		plot.series[i].addPoint(datasets[i].data[j], false, true);
	        	}
	        	*/
    		}
    		plot.redraw();
    	}
    }
    var redoButton;
    function addRedoButton() {
    	redoButton = $('<button>REDO TEST RECORDING</button>').css({
    		float: 'right',
    		fontSize: 'small',
    		position: 'relative',
    		//right: '0px',
    		top: '0px'
    	});   	
    	redoButton.button();
    	redoButton.button("disable");
    	redoButton.click(redoTest);
    	redoButton.appendTo(innerResizer);
    }
    function redoTest() {
    	startTestECG();
		//this.remove();
		location.href = location.href; //reload
    }
    function startTestECG() {
    	socket.send("startTestECG"+name.trim());
    }
    var startButton, stopButton, countDownButton;
    function addStartButton() {
    	startButton = $('<button>START RECORDING</button>').css({
    		float: 'right',
    		fontSize: 'small',
    		position: 'relative',
    		//right: '0px',
    		top: '0px'
    	});   	
    	startButton.button();
    	startButton.button("disable");
    	startButton.click(startECG);
    	startButton.insertBefore(diagram);
    }
    function startECG() {
    	socket.send("startECG"+name.trim());
    	startButton.hide();
    	redoButton.hide();
    	stopButton.show();
    	showSpinner();
    }
    function stopECG() {
    	if(countDownDiv.countdown('getTimes') != null)
    		countDownDiv.countdown('destroy');
    	socket.send("stopECG"+name.trim());
    	stopButton.hide();
    	hideSpinner();
    	showCompleteDialog();
    	//startButton.show();
    }
    function showCompleteDialog(){
    	$( "<div id='complete'>RECORDING COMPLETE, PLEASE DETACH SENSOR</div>" ).dialog({
    		position: {
    			my: "top",
    			at: "top",
    			of: $("#diagram")
    		},
	      resizable: false,
	      height: 300,
	      width: 300,
	      modal: true,
	      buttons: {
	        "OK": function() {
	          open('/administration', '_self', true);
    	     }
    	  }
    	});
    	$(".ui-dialog-titlebar").hide();
    }
    function addStopButton() {
    	stopButton = $('<button>STOP RECORDING</button>').css({
			float: 'right',
			fontSize: 'small',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
		stopButton.button();
		stopButton.button("enable");
		stopButton.click(stopECG);
		stopButton.insertBefore(diagram);
    }
    function addCountDownButton() {
    	countDownButton = $('<button>SET TIMER</button>').css({
			float: 'right',
			fontSize: 'small',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
    	countDownButton.button();
    	countDownButton.click(countDownPopup);
    	countDownButton.insertBefore(diagram);
    }
    var countDownDiv;
    function addCountDownDiv() {
    	countDownDiv = $("<div id='countDown' ></div").css({
    		margin: 'auto',
    		width: '200px',
    		height: '45px'
    	});
    	countDownDiv.insertBefore(spinTarget);
    	countDownDiv.hide();
    }
    //var countDownInput;
    function countDownPopup() {
    	var popUpDiv = $('<div id="popUpBox"><div>');
    	$("<p>Please choose the time for EKG recording: </p>").appendTo(popUpDiv);
    	
		var input = $("<input id='countDownInput' value = '5'/>").css({
			fontSize: 'small',
			width: '30px'
		});
		input.appendTo(popUpDiv);
		$("<label for='countDownInput'> MINUTE(S)</label>").appendTo(popUpDiv);
		input.spinner({min: 1});
    	popUpDiv.dialog({
    		position: {
    			my: "top",
    			at: "bottom",
    			of: startButton
    		},
            width: 300,
            modal: true,
            resizable: false,
            buttons: {
                "START": function() {
                	t = input.spinner("value") * 60;
                	startECG();
                	countDownDiv.countdown({until: +t, format: 'MS', onExpiry:stopECG});
                	countDownDiv.show();
                	countDownButton.hide();
                    $( this ).dialog( "destroy" );
                }
            }
        }).css({
        	fontSize: 'small'
        });
    	$('.ui-button').css({
    		fontSize: 'small'
    	});
    }
    
    var progressBar;
    var progressLabel;
    function showProgressBar() {
    	progressLabel = $("<div id='progressLabel'>Recording...</div>").css({
    		float: 'left',
        	marginLeft: '45%',
        	fontWeight: 'bold',
        	textShadow: '1px 1px 0 #fff',
    	});
    	progressBar = $("<div id='progress'></div>");
    	progressLabel.appendTo(progressBar);
    	progressBar.progressbar({
    	      value: false,
    	      change: function() {
    	          progressLabel.text( progressBar.progressbar( "value" ) + "%" ).css({
    	          });
    	        },
    	        complete: function() {
    	          progressLabel.text( "Complete!" );
    	        }
        }).css({
        	width: '98%',
        	margin: 'auto'
        });
    	progressBar.appendTo("body");
    }
    
    function removeProgressBar() {
    	progressBar.remove();
    	progressLabel.remove()
    }
    
    function updateProgress(percent){
    	progressBar.progressbar( "value", percent );
    	if(percent == 100){
			removeProgressBar();
			addCountDownDiv();
			addCountDownButton();
			addStartButton();
			addStopButton();
			stopButton.hide();
    	}
    }
    
	var socket = null; //websocket object	
	var reconMsg = null; //reconnect div object
	
	/**
	* use to store reconnect procedure, to make sure there is only 1 websocket to server generated
	* not thread safe!!!TBD
	*/
	var reconn = null; 	
	function showReconMsg(msg) {
		if(reconMsg == null) {
			reconMsg = $('<div id="reconnect" >' + msg + '</div>').css( {
		        position: 'absolute',
		        top:0,
		        right:0,
		        //width: '100%',
		        //height: '50px',
		        margin: 'auto'
			});
			reconMsg.appendTo("body");
		}
	}
	
	function hideReconMsg() {
		if(reconMsg != null){
			reconMsg.remove();
			reconMsg = null;
		}
	}
	
	function establishConnection() {
		/*
		if(socket != null){
			socket.close();
			socket = null;
		}
		*/
	    socket = new WebSocket(url);
	    hideReconMsg();
		showReconMsg('connecting to server...');
	    socket.onopen = function(event) {
			hideReconMsg();
	    };
	    socket.onmessage = function(event) {
	    	onDataReceived($.parseJSON(event.data));
	    };
	    socket.onerror = function(event) {
	    	alert('Error, readyState code is: ' + socket.readyState);
	    	socket.close();
	    	establishConnection();
	    };
	    
	    socket.onclose = function(event) {
	    	//alert(socket.readyState);
		    //var t = setInterval(function() {//check if connection is lost, for the case when server is down
				//if(socket.readyState == 2 || socket.readyState == 3){ //connection is closed or closing
			
	    	/**
			 * try to reconnect when connection is closed or closing. If reconnection has been 
			 * issued by other functions such as 'online' event handler then skip to prevent
			 * duplication of socket. 'closing' connection will eventually be timed out and garbage collected,
			 * so no worry of duplicated connection
			 * 
			 * */
	    	if(socket.readyState == 2 || socket.readyState == 3){
				hideReconMsg();
				showReconMsg('connection reset by server, reconnecting in 5 secs...');
				if(reconn == null){
					reconn = setTimeout(function() {
						establishConnection();
						hideReconMsg();
						reconn = null;
						//alert('Network is back, readyState is: ' + socket.readyState);
					}, 5000);
				}
				/*
				else {
					alert('reconnect issued!');
				}
				*/
			}
			/*
			else if(socket.readyState == 1) {
				clearInterval(t);
				hideReconMsg();
			}
			*/			
		    //}, 6000);
	    };
	}
	
	function update(){
		if (navigator.onLine) { //navigator.onLine supports limited browsers, see https://developer.mozilla.org/en-US/docs/DOM/window.navigator.onLine
			establishConnection();	
		}
		else {
			showReconMsg('brower is offline, check wifi...');
		}
	}
	
	$(window).bind('load', function(e) {
		init();
		//animate();
		update();
		/*
		setInterval(function(){
			render();
		}, 1000);
		*/
	});

	$(window).bind('online', function(e) {
		/*
		if(socket != null)
			alert('Network is back, readyState is: ' + socket.readyState);
		*/
		/*
		if(socket != null){
			socket.close();
			//socket = null;
		}
		*/ 
		hideReconMsg();
		showReconMsg('connection is back, connecting server in 5 secs...');
		if(reconn == null) {
			reconn = setTimeout(function() {
				establishConnection();
				//alert('Network is back, readyState is: ' + socket.readyState);
				hideReconMsg();
				reconn = null;
			}, 5000);
		}
	});
	
	$(window).bind('offline', function(e) {
		/**
		 * firing a close() cause a connection to close or to timeout on user browser's side after 
		 * 300secs by default; WebSocket on tornado server will also be closed or timed out.
		 * 
		 * This is just for the purpose of setting socket.readyState to 'CLOSED' in order to garbage 
		 * collect old socket and generate new socket next time when browser is online.
		 * This is used for the case of lost connection when browser waked up from sleep and timed 
		 * out at server side. if close() is not issued, when browser is back from sleep, readyState 
		 * will still be 'OPEN'. Connection lost will only be detected unless after 300secs or 
		 * (by sending to server something such as close(), send() I guess...).
		 * 
		 * The close is actually issued when browser is back from wake since there is no way close
		 * request can be sent to server when offline 
		 * 
		 * This is only a workaround since there is no way whether the connection still exist even if
		 * websocket.readyState on browser side is 'OPEN'. A short ping-pong mechanism might resolve 
		 * the issue.
		 * */
		socket.close();
		hideReconMsg();
		showReconMsg('connection lost, check wifi...')
	});	

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
        margin: 'auto',
        display: 'none'
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
    
    //init();
});