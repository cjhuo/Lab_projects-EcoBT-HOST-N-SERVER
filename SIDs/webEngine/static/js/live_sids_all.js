$(function () {
	var url = $('#serverAddr').text(); 	//push url, need to change this to server's url, 
	var name =  $('#name').text();
	var soundUrl = $('#soundServerAddr').text();;
		
    var datasets; //store datasets
	function onDataReceived(data) { //setup plot after retrieving data
		console.log(data);
		if( data.from == 'node'){
			if(name.trim() == data.data.address.trim())
				if(data.data.type == 'orientation'){
					updateSimulation(data.data);
					updateACCChart(data.data);
				}
				if(data.data.type == 'SIDsRead'){ //real data
					console.log(data.data.value);
				}
		}
		else if(data.from == 'central') {
			if(data.data.type == 'message'){
				alert(data.data.value);
				//open('/administration', '_self', true);
			}
		}
	}
	
	
	function updateSimulation(data) {
		//update simulation
		parent.lookAt(new THREE.Vector3(-data.value.x, -data.value.y, data.value.z));
		renderer.render( scene, camera );
	}
	
	function updateACCChart(data) {
		//update ACC chart
		chart.series[0].addPoint(data.value.x, false, true);
		chart.series[1].addPoint(data.value.y, false, true);
		chart.series[2].addPoint(data.value.z, true, true);
	}
	
	/**
	 * SIDsRead value content: [hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp]
	 * */
	function updateTempHumChart(data){
		//update Temp chart
		var point = chartTemp.series[0].points[0];
		console.log()
		point.update(data[9], true);
		
		//update Hum chart
		var point = chartHum.series[0].points[0];
		console.log()
		point.update(data[10], true);

	}
	
	var init = function() {
		showSpinner();
		initLayout();
		initSimulation();
		initChart();
		initTemperatureChart();
		initHumidityChart();
		initSoundMonitor();
		
	}
	
	function initSoundMonitor(){
		
		var player = $('<div><audio autoplay="autoplay" \
				src='+ soundUrl +' \
				controls="controls" /></div>').css({
				position: 'relative',
				display: 'table',
				top: '40%',
			    margin: 'auto'
				});
		$('#sound').append(player);
		

		//$('audio,video').mediaelementplayer();
	}
	
	function initLayout(){
		$('body').layout({
			closable: false,
			west__size:	.80,	
			west__childOptions:	{
				closable: false,
				south__size: .40,
				center__childOptions:	{
					closable: false,
					west__size:		.50
				},
				south__childOptions:	{
					closable: false,
					west__size:		.50
				}			}
		});
	}
	
	var chartContainer;
	var chart;
	var container = $("#acceleration");
	var total_points = 100;
	function initChart() {
		chartContainer = $("<div id='chart' class='chart'/>").appendTo(container);
		options = {
            chart: {
                renderTo: 'chart',
                type: 'line',
                backgroundColor: 'transparent'
            },
            title: {
                text: 'Live ACC RAW Data'
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
                lineWidth:0,
                tickWidth:0
            },
            yAxis: [{
                title: {
                    text: 'X',
                    rotation: 0
                },
                min: -1.0,
                max: 1.0,
                offset: 0,
                lineWidth: 2,
                height: 50
            }, 
            {
                title: {
                    text: 'Y',
                    rotation: 0
                },
                min: -1.0,
                max: 1.0,
                offset: 0,
                top: 100,
                lineWidth: 2,
                height: 50
            	
            },
            {
                title: {
                    text: 'Z',
                    rotation: 0
                },
                min: -1.0,
                max: 1.0,
                offset: 0,
                top: 160,
                lineWidth: 2,
                height: 50
            	
            }],
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
                	return '<b>'+ this.series.yAxis.axisTitle.text +'</b>:'+ this.y;
                }
            },
            legend: {
            	enabled: false,
            	layout: 'vertical',
                align: 'right',
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
        	name: 'X',
            data: data,
        });
        options.series.push({
        	name: 'Y',
            data: data,
            yAxis: 1
        });
        options.series.push({
        	name: 'Z',
            data: data,
            yAxis: 2
        });
		chart = new Highcharts.Chart(options, function() {
    		hideSpinner();
    	});
	}
	
	var simContainer, stats;

	var camera, scene, renderer;

	var cube, plane;

	var parent;	
	function initSimulation() {

		simContainer = $("<div id='simulation' class='simulation'/>").appendTo(container);;
		//console.log(simContainer);
		//simContainer = document.createElement( 'div' );
		//simContainer.style.width = '400px';
		//$("body").append( simContainer );
		//console.log(simContainer.width());
		stats = new Stats();
		stats.domElement.style.position = 'relative';
		//stats.domElement.style.float = 'left';
		//stats.domElement.style.top = 'auto';
		//simContainer.append( stats.domElement );

		var info = $("<div/>").css( {
            position: 'relative',
            //width: '10%',
            //cssFloat: 'center',
			fontWeight: 'bold',
			margin: '0px 0px 0px 0px',
            textAlign: 'center'
        });
		//info.style.position = 'absolute';
		//info.style.top = '100px';
		//info.style.width = '100%';
		//info.style.textAlign = 'center';
		info.html("Simulator of the node's movement");
		simContainer.append( info );

		camera = new THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 1000 );
		camera.position.x = -350;
		camera.position.y = 0;
		//camera.position.y = -250;
		
		camera.position.z = 0;

		camera.rotation = new THREE.Vector3( 0, -1.50, -1.57 ); // turn z to be parallel to gravity, facing up

		scene = new THREE.Scene();

		// Cube

		var materials = [];

		for ( var i = 0; i < 6; i ++ ) {

			materials.push( new THREE.MeshBasicMaterial( { color: (i/100)* 0xffffff } ) );

		}

		cube = new THREE.Mesh( new THREE.CubeGeometry( 100, 200, 10, 1, 1, 1, materials ), new THREE.MeshFaceMaterial() );
		cube.position.x = 0;//150;
		
		//cube.lookAt(a);
		
		//cube.rotation.x = 1.57;//0.1;
		
		//cube.rotation.y = 0;//0.1;
		//cube.rotation.z = 0.5;//0.1;
		//scene.add( cube );
		
		// Get text from hash

		var theText = "SIDs node #1";

		var hash = document.location.hash.substr( 1 );

		if ( hash.length !== 0 ) {

			theText = hash;

		}

		var text3d = new THREE.TextGeometry( theText, {

			size: 20,
			height: 3,
			curveSegments: 2,
			font: "helvetiker"

		});

		text3d.computeBoundingBox();
		var centerOffset = -0.5 * ( text3d.boundingBox.max.x - text3d.boundingBox.min.x );

		var textMaterial = new THREE.MeshBasicMaterial( { color: Math.random() * 0xffffff, overdraw: true } );
		text = new THREE.Mesh( text3d, textMaterial );

		text.position.x = centerOffset;
		text.position.y = 80;
		text.position.z = 20;
		text.rotation.x = 1.57; 
		text.rotation.y = -1.57;
		text.rotation.z = 0;

		parent = new THREE.Object3D();
		
		parent.add( cube );
		parent.add( text );
		//parent.lookAt(new THREE.Vector3(0,0,0));
		//parent.rotation.x = 1.57
		scene.add( parent );


		renderer = new THREE.CanvasRenderer();
		renderer.setSize( simContainer.width(), 200 );

		simContainer.append( renderer.domElement );


		//window.addEventListener( 'resize', onWindowResize, false );
		
		//render();
		renderer.render( scene, camera );
		
		animate();
	}

	function onWindowResize() {

		//windowHalfX = window.innerWidth / 2;
		//windowHalfY = window.innerHeight / 2;

		camera.aspect = window.innerWidth / window.innerHeight;
		camera.updateProjectionMatrix();

		renderer.setSize( window.innerWidth, window.innerHeight );
	}

	function animate() {

		requestAnimationFrame( animate );

		render();
		stats.update();

	}

	function render() {

		//parent.rotation.y += (Math.random()-0.5)*0.1;
		//parent.rotation.x += (Math.random()-0.5)*0.3;
		renderer.render( scene, camera );

	}
	
	var chartTemp;
	function initTemperatureChart(){
		chartTemp = new Highcharts.Chart({
		    
	        chart: {
	            renderTo: 'temperature',
	            type: 'gauge',
	            backgroundColor: 'transparent',
	            plotBackgroundColor: null,
	            plotBackgroundImage: null,
	            plotBorderWidth: 1,
	            plotShadow: false
	        },
	        exporting:{
	        	enabled: false
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
	            data: [0],
	            yAxis: 0,
	            tooltip: {
	                valueSuffix: ' Degree'
	            },
	        }]
	    });
	}
	var chartHum;
	function initHumidityChart(){
		chartHum = new Highcharts.Chart({
	        
	        chart: {
	            renderTo: 'humidity',
	            type: 'gauge',
	            backgroundColor: 'transparent',
	            plotBackgroundColor: null,
	            plotBackgroundImage: null,
	            plotBorderWidth: 1,
	            plotShadow: false
	        },
	        exporting:{
	        	enabled: false
	        },
	        credits: {
	        	href: "http://cps.eng.uci.edu",
	        	text: "CECS Lab UI"
	        },
	        
	        title:{
	            text: 'CO2 Density Monitor'
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