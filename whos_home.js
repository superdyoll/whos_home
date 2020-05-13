var prettydate = require("pretty-date");

Module.register("whos_home", {
	defaults: {
		updateInterval: 1 * 60 * 1000, // every 1 minute
		database: "./whos_home.db"
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
			self.updateDom(2);
		}
	},

	// Override dom generator.
	getDom: function() {
		var wrapper = document.createElement("div");
		if (this.named_devices){
			this.named_devices.forEach((row) => {
				console.log(row.name);
				var device = document.createElement("p");
				device.className = "small bright";
				device.innerHTML(row.name + " Last seen " + prettydate.format(new Date(row.unixdate * 1000)));
				wrapper.appendChild(device);
			});
		}
		return wrapper;
	}
});
