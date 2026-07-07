/**
 * Shape of the User object returned from the API upon successful login
 */
export interface User {
    id: string;
    email: string;
    firstName?: string;
    lastName?: string;
    token?: string; // JWT token if your API returns it directly in the user object
}

/**
 * Credentials required to payload into the login action
 */
export interface LoginCredentials {
    username: string;
    password: string; // Optional if you support alternative passwordless or OAuth routes later
}

/**
 * The internal Redux state slice structure for authentication
 */
export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null; // Stores API or network error messages
}