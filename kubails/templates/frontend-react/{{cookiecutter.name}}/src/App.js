import React from "react";
import {Provider} from "react-redux";
import {Switch, Route} from "react-router";
import {ConnectedRouter} from "connected-react-router";
import configureStore, {history} from "store/";
import "./App.scss";

const store = configureStore();

const App = () => (
    <Provider store={store}>
        <ConnectedRouter history={history}>
            <AppLayout />
        </ConnectedRouter>
    </Provider>
);

const AppLayout = () => (
    <Switch>
        <Route
            path="/"
            render={() => (
                <div id="app">
                    <h1>{{cookiecutter.title}}</h1>
                </div>
            )}
        />
    </Switch>
);

export default App;
