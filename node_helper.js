var NodeHelper = require("node_helper");
module.exports = NodeHelper.create({
	start() {
		console.log(`Starting module helper: ${this.name}`);
	}
});
