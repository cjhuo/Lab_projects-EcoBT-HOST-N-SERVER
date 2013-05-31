$(function () {
	var url = $('#serverAddr').text(); 	//push url, need to change this to server's url, 
	var name0 =  $('#name0').text(); // left node
	var name1 =  $('#name1').text(); // right node
		
    var datasets; //store datasets
	function onDataReceived(data) { //setup plot after retrieving data
		console.log(data);
		if( data.from == 'node'){
			if(name0.trim() == data.data.address.trim() || name1.trim() == data.data.address.trim())
				if(data.data.type == 'SIDsRead'){ //real data
					updateChart(data);
				}
		}
		else if(data.from == 'central') {
			//console.log(data);
			if(data.data.type == 'message'){
				alert(data.data.value);
				open('/', '_self', true);
			}
		}
	}
	
	function updateChart(data) {
		//update chart
		if(name0.trim() == data.data.address.trim()){
			chart.series[0].addPoint(data.data.value[3], false, true);
			chart.series[1].addPoint(data.data.value[6], true, true);
		}
		if(name1.trim() == data.data.address.trim()){
			chart.series[2].addPoint(data.data.value[3], false, true);
			chart.series[3].addPoint(data.data.value[6], true, true);
		}
	}
	
	var init = function() {
		//showSpinner();
		initLayout();
		initChart();
		/*
		initSimulation();
		initTemperatureChart();
		initHumidityChart();
		initSoundMonitor();
		*/
		
	}
	
	function initLayout(){
		$('body').layout({
			closable: false,
			resizable: false,
			north__size:	.65,	
			north__childOptions:	{
				closable: false,
				resizable: false,
				east__size: .50,		
			}
		});
	}
	
	var chartContainer;
	var chart;
	var container = $("#simulation");
	var total_points = 100;
	function initChart() {
		chartContainer = $("<div id='chart' class='chart'/>").appendTo(container);
		options = {
            chart: {
                renderTo: 'chart',
                type: 'line',
                backgroundColor: 'transparent',
            },
            title: {
                text: 'Simulation of RAW Data'
            },
            credits: {
            	href: "http://embedded.ece.uci.edu/",
            	text: "UCI Embedded Lab"
            },
            xAxis: {
            	reversed: true,
            	labels: {
            		enabled: false
            	},

            },
            yAxis: {
            	title: {
            		text: ''
            	},
            	labels: {
            		enabled: true
            	},

            },

            plotOptions: {
            	line: {
            		animation: false
            	},
                series: {
                    marker: {
                        enabled: false
                    }
                }
            },
            tooltip: {
                formatter: function() {
                	return '<b>'+ this.series.name +'</b>:'+ this.y;
                }
            },
            legend: {
            	enabled: true,
            	layout: 'vertical',
                align: 'left',
                verticalAlign: 'top',
                x: -10,
                y: 100,
                borderWidth: 0
            },
            exporting: {
                enabled: false
            },
            series: []
        };
		
		// init chart with all point with 0
	    var data = [];
	    for (var i = 0; i < total_points; i++){
			data.push(0);
		}
        options.series.push({
        	name: 'LED1 from left node',
            data: data,
        });
        options.series.push({
        	name: 'LED2 from left node',
            data: data,
        });
        options.series.push({
        	name: 'LED1 from right node',
            data: data,
        });
        options.series.push({
        	name: 'LED2 from right node',
            data: data,
        });
		chart = new Highcharts.Chart(options);
		$(window).resize(function() {   
				    clearTimeout(this.id);
				    this.id = setTimeout(function(){
					    chart.setSize(
							       $('#chart').width(), 
							       $('#chart').height(),
							       true
							    );  
				    }, 500);
				});
	}
	
	// start of handling websocket connection
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
			//socket.send("sendSIDsSet"+name.trim());
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
		if(url.indexOf('ws://localhost') == -1){
			if (navigator.onLine) { //navigator.onLine supports limited browsers, see https://developer.mozilla.org/en-US/docs/DOM/window.navigator.onLine
				establishConnection();	
			}
			else {
				showReconMsg('brower is offline, check wifi...');
			}
		}
		else{
			establishConnection();
		}
	}
	
	//$(window).bind('resize', onWindowResize);
	
	$(window).bind('load', function(e) {
		init();
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
		if(url.indexOf('ws://localhost') == -1){
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
		if(url.indexOf('ws://localhost') == -1){
			socket.close();
			hideReconMsg();
			showReconMsg('connection lost, check wifi...');
		}
	});	
	//end of handling websocket connection
	
	
	//start of ajax animation
	var spinTarget, spinner;; //spinner
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
    /* show loading spinner, stopped when chart is fully loaded */
    function showSpinner(){
    	if(spinTarget == null){
    		spinTarget = $('<div id="spinner" ></div>').css( {
    	        position: 'relative',
    	        width: '50px',
    	        height: '50px',
    	        margin: 'auto'
    		});  
    		spinTarget.appendTo("body");
    		spinner = new Spinner(spinnerOpts);
    	}
    	spinTarget.show();
		spinner.spin(spinTarget[0]);
    }
    
    function hideSpinner(){
		spinTarget.hide();
		spinner.stop();
    }
    //end of ajax animation
});