const migrator = require("./migrator");
const {sequelize} = require("./database");

module.exports = {
    migrator,
    sequelize
};
