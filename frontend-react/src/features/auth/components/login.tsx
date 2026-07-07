import { useState } from "react";
import { useDispatch, useSelector } from 'react-redux';
import { Segment, Form, Button, Header, Icon } from 'semantic-ui-react';
import { loginRequest } from "../authSlice";

interface LoginProps {
    switchToRegister: Function
}

export default function Login({
    switchToRegister,
}: LoginProps) {
    const dispatch = useDispatch();
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [loading, _] = useState<boolean>(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // setLoading(true);
        dispatch(loginRequest({ username, password }));
    };

    return (
        <Segment raised style={{ marginTop: '1.5rem', padding: '2rem' }}>
            <Header as="h2" color="blue" textAlign="center">
                <Icon name="shield" />
                <Header.Content>
                    Platform Access
                    <Header.Subheader>Enter your credentials to manage parcels</Header.Subheader>
                </Header.Content>
            </Header>

            {/* Form is placed inside the card for proper visibility and layout */}
            <Form size="large" onSubmit={handleSubmit}>
                <Form.Input
                    fluid
                    icon="user"
                    iconPosition="left"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <Form.Input
                    fluid
                    icon="lock"
                    iconPosition="left"
                    placeholder="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <Button
                    fluid
                    color="blue"
                    size="large"
                    type="submit"
                    loading={loading}
                    disabled={loading}
                    style={{ marginTop: '1rem', marginRight: '0.5rem' }}
                >
                    SIGN IN
                </Button>
                <Button
                    fluid
                    color="green"
                    size="large"
                    type="button"
                    style={{ marginTop: '1rem' }}
                    onClick={() => switchToRegister()}
                >
                    REGISTER
                </Button>
            </Form>
        </Segment>
    );
}