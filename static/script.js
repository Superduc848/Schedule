/*jslint white: true, browser: true, undef: true, nomen: true, eqeqeq: true, plusplus: false, bitwise: true, regexp: true, strict: true, newcap: true, immed: true, maxerr: 14 */
/*global window: false, REDIPS: true */

/* enable strict mode */
"use strict";

// create redips container
var redips = {},
	rd = REDIPS.drag,
	date,
	weekNo,
	pos = {},
	rigsSave = [],
	techsSave = [];

// redips initialization
redips.init = function () {
	var num = 0;			// number of successfully placed elements
		//rd = REDIPS.drag;	// reference to the REDIPS.drag lib
	// initialization
	rd.init('techs');
	rd.init('rigs');
	// set hover color
	rd.hover.colorTd = '#9BB3DA';
	// call initially showContent
	redips.showContent();
	// on each drop refresh content
	rd.event.dropped = function () {
		redips.showContent();
	};
	// call showContent() after DIV element is deleted
	rd.event.deleted = function () {
		redips.showContent();
	};
	//redips.startPositions();
	//redips.moveTechs();
};


//Function iterates over rigs and techs and moves techs the rigs table based on rig assignment in users db
redips.startPositions = function () {
	var rigs = [],
		techs = [],
		id,
		i,
		j,
		position,
		idTech,
		idRig;
	// collect DIV elements from both dragging areas
	techs = document.getElementById('techs').getElementsByTagName('div');
	rigs = document.getElementById('rigs').getElementsByTagName('div');
	// open loop to iterate over rigs
	for (i = 0; i < rigs.length; i++) {
		// open loop to iterate over techs
		for (j = 0; j < techs.length; j++) {
			// set element ids
			idTech = techs[j].id;
			idRig = rigs[i].id;
			var techPos = rd.getPosition(techs[j]); // get starting position of tech in tech list for return move
			// if div has position (filter obj_new)
			if (techPos.length > 0) {
				pos[idTech] = techPos;
			}
			// if techs rig assignement and rig list names match and tech is not in set going off then move techs
			var rotation = idTech.charAt(idTech.length -1);
			var week = (weekNo % 3) + 1;
			if ((idTech.slice(0,-2) == idRig) && (rotation != week)) {
				// get the position of the destination cell in rigs table
				position = rd.getPosition(rigs[i]); // previosly rigs[i]
				rd.moveObject({id: idTech, target: position, callback: redips.moveTechs});
				//deleteRow(techs[j]);
			}
		}
	}
};

// function to delete rows
function deleteRow(pos) {
  var row = pos.parentNode.parentNode;
  row.parentNode.removeChild(row);
}

// move techs on rigs to days off table
redips.moveTechs = function () {
	var techs = [],
		idTech,
		rotation,
		week;
	techs = document.getElementById('rigs').getElementsByClassName('redips-drag');
	for (var i = 0; i < techs.length; i++) {
		idTech = techs[i].id;
		rotation = idTech.charAt(idTech.length -1);
		week = (weekNo % 3) + 1;
		//console.log(idTech,i);
		if(rotation == week) {
			console.log('Moving:',idTech,' To:',pos[idTech]);
			rd.moveObject({id: idTech, target: pos[idTech]}); // Move techs back to starting list when they are on days off
		}
	}
};

// show TD content
redips.showContent = function () {
	// get content of TD cells in right table
	var td1 = redips.getContent('td1'),
		td2 = redips.getContent('td2'),
		td3 = redips.getContent('td3'),
		td4 = redips.getContent('td4'),
		// set reference to the message DIV (below tables)
		message = document.getElementById('message');
	// show block content
	message.innerHTML = 'td1 = ' + td1 + '<br>' +
						'td2 = ' + td2 + '<br>' +
						'td3 = ' + td3 + '<br>' +
						'td4 = ' + td4;
};


// get content (DIV elements in TD)
redips.getContent = function (id) {
	var td = document.getElementById(id),
		content = '',
		cn, i;
	// TD can contain many DIV elements
	for (i = 0; i < td.childNodes.length; i++) {
		// set reference to the child node
		cn = td.childNodes[i];
		// childNode should be DIV with containing "drag" class name
		if (cn.nodeName === 'DIV' && cn.className.indexOf('drag') > -1) { // and yes, it should be uppercase
			// append DIV id to the result string
			content += cn.id + '_';
		}
	}
	// cut last '_' from string
	content = content.substring(0, content.length - 1);
	// return result
	return content;
};


// add onload event listener
if (window.addEventListener) {
	window.addEventListener('load', redips.init, false);
}
else if (window.attachEvent) {
	window.attachEvent('onload', redips.init);
}

/*
* javascript for bootstrap date picker
*/
$(document).ready(function(){
    $('#datepicker').datepicker({ // set options for the embeded date picker
    weekStart: 4,
    todayBtn: "linked",
    daysOfWeekHighlighted: "4",
    calendarWeeks: true,
    todayHighlight: true
	});
	$('#datepicker').on('changeDate', function() { // store selected date in hidden input when date changes
		date = $('#datepicker').datepicker('getDate'); // store date object from datepicker
		getWeekNumber(date); // get week of year
		redips.startPositions();
	});
	$('#datepicker').datepicker('setDate', new Date()); // set the date as current day
});

/*
* Function to provide week of year from date
* The week number is modified for a thursday start to 7 day week rathe than Monday
* This is to fit SR rotation starting every Thursday
* https://stackoverflow.com/questions/6117814/get-week-of-year-in-javascript-like-in-php
*/
function getWeekNumber(d) {
    // Get day of the week from cal
    var day = d.getDay();
    // Copy date so don't modify original
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    // Set to nearest Thursday: current date + 4 - current day number
    // Make Sunday's day number 7
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay()||7));
    // Get first day of year
    var yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
    // Calculate full weeks to nearest Thursday
    weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7);
    // adjust week number so weeks run Thursday - Wed
    if (day <= 3 && day > 0){
    	weekNo = weekNo - 1;
    }
    return weekNo;
}

/*
* testing function to get json from application.py
*/
function testJson(){
	$.getJSON(Flask.url_for("schedule"), parameters)
    .done(function(data, textStatus, jqXHR) {
    	var test = data[0];
    	console.log(test);
    })
}

// method parses form elements and submits to the server
redips.save = function () {
	rigsSave = REDIPS.drag.saveContent(schedule, 'json');
	techsSave = REDIPS.drag.saveContent(daysOff, 'json');
	console.log(test);
};

// load saved elements into table
redips.load = function () {
	rd.clearTable('schedule');
	REDIPS.drag.loadContent('schedule', rigsSave);
	REDIPS.drag.loadContent('daysOff', techsSave);
};