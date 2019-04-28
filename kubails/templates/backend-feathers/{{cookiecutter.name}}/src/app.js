const compress = require("compression");
const helmet = require("helmet");
const cors = require("cors");
const {logger} = require("utils/");

const feathers = require("@feathersjs/feathers");
const configuration = require("@feathersjs/configuration");
const express = require("@feathersjs/express");
const socketio = require("@feathersjs/socketio");

const {authentication} = require("middleware/");
const {services} = require("components/");
const appHooks = require("./app.hooks");
const channels = require("./channels");

const {sequelize} = require("./db");

const app = express(feathers());

// Load app configuration
app.configure(configuration());

// Enable security, CORS, compression, and body parsing
app.use(helmet());
app.use(cors());
app.use(compress());
app.use(express.json());
app.use(express.urlencoded({extended: true}));

// Set up Plugins and providers
app.configure(express.rest());
app.configure(socketio());

app.configure(sequelize);

// Configure other middleware (see `middleware/index.js`)
app.configure(authentication);
// Set up our services (see `components/index.js`)
app.configure(services);
// Set up event channels (see channels.js)
app.configure(channels);

// Configure a middleware for 404s and the error handler
app.use(express.notFound());
app.use(express.errorHandler({logger}));

app.hooks(appHooks);

module.exports = app;
