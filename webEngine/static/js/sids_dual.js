$(function () {
	var url = $('#serverAddr').text(); 	//push url, need to change this to server's url, 
	var name0 =  $('#name0').text(); // left node
	var name1 =  $('#name1').text(); // right node
	var configUrl = 'config';
	
    var datasets; //store datasets
	function onDataReceived(data) { //setup plot after retrieving data
		//console.log(data);
		if( data.from == 'node'){
			if(data.data.type == 'SIDsRead'){ //real data
				console.log(data.data.address, data.data.value);
				if(name0.trim() == data.data.address.trim())
					updateDataTable(data.data.value, "left");
				else if(name1.trim() == data.data.address.trim())
					updateDataTable(data.data.value, "right");
				updateChart(data);
			}
			else if(data.data.type == 'SIDsSettings'){
				if(name0.trim() == data.data.address.trim())
					addSettings(data.data.value, "left");
				else if(name1.trim() == data.data.address.trim())
					addSettings(data.data.value, "right");
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
	
    function updateDataTable(data, side){
    	if(side == 'left'){
	    	$("#dataTableL tbody").prepend("<tr>" +
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
	    	$("#dataTableR tbody").prepend("<tr>" +
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
    
	function updateChart(data) {
		//update chart
		if(name0.trim() == data.data.address.trim()){
			chart.series[0].addPoint(data.data.value[3], true, true);
			chart.series[1].addPoint(data.data.value[6], true, true);
		}
		if(name1.trim() == data.data.address.trim()){
			chart.series[2].addPoint(data.data.value[3], true, true);
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
		
		addSettingContainers();
		addUpdateButtons();
		addSaveButtons();
		addFileUploadDivL();
		addFileUploadDivR();
		
		addStartButton();
		addStopButton();
		startButton.button("enable");
		stopButton.hide();
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
    	startButton.insertBefore("#dataContainerL");
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
		stopButton.insertBefore("#dataContainerL");
    }
    
    function startSIDs() {
    	//disable all setting inputs
    	$.each(inputsL, function(key,val){
    		val.spinner("disable");
    	});
    	$.each(inputsR, function(key,val){
    		val.spinner("disable");
    	});    	
    	fileInputL.hide();
    	fileInputR.hide();    	
    	startButton.hide();
    	stopButton.show();
    	updateButtonL.hide();
    	updateButtonR.hide();
    	socket.send("startSIDs"+name0.trim());
    	setTimeout(function(){		//wait 1 second before starting the right board
    		socket.send("startSIDs"+name1.trim());
    	}, 1000);
    	
    } 
    
    function stopSIDs() {
    	//enable all setting inputs
    	$.each(inputsL, function(key,val){
    		if(val[0].id != "SAMPLE CACULATION"){
    			val.spinner("enable");
    		}
    	});   
    	
    	$.each(inputsR, function(key,val){
    		if(val[0].id != "SAMPLE CACULATION"){
    			val.spinner("enable");
    		}
    	});       	
    	fileInputL.show();
    	fileInputR.show();
    	stopButton.hide();
    	startButton.show();
    	updateButtonL.show();
    	updateButtonR.show();
    	socket.send("stopSIDs"+name0.trim());
    	socket.send("stopSIDs"+name1.trim());
    	setTimeout(function(){ 				// wait long enough for separate log files to be closed
    		socket.send("combineLog");
    	}, 3000);
    	
    }    
	
    var fileInputL, fileInputR;
    function addFileUploadDivL() {
    	fileInputL = $('<span class="file-wrapper" title="Submit a different Dicom file">\
    			<span>UPLOAD CONFIG FILE</span>\
                <input type="file" name="uploaded_files" >\
            </span>').css({
    		float: 'right',
    		fontSize: '30%',
    	});
    	fileInputL.button();
    	fileInputL.fileupload({
    		url: configUrl,
            dataType: 'json',
            formData: {
            	address: name0.trim()
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
    	fileInputL.insertBefore("#dataContainerL");
    }	
	
    function addFileUploadDivR() {
    	fileInputR = $('<span class="file-wrapper" title="Submit a different Dicom file">\
    			<span>UPLOAD CONFIG FILE</span>\
                <input type="file" name="uploaded_files" >\
            </span>').css({
    		float: 'right',
    		fontSize: '30%',
    	});
    	fileInputR.button();
    	fileInputR.fileupload({
    		url: configUrl,
            dataType: 'json',
            formData: {
            	address: name1.trim()
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
    	fileInputR.insertBefore("#dataContainerR");
    }	
    
    var saveButtonL, saveButtonR;
    function addSaveButtons() {
    	saveButtonL = $('<button>SAVE SETTINGS</button>').css({
			float: 'right',
			fontSize: '30%',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
    	saveButtonL.button();
    	saveButtonL.button("enable");
    	saveButtonL.click(saveSettingsL);
    	saveButtonL.insertBefore("#dataContainerL");
    	
    	saveButtonR = $('<button>SAVE SETTINGS</button>').css({
			float: 'right',
			fontSize: '30%',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
    	saveButtonR.button();
    	saveButtonR.button("enable");
    	saveButtonR.click(saveSettingsR);
    	saveButtonR.insertBefore("#dataContainerR");    	
    }	
	
    function saveSettingsL(){
    	var config = {};
    	$.each(inputsL, function(key, val){
    		//config.push(val[0].value);
    		
    		config[val[0].id] = val[0].value;
    		
    	});
    	var data = {
    			'address': name0.trim(),
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
    
    function saveSettingsR(){
    	var config = {};
    	$.each(inputsR, function(key, val){
    		//config.push(val[0].value);
    		
    		config[val[0].id] = val[0].value;
    		
    	});
    	var data = {
    			'address': name1.trim(),
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
    
    var updateButtonL, updateButtonR;
    function addUpdateButtons() {
    	updateButtonL = $('<button>UPDATE SETTINGS</button>').css({
			float: 'right',
			fontSize: '30%',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
    	updateButtonL.button();
    	updateButtonL.button("enable");
    	updateButtonL.click(updateSettingsL);
    	updateButtonL.insertBefore("#dataContainerL");
    	
    	updateButtonR = $('<button>UPDATE SETTINGS</button>').css({
			float: 'right',
			fontSize: '30%',
			position: 'relative',
			//right: '0px',
			top: '0px'
		});   	
    	updateButtonR.button();
    	updateButtonR.button("enable");
    	updateButtonR.click(updateSettingsR);
    	updateButtonR.insertBefore("#dataContainerR");    	
    }
    
    function updateSettingsL() { //update setting through ajax
    	var config = {};
    	$.each(inputsL, function(key, val){
    		//config.push(val[0].value);
    		
    		config[val[0].id] = val[0].value;
    		
    	});
    	var data = {
    			'address': name0.trim(),
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

    function updateSettingsR() { //update setting through ajax
    	var config = {};
    	$.each(inputsR, function(key, val){
    		//config.push(val[0].value);
    		
    		config[val[0].id] = val[0].value;
    		
    	});
    	var data = {
    			'address': name1.trim(),
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
    
	/*
    var settings = [
                    {name: 'setting1', value: '0'},
                    {name: 'setting2', value: '2'},
                    {name: 'setting3', value: '3'},
                    {name: 'setting4', value: '4'}
                    ]; //demo settings array
    */
    var settingContainerL, settingContainerR, inputsL, inputsR;
    function addSettingContainers(){
    	settingContainerL = $("<div id='settingContainerL'/>"); 
    	settingContainerL.insertBefore("#dataTableL");
    	settingContainerR = $("<div id='settingContainerR'/>"); 
    	settingContainerR.insertBefore("#dataTableR");
    }
    
    function addSettings(settings, side){
    	//console.log(settings);
    	if(side == "left"){
	    	if(inputsL == null){
		    	settingTable = $("<table id='settingTable' border='0'></table>");
		    	inputsL = [];
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
		    		inputsL.push(input);
		    		
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
		    	settingTable.appendTo(settingContainerL);
	    	}
	    	else { // update tables
	        	$.each(inputsL, function(key, val){
	        		//config.push(val[0].value);
	        		val[0].value = settings[val[0].id];
	        	});
	    	}
    	}
    	else if(side == "right"){
    		if(inputsR == null){
		    	settingTable = $("<table id='settingTable' border='0'></table>");
		    	inputsR = [];
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
		    		inputsR.push(input);
		    		
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
		    	settingTable.appendTo(settingContainerR);
	    	}
	    	else { // update tables
	        	$.each(inputsR, function(key, val){
	        		//config.push(val[0].value);
	        		val[0].value = settings[val[0].id];
	        	});
	    	}
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
			socket.send("sendSIDsSet"+name0.trim());
			socket.send("sendSIDsSet"+name1.trim());
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