const path = require("path");
const Umzug = require("umzug");
const {sequelize, Sequelize} = require("db/database");

const umzug = new Umzug({
    storage: "sequelize",
    storageOptions: {
        sequelize
    },
    migrations: {
        params: [
            sequelize.getQueryInterface(),
            Sequelize
        ],
        path: path.join(__dirname, "migrations"),
        pattern: /\.js$/
    }
});

module.exports = umzug;
