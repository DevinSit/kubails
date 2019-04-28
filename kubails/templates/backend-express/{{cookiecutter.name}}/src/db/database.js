const env = process.env.NODE_ENV || "development";

const config = require("db/config/config.json")[env];
const Sequelize = require("sequelize");

const sequelize = new Sequelize(config.database, config.username, config.password, config);

module.exports = {
    sequelize,
    Sequelize
};
