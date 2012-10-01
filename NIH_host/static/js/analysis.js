/* Main script for analysis.html page.
 *
 * .
 *
 */

$(function () {
	var dataurl = 'dsp'; //ajax call url
	
	var datasets; //store datasets
	var diagram; //store DOM object of plot div
	var overview; //store DOM object of overview plot
	var choice;  //store DOM objects of checkbox of channels
    var plot;  //store mian plot object will be returned by flot
    var options; //options settings for main plot
    var overviewPlot; ///store overview plot object will be returned by flot
    var peakText;// store DOM object of peak point
    var submit; //store DOM object of submit button
    
    var peaks = [];

	function getAndProcessData() { //issue ajax call and further process the data on sucess
		$.ajax({
			url: dataurl,
			cache: false,
			method: 'GET',
			dataType: 'json',
			success: onDataReceived
		});
	}
	
    /* 
	    data retrieved from server for n channels with 100 data each, ranged from (-100, 100)
	    should have the structure as below:
	    datasets.dspData = {
	                    "channel1": {
	                        'label': "channel1",
	                        'data': [array of [x, y]]
	                    },
	                    "channel2": {
	                        'label': "channel2",
	                        'data': [array of [x, y]]
	                    }
	                }
    */
    function onDataReceived(data) { //setup plot after retrieving data
        datasets = extractDatasets(data); //JSON {'dspData': datasets}         
		addChoices(); //add channel radio buttons
		addPlot();  //generate main plot div
		addOverview(); // generate overview plot div
		plotAccordingToChoices(); //plot diagram on generated div and generate overview

    }
	    
	function extractDatasets(data) {
		return data.dspData;
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
            position: 'relative',
            width: '800px',
            height: '400px',
            margin: 'auto',
            padding: '2px'
        });
    	diagram.appendTo("body");
    }

    
    function addChoices() {
        var i = 0;
        choice = $('<div id="choices">Show:</div>').css( {
            position: 'relative',
            cssFloat: 'left',
			fontWeight: 'bold',
			margin: 'auto',
            //textAlign: 'center'
        });
        var checked = 0;
        $.each(datasets, function(key, val){
        	val.color = i; //hard-code to assign a color to each channel choice
        	
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

        choice.find("input:checked").each(function () {
            var key = $(this).attr("value");

            if (key && datasets[key])
                data.push(datasets[key]);
        });
        options = {
        		series: {
        			lines: { show: true, fill: true },
        			points: { show: true }
        		},
        		//crosshair: { mode: "x" },
        		grid: { hoverable: true, clickable: true },
                yaxis: { show: true },
                xaxis: { autoscaleMargin: 0.002, tickDecimals: 0 },
                selection: { mode: "x" }
            };
        if (data.length > 0)
	        if(diagram) {//just in case the plot div is not yet generated when user starts to click radio buttons
	        	/* re-initialize every parameter */
	        	diagram.unbind();
	        	peaks = [];
				if(peakText)
					peakText.remove();
				if(submit)
					submit.remove();
	        	
				/* re-plot everything */
	            plot = $.plot(diagram, data, options);
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
    	});
    	
    	//bind select event for overview plot
    	overview.bind("plotselected", function (event, ranges) {
            plot.setSelection(ranges);
        });
    }
    
    function addOverview(data) {
    	//generate div to contain overview plot
    	overview = $('<div id="overview"></div>').css( {
            position: 'relative',
            width: '200px',
            height: '100px',
            margin: 'auto',
            padding: '1px'
        });
    	overview.appendTo("body");    	
    }
    
    function plotOverview(data) {	
    	//setup overview plot
    	var opts = {
    	        legend: { show: false },
    	        series: {
    	            lines: { show: true, lineWidth: 1 },
    	            shadowSize: 0
    	        },
    	        xaxis: { ticks: 4 },
    	        yaxis: { ticks: 3, autoscaleMargin: 0.1 },
    	        grid: { color: "#999" },
    	        selection: { mode: "x" }
    	    };
    	
    	overviewPlot = $.plot(overview, data, opts); 	
    }
    
    function addClickEvent() {//click to select peak points
        diagram.bind("plotclick", function (event, pos, item) {
            if (item) {           	
            	if(peaks.length > 0) {
            		var index = -1;
            		$.each(peaks, function(i, val) {
            			if(val.datapoint[0]==item.datapoint[0] && val.datapoint[1]==item.datapoint[1])
            				index = i;
            		});
            		/*
            		for(var i=0; i<peaks.length; ++i) {
            			if(peaks[i][0]==item.datapoint[0] && peaks[i][1]==item.datapoint[1])
            				index = i;
            		}
            		*/
            		if(index != -1) {            			
            			plot.unhighlight(item.series, item.datapoint);
            			peaks.splice(index, 1);          			
            		}
            		else if(peaks.length < 2){ //only store 2 peak points
            			peaks.push(item); //add only x, y to peaks array
            			plot.highlight(item.series, item.datapoint);	                   	
            		}
            	}
            	else { //peaks.length == 0           		
        			peaks.push(item); //add only x, y to peaks array
        			plot.highlight(item.series, item.datapoint);
            	}
            	//$("#clickdata").text("You clicked point " + item.dataIndex + " in " + item.series.label + ".");
				//alert(JSON.stringify(peakText));
				
				/* show peak selection in peakText div */
				if(peakText)
					peakText.remove();
				if(peaks.length > 0){
					peakText = $('<p id="peaks" ></p>').css( {
			            position: 'relative',
						fontWeight: 'bold'
			        });
			    	peakText.appendTo(choice);
					$.each(peaks, function(i, val) {
						var domStr = 'You clicked point (x: ' + val.datapoint[0] + ', y: '
						+ val.datapoint[1] + ') in ' + val.series.label + '.<br>'
						peakText.append(domStr);
					});
				}
				
				/* show submit button when there are 2 peak points selected */
				if(submit)
					submit.remove();
				if(peaks.length == 2) {
					submit = $('<input id="submit" type="button" value="submit" >');
					submit.appendTo(choice);
				}
            }
        });
    }
    
    getAndProcessData();
});