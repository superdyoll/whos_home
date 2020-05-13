var NodeHelper = require("node_helper");
var sqlite3 = require('sqlite3').verbose();
var prettydate = require("pretty-date");

module.exports = NodeHelper.create({
	config: {},

	updateTimer: null,
	updateProcessStarted: false,
	people: [],

	start: function () {
		console.log(`Starting module helper: ${this.name}`);
	},


	socketNotificationReceived: function (notification, payload) {
		if (notification === "CONFIG") {
			console.log("Configuring whos home");
			this.config = payload;
			this.performFetch();
		}
	},

	performFetch: function() {
		console.log('Whos home fetch');
		var self = this;
		let db = new sqlite3.Database(this.config.database, (err) => {
			if (err) {
				console.log(err.message);
			}
			console.log('Connected to the whos home database');
		});

		db.serialize(function() {
			this.people = [];

			db.each(`SELECT t1.*, names.name 
				FROM history t1 
				LEFT JOIN names
				ON t1.mac = names.mac`, (err, row) => {
					if (err) {
						console.error(err.message);
					}
					if (row.name) {
						var person = {
							name: row.name,
							lastSeen: new Date(row.unixdate),
							prettySeen: prettydate.format(new Date(row.unixdate * 1000))
						};

						this.people.push(person);
					}
				}, () => {
					console.log(this.people);
					self.sendSocketNotification("STATUS", this.people); 
				});

		});
		db.close();

		this.scheduleNextFetch(this.config.updateInterval);
	},

	scheduleNextFetch: function(delay) {
		if (delay < 60 * 1000) {
			delay = 60 * 1000;
		}

		var self = this;
		clearTimeout(this.updateTimer);
		this.updateTimer = setTimeout(function() {
			self.performFetch();
		}, delay);
	},
});
