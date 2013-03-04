$(function () {
	var url = $('#serverAddr').text(); 	//push url, need to change this to server's url, 
	var name =  $('#name').text();
	var configUrl = 'config';
		
    var datasets; //store datasets
	function onDataReceived(data) { //setup plot after retrieving data
		console.log(data);
		if( data.from == 'node'){
			if(name.trim() == data.data.address.trim())
				if(data.data.type == 'sids'){ //real data
					/*
					datasets = data.data.data;
					console.log(datasets.length);
					removeProgressBar();
					//addResizer();
					addStartButton();
					addStopButton();
					stopButton.hide();
					//addRedoButton();
					plotEverything();
					*/
				}
				/*
				else if(data.data.type == 'SIDs'){ //state info
					if(data.data.value.type == 'state'){
						if(data.data.value.value == 0){
							// ready to start real recording
							if(startButton != null && redoButton != null){
								startButton.button("enable");
								redoButton.button("enable");
							}
							
						}	
					}
				}
				*/
		}
		else if(data.from == 'central') {
			if(data.data.type == 'message'){
				alert(data.data.value);
				open('/administration', '_self', true);
			}
		}
	}
	
	
	var init = function() {
		addSettings();
		
		addUpdateButton();
		addSaveButton();
		addFileUploadDiv();
		addStartButton();
		addStopButton();
		startButton.button("enable");
		stopButton.hide();

	}
	
	function onFileReceived(){

	}
	
    var settings = [
                    {name: 'setting1', value: '0'},
                    {name: 'setting2', value: '2'},
                    {name: 'setting3', value: '3'},
                    {name: 'setting4', value: '4'}
                    ]; //demo settings array
    var settingContainer, inputs;
    function addSettings(){
    	settingContainer = $("<div id='settingContainer'/>"); 
    	inputs = [];
    	for(var i=0; i<settings.length;i++){
    		$("<label for='" + settings[i].name + "'> " + settings[i].name + " </label><br>").appendTo(settingContainer);
    		var input = $("<input id='" + settings[i].name + "' value = '" + settings[i].value + "'/>").css({
    			fontSize: 'small',
    			width: '30px'
    		});	
    		input.appendTo(settingContainer);
    		input.spinner();
    		//input.spinner("disable");
    		inputs.push(input);
    		$("<br>").appendTo(settingContainer);
    	}
    	settingContainer.insertBefore("#dataContainer");
    }
	
    function startSIDs() {
    	//disable all setting inputs
    	$.each(inputs, function(key,val){
    		val.spinner("disable");
    	});
    	fileInput.hide();
    	startButton.hide();
    	stopButton.show();
    	socket.send("startSIDs"+name.trim());
    	/*
    	socket.send("startECG"+name.trim());
    	startButton.hide();
    	redoButton.hide();
    	stopButton.show();
    	showSpinner();
    	*/
    }
    
    function stopSIDs() {
    	//enable all setting inputs
    	$.each(inputs, function(key,val){
    		val.spinner("enable");
    	});    	
    	fileInput.show();
    	stopButton.hide();
    	startButton.show();
    	/*
    	socket.send("stopECG"+name.trim());
    	stopButton.hide();
    	hideSpinner();
    	showCompleteDialog();
    	//startButton.show();
    	*/
    }
	
    var startButton, stopButton;
    function addStartButton() {
    	startButton = $('<button>START RECORDING</button>').css({
    		float: 'right',
    		fontSize: '30%',
    		position: 'relative',
    		//right: '0px',
    		top: '0px'
    	});   	
    	startButton.button();
    	startButton.button("disable");
    	startButton.click(startSIDs);
    	startButton.insertBefore("#settingContainer");
    }
    
    function addStopButton() {
    	stopButton = $('<button>STOP RECORDING</button>').css({
			float: 'right',
			fontSize: '30%',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
		stopButton.button();
		stopButton.button("enable");
		stopButton.click(stopSIDs);
		stopButton.insertBefore("#settingContainer");
    }
    
    var fileInput;
    function addFileUploadDiv() {
    	fileInput = $('<span class="file-wrapper" title="Submit a different Dicom file">\
    			<span>UPLOAD CONFIG FILE</span>\
                <input type="file" name="uploaded_files" >\
            </span>').css({
    		float: 'right',
    		fontSize: '30%',
    	});
    	fileInput.button();
    	fileInput.fileupload({
    		url: configUrl,
            dataType: 'json',
            send: function (e, data) {
            	showSpinner();
            	//console.log(data);
            },
            done: function (e, data) {
            	//console.log(data.result);
            	hideSpinner();
            	onFileReceived(data.result);
            },
            fail: function (e, data) {
            	alert('invalid file');
            	hideSpinner();
            }
        });
    	fileInput.insertBefore("#settingContainer");
    }
    var saveButton;
    function addSaveButton() {
    	saveButton = $('<button>SAVE SETTINGS</button>').css({
			float: 'right',
			fontSize: '30%',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
    	saveButton.button();
    	saveButton.button("enable");
    	saveButton.click(saveSettings);
    	saveButton.insertBefore("#settingContainer");
    }
    
    function saveSettings(){
    	var config = [];
    	$.each(inputs, function(key, val){
    		config.push({
    			name: val[0].id,
    			value: val[0].value
    		});
    	});
		$.ajax({
			type: 'get',
			url: configUrl,
			dataType: 'json',
			cache: false,
			data: {"data":JSON.stringify(config)},
			beforeSend: showSpinner,
			complete: hideSpinner,
			success: function(data){
				window.open(data.url, '_self', false);
			},
			error: function() {alert("Save Failed!!");}
		});
    	
    }

    var updateButton;
    function addUpdateButton() {
    	updateButton = $('<button>UPDATE SETTINGS</button>').css({
			float: 'right',
			fontSize: '30%',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
    	updateButton.button();
    	updateButton.button("enable");
    	updateButton.click(updateSettings);
    	updateButton.insertBefore("#settingContainer");
    }
    
    function updateSettings() { //update setting through ajax
    	var config = [];
    	$.each(inputs, function(key, val){
    		config.push({
    			name: val[0].id,
    			value: val[0].value
    		});
    	});
		$.ajax({
			type: 'put',
			url: configUrl,
			dataType: 'json',
			cache: false,
			data: {"data":JSON.stringify(config)},
			beforeSend: showSpinner,
			success: function(){
				hideSpinner();
				alert("Update Success!!");
			},
			error: function() {alert("Update Failed!!");}
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
    
    //getAndProcessData();
    
    //init();
});