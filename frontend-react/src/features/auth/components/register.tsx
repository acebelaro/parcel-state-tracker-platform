import { useState } from "react";
import { Segment, Form, Button, Header, Icon } from 'semantic-ui-react';


interface RegisterProps {
    switchToLogin: Function
}

export default function Register({
    switchToLogin,
}: RegisterProps) {

    const [username, setUsername] = useState<string>('');
    const [email, setEmail] = useState<string>('');
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
                    <Header.Subheader>Enter information for registration.</Header.Subheader>
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
                    icon="email"
                    iconPosition="left"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
                    REGISTER
                </Button>
                <Button
                    fluid
                    color="green"
                    size="large"
                    type="button"
                    style={{ marginTop: '1rem' }}
                    onClick={() => switchToLogin()}
                >
                    SWITCH TO LOGIN
                </Button>
            </Form>
        </Segment>
    );
}