import { call, put, takeLatest } from 'redux-saga/effects';
import type { PayloadAction } from '@reduxjs/toolkit';
import { loginRequest, loginSuccess, loginFailure } from './authSlice';
import type { LoginCredentials, User } from './types';

// Mock API Call (Replace this with your actual axios/fetch instance)
const loginApi = async (credentials: LoginCredentials): Promise<User> => {
    const response = await fetch('https://localhost:3000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
    }

    return response.json(); // Expected to return user data + tokens
};

// Worker Saga: Handlers the side effects
function* handleLogin(action: PayloadAction<LoginCredentials>) {
    try {
        // Call the API function with the payload from the action
        const userData: User = yield call(loginApi, action.payload);

        // Save token to localStorage if needed
        // localStorage.setItem('token', userData.token); 

        // Dispatch success action to update Redux store
        yield put(loginSuccess(userData));
    } catch (error: any) {
        // Dispatch failure action with error message
        yield put(loginFailure(error.message || 'An unknown error occurred'));
    }
}

// Watcher Saga: Watches for actions dispatched to the store
export function* authSaga() {
    // takeLatest ensures that if the user clicks "Submit" multiple times quickly, 
    // only the latest request is executed.
    yield takeLatest(loginRequest.type, handleLogin);
}