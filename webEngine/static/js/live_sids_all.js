$(function () {
    var url = $('#serverAddr').text(); //push url, need to change this to server's url, 
    var name = $('#name').text();
    var soundUrl = $('#soundServerAddr').text();
    var configUrl = 'config';

    var datasets; //store datasets
    var tempMonEnable = true;

    var CO2FormulaParams;

    function onDataReceived(data) { //setup plot after retrieving data
        //console.log(data);
        if (data.from == 'node') {
            if (name.trim() == data.data.address.trim())
                if (data.data.type == 'orientation') {
                    updateSimulation(data.data);
                    //updateACCChart(data.data);
                }
            if (data.data.type == 'SIDsRead') { //real data
                //console.log("CO2 raw reading");
                //console.log(data.data.value);
                updateDataTable(data.data.value);
            }
            if (data.data.type == 'SIDsSettings') {
                console.log("CO2 Settings");
                addSettings(data.data.value);
            }
            if (data.data.type == 'CO2FormulaParams') {
                console.log("CO2 Conversion parameters");
                //console.log(data.data.value);
                if (CO2FormulaParams == null) {
                    CO2FormulaParams = data.data.value;
                    //$.each(data.data.value, function (key, val) {
                    //    console.log(key, val);
                    //});

                } else {
                    //$.each(data.data.value, function (key, val) {
                    //    console.log(key, val);
                    //});
                }
            }
            if (data.data.type == 'CO2') {
                console.log("CO2 reading");
                var val = data.data.value;
                console.log(val);
                var point = chartHum.series[0].points[0];
                point.update(parseFloat(val), true);
            }
            if (data.data.type == 'Audio') {
                console.log("Audio Indicators");
                console.log(data.data.series);
                series = data.data.series;
                for (var i = 0; i < series.length; i++) {
                    val = (series[i] * 2 + 0.0) / 65536;
                    chart.series[0].addPoint(val, false, true);
                    chart.series[1].addPoint(-val, true, true);
                }
            }
            if (data.data.type == 'BodyTemp') { // update body temp chart
                if (tempMonEnable) {
                    slider.setValue(data.data.value);
                }
                console.log("temp");
                console.log(data.data.value);
            }
        } else if (data.from == 'central') {
            if (data.data.type == 'message') {
                alert(data.data.value);
                open('/', '_self', true);
            }
        }
        fakeCheckCondition(data.data);
    }

    jQuery.fn.center = function () {
        this.css("position", "absolute");
        this.css("top", ($(window).height() - this.height()) / 2 + $(window).scrollTop() + "px");
        this.css("left", ($(window).width() - this.width()) / 2 + $(window).scrollLeft() + "px");
        return this;
    }

    function updateSimulation(data) {
        //update simulation
        parent.lookAt(new THREE.Vector3(-data.value.x, -data.value.y, data.value.z));
        renderer.render(scene, camera);
    }

    function updateACCChart(data) {
        console.log(data.value.x, data.value.y, data.value.z);
        //update ACC chart
        chart.series[0].addPoint(data.value.z, true, true);
        /*
		chart.series[0].addPoint(data.value.x, false, true);
		chart.series[1].addPoint(data.value.y, false, true);
		chart.series[2].addPoint(data.value.z, true, true);
		*/
    }

    /**
     * SIDsRead value content: [hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp]
     * */
    function updateTempHumChart(data) {
        //update Temp chart
        //var point = chartTemp.series[0].points[0];
        //console.log()
        //point.update(data[9], true);
        slider.setValue(data[9]);

        //update Hum chart
        var point = chartHum.series[0].points[0];
        point.update(data[10], true);
        /*
		//check if alert need to be sent		
		if(alertSet == true){
			if(data[9] < tempRangeMin || data[9] > tempRangeMax || data[10] > humRangeMax){
				//send alert TBD
				var data = {
						'temp': data[9],
						'hum': data[10],
						'tempRangeMin': tempRangeMin,
						'tempRangeMax': tempRangeMax,
						'humRangeMin': humRangeMin,
						'humRangeMax': humRangeMax,
						'email': email
				};
				socket.send(JSON.stringify(data));
				//alert has been send wait enough time to start alert again
				alertSet = false;
				setTimeout(function(){
					alertSet = true;
				}, 60000); //60s delay
			}
		}
		*/
    }

    var init = function () {
        showSpinner();
        initLayout();
        initChart();
        initTemperatureChart();
        initHumidityChart();
        initAlert();
        initRiskState();
        initSoundMonitor();
        initSimulation();
        demoScriptInit();

        //window.addEventListener( 'orientationchange', onWindowResize, false );
    }

    var fakeItrv, gradual = 0.0;

    function demoScriptInit() {
        setTimeout(function () {
            //set temp to 37
            //			slider.setValue(37);

            //set CO2 to 0.05;
            //update Hum chart
            //			var point = chartHum.series[0].points[0];			
            //			point.update(0.05, true);


            //set risk level to Low
            toggleState('low');

            //fake breathing data
            fakeItrv = setInterval(function () {
                if (riskLvl == 2 && gradual < 0.7) {
                    gradual = gradual + 0.015;
                }
                var val = 0.7 - (Math.random() * 0.2) - gradual;
                if (val > 0.0) {
                    //	        		chart.series[0].addPoint(val, false, true);
                    //	        		chart.series[1].addPoint(-val, true, true);
                } else {
                    //	        		chart.series[0].addPoint(0, false, true);
                    //	        		chart.series[1].addPoint(0, true, true);
                    //clearInterval(fakeItrv);
                    //no sound over 5 sec
                    setTimeout(function () {
                        clearInterval(fakeItrv);
                        toggleState('emergency');
                    }, 5000)
                }
            }, 150);

        }, 2000);


    }

    var faceDownTime;

    function fakeCheckCondition(data) {
        //data is from acc
        if (data.type == "orientation" && data.value.z < -0.5 && riskLvl < 1) { // face down

            if (faceDownTime == null) {
                faceDownTime = new Date();
            } else if (new Date() - faceDownTime > 5000) {
                //toggle medium
                toggleState('medium');
                //reset faceDownTime
                faceDownTime = null;
                fakeTempInc = 0;
            }
        }

        // fake temp growing
        else if (riskLvl == 1 && slider.getValue() < 38.9) {
            tempMonEnable = false;
            setTimeout(function () { // grow temp by 14 over 5 sec
                if (slider.getValue() < 38.9)
                    slider.setValue(slider.getValue() + 2.8);
            }, 1000);
        } else if (riskLvl == 1 && chartHum.series[0].points[0].y < 4.0) {
            setTimeout(function () { //grow co2 to 4 over 5 sec
                if (chartHum.series[0].points[0].y < 4.0) {
                    var newVal = parseFloat((chartHum.series[0].points[0].y + 0.79).toFixed(2));
                    chartHum.series[0].points[0].update(newVal, true);
                }
            }, 1000);
        } else if (riskLvl == 1 && chartHum.series[0].points[0].y == 4.0) {
            toggleState('high');
        }

    }

    var riskLvl, stateLow, stateMedium, stateHigh, stateEmergency, itrVal;

    function initRiskState() {
        var riskDiv = $('<div id="riskLevel"/>')
            .css({
                marginTop: '50px',
                fontSize: 'normal'
            }).appendTo($('#alert'));
        var title = $('<div>Current sleep state:</div>').appendTo(riskDiv);
        //var stateDiv = $('<div id="state"/>').appendTo(riskDiv);

        //default state is no state
        //stateDiv.html('NONE').addClass("noLevel");

        stateLow = $('<div/>').text('low').attr('class', 'noLevel').appendTo(riskDiv);

        stateMedium = $('<div/>').text('medium').attr('class', 'noLevel').appendTo(riskDiv);

        stateHigh = $('<div/>').text('high').attr('class', 'noLevel').appendTo(riskDiv);

        stateEmergency = $('<div/>').text('emergency').attr('class', 'noLevel').appendTo(riskDiv);

        /*
		toggleState("low");
		toggleState("medium");
		toggleState("high");
		toggleState("emergency");
		*/
    }

    //state: low: 0; medium: 1; high: 2; emergency: 3
    function toggleState(state) {
        //turn off all state first
        if (itrVal != null)
            clearInterval(itrVal);
        stateLow.attr('class', 'noLevel');
        stateMedium.attr('class', 'noLevel');
        stateHigh.attr('class', 'noLevel');
        stateEmergency.attr('class', 'noLevel');

        if (state == "low") {
            stateLow.toggleClass('low', 1000);
            riskLvl = 0;
        } else if (state == "medium") {
            stateMedium.toggleClass('medium', 1000);
            riskLvl = 1;
        } else if (state == "high") {
            stateHigh.toggleClass('high', 1000);
            riskLvl = 2;
        } else if (state == "emergency") {
            stateEmergency.attr('class', 'high');
            itrVal = setInterval(function () {
                stateEmergency.addClass("emergency", 200, "linear", function () {
                    stateEmergency.removeClass("emergency", 1000, "linear");
                });
            }, 1210);
            riskLvl = 3;
            alertSound[0].play();

        }
    }

    var emailSetButton, emailSRmvButton;

    function initAlert() {
        $('<div style="display: block; margin-top: 10px; color: #3E576F">Alert Settings</div>')
            .appendTo($('#alert'));
        var emailDiv = $('<div id="emailSettings" />')
            .css({
                marginTop: '10px',
                fontSize: 'normal',
                display: 'block'
            }).appendTo($('#alert'));
        var emailLabel = $('<label for="email">Email to send for alert messages</label>');
        var emailTxt = $('<input type="text" name="email" \
				id="email" class="text ui-widget-content ui-corner-all">')
            .css({
                marginBottom: '0px'
            });
        emailSetButton = $('<button>Start Alert</button>').css({
            fontSize: 'smaller'
        }).button();
        emailSRmvButton = $('<button>Stop Alert</button>').button().hide();
        emailSetButton.click(startAlert);
        emailSRmvButton.click(stopAlert)
        emailDiv.append(emailLabel);
        emailDiv.append(emailTxt);
        emailDiv.append(emailSetButton);
        emailDiv.append(emailSRmvButton);
    }

    function stopAlert() {
        emailSRmvButton.hide();
        emailSetButton.show();
        alertSet = false;
    }
    var alertSet = false,
        email;

    function startAlert() {
        email = $('#email').val().trim();
        if (email != "" && isValidEmailAddress(email)) {
            emailSetButton.hide();
            emailSRmvButton.show();
            alertSet = true;
        } else {
            alert("It's not a valid Email format!");
        }
    }

    function isValidEmailAddress(emailAddress) {
        var pattern = new RegExp(/^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
        return pattern.test(emailAddress);
    };

    var alertSound;

    function initSoundMonitor() {
        alertSound = $('<audio src=' + soundUrl + ' />').appendTo('#alert');
        alertSound.bind('ended', function () {
            alertSound[0].play();
        });

        /*
		var player = $('<div><audio autoplay="autoplay" \
				src='+ soundUrl +' \
				controls="controls" /></div>').css({
				position: 'relative',
				display: 'table',
				top: '40%',
			    margin: 'auto'
				});
		$('#sound').append(player);
		*/


        //$('audio,video').mediaelementplayer();
    }

    function initLayout() {
        if (document.ontouchstart === undefined) { // touch device
            $('body').layout({
                closable: false,
                resizable: false,
                west__size: .70,
                west__childOptions: {
                    closable: false,
                    resizable: false,
                    south__size: .50,
                    center__childOptions: {
                        closable: false,
                        resizable: false,
                        west__size: .50
                    },
                    south__childOptions: {
                        closable: false,
                        resizable: false,
                        west__size: .50
                    }
                }
            });
        } else {
            $('#charts').attr('class', 'ui-layout-north');
            $('body').layout({
                closable: false,
                resizable: false,
                north__size: .70,
                north__childOptions: {
                    closable: false,
                    resizable: false,
                    south__size: .50,
                    center__childOptions: {
                        closable: false,
                        resizable: false,
                        west__size: .50
                    },
                    south__childOptions: {
                        closable: false,
                        resizable: false,
                        west__size: .50
                    }
                }
            });

        }
    }

    var chartContainer;
    var chart;
    var container = $("#acceleration");
    var total_points = 100;

    function initChart() {
        //chartContainer = $("<div id='chart' class='chart'/>").appendTo($("#sound"));
        options = {
            chart: {
                renderTo: 'sound',
                type: 'area',
                backgroundColor: 'transparent',
                animation: false
            },
            title: {
                text: 'Breathing'
            },
            credits: {
                href: "http://embedded.ece.uci.edu/",
                text: "" //"UCI Embedded Lab"
            },
            xAxis: {
                reversed: true,
                labels: {
                    enabled: false
                },
                lineWidth: 0,
                tickWidth: 0
            },
            yAxis: [{
                    title: {
                        text: '',
                        rotation: 0
                    },
                    labels: {
                        enabled: false
                    },
                    min: -1,
                    max: 1,
                    offset: 0,
                    lineWidth: 2,
                    plotLines: [{
                        value: 0,
                        width: 2,
                        color: '#C0D0E0'
                    }],
                    //height: 50
                }
                /*, 
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
            	
            }*/
            ],
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
                formatter: function () {
                    return this.y; //'<b>'+ this.series.yAxis.axisTitle.text +'</b>:'+ this.y;
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
        for (var i = 0; i < total_points; i++) {
            data.push(0);
        }
        options.series.push({
            name: 'X',
            data: data,
            color: '#909090'
        });
        data = [];
        for (var i = 0; i < total_points; i++) {
            data.push(0);
        }
        options.series.push({
            name: 'Y',
            data: data,
            color: '#909090'
        });
        /*
        options.series.push({
        	name: 'Y',
            data: data,
            yAxis: 1
        });
        options.series.push({
        	name: 'Z',
            data: data,
            yAxis: 2
        });*/
        chart = new Highcharts.Chart(options, function () {
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
        stats.domElement.style.float = 'left';
        stats.domElement.style.top = 'auto';
        //simContainer.append( stats.domElement );

        var info = $("<div/>").css({
            position: 'relative',
            //width: '10%',
            //cssFloat: 'center',
            color: '#3E576F',
            fontWeight: 'bold',
            margin: '0px 0px 0px 0px',
            textAlign: 'center'
        });
        //info.style.position = 'absolute';
        //info.style.top = '100px';
        //info.style.width = '100%';
        //info.style.textAlign = 'center';
        info.html("Sleep position");
        simContainer.append(info);

        camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 1000);
        camera.position.x = -350;
        camera.position.y = 0;
        camera.position.z = 0;
        // turn z to be parallel to gravity, facing up
        //camera.rotation = new THREE.Vector3( 0,0, -1.50, -1.57 ); // doesn't work on r59
        camera.rotation.y = -1.57;
        camera.rotation.z = -1.57;

        scene = new THREE.Scene();

        // Cube

        var materials = [];

        var geometry = new THREE.CubeGeometry(50, 50, 10);

        for (var i = 0; i < 6; i++) {

            geometry.faces[i].color.setHex((i / 100) * 0xffffff);

        }

        cube = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({
            vertexColors: THREE.FaceColors
        }));
        cube.position.x = 0; //150;

        //cube.lookAt(a);

        //cube.rotation.x = 1.57;//0.1;

        //cube.rotation.y = 0;//0.1;
        //cube.rotation.z = 0.5;//0.1;
        //scene.add( cube );


        // Get text from hash

        var theText = "SIDs node #1"; //TBD: node name should be retrieved from device

        var hash = document.location.hash.substr(1);

        if (hash.length !== 0) {

            theText = hash;

        }

        var text3d = new THREE.TextGeometry(theText, {

            size: 15,
            height: 3,
            curveSegments: 2,
            font: "helvetiker"

        });

        text3d.computeBoundingBox();
        var centerOffset = -0.5 * (text3d.boundingBox.max.x - text3d.boundingBox.min.x);

        var textMaterial = new THREE.MeshBasicMaterial({
            color: Math.random() * 0xffffff,
            overdraw: true
        });
        text = new THREE.Mesh(text3d, textMaterial);

        //text.position.x = centerOffset;
        text.position.y = 80;
        text.position.z = 20;
        text.rotation.x = 1.57;
        text.rotation.y = -1.57;
        text.rotation.z = 0;

        //LIGHTS

        hemiLight = new THREE.HemisphereLight(0xffffff, 0xffffff, 1);
        hemiLight.color.setHSL(0.6, 1, 0.6);
        hemiLight.groundColor.setHSL(0.095, 1, 0.75);
        hemiLight.position.set(0, 500, 0);
        scene.add(hemiLight);

        dirLight = new THREE.DirectionalLight(0xffffff, 1);
        dirLight.color.setHSL(0.1, 1, 0.95);
        dirLight.position.set(-1, 1.75, 1);
        dirLight.position.multiplyScalar(50);
        scene.add(dirLight);

        dirLight.castShadow = true;

        dirLight.shadowMapWidth = 2048;
        dirLight.shadowMapHeight = 2048;

        var d = 50;

        dirLight.shadowCameraLeft = -d;
        dirLight.shadowCameraRight = d;
        dirLight.shadowCameraTop = d;
        dirLight.shadowCameraBottom = -d;

        dirLight.shadowCameraFar = 3500;
        dirLight.shadowBias = -0.0001;
        dirLight.shadowDarkness = 0.35;
        //dirLight.shadowCameraVisible = true;

        var directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
        directionalLight.position.set(0, 0, 1).normalize();
        scene.add(directionalLight);

        parent = new THREE.Object3D();

        // add human 3D obj
        var manager = new THREE.LoadingManager();
        var loader = new THREE.OBJMTLLoader(); //OBJLoader( manager );
        loader.load('static/css/objs/baby.obj', 'static/css/objs/baby.mtl', function (object) {
            /*
			object.traverse( function ( child ) {

				if ( child instanceof THREE.Mesh ) {

					child.material = new THREE.MeshBasicMaterial( { color: 0xFFDFC4 } );

				}

			} );*/
            object.position.z = -90;
            object.position.y = -200;
            object.position.x = -170;
            object.scale.set(0.8, 0.8, 0.8);
            object.rotation.y = -0.5;
            parent.add(object);
            //console.log(object);
        });
        //parent.add( cube );
        //parent.add( text );
        //parent.lookAt(new THREE.Vector3(0,0,0));
        //parent.rotation.x = 1.57
        //alert(document.width);
        /*
		if(simContainer.width()<250){
			parent.scale.set(0.5,0.5,0.5);
		}
		*/

        scene.add(parent);



        renderer = new THREE.WebGLRenderer();
        renderer.setSize(simContainer.width(), container.height() - 100);

        simContainer.append(renderer.domElement);

        $(window).resize(function (e) {
            console.log(simContainer.width());
            renderer.setSize(simContainer.width(), container.height() - 100);
            render();
            //animate();
        });
        //render();
        renderer.render(scene, camera);

        animate();
    }

    function onWindowResize() {
        //location.reload();

        //windowHalfX = window.innerWidth / 2;
        //windowHalfY = window.innerHeight / 2;

        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();

        renderer.setSize(window.innerWidth, window.innerHeight);

    }

    function animate() {

        requestAnimationFrame(animate);

        render();
        //stats.update();

    }

    function render() {

        //parent.rotation.y += (Math.random()-0.5)*0.1;
        //parent.rotation.x += (Math.random()-0.5)*0.3;
        renderer.render(scene, camera);

    }

    var chartTemp, slider, tempRangeMin = 36,
        tempRangeMax = 38;

    function initTemperatureChart() {
        tempContainer = $("<div id='temperature'/>").appendTo($('#temperature'));;
        var info = $("<div/>").css({
            position: 'relative',
            //width: '10%',
            //cssFloat: 'center',
            color: '#3E576F',
            fontWeight: 'bold',
            margin: '0px 0px 0px 0px',
            textAlign: 'center',
            marginTop: '10px'
        });
        //info.style.position = 'absolute';
        //info.style.top = '100px';
        //info.style.width = '100%';
        //info.style.textAlign = 'center';
        info.html("Body temperature");
        info.appendTo(tempContainer);
        //console.log(info);

        var chartTempDiv = $('<div id="chartTemp"/>')
            .css({
                textAlign: 'center',
                marginTop: '50px'
            });
        chartTempDiv.appendTo($('#temperature'));
        var jsonModel = {
            "Active": true,
            "BreakEventsBubbling": false,
            "CssClass": {
                "SelectedCssClass": "none"
            },
            "Fill": null,
            "JSBindingsText": null,
            "Name": "Instrument",
            "RecalculateAll": false,
            "Smooth": true,
            "Stroke": null,
            "Style": "",
            "ToolTipValue": null,
            "Visible": true,
            "Elements": [{
                "__type": "RoundedRectangle:#PerpetuumSoft.Instrumentation.Model",
                "Active": true,
                "BreakEventsBubbling": false,
                "CssClass": {
                    "SelectedCssClass": "none"
                },
                "Fill": {
                    "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                    "Color": {
                        "knownColor": 164,
                        "name": null,
                        "state": 1,
                        "value": 0
                    }
                },
                "JSBindingsText": null,
                "Name": "RoundedRectangle1",
                "RecalculateAll": false,
                "Smooth": true,
                "Stroke": {
                    "__type": "SimpleStroke:#PerpetuumSoft.Framework.Drawing",
                    "Width": 1,
                    "Color": {
                        "knownColor": 35,
                        "name": null,
                        "state": 1,
                        "value": 0
                    },
                    "DashLenght": 5,
                    "DotLenght": 1,
                    "SpaceLenght": 2,
                    "Style": 1
                },
                "Style": "Default",
                "ToolTipValue": null,
                "Visible": true,
                "Center": {
                    "Height": 475,
                    "Length": 561.8051263561058,
                    "Rotation": 1.0074800653029286,
                    "Width": 300,
                    "X": 300,
                    "Y": 475
                },
                "Size": {
                    "Height": 850,
                    "Length": 939.4147114027968,
                    "Rotation": 1.1309537439791604,
                    "Width": 400,
                    "X": 400,
                    "Y": 850
                },
                "Angle": 0,
                "Radius": 50
            }, {
                "__type": "Guide:#PerpetuumSoft.Instrumentation.Model",
                "Active": true,
                "BreakEventsBubbling": false,
                "CssClass": {
                    "SelectedCssClass": "none"
                },
                "Fill": null,
                "JSBindingsText": null,
                "Name": "Guide1",
                "RecalculateAll": false,
                "Smooth": true,
                "Stroke": null,
                "Style": "",
                "ToolTipValue": null,
                "Visible": true,
                "Elements": [{
                    "__type": "Scale:#PerpetuumSoft.Instrumentation.Model",
                    "Active": true,
                    "BreakEventsBubbling": false,
                    "CssClass": {
                        "SelectedCssClass": "none"
                    },
                    "Fill": null,
                    "JSBindingsText": null,
                    "Name": "Scale2",
                    "RecalculateAll": false,
                    "Smooth": true,
                    "Stroke": null,
                    "Style": "",
                    "ToolTipValue": null,
                    "Visible": true,
                    "Elements": [{
                        "__type": "NumericLabels:#PerpetuumSoft.Instrumentation.Model",
                        "Active": true,
                        "BreakEventsBubbling": false,
                        "CssClass": {
                            "SelectedCssClass": "none"
                        },
                        "Fill": null,
                        "JSBindingsText": null,
                        "Name": "NumericLabels2",
                        "RecalculateAll": false,
                        "Smooth": true,
                        "Stroke": null,
                        "Style": "LabelsStyle",
                        "ToolTipValue": null,
                        "Visible": true,
                        "Colorizer": {
                            "__type": "SingleColorColorizer:#PerpetuumSoft.Instrumentation.Model.Drawing",
                            "Color": {
                                "knownColor": 35,
                                "name": null,
                                "state": 1,
                                "value": 0
                            }
                        },
                        "Distance": 127.13749999999999,
                        "Dock": 0,
                        "MaxLimitWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 2,
                            "Value": 100
                        },
                        "MinLimitWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 2,
                            "Value": 0
                        },
                        "OriginWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 0,
                            "Value": 0
                        },
                        "Padding": 0,
                        "Font": {
                            "Bold": 0,
                            "FamilyName": "Microsoft Sans Serif",
                            "Italic": 0,
                            "Size": 8,
                            "Strikeout": 0,
                            "Underline": 0
                        },
                        "Format": {
                            "CurrencyNegativePattern": 0,
                            "CurrencyPositivePattern": 0,
                            "CurrencySymbol": "$",
                            "DateSeparator": ".",
                            "DecimalPlaces": 2,
                            "DecimalSeparator": ".",
                            "FormatMask": "####0.##",
                            "FormatStringMask": "####0.##",
                            "FormatStyle": 6,
                            "GroupSeparator": " ",
                            "NumberNegativePattern": 0,
                            "PercentNegativePattern": 0,
                            "PercentPositivePattern": 0,
                            "UseCultureSettings": true,
                            "UseGroupSeparator": true
                        },
                        "Formula": "",
                        "ItemMargins": {},
                        "OddLabelsDistance": 0,
                        "Position": 1,
                        "ShowSuperposableLabels": true,
                        "TextAlignment": 1,
                        "TextAngle": 0,
                        "TextRotationMode": 0,
                        "Divisions": 10,
                        "StepWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 0,
                            "Value": 0
                        },
                        "UseRoundValues": true
                    }, {
                        "__type": "Ticks:#PerpetuumSoft.Instrumentation.Model",
                        "Active": true,
                        "BreakEventsBubbling": false,
                        "CssClass": {
                            "SelectedCssClass": "none"
                        },
                        "Fill": null,
                        "JSBindingsText": null,
                        "Name": "Ticks2",
                        "RecalculateAll": false,
                        "Smooth": true,
                        "Stroke": {
                            "__type": "SimpleStroke:#PerpetuumSoft.Framework.Drawing",
                            "Width": 1,
                            "Color": {
                                "knownColor": 164,
                                "name": null,
                                "state": 1,
                                "value": 0
                            },
                            "DashLenght": 5,
                            "DotLenght": 1,
                            "SpaceLenght": 2,
                            "Style": 1
                        },
                        "Style": "Default",
                        "ToolTipValue": null,
                        "Visible": true,
                        "Colorizer": {
                            "__type": "SectionsColorizer:#PerpetuumSoft.Instrumentation.Model.Drawing",
                            "ColorSections": [{
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 166,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 166,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.23062015503875968
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 104,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.4825581395348838
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 166,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.59496124031007747
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 141,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 1
                            }]
                        },
                        "Distance": 62.071875,
                        "Dock": 0,
                        "MaxLimitWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 2,
                            "Value": 100
                        },
                        "MinLimitWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 2,
                            "Value": 0
                        },
                        "OriginWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 0,
                            "Value": 0
                        },
                        "Padding": 0,
                        "Divisions": 10,
                        "StepWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 1,
                            "Value": 2
                        },
                        "SubDivisions": 5,
                        "SubTicksPosition": 0,
                        "UseDescreteValues": false,
                        "UseRoundValues": false,
                        "Length": 15.625,
                        "SubLength": 9.375
                    }],
                    "Colorizer": null,
                    "Maximum": 107.6,
                    "Minimum": 77,
                    "Reverse": false
                }, {
                    "__type": "Scale:#PerpetuumSoft.Instrumentation.Model",
                    "Active": true,
                    "BreakEventsBubbling": false,
                    "CssClass": {
                        "SelectedCssClass": "none"
                    },
                    "Fill": null,
                    "JSBindingsText": null,
                    "Name": "Scale1",
                    "RecalculateAll": false,
                    "Smooth": true,
                    "Stroke": null,
                    "Style": "",
                    "ToolTipValue": null,
                    "Visible": true,
                    "Elements": [{
                        "__type": "NumericLabels:#PerpetuumSoft.Instrumentation.Model",
                        "Active": true,
                        "BreakEventsBubbling": false,
                        "CssClass": {
                            "SelectedCssClass": "none"
                        },
                        "Fill": null,
                        "JSBindingsText": null,
                        "Name": "NumericLabels1",
                        "RecalculateAll": false,
                        "Smooth": false,
                        "Stroke": null,
                        "Style": "LabelsStyle",
                        "ToolTipValue": null,
                        "Visible": true,
                        "Colorizer": {
                            "__type": "SingleColorColorizer:#PerpetuumSoft.Instrumentation.Model.Drawing",
                            "Color": {
                                "knownColor": 35,
                                "name": null,
                                "state": 1,
                                "value": 0
                            }
                        },
                        "Distance": -122.8745122189264,
                        "Dock": 0,
                        "MaxLimitWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 2,
                            "Value": 100
                        },
                        "MinLimitWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 2,
                            "Value": 0
                        },
                        "OriginWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 0,
                            "Value": 0
                        },
                        "Padding": 0,
                        "Font": {
                            "Bold": 0,
                            "FamilyName": "Microsoft Sans Serif",
                            "Italic": 0,
                            "Size": 8,
                            "Strikeout": 0,
                            "Underline": 0
                        },
                        "Format": {
                            "CurrencyNegativePattern": 0,
                            "CurrencyPositivePattern": 0,
                            "CurrencySymbol": "$",
                            "DateSeparator": ".",
                            "DecimalPlaces": 2,
                            "DecimalSeparator": ".",
                            "FormatMask": "",
                            "FormatStringMask": "",
                            "FormatStyle": 0,
                            "GroupSeparator": " ",
                            "NumberNegativePattern": 0,
                            "PercentNegativePattern": 0,
                            "PercentPositivePattern": 0,
                            "UseCultureSettings": true,
                            "UseGroupSeparator": true
                        },
                        "Formula": "",
                        "ItemMargins": {},
                        "OddLabelsDistance": 0,
                        "Position": 1,
                        "ShowSuperposableLabels": true,
                        "TextAlignment": 1,
                        "TextAngle": 0,
                        "TextRotationMode": 0,
                        "Divisions": 10,
                        "StepWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 1,
                            "Value": 1
                        },
                        "UseRoundValues": true
                    }, {
                        "__type": "Ticks:#PerpetuumSoft.Instrumentation.Model",
                        "Active": true,
                        "BreakEventsBubbling": false,
                        "CssClass": {
                            "SelectedCssClass": "none"
                        },
                        "Fill": null,
                        "JSBindingsText": null,
                        "Name": "Ticks1",
                        "RecalculateAll": false,
                        "Smooth": true,
                        "Stroke": {
                            "__type": "SimpleStroke:#PerpetuumSoft.Framework.Drawing",
                            "Width": 1,
                            "Color": {
                                "knownColor": 164,
                                "name": null,
                                "state": 1,
                                "value": 0
                            },
                            "DashLenght": 5,
                            "DotLenght": 1,
                            "SpaceLenght": 2,
                            "Style": 1
                        },
                        "Style": "Default",
                        "ToolTipValue": null,
                        "Visible": true,
                        "Colorizer": {
                            "__type": "SectionsColorizer:#PerpetuumSoft.Instrumentation.Model.Drawing",
                            "ColorSections": [{
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 166,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 166,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.22480620155038761
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 104,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.47093023255813954
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 166,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.57751937984496127
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 141,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 1
                            }]
                        },
                        "Distance": -79.584548438149653,
                        "Dock": 0,
                        "MaxLimitWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 2,
                            "Value": 100
                        },
                        "MinLimitWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 2,
                            "Value": 0
                        },
                        "OriginWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 0,
                            "Value": 0
                        },
                        "Padding": 0,
                        "Divisions": 10,
                        "StepWrapper": {
                            "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                            "Kind": 1,
                            "Value": 1
                        },
                        "SubDivisions": 5,
                        "SubTicksPosition": 2,
                        "UseDescreteValues": false,
                        "UseRoundValues": false,
                        "Length": 21.875,
                        "SubLength": 9.375
                    }, {
                        "__type": "Slider:#PerpetuumSoft.Instrumentation.Model",
                        "Active": true,
                        "BreakEventsBubbling": false,
                        "CssClass": {
                            "SelectedCssClass": "none"
                        },
                        "Fill": null,
                        "JSBindingsText": null,
                        "Name": "Slider1",
                        "RecalculateAll": false,
                        "Smooth": true,
                        "Stroke": null,
                        "Style": "",
                        "ToolTipValue": null,
                        "Visible": true,
                        "Elements": [{
                            "__type": "Rectangle:#PerpetuumSoft.Instrumentation.Model",
                            "Active": true,
                            "BreakEventsBubbling": false,
                            "CssClass": {
                                "SelectedCssClass": "none"
                            },
                            "Fill": {
                                "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                                "Color": {
                                    "knownColor": 0,
                                    "name": null,
                                    "state": 2,
                                    "value": 4291486975
                                }
                            },
                            "JSBindingsText": "this.setCenter(this.getInstrument().getByName(\"Slider1\").getPosition(-165.625));\u000a",
                            "Name": "Rectangle1",
                            "RecalculateAll": false,
                            "Smooth": true,
                            "Stroke": {
                                "__type": "SimpleStroke:#PerpetuumSoft.Framework.Drawing",
                                "Width": 1,
                                "Color": {
                                    "knownColor": 35,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "DashLenght": 5,
                                "DotLenght": 1,
                                "SpaceLenght": 2,
                                "Style": 1
                            },
                            "Style": "LabelBack",
                            "ToolTipValue": null,
                            "Visible": true,
                            "Center": {
                                "Height": 125.00000000000004,
                                "Length": 183.52558575032523,
                                "Rotation": 0.74926931288467336,
                                "Width": 134.37499999999989,
                                "X": 134.37499999999989,
                                "Y": 125.00000000000004
                            },
                            "Size": {
                                "Height": 59.375,
                                "Length": 170.07581030234724,
                                "Rotation": 0.35662013595143194,
                                "Width": 159.375,
                                "X": 159.375,
                                "Y": 59.375
                            },
                            "Angle": 0
                        }, {
                            "__type": "Label:#PerpetuumSoft.Instrumentation.Model",
                            "Active": true,
                            "BreakEventsBubbling": false,
                            "CssClass": {
                                "SelectedCssClass": "none"
                            },
                            "Fill": {
                                "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                                "Color": {
                                    "knownColor": 35,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                }
                            },
                            "JSBindingsText": "this.setText((PerfectWidgets.Framework.Utilities.BuiltIn.netFormat('##0.0',this.getInstrument().getByName('Slider1').getAnimationValue())+\" C\"));\u000athis.setCenter(this.getInstrument().getByName(\"Slider1\").getPosition(-153.125));\u000a",
                            "Name": "Label1",
                            "RecalculateAll": false,
                            "Smooth": false,
                            "Stroke": null,
                            "Style": "CurrentValueStyle",
                            "ToolTipValue": null,
                            "Visible": true,
                            "Center": {
                                "Height": 125.00000000000004,
                                "Length": 192.86592655261836,
                                "Rotation": 0.70511134811443243,
                                "Width": 146.87499999999989,
                                "X": 146.87499999999989,
                                "Y": 125.00000000000004
                            },
                            "Size": {
                                "Height": 56.250000000000114,
                                "Length": 183.81801462315931,
                                "Rotation": 0.31099828060554152,
                                "Width": 175,
                                "X": 175,
                                "Y": 56.250000000000114
                            },
                            "Angle": 0,
                            "Font": {
                                "Bold": 0,
                                "FamilyName": "Microsoft Sans Serif",
                                "Italic": 0,
                                "Size": 8,
                                "Strikeout": 0,
                                "Underline": 0
                            },
                            "Margins": {},
                            "Text": "42.5 C",
                            "TextAlign": 32
                        }, {
                            "__type": "Rectangle:#PerpetuumSoft.Instrumentation.Model",
                            "Active": true,
                            "BreakEventsBubbling": false,
                            "CssClass": {
                                "SelectedCssClass": "none"
                            },
                            "Fill": {
                                "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                                "Color": {
                                    "knownColor": 0,
                                    "name": null,
                                    "state": 2,
                                    "value": 4291486975
                                }
                            },
                            "JSBindingsText": "this.setCenter(this.getInstrument().getByName(\"Slider1\").getPosition(165.625));\u000a",
                            "Name": "Rectangle2",
                            "RecalculateAll": false,
                            "Smooth": true,
                            "Stroke": {
                                "__type": "SimpleStroke:#PerpetuumSoft.Framework.Drawing",
                                "Width": 1,
                                "Color": {
                                    "knownColor": 35,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "DashLenght": 5,
                                "DotLenght": 1,
                                "SpaceLenght": 2,
                                "Style": 1
                            },
                            "Style": "LabelBack",
                            "ToolTipValue": null,
                            "Visible": true,
                            "Center": {
                                "Height": 124.99999999999996,
                                "Length": 482.1116474687164,
                                "Rotation": 0.26227253633223535,
                                "Width": 465.62499999999989,
                                "X": 465.62499999999989,
                                "Y": 124.99999999999996
                            },
                            "Size": {
                                "Height": 59.375,
                                "Length": 170.07581030234724,
                                "Rotation": 0.35662013595143194,
                                "Width": 159.375,
                                "X": 159.375,
                                "Y": 59.375
                            },
                            "Angle": 0
                        }, {
                            "__type": "Label:#PerpetuumSoft.Instrumentation.Model",
                            "Active": true,
                            "BreakEventsBubbling": false,
                            "CssClass": {
                                "SelectedCssClass": "none"
                            },
                            "Fill": {
                                "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                                "Color": {
                                    "knownColor": 35,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                }
                            },
                            "JSBindingsText": "this.setCenter(this.getInstrument().getByName(\"Slider1\").getPosition(162.5));\u000athis.setText((PerfectWidgets.Framework.Utilities.BuiltIn.netFormat('##0.0',(((this.getInstrument().getByName('Slider1').getAnimationValue()*9)\/5)+32))+\" F\"));\u000a",
                            "Name": "Label2",
                            "RecalculateAll": false,
                            "Smooth": false,
                            "Stroke": null,
                            "Style": "CurrentValueStyle",
                            "ToolTipValue": null,
                            "Visible": true,
                            "Center": {
                                "Height": 124.99999999999996,
                                "Length": 479.09419741841987,
                                "Rotation": 0.26396372362570453,
                                "Width": 462.49999999999989,
                                "X": 462.49999999999989,
                                "Y": 124.99999999999996
                            },
                            "Size": {
                                "Height": 56.25,
                                "Length": 195.75574704207281,
                                "Rotation": 0.2914567944778671,
                                "Width": 187.5,
                                "X": 187.5,
                                "Y": 56.25
                            },
                            "Angle": 0,
                            "Font": {
                                "Bold": 0,
                                "FamilyName": "Microsoft Sans Serif",
                                "Italic": 0,
                                "Size": 8,
                                "Strikeout": 0,
                                "Underline": 0
                            },
                            "Margins": {},
                            "Text": "108.5 F",
                            "TextAlign": 32
                        }, {
                            "__type": "LinearLevel:#PerpetuumSoft.Instrumentation.Model",
                            "Active": true,
                            "BreakEventsBubbling": false,
                            "CssClass": {
                                "SelectedCssClass": "none"
                            },
                            "Fill": null,
                            "JSBindingsText": null,
                            "Name": "LinearLevel2",
                            "RecalculateAll": false,
                            "Smooth": true,
                            "Stroke": null,
                            "Style": "",
                            "ToolTipValue": null,
                            "Visible": true,
                            "Colorizer": null,
                            "Distance": 0,
                            "Dock": 0,
                            "MaxLimitWrapper": {
                                "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                                "Kind": 0,
                                "Value": 0
                            },
                            "MinLimitWrapper": {
                                "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                                "Kind": 0,
                                "Value": 0
                            },
                            "OriginWrapper": {
                                "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                                "Kind": 0,
                                "Value": 0
                            },
                            "Padding": 0,
                            "ValueWrapper": {
                                "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                                "Kind": 0,
                                "Value": 0
                            },
                            "Colors": [],
                            "Divisions": 0,
                            "DivisionsStroke": null,
                            "EndColor": {
                                "knownColor": 150,
                                "name": null,
                                "state": 1,
                                "value": 0
                            },
                            "StartColor": {
                                "knownColor": 150,
                                "name": null,
                                "state": 1,
                                "value": 0
                            },
                            "Effect3D": 1,
                            "EndCap": 1,
                            "PocketRadius": 37.5,
                            "ShowAsThermometer": true,
                            "StartCap": 1,
                            "Width": 31.25
                        }, {
                            "__type": "LinearLevel:#PerpetuumSoft.Instrumentation.Model",
                            "Active": true,
                            "BreakEventsBubbling": false,
                            "CssClass": {
                                "SelectedCssClass": "none"
                            },
                            "Fill": null,
                            "JSBindingsText": "this.setValue(this.getInstrument().getByName('Slider1').getAnimationValue());\u000a",
                            "Name": "LinearLevel1",
                            "RecalculateAll": false,
                            "Smooth": true,
                            "Stroke": null,
                            "Style": "",
                            "ToolTipValue": null,
                            "Visible": true,
                            "Colorizer": null,
                            "Distance": 0,
                            "Dock": 0,
                            "MaxLimitWrapper": {
                                "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                                "Kind": 0,
                                "Value": 0
                            },
                            "MinLimitWrapper": {
                                "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                                "Kind": 0,
                                "Value": 0
                            },
                            "OriginWrapper": {
                                "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                                "Kind": 0,
                                "Value": 0
                            },
                            "Padding": 0,
                            "ValueWrapper": {
                                "__type": "SmartValueWrapper:#PerpetuumSoft.Instrumentation.Model",
                                "Kind": 1,
                                "Value": 42.5
                            },
                            "Colors": [{
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 166,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.2
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 105,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.25
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 166,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 0.55
                            }, {
                                "__type": "ColorSection:#PerpetuumSoft.Instrumentation.Model.Drawing",
                                "Color": {
                                    "knownColor": 141,
                                    "name": null,
                                    "state": 1,
                                    "value": 0
                                },
                                "Portion": 1
                            }],
                            "Divisions": 0,
                            "DivisionsStroke": {
                                "__type": "EmptyStroke:#PerpetuumSoft.Framework.Drawing",
                                "Width": 0
                            },
                            "EndColor": {
                                "knownColor": 141,
                                "name": null,
                                "state": 1,
                                "value": 0
                            },
                            "StartColor": {
                                "knownColor": 166,
                                "name": null,
                                "state": 1,
                                "value": 0
                            },
                            "Effect3D": 0,
                            "EndCap": 1,
                            "PocketRadius": 37.5,
                            "ShowAsThermometer": true,
                            "StartCap": 1,
                            "Width": 31.25
                        }],
                        "MaxLimit": {
                            "Kind": 0,
                            "Value": 0
                        },
                        "MinLimit": {
                            "Kind": 0,
                            "Value": 0
                        },
                        "Step": 0,
                        "Value": 42.5,
                        "MarkerPoint": {
                            "Height": 125,
                            "Length": 324.99999999999989,
                            "Rotation": 0.39479111969976166,
                            "Width": 299.99999999999989,
                            "X": 299.99999999999989,
                            "Y": 125
                        }
                    }],
                    "Colorizer": null,
                    "Maximum": 42,
                    "Minimum": 25,
                    "Reverse": false
                }],
                "Margins": {},
                "Align": 0,
                "EndPoint": {
                    "Height": 125,
                    "Length": 325,
                    "Rotation": 0.39479111969976149,
                    "Width": 300,
                    "X": 300,
                    "Y": 125
                },
                "GuideDirection": 1,
                "StartPoint": {
                    "Height": 793.75,
                    "Length": 848.55115491053334,
                    "Rotation": 1.2094394553936687,
                    "Width": 300,
                    "X": 300,
                    "Y": 793.75
                }
            }, {
                "__type": "TrialLabel:#PerpetuumSoft.Instrumentation.Model",
                "Active": true,
                "BreakEventsBubbling": false,
                "CssClass": {
                    "SelectedCssClass": "none"
                },
                "Fill": {
                    "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                    "Color": {
                        "knownColor": 0,
                        "name": null,
                        "state": 2,
                        "value": 4285406750
                    }
                },
                "JSBindingsText": null,
                "Name": "",
                "RecalculateAll": false,
                "Smooth": true,
                "Stroke": {
                    "__type": "EmptyStroke:#PerpetuumSoft.Framework.Drawing",
                    "Width": 0
                },
                "Style": "",
                "ToolTipValue": null,
                "Visible": true,
                "Center": {
                    "Height": 475,
                    "Length": 589.19178541456267,
                    "Rotation": 0.9376825149849477,
                    "Width": 348.6,
                    "X": 348.6,
                    "Y": 475
                },
                "Size": {
                    "Height": 697.2,
                    "Length": 1178.3835708291254,
                    "Rotation": 0.63311381180994886,
                    "Width": 950,
                    "X": 950,
                    "Y": 697.2
                },
                "Angle": -90,
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Comic Sans MS",
                    "Italic": 0,
                    "Size": 8,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Margins": {},
                "Text": "",
                "TextAlign": 512
            }, {
                "__type": "Rectangle:#PerpetuumSoft.Instrumentation.Model",
                "Active": false,
                "BreakEventsBubbling": false,
                "CssClass": {
                    "SelectedCssClass": "none"
                },
                "Fill": {
                    "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                    "Color": {
                        "knownColor": 0,
                        "name": null,
                        "state": 2,
                        "value": 16711680
                    }
                },
                "JSBindingsText": null,
                "Name": "Cap",
                "RecalculateAll": false,
                "Smooth": true,
                "Stroke": null,
                "Style": "",
                "ToolTipValue": null,
                "Visible": true,
                "Center": {
                    "Height": 475,
                    "Length": 561.8051263561058,
                    "Rotation": 1.0074800653029286,
                    "Width": 300,
                    "X": 300,
                    "Y": 475
                },
                "Size": {
                    "Height": 950,
                    "Length": 1123.6102527122116,
                    "Rotation": 1.0074800653029286,
                    "Width": 600,
                    "X": 600,
                    "Y": 950
                },
                "Angle": 0
            }],
            "Enabled": true,
            "Focused": false,
            "GridStep": 50,
            "IsFixed": false,
            "MeasureUnit": {},
            "ShadowDX": 0,
            "ShadowDY": 0,
            "ShadowFill": null,
            "ShowGrid": true,
            "Size": {
                "Height": 950,
                "Length": 1123.6102527122116,
                "Rotation": 1.0074800653029286,
                "Width": 600,
                "X": 600,
                "Y": 950
            },
            "SnapToGrid": false,
            "StubBevel": null,
            "Styles": [{
                "__type": "Style:#PerpetuumSoft.Instrumentation.Styles",
                "Fill": null,
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Microsoft Sans Serif",
                    "Italic": 0,
                    "Size": 7,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Image": null,
                "Name": "LabelsStyle",
                "Stroke": null
            }, {
                "__type": "Style:#PerpetuumSoft.Instrumentation.Styles",
                "Fill": {
                    "__type": "LinearGradientFill:#PerpetuumSoft.Framework.Drawing",
                    "Angle": 0,
                    "Colors": [{
                        "__type": "GradientColor:#PerpetuumSoft.Framework.Drawing",
                        "Color": {
                            "knownColor": 141,
                            "name": null,
                            "state": 1,
                            "value": 0
                        },
                        "Portion": 0
                    }, {
                        "__type": "GradientColor:#PerpetuumSoft.Framework.Drawing",
                        "Color": {
                            "knownColor": 108,
                            "name": null,
                            "state": 1,
                            "value": 0
                        },
                        "Portion": 1
                    }],
                    "EndColor": {
                        "knownColor": 108,
                        "name": null,
                        "state": 1,
                        "value": 0
                    },
                    "StartColor": {
                        "knownColor": 141,
                        "name": null,
                        "state": 1,
                        "value": 0
                    }
                },
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Microsoft Sans Serif",
                    "Italic": 0,
                    "Size": 10,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Image": null,
                "Name": "ActiveStyle",
                "Stroke": null
            }, {
                "__type": "Style:#PerpetuumSoft.Instrumentation.Styles",
                "Fill": {
                    "__type": "LinearGradientFill:#PerpetuumSoft.Framework.Drawing",
                    "Angle": 0,
                    "Colors": [{
                        "__type": "GradientColor:#PerpetuumSoft.Framework.Drawing",
                        "Color": {
                            "knownColor": 74,
                            "name": null,
                            "state": 1,
                            "value": 0
                        },
                        "Portion": 0
                    }, {
                        "__type": "GradientColor:#PerpetuumSoft.Framework.Drawing",
                        "Color": {
                            "knownColor": 52,
                            "name": null,
                            "state": 1,
                            "value": 0
                        },
                        "Portion": 1
                    }],
                    "EndColor": {
                        "knownColor": 52,
                        "name": null,
                        "state": 1,
                        "value": 0
                    },
                    "StartColor": {
                        "knownColor": 74,
                        "name": null,
                        "state": 1,
                        "value": 0
                    }
                },
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Microsoft Sans Serif",
                    "Italic": 0,
                    "Size": 10,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Image": null,
                "Name": "InactiveStyle",
                "Stroke": null
            }, {
                "__type": "Style:#PerpetuumSoft.Instrumentation.Styles",
                "Fill": {
                    "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                    "Color": {
                        "knownColor": 67,
                        "name": null,
                        "state": 1,
                        "value": 0
                    }
                },
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Microsoft Sans Serif",
                    "Italic": 0,
                    "Size": 10,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Image": null,
                "Name": "LevelStyle",
                "Stroke": null
            }, {
                "__type": "Style:#PerpetuumSoft.Instrumentation.Styles",
                "Fill": {
                    "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                    "Color": {
                        "knownColor": 35,
                        "name": null,
                        "state": 1,
                        "value": 0
                    }
                },
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Microsoft Sans Serif",
                    "Italic": 0,
                    "Size": 10,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Image": null,
                "Name": "CurrentValueStyle",
                "Stroke": null
            }, {
                "__type": "Style:#PerpetuumSoft.Instrumentation.Styles",
                "Fill": {
                    "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                    "Color": {
                        "knownColor": 95,
                        "name": null,
                        "state": 1,
                        "value": 0
                    }
                },
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Microsoft Sans Serif",
                    "Italic": 0,
                    "Size": 10,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Image": null,
                "Name": "ThermometerBack",
                "Stroke": null
            }, {
                "__type": "Style:#PerpetuumSoft.Instrumentation.Styles",
                "Fill": {
                    "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                    "Color": {
                        "knownColor": 0,
                        "name": null,
                        "state": 2,
                        "value": 4291486975
                    }
                },
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Microsoft Sans Serif",
                    "Italic": 0,
                    "Size": 10,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Image": null,
                "Name": "LabelBack",
                "Stroke": {
                    "__type": "SimpleStroke:#PerpetuumSoft.Framework.Drawing",
                    "Width": 1,
                    "Color": {
                        "knownColor": 35,
                        "name": null,
                        "state": 1,
                        "value": 0
                    },
                    "DashLenght": 5,
                    "DotLenght": 1,
                    "SpaceLenght": 2,
                    "Style": 1
                }
            }, {
                "__type": "Style:#PerpetuumSoft.Instrumentation.Styles",
                "Fill": {
                    "__type": "SolidFill:#PerpetuumSoft.Framework.Drawing",
                    "Color": {
                        "knownColor": 164,
                        "name": null,
                        "state": 1,
                        "value": 0
                    }
                },
                "Font": {
                    "Bold": 0,
                    "FamilyName": "Microsoft Sans Serif",
                    "Italic": 0,
                    "Size": 10,
                    "Strikeout": 0,
                    "Underline": 0
                },
                "Image": null,
                "Name": "Default",
                "Stroke": {
                    "__type": "SimpleStroke:#PerpetuumSoft.Framework.Drawing",
                    "Width": 1,
                    "Color": {
                        "knownColor": 35,
                        "name": null,
                        "state": 1,
                        "value": 0
                    },
                    "DashLenght": 5,
                    "DotLenght": 1,
                    "SpaceLenght": 2,
                    "Style": 1
                }
            }]
        };
        //creating widget
        var additionalParams = {
            "uniqueClassName": "widget_id",
            "keepRatio": true,
            "Slider1.Value": 20
        };
        var widget = new PerfectWidgets.Widget("chartTemp", jsonModel, additionalParams);
        //getting slider object
        slider = widget.getByName("Slider1");


        //test widget       
        /*
        setInterval(function(){
        	var val = Math.floor((Math.random()*8)+34);
        	slider.setValue(val);
        }, 1000);
        */

        /*
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
	        	text: ""//"UCI Embedded System Lab"
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
	            min: 34,
	            max: 42,
	            
	            minorTickInterval: 'auto',
	            minorTickWidth: 1,
	            minorTickLength: 10,
	            minorTickPosition: 'inside',
	            minorTickColor: '#666',
	    
	            tickInterval: 1,
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
	                from: 34,
	                to: tempRangeMin,
	                color: '#DDDF0D' // green
	            },{
	                from: tempRangeMin,
	                to: tempRangeMax,
	                color: '#55BF3B' // green
	            }, {
	                from: tempRangeMax,
	                to: 39,
	                color: '#DDDF0D' // yellow
	            }, {
	                from: 39,
	                to: 42,
	                color: '#DF5353' // red
	            }]
	        },
	    
	        series: [{
	            name: 'Skin',
	            data: [34],
	            yAxis: 0,
	            tooltip: {
	                valueSuffix: ' Degree'
	            },
	        }]
	    });*/
    }

    var settingContainer, inputs;
    var fakeSettings = [{
        name: "setting1",
        value: "1"
    }, {
        name: "setting2",
        value: "2"
    }, {
        name: "setting3",
        value: "3"
    }, {
        name: "setting4",
        value: "4"
    }];

    function addSettingContainer() {
        settingContainer = $("<div id='settingContainer'/>").css({
            "z-index": 99999
        });
        settingContainer.insertBefore("#co2ReadingContainer");
        //        addSettings(null);
    }

    function addSettings(settings) {
        settingTable = $("<table id='settingTable' border='0'></table>")
        if (inputs == null) {
            inputs = [];
            var rowDom, tdDom1, tdDom2, counter = 1,
                numOfCol = 4;
            $.each(settings, function (key, val) {
                console.log(key);
                console.log(val);
                if (counter == 1) {
                    rowDom = $("<tr></tr>");
                }
                if (counter % numOfCol == 1) {
                    rowDom.appendTo(settingTable);
                    rowDom = $("<tr></tr>");
                }
                var label = $("<lable for='" + val['name'] + "'>" + val['name'] + "</label><br>").css({
                    fontSize: 'small',
                    width: '40px'
                });
                var input = $("<input  id='" + val['name'] + "' value='" + val['value'] + "'/>").css({
                    fontSize: 'small',
                    width: '40px'
                });
                inputs.push(input);

                tdDom1 = $("<td></td>");
                label.appendTo(tdDom1);
                tdDom2 = $("<td></td>");
                input.appendTo(tdDom2);
                input.spinner();

                tdDom1.appendTo(rowDom);
                tdDom2.appendTo(rowDom);
                counter++;
            });
            rowDom.appendTo(settingTable);
            settingTable.appendTo(settingContainer);
        } else {
            $.each(inputs, function (key, val) {
                val[0].value = settings[val[0].id];
            });
        }
    }

    var formulaContainer, formulaInputs;

    function addFormulaContainer() {
        formulaContainer = $("<div id='settingContainer'/>").css({
            "z-index": 99999
        });
        formulaContainer.insertBefore("#co2ReadingContainer");
        //addFormulaParams(null);
    }

    function addFormulaParams(settings) {
        formulaTable = $("<table id='formulaTable' border='0'></table>")
        if (formulaInputs == null) {
            formulaInputs = [];
            var rowDom, tdDom1, tdDom2, counter = 1,
                numOfCol = 4;
            $.each(settings, function (key, val) {
                console.log(key);
                console.log(val);
                if (counter == 1) {
                    rowDom = $("<tr></tr>");
                }
                if (counter % numOfCol == 1) {
                    rowDom.appendTo(formulaTable);
                    rowDom = $("<tr></tr>");
                }
                var label = $("<lable for='" + val['name'] + "'>" + val['name'] + "</label><br>").css({
                    fontSize: 'small',
                    width: '40px'
                });
                var input = $("<input  id='" + val['name'] + "' value='" + (val['value'] + 1) + "'/>").css({
                    fontSize: 'small',
                    width: '40px'
                });
                formulaInputs.push(input);

                tdDom1 = $("<td></td>");
                label.appendTo(tdDom1);
                tdDom2 = $("<td></td>");
                input.appendTo(tdDom2);
                input.spinner();

                tdDom1.appendTo(rowDom);
                tdDom2.appendTo(rowDom);
                counter++;
            });
            rowDom.appendTo(formulaTable);
            formulaTable.appendTo(formulaContainer);
        }
    }


    function showReadingDiv() {
        $("#dataTable").css({
            width: '100%'
        });
        //		$("#co2Reading").attr('class', 'ui-layout-west');
        $("#co2Reading").toggle();
        $("#dataTable").css({
            fontSize: 'small'
        });
        //		$("#co2Reading").removeClass('ui-layout-west');
        //		$("#charts").toggle();
        $("#charts_center").toggle();
        //		$("#charts_south").toggle();
    }

    function hideReadingDiv() {
        //		$("#co2Reading").removeClass('ui-layout-west');
        $("#co2Reading").toggle();
        //		$("#charts").attr('class', 'ui-layout-west');
        //		$("#charts").toggle();
        $("#charts_center").toggle();
        //		$("#charts_south").toggle();
    }

    var closeReadingButton;

    function addCloseReadingButton() {
        closeReadingButton = $('<button>Close</button>').css({
            "zIndex": 99999,
            float: 'right',
            fontSize: '30%',
            position: 'relative',
            top: '0px'
        });
        closeReadingButton.button();
        closeReadingButton.click(hideReadingDiv);
        closeReadingButton.insertBefore("#co2ReadingContainer");
    }

    function clearTable() {
        $("#dataTable tbody > tr").remove();
    }
    var clearReadingButton;

    function addClearReadingButton() {
        clearReadingButton = $("<button>Clear Table</button>").css({
            "z-index": 99999,
            float: 'right',
            fontSize: '30%',
            position: 'relative',
            top: '0px'
        });
        clearReadingButton.button();
        clearReadingButton.click(clearTable);
        clearReadingButton.insertBefore("#co2ReadingContainer");
    }

    var updateConfButton;

    function addUpdateConfButton() {
        updateConfButton = $("<button>Update Config</button>").css({
            "z-index": 99999,
            float: 'right',
            fontSize: '30%',
            position: 'relative',
            top: '0px'
        });
        updateConfButton.button();
        updateConfButton.insertBefore("#co2ReadingContainer");
    }

    var MAX_ROW_NUM_DATATABLE = 10;

    function updateDataTable(data) {
        //console.log("raw CO2 reading");
        //console.log(data);
        var sec = parseInt(data[2]);
        var sec_str;
        if (sec < 10) {
            sec_str = "0" + sec;
        } else {
            sec_str = sec;
        }
        var row = "<tr>" +
            "<td>" + data[0] + ":" + data[1] + ":" + sec_str + "</td>" +
            "<td>" + data[3] + "</td>" +
            "<td>" + data[4] + "</td>" +
            "<td>" + data[5] + "</td>" +
            "<td>" + data[6] + "</td>" +
            "<td>" + data[7] + "</td>" +
            "<td>" + data[8] + "</td>" +
            "<td>" + parseFloat(data[9]).toFixed(2) + "</td>" +
            "<td>" + parseFloat(data[10]).toFixed(2) + "</td>" +
            "<td>" + parseFloat(data[11]).toFixed(2) + "</td>" +
            "</tr>";
        $("#dataTable tbody").prepend(row);
        if ($("#dataTable tr").length > MAX_ROW_NUM_DATATABLE) {
            $("#dataTable tr:last").remove();
        }
        $("#dataTable").css({
            fontSize: 'small'
        });
    }

    var chartHum, humRangeMin = 0,
        humRangeMax = 1;

    function initHumidityChart() {
        // init. CO2 Reading Div
        addSettingContainer();
        addFormulaContainer();
        addClearReadingButton();
        addCloseReadingButton();
        addUpdateConfButton();

        //		$("#co2Reading").center();


        Highcharts.setOptions({
            lang: {
                customButtonTitle: "Calibration"
            }
        });

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
            exporting: {
                buttons: {
                    printButton: {
                        enabled: false
                    },
                    exportButton: {
                        enabled: false
                    },
                    customButton: {
                        _titleKey: "customButtonTitle",
                        x: -10,
                        onclick: function () {
                            $("#co2Reading").css({
                                "z-index": 99999,
                                margin: 'auto'

                            });
                            showReadingDiv();
                        },
                        symbol: 'circle'
                    }
                }
            },
            credits: {
                href: "", //"http://cps.eng.uci.edu",
                text: "UCI Embedded System Lab"
            },

            title: {
                text: 'CO2 level'
            },

            pane: {
                startAngle: -120,
                endAngle: 120,

            },

            plotOptions: {
                gauge: {
                    dataLabels: {
                        style: {
                            fontSize: '18px'
                        }
                    }
                }
            },

            // the value axis
            yAxis: {
                min: 0,
                max: 100,

                minorTickInterval: 'auto',
                minorTickWidth: 3,
                minorTickLength: 3,
                minorTickPosition: 'inside',
                minorTickColor: '#666',

                tickInterval: 10,
                tickWidth: 3,
                tickPosition: 'inside',
                tickLength: 10,
                tickColor: '#666',
                labels: {
                    step: 2,
                    rotation: 'auto',
                    style: {
                        fontSize: '22px'
                    },
                    distance: -40
                },
                /*
	            title: {
	                text: '%',
	                style: {
	                	fontSize: '18px'
	                }
	            },
	            */
                plotBands: [{
                    from: 0,
                    to: 35,
                    color: '#55BF3B' // green
                }, {
                    from: 35,
                    to: 65,
                    color: '#DDDF0D' // yellow
                }, {
                    from: 65,
                    to: 100,
                    color: '#DF5353' // red
                }]
            },

            series: [{
                name: 'CO2 level',
                data: [0],
                yAxis: 0,
                tooltip: {
                    valueSuffix: ' %'
                },
                dataLabels: {
                    formatter: function () {
                        var val = this.y;
                        return '<span style="color:#339">' + val + ' %</span>';
                    },
                    backgroundColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1
                        },
                        stops: [
                            [0, '#DDD'],
                            [1, '#FFF']
                        ]
                    }
                }
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
        if (reconMsg == null) {
            reconMsg = $('<div id="reconnect" >' + msg + '</div>').css({
                position: 'absolute',
                top: 0,
                right: 0,
                //width: '100%',
                //height: '50px',
                margin: 'auto'
            });
            reconMsg.appendTo("body");
        }
    }

    function hideReconMsg() {
        if (reconMsg != null) {
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
        socket.onopen = function (event) {
            hideReconMsg();
            //socket.send("sendSIDsSet"+name.trim());
        };
        socket.onmessage = function (event) {
            onDataReceived($.parseJSON(event.data));
        };
        socket.onerror = function (event) {
            alert('Error, readyState code is: ' + socket.readyState);
            socket.close();
            open('/', '_self', true);
            //establishConnection();
        };

        socket.onclose = function (event) {
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
            if (socket.readyState == 2 || socket.readyState == 3) {
                hideReconMsg();
                showReconMsg('connection reset by server, reconnecting in 5 secs...');
                if (reconn == null) {
                    reconn = setTimeout(function () {
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

    function update() {
        if (url.indexOf('ws://localhost') == -1) {
            if (navigator.onLine) { //navigator.onLine supports limited browsers, see https://developer.mozilla.org/en-US/docs/DOM/window.navigator.onLine
                establishConnection();
            } else {
                showReconMsg('brower is offline, check wifi...');
            }
        } else {
            establishConnection();
        }
    }

    //$(window).bind('resize', onWindowResize);

    $(window).bind('load', function (e) {
        init();
        update();
        /*
		setInterval(function(){
			render();
		}, 1000);
		*/
    });

    $(window).bind('online', function (e) {
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
        if (url.indexOf('ws://localhost') == -1) {
            hideReconMsg();
            showReconMsg('connection is back, connecting server in 5 secs...');
            if (reconn == null) {
                reconn = setTimeout(function () {
                    establishConnection();
                    //alert('Network is back, readyState is: ' + socket.readyState);
                    hideReconMsg();
                    reconn = null;
                }, 5000);
            }
        }
    });

    $(window).bind('offline', function (e) {
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
        if (url.indexOf('ws://localhost') == -1) {
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
    function showSpinner() {
        if (spinTarget == null) {
            spinTarget = $('<div id="spinner" ></div>').css({
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

    function hideSpinner() {
        spinTarget.hide();
        spinner.stop();
    }
    //end of ajax animation

});