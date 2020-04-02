import {routerMiddleware} from "connected-react-router";
import {createBrowserHistory} from "history";
import {configureStore} from "@reduxjs/toolkit";
import createSagaMiddleware from "redux-saga";
import thunkMiddleware from "redux-thunk";

import registerSagas from "./sagas";
import createRootReducer from "./rootReducer";

export const history = createBrowserHistory({forceRefresh: false});

export default () => {
    const reducer = createRootReducer(history);

    const sagaMiddleware = createSagaMiddleware();
    const middleware = [thunkMiddleware, sagaMiddleware, routerMiddleware(history)];

    const preloadedState = {};

    const store = configureStore({
        reducer,
        middleware,
        preloadedState,
        devTools: true
    });

    registerSagas(sagaMiddleware);

    return store;
};
