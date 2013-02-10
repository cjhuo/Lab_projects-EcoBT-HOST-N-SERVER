/**
 * Main script for generating plot.
 *
 * .with push technology
 *
 */

$(function () {
	var url = $('#serverAddr').val(); 	//push url, need to change this to server's url, 
										//such as cps.eng.uci.edu:8000/socket
	var name =  $('#name').text();
	console.log(url);
	var chartTemp;
	var chartHum;
	var reconMsg = null; //reconnect div object
	/**
	* use to store reconnect procedure, to make sure there is only 1 websocket to server generated
	* not thread safe!!!TBD
	*/
	var reconn = null; 
	var socket = null; //websocket object
	
	function onDataReceived(data){
		if(name == "Demo" || name == data.name) {
			if(data.type == 'temperature') {
				updateChart(chartTemp, data.value);
			}
			
			if(data.type == 'humidity') {
				updateChart(chartHum, data.value);
			}			
		}
	}
	
    // Add some life
    function updateChart(chart, value) {
		var point = chart.series[0].points[0];
		console.log()
		point.update(value);
    }
	
	function init() {
		chartTemp = new Highcharts.Chart({
		    
	        chart: {
	            renderTo: 'container1',
	            type: 'gauge',
	            plotBackgroundColor: null,
	            plotBackgroundImage: null,
	            plotBorderWidth: 1,
	            plotShadow: false
	        },
	        
	        credits: {
	        	href: "http://cps.eng.uci.edu",
	        	text: "CECS Lab UI"
	        },
	        
	        title:{
	            text: 'Skin Temperature Monitor'
	        },
	        
	        pane: {
	            startAngle: -100,
	            endAngle: 100,

	        },
	           
	        // the value axis
	        yAxis: {
	            min: 10,
	            max: 45,
	            
	            minorTickInterval: 'auto',
	            minorTickWidth: 1,
	            minorTickLength: 10,
	            minorTickPosition: 'inside',
	            minorTickColor: '#666',
	    
	            tickInterval: 5,
	            tickWidth: 2,
	            tickPosition: 'inside',
	            tickLength: 10,
	            tickColor: '#666',
	            labels: {
	                step: 1,
	                rotation: 'auto'
	            },
	            title: {
	                text: '°C'
	            },
	            plotBands: [{
	                from: 30,
	                to: 35,
	                color: '#55BF3B' // green
	            }, {
	                from: 35,
	                to: 37,
	                color: '#DDDF0D' // yellow
	            }, {
	                from: 37,
	                to: 45,
	                color: '#DF5353' // red
	            }]
	        },
	    
	        series: [{
	            name: 'Skin',
	            data: [10],
	            yAxis: 0,
	            tooltip: {
	                valueSuffix: ' Degree'
	            },
	        }]
	    });
	    
		chartHum = new Highcharts.Chart({
	        
	        chart: {
	            renderTo: 'container2',
	            type: 'gauge',
	            plotBackgroundColor: null,
	            plotBackgroundImage: null,
	            plotBorderWidth: 1,
	            plotShadow: false
	        },
	        
	        credits: {
	        	href: "http://cps.eng.uci.edu",
	        	text: "CECS Lab UI"
	        },
	        
	        title:{
	            text: 'Humidity Monitor'
	        },
	        
	        pane: {
	            startAngle: -100,
	            endAngle: 100,

	        },
	           
	        // the value axis
	        yAxis: {
	            min: 0,
	            max: 100,
	            
	            minorTickInterval: 'auto',
	            minorTickWidth: 1,
	            minorTickLength: 10,
	            minorTickPosition: 'inside',
	            minorTickColor: '#666',
	    
	            tickInterval: 10,
	            tickWidth: 1,
	            tickPosition: 'inside',
	            tickLength: 10,
	            tickColor: '#666',
	            labels: {
	                step: 1,
	                rotation: 'auto'
	            },
	            title: {
	                text: '%'
	            },
	            plotBands: [{
	                from: -10,
	                to: 10,
	                color: '#55BF3B' // green
	            }, {
	                from: 10,
	                to: 30,
	                color: '#DDDF0D' // yellow
	            }, {
	                from: 30,
	                to: 45,
	                color: '#DF5353' // red
	            }]
	        },
	    
	        series: [{
	            name: 'Humidity',
	            data: [0],
	            yAxis: 0,
	            tooltip: {
	                valueSuffix: ' %'
	            },
	        }]
	    
	    });		
	}
    

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
	
	$(window).bind('load', function(e) {
		init();
		update();
		/*
		setInterval(function(){
			render();
		}, 1000);
		*/
	});
});