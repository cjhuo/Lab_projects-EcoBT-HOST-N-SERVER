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
	var dataurl = 'dsp'; 
	var submitUrl = 'submit'; 
	
	var datasets; //store datasets
	var peaks; //store indice of peak points for channels 
			   //only need 1-d array since peak indice for every channel are the same
	var diagram; //store DOM object of plot div
	var overview; //store DOM object of overview plot
	var choice;  //store DOM objects of checkbox of channels
    var plot;  //store mian plot object will be returned by flot
    var options; //options settings for main plot
    var overviewPlot; ///store overview plot object will be returned by flot
    var peakText;// store DOM object of peak point
    var submit; //store DOM object of submit button
    
    var selectedPoints = [];

	function getAndProcessData() { //issue ajax call and further process the data on sucess
		$.ajax({
			url: dataurl,
			cache: false,
			type: 'GET',
			dataType: 'json',
			success: onDataReceived
		});
	}
	
    /* 
	    Data received should have the structure as below:
	    data.dspData = {
	                    "channel1": {
	                        'label': "channel1",
	                        'data': [array of [x, y]]
	                    },
	                    "channel2": {
	                        'label': "channel2",
	                        'data': [array of [x, y]]
	                    }
	                }
	    data.peaks = [index of 1st peak, index of 2nd peak, ...]
	    
	    for fakePlot only:
	    	data retrieved from server for n channels with 100 data each, ranged from (-100, 100)
	    
    */
    function onDataReceived(data) { //setup plot after retrieving data
        extractDatasets(data); //JSON {'dspData': datasets, 'peaks': indice of peak points}         
		addChoices(); //add channel radio buttons
		addPlot();  //generate main plot div
		addOverview(); // generate overview plot div
		plotAccordingToChoices(); //plot diagram on generated div and generate overview

    }
	    
	function extractDatasets(data) {
		datasets = data.dspData;
		
		peaks = data.peaks;
	}
    
    function addPlot() { 
    	/*//generate one plot for each channel
    	var diagram = $('<div id="channel'+ index +'"/>').css( {
            position: 'relative',
            width: '500px',
            height: '200px',
            margin: 'auto',
            padding: '2px'
        });
    	*/
    		
    	//plot all channels on one plot
    	diagram = $('<div id="diagram" ></div>').css( {
            position: 'right',
            width: '70%',
            height: '400px',
            margin: 'auto',
            padding: '2px'
        });
    	diagram.appendTo("body");
    }

    
    function addChoices() {
        var i = 1;
        choice = $('<div id="choices">Show:</div>').css( {
            position: 'relative',
            width: '10%',
            cssFloat: 'left',
			fontWeight: 'bold',
			margin: '10px 0px 0px 10px'
            //textAlign: 'center'
        });
        var checked = 0;
        $.each(datasets, function(key, val){
        	val.color = i; //hard-code to assign a color to each channel choice
        	val.lines = { show: true, fill: true }; //do not need to show point nor
        	val.points = { show: false};				//hoverable nor clickable on points
        	val.hoverable = false;					//which are not peaks
        	val.clickable = false;
			
        	//generate radiobox for each channel 
        	var domStr = '<br/><input type="radio" name="channel" id="id' + key 
        	+ '" value="' + key + '"' + (checked==0?' checked':'') + '>' 
        	+'<label for="id' + key + '">'+ val.label + '</label>';
        	
        	choice.append(domStr);
        	
        	++i;
        });
        choice.appendTo("body");
		
		choice.find("input").click(plotAccordingToChoices);
    }
    
    function plotAccordingToChoices() {
        var data = [];
        var peakSeries = {};

        choice.find("input:checked").each(function () {
            var key = $(this).attr("value");

            if (key && datasets[key])
                data.push(datasets[key]);
            
            //setting up peaks series           
            peakSeries.data = [];
            $.each(peaks, function(i,val) {
            	peakSeries.data.push(datasets[key].data[val]);
            });
            peakSeries.lines = { show: false};
            peakSeries.points = { show: true, radius: 5 };
            peakSeries.color = 'red';
            data.push(peakSeries);
        });
        
        options = {
        		/*series: {
        			lines: { show: true, fill: true },
        			points: { show: true, radius: 2, symbol: "diamond" },
        			highlightColor: 2
        		},
        		*/
        		crosshair: { mode: "x" },
        		grid: { backgroundColor: 'white', hoverable: true, clickable: true },
                yaxis: { show: true },
                xaxis: { autoscaleMargin: 0.002, tickDecimals: 0 },
                selection: { mode: "x" }
            };
        if (data.length > 0)
	        if(diagram) {//just in case the plot div is not yet generated when user starts to click radio buttons
	        	/* re-initialize every parameter */
	        	diagram.unbind();
	        	selectedPoints = [];
				if(peakText)
					peakText.remove();
				if(submit)
					submit.remove();
				
				/* re-plot everything */
	            plot = $.plot(diagram, data, options);
	            addHoverEvent();
	           	plotOverview(data);
	           	addSelectionEvent(data);
	            addClickEvent();
	        }
	        else {
	        	alert('plot div has not been generated!');
	        }        
    }
    
    function addSelectionEvent(data) {
    	// connect the two plot
    	
    	//bind select event for main plot
    	diagram.bind("plotselected", function (event, ranges) {
    		/*
            // clamp the zooming to prevent eternal zoom
            if (ranges.xaxis.to - ranges.xaxis.from < 0.00001)
                ranges.xaxis.to = ranges.xaxis.from + 0.00001;
            if (ranges.yaxis.to - ranges.yaxis.from < 0.00001)
                ranges.yaxis.to = ranges.yaxis.from + 0.00001;
            */
            // do the zooming
            plot = $.plot(diagram, data,
                          $.extend(true, {}, options, {
                        	  xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to }
                          }));
            
            // don't fire event on the overview to prevent eternal loop
            overviewPlot.setSelection(ranges, true);
            
            if(selectedPoints.length > 0) {
            	for(var i=0; i<selectedPoints.length; ++i){
            		plot.highlight(selectedPoints[i].seriesIndex, selectedPoints[i].dataIndex);
            	}
            }

    	});
    	
    	//bind select event for overview plot
    	overview.bind("plotselected", function (event, ranges) {
            plot.setSelection(ranges);
        });
    }
    
    function addOverview(data) {
    	//generate div to contain overview plot
    	overview = $('<div id="overview" style="margin-top:50px;margin-right: auto;margin-left: auto"></div>').css( {
            position: 'relative',
            width: '200px',
            height: '100px'
        });
    	overview.appendTo("body");    	
    }
    
    function plotOverview(data) {	
    	//setup overview plot
    	var opts = {
    	        legend: { show: false },
    	        series: {
    	            lines: { show: true, lineWidth: 1 }
    	            //shadowSize: 0
    	        },
    	        xaxis: { ticks: 4 },
    	        yaxis: { ticks: 3, autoscaleMargin: 0.1 },
    	        grid: { backgroundColor:'white', color: "#999" },
    	        selection: { mode: "x" }
    	    };
    	
    	overviewPlot = $.plot(overview, data, opts); 	
    }
    
    function addClickEvent() {//click to select peak points
        diagram.bind("plotclick", function (event, pos, item) {
            if (item) {           	
            	if(selectedPoints.length > 0) {
            		var index = -1;
            		$.each(selectedPoints, function(i, val) {
            			if(val.datapoint[0]==item.datapoint[0] && val.datapoint[1]==item.datapoint[1])
            				index = i;
            		});
            		/*
            		for(var i=0; i<selectedPoints.length; ++i) {
            			if(selectedPoints[i][0]==item.datapoint[0] && selectedPoints[i][1]==item.datapoint[1])
            				index = i;
            		}
            		*/
            		if(index != -1) {            			
            			plot.unhighlight(item.series, item.datapoint);
            			overviewPlot.unhighlight(item.seriesIndex, item.dataIndex);
            			selectedPoints.splice(index, 1);          			
            		}
            		else if(selectedPoints.length < 2){ //only store 2 peak points
            			selectedPoints.push(item); //add only x, y to selectedPoints array
            			plot.highlight(item.series, item.datapoint);
            			overviewPlot.highlight(item.seriesIndex, item.dataIndex);
            		}
            	}
            	else { //selectedPoints.length == 0           		
        			selectedPoints.push(item); //add only x, y to selectedPoints array
        			plot.highlight(item.series, item.datapoint);
        			overviewPlot.highlight(item.seriesIndex, item.dataIndex);
            	}
            	//$("#clickdata").text("You clicked point " + item.dataIndex + " in " + item.series.label + ".");
				//alert(JSON.stringify(peakText));
				
				/* show peak selection in peakText div */
				if(peakText)
					peakText.remove();
				/* remove submit button if any */
				if(submit)
					submit.remove();
				if(selectedPoints.length > 0){
					peakText = $('<p id="selectedPoints" ></p>').css( {
			            position: 'relative',
						fontWeight: 'bold'
			        });
			    	peakText.appendTo(choice);
			    	/*$.each(selectedPoints, function(i, val) {
						var domStr = 'You have selected peak point (x: ' + val.datapoint[0] + ', y: '
						+ val.datapoint[1] + ') in ' + val.series.label + '.<br>'
						peakText.append(domStr);*/
			    	if(selectedPoints.length == 1){
						$.each(selectedPoints, function(i, val) {
							var domStr = 'You have picked starting point at (x: ' 
								+ val.datapoint[0] + ', y: '
								+ val.datapoint[1] + ') for a range, please pick the ending point.<br>';
							peakText.append(domStr);
						});
			    	}else if(selectedPoints.length == 2){
			    		var start, end;
			    		if(selectedPoints[0].dataIndex > selectedPoints[1].dataIndex){
			    			start = selectedPoints[1];
			    			end = selectedPoints[0];
			    		}else{
			    			start = selectedPoints[0];
			    			end = selectedPoints[1];
			    		}
						var domStr = 'You have picked a range starting from (x: ' 
								+ start.datapoint[0] + ', y: '
								+ start.datapoint[1] + ') to (x: ' 
								+ end.datapoint[0] + ', y: '+ end.datapoint[1] 
								+ '). Click "submit" button to send your request to server<br>';
						peakText.append(domStr);			    		
						
						/* show submit button when there are 2 peak points selected */

						if(selectedPoints.length == 2) {
							submit = $('<input id="submit" type="button" value="submit" >');
							submit.appendTo(choice);
							submit.click(doSubmit);
							
							//use setSelection to plot selection between 2 points, 
							//TBD
						}
			    	}
				}		
            }
        });
    }	
    
    /* submit the peak information to server */
    function doSubmit() {
    	/* data to be sent should follow fomat as:
    		data = {'channel': channelNo,
    				'selectedPoints': array of peak, e.g. [[1, 20], [5, 40]]
    		}
    	*/
    	var pdata = {//'channel': selectedPoints[0].series.label.substring(8),
    			'selectedPoints': [
    			          [selectedPoints[0].datapoint[0], selectedPoints[0].datapoint[1]], 
    			          [selectedPoints[1].datapoint[0], selectedPoints[1].datapoint[1]]
    			          ]
    			
    	};
    	
		$.ajax({
			type: 'POST',
			url: submitUrl,
			dataType: 'json',
			cache: false,
			data: {"data":JSON.stringify(pdata)}
		}).done(function(){
				alert('Peak Points sent to server!' /*+ JSON.stringify(msg)*/);
				plotAccordingToChoices();				
 		});
    }
    
    function showTooltip(x, y, contents) {
        $('<div id="tooltip">' + contents + '</div>').css( {
            position: 'absolute',
            display: 'none',
            top: y + 5,
            left: x + 5,
            border: '1px solid #fdd',
            padding: '2px',
            'background-color': '#fee',
            opacity: 0.80
        }).appendTo("body").fadeIn(200);
    }

    var previousPoint = null;
    function addHoverEvent() {
        diagram.bind("plothover", function (event, pos, item) {

            if (item) {
                if (previousPoint != item.dataIndex) {
                    previousPoint = item.dataIndex;
                    
                    $("#tooltip").remove();
                    var x = item.datapoint[0].toFixed(2),
                        y = item.datapoint[1].toFixed(2);
                    
                    showTooltip(item.pageX, item.pageY,
                    		"(" + x + ", " + y + ")");
                }
            }
            else {
                $("#tooltip").remove();
                previousPoint = null;            
            }

        });
    }

    
    getAndProcessData();
});