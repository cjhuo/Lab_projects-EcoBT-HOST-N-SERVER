/* Main script for generating plot.
 *
 * .with push technology
 *
 */

$(function () {
	var data = [], total_points = 300;
	
	var url = "ws://localhost:8000/socket"; //push url, need to change this to server's url, 
											//such as cps.eng.uci.edu:8000/socket
	var socket = null; //websocket object
	
	var reconMsg = null; //reconnect div object
	
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
	    socket = new WebSocket(url);
	    socket.onmessage = function(event) {
	    	onDataReceived($.parseJSON(event.data));
	    	plot.setData([ dataToRes() ]);
			plot.setupGrid();
			plot.draw();
	    };
	}

	function showReconMsg() {
		if(reconMsg == null) {
			reconMsg = $('<div id="reconnect" >websocket connection is lost, reconnecting...</div>').css( {
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
		establishConnection();
		alert(socket.readyState);		
		
	    setInterval(function() {//check if connection is lost
			if(socket.readyState == 2 || socket.readyState == 3){ //connection is closed or closing
				showReconMsg();
				establishConnection(socket);
			}
			else{
				hideReconMsg();
			}			
	    }, 2000);
	    
	    /*
		$.ajax({
			url: dataurl,
			cache: false,
			method: 'GET',
			dataType: 'json',
			success: onDataReceived
		});

		plot.setData([ dataToRes() ]);
		*/
		/*
		range = yaxisRange();
		var opts = plot.getOptions();
		for (var i = 0; i< opts.yaxes.length; i++){
			opts.yaxes[i].min = range[0];
			opts.yaxes[i].max = range[1];
		}
		*/
	    /*
		plot.setupGrid();
		plot.draw();

		timeVar = setTimeout(update, updateInterval);
		*/
	}

	generatePlot();
	update();
});