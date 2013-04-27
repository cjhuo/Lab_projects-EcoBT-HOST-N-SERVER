/* Main script for analysis.html page.
 *
 *   <p>1. Choose a radio button to pick the channel you want to analyze
 *   <br>
 *      2. Zoom to the range where you feel comfortable to pick start and end peak points
 *   <br>
 *      3. Pick 2 peak points and hit submit for further analysis in range between those 2 peak points
 *   <br>
 *      <b>Note:</b> <br>
 *      a) Click a point you picked will de-select the point <br>
 *      b) You can always go back to the original state by choose any of the radio buttons</p>
 *
 */

$(function () {
	
	//ajax call urls
	var submitUrl = 'ecgHandler'; 
	var fileHandlerUrl = 'ecgHandler'
	
	var datasets; //store datasets
	var peaks; //store indice of peak points for channels 
			   //only need 1-d array since peak indice for every channel are the same
	var diagram; //store DOM object of plot div
	var overview; //store DOM object of overview plot
	var choice;  //store DOM objects of checkbox of channels
    var plot;  //store main plot object will be returned by highchart
    var overviewPlot; ///store overview plot object will be returned by flot
    var peakText;// store DOM object of peak point
    var submit; //store DOM object of submit button
    
    var spinTarget; //store DOM object used to show loading spinner
    var spinner; //spinner
    
    var qPoint;
    var tPoint;
    var bin; //store DOM used to choose bin number
    
    var histogram; //store DOM object of histogram div
    var hPlot; // store histogram plot object will be returned by highchart
        
    var refImgDiv ////store DOM object of reference image div
    
    //store the url for a reference image of ECG chart
    //borrowed from http://www.davita-shop.co.uk/ecg-instruments.html    
    var refImgUrl = "static/css/images/ecg.png"; 
    
    var frequency = parseInt($('#frequency').val());
    var xGridInterval = 200; //0.2 second = 200ms, pointInterval was multiplied by 6, so GridInterval is also multiplied by 6
    var yGridInterval = 500; //0.5 mV
    var xPointInterval = 1000/frequency;
    
    var yTickHeight = document.ontouchstart === undefined ? 20 : 40;
    
    var hOptions = { // //options settings for histogram plot
        chart: {
            renderTo: 'histogram',
            //type: 'column'
        },
        title: {
            text: 'Histogram based on chosen Q/T point'
        },
        subtitle: {
            text: ''
        },
        credits: {
        	href: "http://cps.eng.uci.edu:8000/analysis",
        	text: "UCI Embedded Lab"
        },
        xAxis: {
        	labels: {
        		enabled: false
        	},
        	tickLength: 0
        },
        yAxis: {
        	title: {
        		text: ""
        	},
        	min: 0,
        	//max: 100
        },
        tooltip: {
            formatter: function() {
                var s;
                if (this.point.name) { // the pie chart
                    s = ''+
                        this.point.name +': '+ this.percentage.toFixed(1) +' %';
                } else {
                    s = this.series.name +': '+ this.y;
                }
                return s;
            },
        },
        plotOptions: {
        	pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false,
                    color: '#000000',
                    connectorColor: '#000000',
                    formatter: function() {
                        return '<b>'+ this.point.name +'</b>: '+ this.percentage.toFixed(1) +' %';
                    }
                },
                tooltip: {
                	enabled: false
                },
                showInLegend: false,
                center: [100, 50],
                	size: 100,    
            },
            column: {
                dataLabels: {
                    enabled: false,
                    formatter: function() {
                    	if(this.y != 0)
                    		return '<b>'+ this.series.name +'</b>: '+ this.y;
                    	else
                    		return '';
                    }
                },
                showInLegend: true,
                
                //pointPadding: 0,
                //groupPadding: 0,
                //borderWidth: 0
                
            }
        },
        series: []
    }
    colors = ['#A52A2A', '#DEB887', '#5F9EA0', '#7FFF00', '#D2691E', '#FF7F50','#6495ED','#FFF8DC',
              '#DC143C','#00FFFF','#00008B']
    function drawHistogram(data) {
    	showSpinner();
    	if(histogram != null){
    		histogram.remove();
    	}
    	if(hPlot != null){
    		hPlot.destroy();
    	}
    	histogram = $('<div id="histogram" ></div>').css( {    		
            position: 'relative',
            //width: '100%',
            height: '400px',
            margin: '5px',
            //padding: '2px'
        });
    	histogram.appendTo("body");
    	//var tmpDataColumn = [];
    	var tmpDataPie = [];
    	sum = 0;
    	$.each(data.data, function(key, val) {
    		sum += val[2];
    	});
    	var i = 0
    	hOptions.series = [];
    	$.each(data.data, function(key, val) {    		
    		hOptions.series.push({
    			type: 'column',
    			name: (val[0].toFixed(5) + '~' + val[1].toFixed(5)).toString(),
    			data: [val[2]],
    			dataLabels:{
    				enabled: true
    			},
    			color: colors[i]
    		});
    		tmpDataPie.push({    			
	    		name: (val[0].toFixed(5) + '~' + val[1].toFixed(5)).toString(), 
	    		y: val[2],
	    		color: colors[i]
    		});
    		i++;
    	});

    	hOptions.series.push({
    		//name: label,
    		type: 'pie',
			name: 'percentage',
            data: tmpDataPie
    	});
    	hPlot = new Highcharts.Chart(hOptions, function() {
    		hideSpinner();
    	});

    }
    
    var tableDom, dTable;
    function drawTable(data){
    	console.log(data);
    	if(tableDom != null){
    		dTable.fnDestroy();
        	tableDom.remove();
        	tableDom = null;
    	}
		tableDom = $('<table id="dataTable" class="ui-widget ui-widget-content">\
				<thead>\
		      <tr class="ui-widget-header ">\
		        <th>Average Heart Rate</th>\
		        <th>Heart Rate Range</th>\
		        <th>Number of Heart Beats (RR)</th>\
				<th>Longest QTc</th>\
				<th>Shortest QTc</th>\
				<th>Percent QTc >=450 ms (0.45 sec)</th>\
		      </tr>\
		    </thead>\
		    <tbody>\
		    </tbody>\
		  </table>').css({
			  fontSize: 'small',
			  marginLeft: 'auto',
			  marginRight: 'auto',
			  textAlign: 'center'
		  });
		dTable = tableDom.dataTable({
	        "bPaginate": false,
	        "bLengthChange": false,
	        "bFilter": false,
	        "bSort": false,
	        "bInfo": false,
	        "bAutoWidth": true
		});
		tableDom.appendTo("body");

    	//dTable.fnClearTable();
    	if(data.info != null){
    		dTable.fnAddData(data.info);
    	}
    	
    }
    
    /* 
     * draw histogram with bins
     * format of bins json: {'data': [[min, max, value],[min,max,value],...]}
     */
    function onBinDataReceived(data) {
    	drawTable(data);
		drawHistogram(data);
		plotAccordingToChoices();
    }
    
    var options = { //options settings for main plot
            chart: {
                renderTo: 'diagram',
                zoomType: document.ontouchstart === undefined ? 'x' : '',
                /*animation: {
                    duration: 1000
                },*/
                type: 'line',
                marginTop: 110
            },
            credits: {
            	href: "http://cps.eng.uci.edu:8000/analysis",
            	text: "UCI Embedded Lab"
            },
            loading: {
                labelStyle: {
                    color: 'white'
                },
                style: {
                    backgroundColor: 'gray'
                }
            },
            title: {
                text: 'QRS Wave data analysis'
            },
            subtitle: {
                text: '' //TBD
            },
            legend: {
            	enabled: false
            },
            rangeSelector:{
            	enabled: false,
            	inputEnabled: false,
            	buttons: [{
            		type: 'millisecond',
            		count: 50,
            		text: '50m'
            	}, {
            		type: 'all',
            		text: 'All'
            	}],
            	selected: 1
            },
            subtitle: {
            	align: 'left',
            	text: '*Please manually locate any Q point and any T point on the ECG plot \
            			and submit to server for QTC historgram generation<br>'
            			+ '*Click top-right button for reference of namings of ECG deflections<br>'
            			+ '*The ECG plot is zoomable. '
            			+ (document.ontouchstart === undefined ?
                                'Click and drag in the plot area to zoom in' :
                                'Drag your finger over the plot to zoom in')

            			+ '<br>*Only the first ' + (document.ontouchstart === undefined ? '10' : '5')
            			+ ' seconds data are diplayed for the purpose of getting Q/T inputs from user'
            },
            xAxis: {
            	lineColor: '#F5959A',
            	gridLineColor: '#F5959A',
            	gridLineWidth: document.ontouchstart === undefined ? 0.5 : 2,
            	minorGridLineColor: '#F5959A',
            	minorGridLineWidth: document.ontouchstart === undefined ? 0.2 : 1,
            	
            	minorTickInterval: xGridInterval/5, //a fifth of the tickInterval by default
    	        minorTickWidth: 1,
    	        minorTickLength: 0,
    	        minorTickPosition: 'inside',
    	        minorTickColor: '#F5959A',
    	
    	        //tickPixelInterval: 30,
    	        tickInterval: xGridInterval,
    	        tickWidth: 2,
    	        tickPosition: 'inside',
    	        tickLength: 0,
    	        tickColor: 'rgb(245, 149, 154)',
    	        
    	        labels: {
    	        	enabled: false,
    	        	step: 2
    	        },
    	        startOnTick: false,
    	        endOnTick: false
            },
            yAxis: {
            	lineColor: 'rgb(245, 149, 154)',
            	gridLineColor: 'rgb(245, 149, 154)', 
            	gridLineWidth: document.ontouchstart === undefined ? 0.5 : 2,
            	minorGridLineColor: 'rgb(245, 149, 154)',
            	minorGridLineWidth: document.ontouchstart === undefined ? 0.2 : 1,
            	
            	minorTickInterval: yGridInterval/5,
    	        minorTickWidth: 2,
    	        minorTickLength: 0,
    	        minorTickPosition: 'inside',
    	        minorTickColor: 'rgb(245, 149, 154)',
    	
    	        //tickPixelInterval: 30,
    	        tickInterval: yGridInterval, //assume the unit of output is microVolt, 0.5milliVolt = 500microVolt
    	        tickWidth: 2,
    	        tickPosition: 'inside',
    	        tickLength: 0,
    	        tickColor: 'rgb(245, 149, 154)',
    	        
    	        //height: 120,
    	        
            	title: {
            		text: ""
            	},
            	labels: {
            		enabled: false
            	}
            },
            tooltip: {
                enabled: true,
                crosshairs: true,
                formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+
                    this.x/(1000/frequency) +': '+ this.y;
                },
                positioner: function () {
                	return { x: 550, y: 50 };
                },
                backgroundColor: 'rgba(255, 255, 255, 0.1)'
            },
            plotOptions: {
            	dataGrouping: {
            		enabled: false
            	},  
                line: {
                	animation: false,
                	color: 'black',	
                	lineWidth: 0.7,
                    dataLabels: {
                        enabled: false
                    },
                    states: {
                    	hover: {
                    		lineWidth: 0.7 //gotta be same value as line.lineWidth 
                    					//so that when hovered plot won't look weird
                    	}
                    },
                    shadow: false,
                    enableMouseTracking: true
                },
                series: {
                	allowPointSelect: true,  
                    marker: {
                    	enabled: true,
                    	radius: 0.1,
                        states: {
                			hover: {
                				radius: 4
                			},
                            select: {
                                radius: 4
                            }
                        }
                    },
                    point: {
                    	events: {
                    		click: pointClick
                    	}
                    }
                }	
            },
            series: []
    };
    
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
	spinTarget = $('<div id="spinner" ></div>').css( {
	            position: 'relative',
	            width: '50px',
	            height: '50px',
	            margin: 'auto'
	});
	spinTarget.appendTo("body");
	
	spinner = new Spinner(spinnerOpts);

	/* issue ajax call and further process the data on sucess */
	function getAndProcessData() { 
		chooseFileSource();
	}
	
	function chooseTestFile() {
		showSpinner();
		$.ajax({
			url: fileHandlerUrl,
			cache: false,
			type: 'POST',
			dataType: 'json',
			success: onDataReceived
		});
		$('#fileChooser').dialog( "destroy" );
	}
	
	var dicomList;
	function getDicomList() {
		$.ajax({
			url: '/dicomList',
			cache: false,
			type: 'GET',
			async: false,
			dataType: 'json',
			success: function(data) {
				dicomList = data.fileList;
			}
		});
	}
	
	var dicomListMenu;
	function chooseFileSource(){
    	var popUpDiv = $('<div id="fileChooser"/>');
    	$('<p>Please choose choose a dicom file: </p>')
    		.appendTo(popUpDiv);
    	var defButton = $('<button>Use sample dicom file</button>').css({
    		float: 'left',
    		fontSize: 'small',
    	});

    	defButton.button({
            icons: {
                primary: "ui-icon-triangle-1-s"
              }
    	});
    	//defButton.click(chooseTestFile);
    	popUpDiv.append(defButton);
    	
    	getDicomList();
    	dicomListMenu = $('<ul>').css({
    		zIndex: '2000'
    	}).appendTo('body').hide();
    	$.each(dicomList, function(key, val) {
    		var lnk = $('<li><a href="#">' + val + '</a></li>');
    		lnk.appendTo(dicomListMenu);
    	});
    	
    	dicomListMenu.hide().menu();
    	defButton.click(function(event){
    		console.log(dicomListMenu);
    		//dicomListMenu.appendTo('body').show();
    		
    		dicomListMenu.show().position({
                my: "left top",
                at: "left bottom",
                of: this
              });
            
            $( document ).one( "click", function() {
            	dicomListMenu.hide();
              });
            return false;
    	});
    	    	
    	var fileInput = $('<div class="file-wrapper">\
    			<span>Submit your own Dicom file</span>\
                <input style="width:100%" type="file" name="uploaded_files" >\
            </div>').css({
    		float: 'right',
            marginLeft: '5px',
    		fontSize: 'small',
    	});
    	fileInput.button();
    	fileInput.fileupload({
    		url: fileHandlerUrl,
            dataType: 'json',
            send: function (e, data) {
            	showSpinner();           	
            	//console.log(data);
            },
            done: function (e, data) {
            	//console.log(data.result);
            	$('#fileChooser').dialog( "destroy" );
            	onDataReceived(data.result);
            	$(this).fileupload('destroy');
            },
            fail: function (e, data) {
            	//console.log(data.textStatus);
            	alert('invalid file');
            	hideSpinner();
            	
            }
        });
    	
    	popUpDiv.append(fileInput);
    	
    	
    	//add two button, one for file input handler directed to jquery upload
    	//, one for default file handler
    	//TBD
    	
    	popUpDiv.dialog({
            //height: 200,
    		position: {
    			my: "top",
    			at: "bottom",
    			of: $("#spinner")[0]
    		},
    		width: 450,
            modal: false,
            resizable: false,
            dialogClass: 'alert',
            closeOnEscape: false,
        });
    	$(".ui-dialog-titlebar").hide(); //remove dialog title bar
	}

	/** 
	    Data received should have the structure as below:
	    data.dspData = [
	                    {
	                        'label': "channel1",
	                        'data': [array of [x, y]]
	                    },
	                    {
	                        'label': "channel2",
	                        'data': [array of [x, y]]
	                    }
	                ]
	    data.peaks = [index of 1st peak, index of 2nd peak, ...]
	    
	    for fakePlot only:
	    	data retrieved from server for n channels with 100 data each, ranged from (-100, 100)
	    
	*/						
	function onDataReceived(data) { //setup plot after retrieving data
	    extractDatasets(data); //JSON {'dspData': datasets, 'peaks': indice of peak points}         
		addChoices(); //add channel radio buttons
		addReferenceImg();
		addFileUploadDiv();
		//addPlot();  //generate main plot div
		//addOverview(); // generate overview plot div
		plotAccordingToChoices(); //plot diagram on generated div and generate overview
	
	}
	
	    
	function extractDatasets(data) {
		datasets = data.dspData;		
		peaks = data.peaks;
	}
    
    function addChoices() {
        var i = 1;
        choice = $('<div id="choices">Show:</div>').css( {
            position: 'relative',
            //width: '10%',
            cssFloat: 'center',
			fontWeight: 'bold',
			margin: '10px 5px 10px 5px'
            //textAlign: 'center'
        });
        var checked = 0;
        $.each(datasets, function(key, val){
			
        	//generate radiobox for each channel 
        	/*
        	var domStr = ' <input type="radio" name="channel" id="' + val.label 
        	+ '" value="' + key + '"' + (checked==0?' checked':'') + '>' 
        	+' <label for="' + val.label + '">'+ val.label + '</label>';
        	*/
        	var domStr = ' <input type="radio" name="channel" id="' + val.label 
        	+ '" value="' + key + '"/>' 
        	+' <label for="' + val.label + '">'+ val.label + '</label>';
        	choice.append(domStr);
        	
        	++i;
        });
        

        choice.appendTo("body");
        
        // check leadII by default
        choice.find("input").filter('[id=II]').attr('checked',true);
		
		choice.find("input").click(plotAccordingToChoices);
    }
    
    function addFileUploadDiv() {
    	var fileInput = $('<span class="file-wrapper" title="Submit a different Dicom file">\
    			<span>File</span>\
                <input style="width:100%" type="file" name="uploaded_files" >\
            </span>').css({
    		float: 'right',
    		fontSize: 'small',
    	});
    	fileInput.button();
    	fileInput.fileupload({
    		url: fileHandlerUrl,
            dataType: 'json',
            send: function (e, data) {
            	showSpinner();
            	//console.log(data);
            },
            done: function (e, data) {
            	//console.log(data.result);
            	choice.remove();
            	diagram.remove();
            	if(tableDom != null){
	            	dTable.fnDestroy();
	            	tableDom.remove();
	            	tableDom = null;
            	}
            	if(histogram != null)
            		histogram.remove();
            	onDataReceived(data.result);
            },
            fail: function (e, data) {
            	alert('invalid file');
            	hideSpinner();
            }
        });
    	fileInput.appendTo(choice);
    }
    
    function addReferenceImg() {
    	
    	refImgDiv = $('<div><img src=' + refImgUrl 
    			+ ' alt="reference image borrowed from www.davita-shop.co.uk" style="margin: 0 auto;display:block">'
    			+ '</div>');  
        
        refImgDiv.dialog({
            autoOpen: false,
            resizable: false,
            position: { 
            	my: "top", 
            	at: "bottom", 
            	of: "#ref", 
            	},
            show: "blind",
            hide: "blind"
        });
        $(".ui-dialog-titlebar").hide(); //remove dialog title bar

    	//refImgDiv.appendTo(choice);

    	var refButton = $('<span id="ref" title="show/hide reference of Q/T point</span>">Reference</span>').css({
    		float: 'right',
    		fontSize: 'small',
    	});
    	

    	refButton.button();
    	refButton.click(showRef);

        refButton.appendTo(choice);
    }
    
    function showRef(e) {
    	if(refImgDiv.dialog("isOpen")){
    		refImgDiv.dialog("close");
    	}
    	else{
    		refImgDiv.dialog("open");
    	}
    }
    /*
    function addPlot() { 
    		
    	//plot all channels on one plot
    	diagram = $('<div id="diagram" ></div>').css( {
            position: 'relative',
            //width: '100%',
            height: '240px',
            margin: '5px',
            //marginRight: '10px',
            //padding: '2px'
        });
    	diagram.appendTo("body");
    }
    */
    
    function clearAndPlot(){
    	if(plot != null){
      		//remove selected points if there is any, bug in new version
    		var pList = plot.getSelectedPoints();      		
    		for(var i=0; i<pList.length;i++){
    			pList[i].select(false, false);
    		}
        		
    		plot.destroy();
    		diagram.remove();
    	}
    		
    	/* re-initialize every parameter */
    	//diagram.unbind();
    	qPoint = null;
    	tPoint = null;
		/* remove peakText button if any */
		if(peakText)
			peakText.remove();
		/* remove submit button if any */
		if(submit)
			submit.remove();
    }
	
    
    function plotAccordingToChoices() {
        var data = [];
        var key;
        var label;
        var yTop = 110;
        var min, max;
        
        choice.find("input:checked").each(function () {
        	key = $(this).attr("value");
        	label = $(this).attr("id");

            if (key && datasets[key]){                
                if(document.ontouchstart === undefined){ 
                	data = datasets[key].data;
                }
                else{ //only take half the data received to display on mobile device
                	for(var i=0;i<datasets[key].data.length/2;i++){
                		data.push(datasets[key].data[i]);
                	}
                }
                min = datasets[key].min;
                max = datasets[key].max;
            }
            	
        });
    	//options.yAxis.min = min;
    	//options.yAxis.max = min + 11 * yGridInterval;
        options.yAxis.minRange = 12 * yGridInterval;
        options.yAxis.range = 12 * yGridInterval;
    	//options.yAxis.height = yTickHeight*(Math.ceil(options.yAxis.max/yGridInterval)-Math.floor(options.yAxis.min/yGridInterval));
        options.yAxis.height = 12 * yTickHeight;
        options.yAxis.top = yTop;
    	var diagramHeight = yTop + options.yAxis.height + 15;
        if (data.length > 0){
        	clearAndPlot();
			/* re-plot everything */
        	options.series = [];
        	options.series.push({
        		name: label,
                data: data,
                pointInterval: xPointInterval
        	});
        	
        	//plot all channels on one plot
        	diagram = $('<div id="diagram" ></div>').css( {
                position: 'relative',
                //width: document.ontouchstart === undefined ? 'auto' : 'auto',
                //width: 'auto',
                height: diagramHeight.toString() + 'px',
                margin: '5px',
                //marginRight: '10px',
                //padding: '2px'
            });
        	diagram.insertAfter(choice);
        	
        	plot = new Highcharts.Chart(options, function() {
        		hideSpinner();
        	});
        	
        	//end loading data   
        }
    }
    
    /* show loading spinner, stopped when chart is fully loaded */
    function showSpinner(){
    	spinTarget.show();
		spinner.spin(spinTarget[0]);
    }
    
    function hideSpinner(){
		spinTarget.hide();
		spinner.stop();
    }
    
    function pointClick(event) { //click event function
		if(qPoint == this) {
			this.select(false, true);
			qPoint = null; 
		}
		else if(tPoint == this) {
			this.select(false, true);
			tPoint = null; 
		}
		else { //add Q/T point base on pop-up selection
			pointPopup(this, event);
		}
		makeQTText();
		return false;
    }
    
    /* toggle point and set Q/T point after user make the selection from pop-up dialog */
    function makeSelection(point, pSelection) {
		//alert(pSelection);
		//add clicked point to qPoint/tPoint
		if(pSelection != null){
			if(pSelection == 1){
				if(qPoint){
					qPoint.select(false, true);
				}
				qPoint = point;
			}
			else if(pSelection == 0){
				if(tPoint){
					tPoint.select(false, true);
				}
				tPoint = point;
			}
			point.select(true, true);
		} //else null without any selection, do nothing	
		makeQTText();
    }
    
    /* Q/T point selection pop-up window */
    var popUpDiv;
    function pointPopup(point, event) { 
    	var pSelection = null;
    	popUpDiv = $('<div id="popUpBox">Please choose the type for the point: </div>');
    	//popUpDiv.html('');
    	
    	popUpDiv.dialog({
    		position: {
    			my: "center",
    			at: "center",
    			of: $("#diagram")
    		},
            height: 200,
            width: 250,
            modal: true,
            resizable: false,
            buttons: {
                "Q Point": function() {
                	pSelection = 1;
                	makeSelection(point, pSelection);
                    $( this ).dialog( "destroy" );
                    popUpDiv.remove();
                },
                "T Point": function() {
                	pSelection = 0;
                	makeSelection(point, pSelection);
                    $( this ).dialog( "destroy" );
                    popUpDiv.remove();
                }
            }
        }).css({
        	fontSize: 'small',
        	zoom: document.ontouchstart === undefined ? '1' : '0.2'
        });
    	$('.ui-dialog-buttonset').css({
    		fontSize: 'small',
    		zoom: document.ontouchstart === undefined ? '1' : '0.5'
    	});
    	$('.ui-dialog-titlebar').css({
    		fontSize: 'small',
    		zoom: document.ontouchstart === undefined ? '1' : '0.5'
    	});
    	$('.ui-dialog-buttonset').focus();
    	//return pSelection;
    }
    
    function makeBinChooser(){
    	bin = $('<select id="selector"/>');
    	for (var i = 1; i<=10; i++) { //generate bin number range from 1 - 10
    		bin.append($('<option/>').html(i));
    	}
    	bin.val(3); //by default generate 3 bins
    	
    	var binChooser = $('<div id="binChooser"/>');
    	binChooser.html('<label for="spinner">Select a bin number:</label>');
    	
    	binChooser.append(bin);
    	binChooser.appendTo(choice);
    	return binChooser;
    }

    /* show peak selection in peakText div */
	function makeQTText() {	
		/* remove peakText button if any */
		if(peakText)
			peakText.remove();
		/* remove submit button if any */
		if(submit)
			submit.remove();
		if(qPoint || tPoint){
			peakText = $('<p id="selectedPoints" ></p>').css( {
	            position: 'relative',
				fontWeight: 'bold'
	        });
	    	peakText.appendTo(choice);
	    	/*$.each(selectedPoints, function(i, val) {
				var domStr = 'You have selected peak point (x: ' + val.datapoint[0] + ', y: '
				+ val.datapoint[1] + ') in ' + val.series.label + '.<br>'
				peakText.append(domStr);*/
	    	if(qPoint) {
				var domStr = '<br>You have picked Q point at (x: ' 
					+ qPoint.x/xPointInterval + ', y: '
					+ qPoint.y/xPointInterval + ') .';
				peakText.append(domStr);
	    	}
	    	if(tPoint) {
				var domStr = '<br>You have picked T point at (x: ' 
					+ tPoint.x/xPointInterval + ', y: '
					+ tPoint.y/xPointInterval + ') .';
				peakText.append(domStr);
	    	}	    	
	    	if(qPoint && tPoint) {	    		
	    		peakText.append(makeBinChooser());
				var domStr = '<br>Click "submit" button to send your request to server';
				peakText.append(domStr);	
				submit = $('<input id="submit" type="button" value="submit" >').css({
					fontSize: 'small'
				});
				submit.button();
				submit.appendTo(choice);
				submit.click(doSubmit);
				submit.focus();
	    	}

		}
	}
    
    /* submit the peak information to server */
    function doSubmit() {
    	/* data to be sent should follow fomat as:
    		data = {'channel': channelNo,
    				'selectedPoints': array of peak, e.g. [[1, 20], [5, 40]]
    		}
    	*/
    	//console.log(choice.find('input').filter('[checked=checked]').attr("value"));
    	var pdata = {//'channel': selectedPoints[0].series.label.substring(8),
    			'qPoint': [qPoint.x/xPointInterval, qPoint.y/xPointInterval],
    			'tPoint': [tPoint.x/xPointInterval, tPoint.y/xPointInterval],
    			'bin': parseInt(bin.val()),
    			'lead': choice.find('input').filter('[checked=checked]').attr("value")	
    			};

		$.ajax({
			type: 'GET',
			url: submitUrl,
			dataType: 'json',
			cache: false,
			data: {"data":JSON.stringify(pdata)},
			beforeSend: showSpinner,
			complete: hideSpinner,
			success: onBinDataReceived,
			error: function() {
				alert("ECG module Error!! (mostly because invalid Q/T input)");
		    	if(tableDom != null){
		    		dTable.fnDestroy();
		        	tableDom.remove();
		        	tableDom = null;
		    	}
		    	if(histogram != null){
		    		histogram.remove();
		    		histogram = null;
		    	}
		    	if(hPlot != null){
		    		hPlot.destroy();
		    		hPlot = null;
		    	}
		    	plotAccordingToChoices();
			}
		});
    }
       
    getAndProcessData();
});