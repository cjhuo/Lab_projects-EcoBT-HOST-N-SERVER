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

	function onDataReceived(data) { //setup plot after retrieving data
		if( data.from == 'node')
			if(name == "Demo" || name.trim() == data.data.name.trim())
				if(data.data.type == 'ecg'){
					updateChart(data.data);
				}
	}
	function updateChart(data) {
		//update chart
		chart.series[0].addPoint(data.I, true, true);
		chart.series[1].addPoint(data.II, true, true);
		chart.series[2].addPoint(data.III, true, true);
		chart.series[3].addPoint(data.aVR, true, true);
		chart.series[4].addPoint(data.aVL, true, true);		
		chart.series[5].addPoint(data.aVF, true, true);		
		chart.series[6].addPoint(data.V1, true, true);		
		chart.series[7].addPoint(data.V2, true, true);		
		chart.series[8].addPoint(data.V3, true, true);		
		chart.series[9].addPoint(data.V4, true, true);		
		chart.series[10].addPoint(data.V5, true, true);		
		chart.series[11].addPoint(data.V6, true, true);			
	}
	
	var init = function() {
		showSpinner();
		addPlot();
	}
	

	var diagram; //store DOM object of plot div
    var plot;  //store main plot object will be returned by flot
    var options; //options settings for main plot
        
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
    
    var total_points = 2500;
    function addPlot() { 
    	//generate one plot for each channel

    	var resizer = $('<div id="resizer" />').css( {
            width: '100%',
            minHeight: '400px',
            //border: '1px solid silver'

        });	
		resizer.appendTo("body");
    	
		var innerResizer = $('<div id="innerResizer" />').css( {
			padding: '10px'
        });	
		innerResizer.appendTo(resizer);
		
		//calculate the diagram height
		
		var diagramHeight = 65 + yAxisHeight*ECG_CHANNELLABELS.length + 93; //!!!!!65 is the top padding of chart,
															//93 is bottom padding
		
    	//plot all channels on one plot
    	diagram = $('<div id="diagram" ></div>').css( {
            height: diagramHeight.toString() + 'px',
        });
		
    	diagram.appendTo(innerResizer);
    	
    	plotInit();
		//plotEverything(); //plot diagram on generated div and generate overview
    }
    
    var plotInit = function() {
        var yTop = 65//65;
        
        //loop to fill in yAxis and data series
        for(var i=0; i<ECG_CHANNELLABELS.length;i++) {
        	var yAxisOptions = $.extend(true, {}, yAxisOptionsTemplate); //!!!deep copy JSON object
        	yAxisOptions.title = {
        			text: ECG_CHANNELLABELS[i],
        			y: -20,
        			rotation: 0
        	};
        	yAxisOptions.top = yTop;
        	yTop += yAxisHeight; //!!!!adjust the distance to the top
        	
        	chartOptions.yAxis.push(yAxisOptions);    
        	
        	//generate 0 for all 2500 samples at the beginning
        	var initData = [];
        	for(var j=0; j<total_points; j++){
        		initData.push(0);
        	}
        	chartOptions.series.push({
        		name: ECG_CHANNELLABELS[i],
                data: initData,
                pointStart: Date.UTC(0, 0, 0, 0, 0, 0, 0),
                yAxis: i, //use the index of dataset as the index of yAxis
                pointInterval: 4 // should be 1000/frequency. in this case 1000/250 = 4
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
    
    //init();
});