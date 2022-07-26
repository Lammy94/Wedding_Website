function countdown() {
	const second = 1000, minute = second * 60, hour = minute * 60, day = hour * 24;
	let countDown = new Date('Sep 25, 2021 13:00:00').getTime();
	let x = setInterval(function() {
		let now = new Date().getTime();
		let distance = countDown - now;
		document.getElementById('days').innerText = Math.floor(distance / (day));
		document.getElementById('hours').innerText = Math.floor((distance % (day)) / (hour));
		document.getElementById('minutes').innerText = Math.floor((distance % (hour)) / (minute));
		document.getElementById('seconds').innerText = Math.floor((distance % (minute)) / second);
	}, second);
}

function moveClock(elem, dt){
	var s = Snap(document.getElementById(elem));

	var minutes = s.select("#minutes"),
		hours   = s.select("#hours"),
		rim     = s.select("#rim"),
		face    = {
			elem: s.select("#face"),
			cx: s.select("#face").getBBox().cx,
			cy: s.select("#face").getBBox().cy,
		},
		angle   = 0,
		easing = function(a) {
			return a==!!a?a:Math.pow(4,-10*a)*Math.sin((a-.075)*2*Math.PI/.3)+1;
		};

	//Create a filter to make a blurry black version of a thing
	var filter = Snap.filter.blur(0.1) + Snap.filter.brightness(0);

	function update(dt) {
		var time = new Date(dt);
		setHours(time);
		setMinutes(time);
	}

	function setHours(t) {
		var hour = t.getHours();
		hour %= 12;
		hour += Math.floor(t.getMinutes()/10)/6;
		var angle = hour*360/12;
		hours.animate(
			{transform: "rotate("+angle+" "+face.cx+" "+face.cy+"))"},
			100,
			mina.linear,
			function(){
				if (angle === 360){
					hours.attr({transform: "rotate("+0+" "+face.cx+" "+face.cy+")"});
					hshadow.attr({transform: "translate(0, 2) rotate("+0+" "+face.cx+" "+face.cy+2+")"});
				}
			}
		);

	}
	function setMinutes(t) {
		var minute = t.getMinutes();
		minute %= 60;
		minute += Math.floor(t.getSeconds()/10)/6;
		var angle = minute*360/60;
		minutes.animate(
			{transform: "rotate("+angle+" "+face.cx+" "+face.cy+")"},
			100,
			mina.linear,
			function(){
				if (angle === 360){
					minutes.attr({transform: "rotate("+0+" "+face.cx+" "+face.cy+")"});
					mshadow.attr({transform: "translate(0, 2) rotate("+0+" "+face.cx+" "+face.cy+2+")"});
				}
			}
		);
	}

	update(dt);
}

function get_music(url) {
	const xhr = new XMLHttpRequest();
	xhr.open('GET', url, true);
	xhr.responseType = 'json';
	xhr.onload = function(e) {
		if (this.status == 200) {
			add_music(this.response)
		}
	};
	xhr.send();
}

function add_music(data){
	for (let i = 0; i < data.length; i++) {
		// Create a new div
		var node = document.createElement("div");
		node.id = data[i].request_id;
		node.className = "card";

		var elem = document.createElement("img");
		elem.src = data[i].artwork;
		elem.className = "artwork";
		node.appendChild(elem);

		// Add Song title to the new div
		elem = document.createElement("h3");
		elem.innerText = data[i].title;
		elem.className = "songTitle";
		node.appendChild(elem);

		// Add Song artist to the new div
		elem = document.createElement("p");
		elem.innerText = data[i].artist;
		elem.className = "artistName";
		node.appendChild(elem);

		// Add requester id to the card, will be hidden
		elem = document.createElement("p");
		elem.innerText = data[i].requester_id;
		elem.className = "requester";
		node.appendChild(elem);


		document.getElementById("music").appendChild(node);     // Append <li> to <ul> with id="myList"
	};



}

function showForm(){
	document.getElementById("submit_song").addEventListener("click", function() {
		document.getElementById('submit_song').style.display = "none";
		document.getElementById('make_submission').style.display = " inline-block";
	});
}