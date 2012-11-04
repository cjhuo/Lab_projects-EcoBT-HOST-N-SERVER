/**
 * Main script for generating plot.
 *
 * .with push technology
 *
 */

$(function () {
	var data = [], total_points = 300;
	
	var url = "ws://cps.eng.uci.edu:8000/socket"; //push url, need to change this to server's url, 
											//such as cps.eng.uci.edu:8000/socket
	var socket = null; //websocket object
	
	var reconMsg = null; //reconnect div object
	
	/**
	 * use to store reconnect procedure, to make sure there is only 1 websocket to server generated
	 * not thread safe!!!TBD
	 */
	var reconn = null; 
	
	function initData(){
		for (var i = 0; i < total_points; i++){
			data.push(0);
		}
	}

	function onDataReceived(series){
		if (data.length > 0){
			data = data.slice(0, -1);
		}
		data.unshift(series.point);
	}

	function dataToRes(){
		var res = [];
		for (var i = 0; i < data.length; i++){
			res.push([i, data[i]]);
		}
		return res;
	}

	var plot;
	var timeVar;
	var updateInterval = 1000;
	var dataurl = "point";
	// setup graph
	var options = {
		series: {shadowSize: 0},
		grid: {backgroundColor:'white'},
		yaxis:  { ticks: 2},
		xaxis:  {tickLength:0, show: true}
	};

	function generatePlot(){
		initData();
		plot = $.plot($("#chart"), [ dataToRes() ], options);

		// draggble, resizable
		$(function(){
			$("#chart").draggable();
			$("#chart").resizable();
		});
	}

	function yaxisRange(){
		var ymax = 0, ymin = 0;
		for (i = 0; i < total_points; i++){
			if (data[i] > ymax){
				ymax = data[i];
			}
			if (data[i] < ymin){
				ymin = data[i];
			}
		}
		
		ymin = ymin - 5;
		if (ymin < -180){
			ymin = -180;
		}
		ymax = ymax + 5;
		if (ymax > 180){
			ymax = 180;
		}
		return [ymin, ymax];
	}
	
	function establishConnection() {
		/*
		if(socket != null){
			socket.close();
			socket = null;
		}
		*/
	    socket = new WebSocket(url);
	    socket.onmessage = function(event) {
	    	onDataReceived($.parseJSON(event.data));
	    	plot.setData([ dataToRes() ]);
			plot.setupGrid();
			plot.draw();
	    };
	    socket.onerror = function(event) {
	    	alert('Error, readyState code is: ' + socket.readyState);
	    	socket.close();
	    	establishConnection();
	    };
	    
	    socket.onclose = function(event) {
	    	alert(socket.readyState);
		    //var t = setInterval(function() {//check if connection is lost, for the case when server is down
				//if(socket.readyState == 2 || socket.readyState == 3){ //connection is closed or closing
			
	    	/**
			 * try to reconnect when connection is closed and if reconnection has been 
			 * issued by other functions such as 'online' event handler then skip to prevent
			 * duplication of socket
			 * 
			 * */
	    	if(socket.readyState == 3){ //
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

	function showReconMsg(msg) {
		if(reconMsg == null) {
			reconMsg = $('<div id="reconnect" >' + msg + '</div>').css( {
		        position: 'relative',
		        width: '100%',
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
	
	function update(){
		if (navigator.onLine) { //navigator.onLine supports limited browsers, see https://developer.mozilla.org/en-US/docs/DOM/window.navigator.onLine
			establishConnection();	
		}
		else {
			showReconMsg('brower is offline, check wifi...');
		}
	}
	
	$(window).bind('load', function(e) {
		generatePlot();
		update();
	});
	
	$(window).bind('online', function(e) {		
		if(socket != null)
			alert('Network is back, readyState is: ' + socket.readyState);
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
				if(socket.readyState == 3){
					establishConnection();
					//alert('Network is back, readyState is: ' + socket.readyState);
					hideReconMsg();
					reconn = null;
				}
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
});