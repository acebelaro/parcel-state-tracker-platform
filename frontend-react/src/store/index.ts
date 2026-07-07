import { configureStore } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';
import authReducer from '../features/auth/authSlice';
import rootSaga from './rootSaga';

// 1. Create the Saga middleware
const sagaMiddleware = createSagaMiddleware();

// 2. Configure the store
export const store = configureStore({
    reducer: {
        auth: authReducer,
        // Add other feature reducers here, e.g., products: productReducer
    },
    // Adding Saga middleware, while ensuring standard Redux Toolkit middleware remains intact
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({ thunk: false }).concat(sagaMiddleware),
});

// 3. Run the Root Saga
sagaMiddleware.run(rootSaga);

// 4. Export Types for hooks
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;