import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { AuthState, LoginCredentials, User } from './types';

const initialState: AuthState = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
};

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        // 1. Action to trigger the Saga
        loginRequest: (state, action: PayloadAction<LoginCredentials>) => {
            state.isLoading = true;
            state.error = null;
        },
        // 2. Action dispatched by Saga on success
        loginSuccess: (state, action: PayloadAction<User>) => {
            state.isLoading = false;
            state.isAuthenticated = true;
            state.user = action.payload;
            state.error = null;
        },
        // 3. Action dispatched by Saga on failure
        loginFailure: (state, action: PayloadAction<string>) => {
            state.isLoading = false;
            state.isAuthenticated = false;
            state.user = null;
            state.error = action.payload;
        },
        // Logout action (can be handled synchronously or via Saga if it needs an API call)
        logout: (state) => {
            state.user = null;
            state.isAuthenticated = false;
            state.error = null;
        },
    },
});

export const { loginRequest, loginSuccess, loginFailure, logout } = authSlice.actions;
export default authSlice.reducer;