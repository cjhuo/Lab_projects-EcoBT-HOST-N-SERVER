/**
 * Main script for generating plot.
 *
 * .with push technology
 *
 */

$(function () {
	var container, stats;

	var camera, scene, renderer;

	var cube, plane;

	var targetRotation = 0;
	var targetRotationOnMouseDown = 0;

	//var windowHalfX = window.innerWidth / 2;
	//var windowHalfY = window.innerHeight / 2;

	var parent;

	var url = "ws://cps.eng.uci.edu:8001/socket"; //push url, need to change this to server's url, 
	//such as cps.eng.uci.edu:8000/socket
	var socket = null; //websocket object
	
	
	function onDataReceived(data){
		if(data.axis == 'x')
			parent.rotation.x = data.value;
		else if(data.axis == 'y')
			parent.rotation.y = data.value;
		else if(data.axis == 'z')
			parent.rotation.z = data.value;
		renderer.render( scene, camera );
	}
	
	var reconMsg = null; //reconnect div object
	
	/**
	* use to store reconnect procedure, to make sure there is only 1 websocket to server generated
	* not thread safe!!!TBD
	*/
	var reconn = null; 

	function init() {

		container = document.createElement( 'div' );
		document.body.appendChild( container );
		
		var info = document.createElement( 'div' );
		info.style.position = 'absolute';
		info.style.top = '100px';
		info.style.width = '100%';
		info.style.textAlign = 'center';
		info.innerHTML = "<h1>Simulator of the node's movement</h1>";
		container.appendChild( info );

		camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 1000 );
		camera.position.y = 0;
		camera.position.z = 500;

		scene = new THREE.Scene();

		// Cube

		var materials = [];

		for ( var i = 0; i < 6; i ++ ) {

			materials.push( new THREE.MeshBasicMaterial( { color: Math.random() * 0xffffff } ) );

		}

		cube = new THREE.Mesh( new THREE.CubeGeometry( 200, 10, 100, 1, 1, 1, materials ), new THREE.MeshFaceMaterial() );
		cube.position.y = 0;//150;
		cube.rotation.y = 0;//0.1;
		//scene.add( cube );
		
		// Get text from hash

		var theText = "ECG node #1";

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
		text.position.y = 50;
		text.position.z = 0;

		//text.rotation.x = 0.1;
		text.rotation.y = 0;

		parent = new THREE.Object3D();
		
		parent.add( cube );
		parent.add( text );
		scene.add( parent );


		renderer = new THREE.CanvasRenderer();
		renderer.setSize( window.innerWidth, window.innerHeight );

		container.appendChild( renderer.domElement );

		stats = new Stats();
		stats.domElement.style.position = 'absolute';
		stats.domElement.style.top = '0px';
		container.appendChild( stats.domElement );

		//window.addEventListener( 'resize', onWindowResize, false );
		
		//render();
		renderer.render( scene, camera );

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

		//render();
		stats.update();

	}

	function render() {

		parent.rotation.y += (Math.random()-0.5)*0.1;
		parent.rotation.x += (Math.random()-0.5)*0.3;
		renderer.render( scene, camera );

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
	
	$(window).bind('resize', onWindowResize);
	
	$(window).bind('load', function(e) {
		init();
		animate();
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
});