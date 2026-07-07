import { useState } from "react";
import { Segment, Form, Button, Header, Icon } from 'semantic-ui-react';

interface LoginProps {
    switchToRegister: Function
}

export default function Login({
    switchToRegister,
}: LoginProps) {

    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        // TODO: Connect this to your Redux Action / Saga later
        console.log('Logging in with:', { username, password });

        // Fake loading state for visual feedback
        setTimeout(() => setLoading(false), 1000);
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