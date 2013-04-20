/**
 * Main script for generating plot.
 *
 * .with push technology
 *
 */


$(function () {
	var url = $('#serverAddr').val(); 	//push url, need to change this to server's url, 

	//such as cps.eng.uci.edu:8000/socket
	console.log(url);
	var container = $("<div class='container' style='height:2000px'/>").appendTo(document.body);

	var startDiscoverServices = false;
	function onDataReceived(data){
		//console.log(data);
		console.log(data.data);
		if( data.from == 'central') {
			if(data.data.type == 'state') {
				toggleState(data.data.value);
			}
			if(data.data.type == 'peripheralList'){
				//console.log(data.data.value);
				appendNodes(data.data.value);
				startDiscoverServices = true;
			}
		}
		else if(data.from == 'node' && startDiscoverServices == true){
			// only list some service for demo purpose
			if(data.data.type == 'deviceInfo'){
				$.each(peripheralList, function(key, value){
					if(value.number == data.data.number){ //found a matched peripheral
						updateMac(data.data, value);
					}
				});
			}
			else if(data.data.type == 'ECG'){
				enableECGButtonEvent(data.data);
				//ready to scan
			}
			else if(data.data.type == 'SIDs'){
				enableSIDsButtonEvent(data.data);
				//ready to scan
			}
			/*
			else{
				addServiceNode(data.data);
			}
			*/
		}
			
	}
	
	function init() {
		showSpinner();
		initSVG();
		hideSpinner();
	}
	
	var r; // Raphael canvas object
	var centralManager; // central manager shape object
	var stateText; 
	var scan; 
	function initSVG() {
		initDraw();
		/*
		var p = { 'name': 'bigbig',
				'rssi': 2,
				'number': 3
		};
		addNode(200, 20, p);
		*/

	}
	
	
	//UI handler
    var mousedown = function () {
        this.animate({"fill-opacity": .2}, 500);
    },
        mouseup = function() {
            this.animate({"fill-opacity": 1}, 500);
        },
        initDraw = function(){ 
    		// init Canvas
    		r = Raphael(container[0], container.width(), container.height());
    		
    		// init Central Manager
    		centralManager = r.path(icon['imac']).attr({
    				fill: "red",
                    stroke: "#333",
                    "stroke-width": 0,
                    cursor: "pointer",
                    transform: "t20,150s2,2,0,0"
                });
    		centralManager.mousedown(mousedown);
    		centralManager.mouseup(mouseup);
    		stateText = r.text(50, 150, "Server Down").attr({
    			font: "10px Helvetica", 
    			opacity: 0.5,
    			fill: 'black', 
    			"stroke-width": 0,
    			"font-weight": 400});
        },
        drawDown = function() {
        	r.remove();
        	initDraw();
        	peripheralList = [];
    		
    		/*
    		if(scan != null)
    			scan.remove();  
    		*/      	
        },
        drawUp = function() {
    		centralManager.attr({fill: "green"});
    		stateText.attr({
    			text: "Server Up", 
    			opacity: 1, 
    			fill: 'green', 
    			"stroke-width": 2,
    			"font-weight":900});
    		if(scan != null)
    			scan.remove();
    		scan = r.path(icon['jquery']).attr({
    			fill: "red",
                stroke: "#333",
                "stroke-width": 0,
                cursor: "pointer",
                transform: "t35,110r140s1,1,0,0"
            });        	
        },
        /**
	        0: if down, 
	        1: if up but not startScan, 
	        2: up and startScan, 
	        3: has node connected, still scanning
        */
        toggleState = function(value) {
        	if(value == 0){ //down state
        		toggleScan(false);
        		drawDown();
        		startDiscoverServices = false;
        	}
        	else if(value == 1){
        		drawUp();
        		toggleScan(false);
        		socket.send("start");
        		toggleScan(true);
        	}
        	else if(value == 2){
        		drawUp();
        		toggleScan(true)
        	}
        	else if(value == 3){
        		drawUp();
        		toggleScan(true)
        		socket.send("peripheralList"); //request server to send list of connected peripheral
        	}
        	else if(value == 4){
        		drawUp();
        		toggleScan(false);
        		socket.send("start");
        		toggleScan(true);
        		socket.send("peripheralList");
        	}
        },
        cmInterv, 
        toggleScan = function(value) {
        	if(value == true){
        		if(cmInterv == null) {
        			scan.attr({fill: "green"});
        			cmInterv = setInterval(startScan, 2000);
        		}
        		else{
        			clearInterval(cmInterv);
        			scan.attr({fill: "green"});
        			cmInterv = setInterval(startScan, 2000);
        		}
        	}
        	else {
        		if(scan != null)
        			scan.attr({fill: "red"});
        		if(cmInterv != null)
        			clearInterval(cmInterv);
        		cmInterv = null;
        	}	
        },
        startScan = function() {
			scan.animate({"fill-opacity": .2}, 1000, function() {
				this.animate({"fill-opacity": 1}, 1000);
			});
        },
        peripheralList = [],
        appendNodes = function(plist) {
        	var x, y;
        	if(peripheralList.length == 0) { //draw from start
        		x = 120;
        		y = 20;
        		$.each(plist, function(index, value){ //name, rssi, number
        			addNode(x, y, value);
        			y+=150;
        		});
        	}
        	else{ 	// compare the list, if doesn't in plist then disabled, 
        			// if doesn't in peripheralList then add
        			// if previously disabled then enable
        		var foundInCentral;
        		for(var i=0; i<peripheralList.length; i++){
        			foundInCentral = false;
        			for(var j=0; j<plist.length; j++){
        				if(plist[j].number == peripheralList[i].number){ // found in central list and still active
        					foundInCentral = true;
        					// toggle enable if previously disabled
        					if(peripheralList[i].enabled != true){
        						// toggleNode
        						toggleNode(peripheralList[i], true);
        					}
        					break;
        				}     				
        			}
        			if(foundInCentral == false) { // didn't find in central list, disable it
        				
        				toggleNode(peripheralList[i], false);
        				//remove it
        				removeNode(i);
        			}
        		}
        		var foundInLocal;
        		for(var i=0; i<plist.length; i++){
        			foundInLocal = false;
        			for(var j=0; j<peripheralList.length; j++){
        				if(plist[i].number == peripheralList[j].number){
        					foundInLocal = true;
        					break;
        				}
        			}
        			if(foundInLocal == false) { // didn't find in local plist, add it to list
        				x = peripheralList[peripheralList.length-1].instance.attr("x");
        				y = peripheralList[peripheralList.length-1].instance.attr("y")+150;
        				addNode(x, y, plist[i]);
        			}
        		}
        	}
        },
        toggleNode = function(peripheral, value) {
        	if(value==false){
        		peripheral.connection.line.attr({stroke: "#000"});
        	}
        	else{
        		peripheral.connection.line.attr({stroke: "green"});
        	}
        },
        addNode = function(x, y, value) {
			var peripheral = r.rect(x, y, 60, 40, 10).attr({
				stroke: "orange",
				"stroke-width": 5
			});
			var conn = r.connection(peripheral, centralManager, "#000");
			var text = r.text(x+30, y-10, value.name).attr({
    			opacity: 1, 
    			fill: 'green', 
    			"stroke-width": 2,
    			"font-weight":900});
			conn.line.toBack();
			var address = null;

			var p = { 'name': value.name,
					'address': address,
					'rssi': value.rssi,
					'number': value.number,
					'type': value.type,
					'instance': peripheral,
					'connection': conn,
					'enabled': true,
					'services': [],
					'text': text,
					'readyInstance': null,
					'addrInstance': null
			};
			peripheral.drag(move, dragger, up);
			if(value.address != null){
				updateMac(value, p);
			}
			peripheralList.push(p);
			if(value.type == 'ECG'){
				enableECGButtonEvent(value);
			}
			if(value.type == 'SIDs'){
				enableSIDsButtonEvent(value);
			}
			
			toggleNode(p, true);
        },
        enableECGButtonEvent = function(data) {
        	// find relative peripheral
        	var peripheral;
        	$.each(peripheralList, function(key, val){
        		if(val.number == data.number){
        			peripheral = val;
        		}
        	})
        	
        	if(peripheral != null){
        		if(peripheral.readyInstance == null){
	        		peripheral.instance.attr({cursor: "pointer"});
	        		
	        		// draw ready text
	    			x = peripheral.instance.attr("x") + 10;
	    			y = peripheral.instance.attr("y") + 30;
	    			var text = r.text(x+20, y-10, "START").attr({
	        			opacity: 1, 
	        			fill: 'black', 
	        			"stroke-width": 2,
	        			"font-weight":900});
	    			peripheral.readyInstance = text;
	    			var group = r.set();
	    			group.push(peripheral.instance);
	    			group.push(text);
	    			//group.peripheral = peripheral;
	    			var ecgUrl = "/liveECG?name="+data.address;
	    			group.attr({
	    			    cursor: 'pointer',
	    			}).mouseover(function(e) {
	    				group[0].attr('fill', "green");
	    			}).mouseout(function(e) {
	    				group[0].attr('fill', "");
	    			}).click(function(e) {
	    				group[0].attr('fill', "red");
	    				showSpinner();
	    				startTestECG(peripheral.address);
	    				this.undblclick();
	    				//this.remove();
	    				window.open(ecgUrl, '_self', false);
	    			}); 
        		}
        	}
        },
        enableSIDsButtonEvent = function(data) {
        	// find relative peripheral
        	var peripheral;
        	$.each(peripheralList, function(key, val){
        		if(val.number == data.number){
        			peripheral = val;
        		}
        	})
        	
        	if(peripheral != null){
        		if(peripheral.readyInstance == null){
	        		peripheral.instance.attr({cursor: "pointer"});
	        		
	        		// draw ready text
	    			x = peripheral.instance.attr("x") + 10;
	    			y = peripheral.instance.attr("y") + 30;
	    			var text = r.text(x+20, y-10, "START").attr({
	        			opacity: 1, 
	        			fill: 'black', 
	        			"stroke-width": 2,
	        			"font-weight":900});
	    			peripheral.readyInstance = text;
	    			var group = r.set();
	    			group.push(peripheral.instance);
	    			group.push(text);
	    			//group.peripheral = peripheral;
	    			var ecgUrl = "/liveSIDs?name="+data.address;
	    			group.attr({
	    			    cursor: 'pointer',
	    			}).mouseover(function(e) {
	    				group[0].attr('fill', "green");
	    			}).mouseout(function(e) {
	    				group[0].attr('fill', "");
	    			}).dblclick(function(e) {
	    				group[0].attr('fill', "red");
	    				showSpinner();
	    				//startTestECG(peripheral.address);
	    				this.undblclick();
	    				//this.remove();
	    				window.open(ecgUrl, '_self', false);
	    			}); 
        		}
        	}
        },
        dragger = function (x, y, event) {
        	for(var i=peripheralList.length; i--;){
        		if(peripheralList[i].instance == this){
        			this.p = peripheralList[i];
        		}
        	}
        	this.xIns = this.p.instance.attr("x");
        	this.yIns = this.p.instance.attr("y");
        	this.xTxt = this.p.text.attr("x");
        	this.yTxt = this.p.text.attr("y");
        	if(this.p.addrInstance != null){
        		this.xAdd = this.p.addrInstance.attr("x");
        		this.yAdd = this.p.addrInstance.attr("y");
        	}
        	if(this.p.readyInstance != null){
        		this.xRdy = this.p.readyInstance.attr("x");
        		this.yRdy = this.p.readyInstance.attr("y");
        	}
            this.p.instance.animate({"fill-opacity": .2}, 500);
        },
        move = function (dx, dy) {
        	var att = {x: this.xIns + dx, y: this.yIns + dy};
        	var attTxt = {x: this.xTxt + dx, y: this.yTxt + dy};
            this.p.instance.attr(att);
            this.p.text.attr(attTxt);
        	if(this.xAdd != null){
        		var attAdd = {x: this.xAdd + dx, y: this.yAdd + dy};
        		this.p.addrInstance.attr(attAdd);
        	}
        	if(this.xRdy != null) {
        		var attRdy = {x: this.xRdy + dx, y: this.yRdy + dy};
        		this.p.readyInstance.attr(attRdy);
        	}
            r.connection(this.p.connection);
            r.safari();
        },
        up = function () {
            this.p.instance.animate({"fill-opacity": 0}, 500);
        },
        startTestECG = function(address) {
        	socket.send("startTestECG"+address);
        },
        updateMac = function(data, p) {
			p.address = data.address;
			x = p.instance.attr("x") + 10;
			y = p.instance.attr("y") + 60;
			var text = r.text(x+30, y-10, data.address).attr({
    			opacity: 1, 
    			fill: 'black', 
    			"stroke-width": 2,
    			"font-weight":900});
			p.addrInstance = text;
        },
        addServiceNode = function(value) {
        	// find relative peripheral
        	var peripheral;
        	$.each(peripheralList, function(key, val){
        		if(val.number == value.number){
        			peripheral = val;
        		}
        	})
        	if(peripheral != null){
        		if(value.type == 'orientation' || value.type == 'temperature' || value.type == 'humidity'){
        			var added = false;
        			$.each(peripheral.services, function(key, val){
        				if(val.type == value.type){
        					added = true;
        				}
        			});
        			if(added != true){
	        		// draw Node
		        		var x = peripheral.instance.attr("x") + 150,
		        			y;
		        		if(peripheral.services.length == 0){
		        			y = peripheral.instance.attr("y");
		        		}
		        		else{
		        			y = peripheral.services[peripheral.services.length-1].instance.attr("y")+50;
		        		}
		
		    			var service = r.rect(x, y, 30, 30, 2).attr({
		    				stroke: "blue",
		    				"stroke-width": 5,
		                    cursor: "pointer",
		                    fill: ""
		    			});
		    			var text = r.text(x+70, y+10, value.type).attr({
		        			opacity: 1, 
		        			fill: 'green', 
		        			"stroke-width": 2,
		        			"font-weight":900});
		    			var conn = r.connection(peripheral.instance, service, "#000");
		        		
		    			var s = { 'name': value.address,
		    					'instance': service,
		    					'connection': conn,
		    					'type': value.type,
		    					'text': text
		    					//'enabled': true,
		    			};
		    			var monitorUrl;
		    			if(value.type == 'orientation'){
		    				monitorUrl = "/orientation?name="+value.address;
		    			}
		    			if(value.type == 'temperature'){
		    				monitorUrl = "/temperature?name="+value.address;
		    			}
		    			if(value.type == 'humidity'){
		    				monitorUrl = "/temperature?name="+value.address;
		    			}
		    			service.click(function(){					
							window.open(monitorUrl, '_self', false);
							return false;
						});
		    			peripheral.services.push(s);
	        		}
        		}
        	}
        },
        removeNode = function(i) {
        	$.each(peripheralList[i].services, function(key,val) {
        		val.connection.line.remove();
        		val.text.remove();
        		val.instance.remove();
        	});
        	if(peripheralList[i].addrInstance != null)
        		peripheralList[i].addrInstance.remove();
        	if(peripheralList[i].readyInstance != null)
        		peripheralList[i].readyInstance.remove();        		
    		peripheralList[i].connection.line.remove();
    		peripheralList[i].text.remove();
    		peripheralList[i].instance.remove();
    		peripheralList.splice(i, 1);        	
        }

        
    Raphael.fn.connection = function (obj1, obj2, line, bg) {
	    if (obj1.line && obj1.from && obj1.to) {
	        line = obj1;
	        obj1 = line.from;
	        obj2 = line.to;
	    }
	    var bb1 = obj1.getBBox(),
	        bb2 = obj2.getBBox(),
	        p = [{x: bb1.x + bb1.width / 2, y: bb1.y - 1},
	        {x: bb1.x + bb1.width / 2, y: bb1.y + bb1.height + 1},
	        {x: bb1.x - 1, y: bb1.y + bb1.height / 2},
	        {x: bb1.x + bb1.width + 1, y: bb1.y + bb1.height / 2},
	        {x: bb2.x + bb2.width / 2, y: bb2.y - 1},
	        {x: bb2.x + bb2.width / 2, y: bb2.y + bb2.height + 1},
	        {x: bb2.x - 1, y: bb2.y + bb2.height / 2},
	        {x: bb2.x + bb2.width + 1, y: bb2.y + bb2.height / 2}],
	        d = {}, dis = [];
	    for (var i = 0; i < 4; i++) {
	        for (var j = 4; j < 8; j++) {
	            var dx = Math.abs(p[i].x - p[j].x),
	                dy = Math.abs(p[i].y - p[j].y);
	            if ((i == j - 4) || (((i != 3 && j != 6) || p[i].x < p[j].x) && ((i != 2 && j != 7) || p[i].x > p[j].x) && ((i != 0 && j != 5) || p[i].y > p[j].y) && ((i != 1 && j != 4) || p[i].y < p[j].y))) {
	                dis.push(dx + dy);
	                d[dis[dis.length - 1]] = [i, j];
	            }
	        }
	    }
	    if (dis.length == 0) {
	        var res = [0, 4];
	    } else {
	        res = d[Math.min.apply(Math, dis)];
	    }
	    var x1 = p[res[0]].x,
	        y1 = p[res[0]].y,
	        x4 = p[res[1]].x,
	        y4 = p[res[1]].y;
	    dx = Math.max(Math.abs(x1 - x4) / 2, 10);
	    dy = Math.max(Math.abs(y1 - y4) / 2, 10);
	    var x2 = [x1, x1, x1 - dx, x1 + dx][res[0]].toFixed(3),
	        y2 = [y1 - dy, y1 + dy, y1, y1][res[0]].toFixed(3),
	        x3 = [0, 0, 0, 0, x4, x4, x4 - dx, x4 + dx][res[1]].toFixed(3),
	        y3 = [0, 0, 0, 0, y1 + dy, y1 - dy, y4, y4][res[1]].toFixed(3);
	    var path = ["M", x1.toFixed(3), y1.toFixed(3), "C", x2, y2, x3, y3, x4.toFixed(3), y4.toFixed(3)].join(",");
	    if (line && line.line) {
	        line.bg && line.bg.attr({path: path});
	        line.line.attr({path: path});
	    } else {
	        var color = typeof line == "string" ? line : "#000";
	        return {
	            bg: bg && bg.split && this.path(path).attr({stroke: bg.split("|")[0], fill: "none", "stroke-width": bg.split("|")[1] || 3}),
	            line: this.path(path).attr({stroke: color, fill: "none", "stroke-width": 2}),
	            from: obj1,
	            to: obj2
	        };
	    }
	};

	
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
	    	toggleState(0);
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
});