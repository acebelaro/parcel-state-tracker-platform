import { useState } from "react";
import Login from "./login";
import Register from "./register";


const AuthMode = {
    LOGIN: 0,
    REGISTER: 1,
} as const;

export default function LoginOrRegister() {

    const [authMode, setAuthMode] = useState<number>(AuthMode.LOGIN);

    if (authMode === AuthMode.LOGIN) {
        return (
            <Login switchToRegister={() => setAuthMode(AuthMode.REGISTER)} />
        );
    } else {
        return <Register switchToLogin={() => setAuthMode(AuthMode.LOGIN)} />
    }
}