$(function () {
	var url = $('#serverAddr').text(); 	//push url, need to change this to server's url, 
	var name =  $('#name').text();
	var side =  $('#side').text().trim();
	var configUrl = 'config';
		
    var datasets; //store datasets
	function onDataReceived(data) { //setup plot after retrieving data
		console.log(data);
		if( data.from == 'node'){
			if(name.trim() == data.data.address.trim())
				if(data.data.type == 'SIDsRead'){ //real data
					//console.log(data.data.value);
					updateDataTable(data.data.value);
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
				else if(data.data.type == 'SIDsSettings'){
					addSettings(data.data.value);
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
				//alert(data.data.value);
				//window.parent.open('/administration', '_self', true);
			}
			
		}
	}
	
	
	var init = function() {
		//addSettings();
		addSettingContainer();
		addUpdateButton();
		addSaveButton();
		addFileUploadDiv();
		addStartButton();
		addStopButton();
		//addClearTableButton();
		startButton.button("enable");
		stopButton.hide();

	}
	
	/*
    var settings = [
                    {name: 'setting1', value: '0'},
                    {name: 'setting2', value: '2'},
                    {name: 'setting3', value: '3'},
                    {name: 'setting4', value: '4'}
                    ]; //demo settings array
    */
    var settingContainer, inputs;
    function addSettingContainer(){
    	settingContainer = $("<div id='settingContainer'/>"); 
    	settingContainer.insertBefore("#dataTable");
    }
    function addSettings(settings){
    	//console.log(settings);
    	if(inputs == null){
	    	settingTable = $("<table id='settingTable' border='0'></table>");
	    	inputs = [];
	    	/*
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
	    	*/
	    	tmpSettings = sortOnKeys(settings);
	    	var rowDom, tdDom1, tdDom2, counter = 1;
	    	$.each(tmpSettings, function(key, val){
	    		//console.log(key, val);
	    		if(counter == 1){
	    			rowDom = $("<tr></tr>");
	    		}
	    		if(counter % 4 == 1){
		    		rowDom.appendTo(settingTable);
		    		rowDom = $("<tr></tr>");
	    		}
	    		var label = $("<label for='" + key + "'> " + key + " </label><br>");
	    		var input = $("<input id='" + key + "' value = '" + val + "'/>").css({
	    			fontSize: 'small',
	    			width: '40px'
	    		});
	    		inputs.push(input);
	    		
	    		tdDom1 = $("<td></td>");
	    		label.appendTo(tdDom1);
	    		tdDom2 = $("<td></td>");
	    		input.appendTo(tdDom2);
	    		input.spinner();
	    		if(key == "SAMPLE CACULATION"){
	    			input.spinner("disable");
	    		}
	    		tdDom1.appendTo(rowDom);
	    		tdDom2.appendTo(rowDom);	
	    		counter++;
	    	});
	    	rowDom.appendTo(settingTable);
	    	settingTable.appendTo(settingContainer);
    	}
    	else { // update tables
        	$.each(inputs, function(key, val){
        		//config.push(val[0].value);
        		val[0].value = settings[val[0].id];
        	});
    	}
    }
    
    function sortOnKeys(dict) {

        var sorted = [];
        for(var key in dict) {
            sorted[sorted.length] = key;
        }
        sorted.sort();

        var tempDict = {};
        for(var i = 0; i < sorted.length; i++) {
            tempDict[sorted[i]] = dict[sorted[i]];
        }

        return tempDict;
    }
    
    function updateDataTable(data){
    	/*
    	$("#dataTable tbody").append("<tr>" +
                "<td>" + data[0]+ ":" + data[1] +":"+ data[2] + "</td>" +
                "<td>" + data[3] + "</td>" +
                "<td>" + data[4] + "</td>" +
                "<td>" + data[5] + "</td>" +
                "<td>" + data[6] + "</td>" +
                "<td>" + data[7] + "</td>" +
                "<td>" + data[8] + "</td>" +
                "<td>" + data[9] + "</td>" +
                "<td>" + data[10] + "</td>" +

              "</tr>" );
        */
    	if(side == 'Left'){
	    	$("#dataTable tbody").prepend("<tr>" +
	                "<td>" + data[0]+ ":" + data[1] +":"+ data[2] + "</td>" +
	                "<td>" + data[3] + "</td>" +
	                //"<td>" + data[4] + "</td>" +
	                //"<td>" + data[5] + "</td>" +
	                "<td>" + data[6] + "</td>" +
	                "<td>" + data[7] + "</td>" +
	                "<td>" + data[8] + "</td>" +
	                "<td>" + data[9] + "</td>" +
	                "<td>" + data[10] + "</td>" +
	
	              "</tr>" );
    	}
    	else{
	    	$("#dataTable tbody").prepend("<tr>" +
	                "<td>" + data[0]+ ":" + data[1] +":"+ data[2] + "</td>" +
	                "<td>" + data[3] + "</td>" +
	                //"<td>" + data[4] + "</td>" +
	                //"<td>" + data[5] + "</td>" +
	                "<td>" + data[6] + "</td>" +
	                "<td>" + data[7] + "</td>" +
	                "<td>" + data[8] + "</td>" +
	
	              "</tr>" );
    	}
    }
	
    function startSIDs() {
    	//disable all setting inputs
    	$.each(inputs, function(key,val){
    		val.spinner("disable");
    	});
    	fileInput.hide();
    	startButton.hide();
    	stopButton.show();
    	updateButton.hide();
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
    		if(val[0].id != "SAMPLE CACULATION"){
    			val.spinner("enable");
    		}
    	});    	
    	fileInput.show();
    	stopButton.hide();
    	startButton.show();
    	updateButton.show();
    	socket.send("stopSIDs"+name.trim());
    	/*
    	socket.send("stopECG"+name.trim());
    	stopButton.hide();
    	hideSpinner();
    	showCompleteDialog();
    	//startButton.show();
    	*/
    }
    
    function clearTable() {
    	$("#dataTable tbody > tr").remove();
    }
    
    var clearButton;
    function addClearTableButton() {
    	clearButton = $('<button>CLEAR TABLE</button>').css({
    		float: 'right',
    		fontSize: '30%',
    		position: 'relative',
    		//right: '0px',
    		top: '0px'
    	});
    	clearButton.button();
    	clearButton.click(clearTable);
    	clearButton.insertBefore("#dataContainer");
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
    	startButton.insertBefore("#dataContainer");
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
		stopButton.insertBefore("#dataContainer");
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
            formData: {
            	address: name.trim()
            },
            send: function (e, data) {
            	showSpinner();
            	//console.log(data);
            },
            done: function (e, data) {
            	//console.log(data.result);
            	hideSpinner();
            	alert("Update sent to Node successfully!");
            },
            fail: function (e, data) {
            	alert('invalid file');
            	hideSpinner();
            }
        });
    	fileInput.insertBefore("#dataContainer");
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
    	saveButton.insertBefore("#dataContainer");
    }
    
    function saveSettings(){
    	var config = {};
    	$.each(inputs, function(key, val){
    		//config.push(val[0].value);
    		
    		config[val[0].id] = val[0].value;
    		
    	});
    	var data = {
    			'address': name.trim(),
    			'settings': config
    	};
		$.ajax({
			type: 'get',
			url: configUrl,
			dataType: 'json',
			cache: false,
			data: {"data":JSON.stringify(data)},
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
    	updateButton.insertBefore("#dataContainer");
    }
    
    function updateSettings() { //update setting through ajax
    	var config = {};
    	$.each(inputs, function(key, val){
    		//config.push(val[0].value);
    		
    		config[val[0].id] = val[0].value;
    		
    	});
    	var data = {
    			'address': name.trim(),
    			'settings': config
    	};
		$.ajax({
			type: 'put',
			url: configUrl,
			dataType: 'json',
			cache: false,
			data: {"data":JSON.stringify(data)},
			beforeSend: showSpinner,
			success: function(){
				hideSpinner();
				alert("Update sent to Node successfully!");
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
			socket.send("sendSIDsSet"+name.trim());
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