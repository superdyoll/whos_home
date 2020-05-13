Module.register("whos_home", {
	defaults: {
		updateInterval: 1 * 60 * 1000, // every 1 minute
		fade: true,
		fadePoint: 0.25, // Start on 1/4th of the list.
		database: "./modules/whos_home/whos_home.db"
	},

	named_devices: null,

	start: function () {
		var self = this;
		Log.log("Start Who's Home");
		setInterval( () => { self.updateDom(2); } , self.config.updateInterval);
	},

	notificationReceived: function (notification, payload, sender) {
		if (notification === "DOM_OBJECTS_CREATED") {
			this.sendSocketNotification("CONFIG", this.config);
		}
	},

	socketNotificationReceived: function (notification, payload) {
		if (notification === "STATUS") {
			this.named_devices = payload;
			this.updateDom(2);
		}
	},

	// Override dom generator.
	getDom: function() {
		var wrapper = document.createElement("table");

		if (this.named_devices){
			if (this.config.fade && this.config.fadePoint < 1) {
				if (this.config.fadePoint < 0) {
					this.config.fadePoint = 0;
				}
				var startFade = this.named_devices.length * this.config.fadePoint;
				var fadeSteps = this.named_devices.length - startFade;
			}

			var currentFadeStep = 0;

			this.named_devices.sort((a,b) => new Date(b.lastSeen) - new Date(a.lastSeen));
			this.named_devices.forEach((row, e) => {
				var device = document.createElement("tr");
				device.className = "normal small";
				var name = document.createElement("td");
				name.className = "bright regular";
				name.innerHTML = row.name;
				device.appendChild(name);
				var seen = document.createElement("td");
				seen.className = "thin";
				seen.innerHTML = " Last seen " + row.prettySeen;
				device.appendChild(seen);
				wrapper.appendChild(device);

				if (e >= startFade) {			//fading
					currentFadeStep = e - startFade;
					device.style.opacity = 1 - (1 / fadeSteps * currentFadeStep);
				}
			});
		}
		return wrapper;
	}
});
