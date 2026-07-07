import React, { useState } from 'react';
import { Container, Segment, Form, Button, Header, Icon, Grid } from 'semantic-ui-react';
import welcomeBanner from '../../../assets/welcome-banner.jpg'; // Adjust path based on your folder depth

export const WelcomePage: React.FC = () => {
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
        <Container style={{ marginTop: '2rem', marginBottom: '2rem' }}>
            <Grid centered columns={1}>
                <Grid.Column mobile={16} tablet={12} computer={10}>

                    {/* 1. Banner Image Segment */}
                    <Segment basic style={{ padding: 0, overflow: 'hidden', borderRadius: '8px' }}>
                        <img
                            src={welcomeBanner}
                            alt="ParcelSafe Welcome Banner"
                            style={{ width: '100%', height: 'auto', display: 'block' }}
                        />
                    </Segment>

                    {/* 2. Login Card Segment (Form is now INSIDE here) */}
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
                                // fluid
                                icon="user"
                                // iconPosition="left"
                                placeholder="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                            <Form.Input
                                // fluid
                                icon="lock"
                                // iconPosition="left"
                                placeholder="Password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />

                            <Button
                                // fluid
                                color="blue"
                                size="large"
                                type="submit"
                                loading={loading}
                                disabled={loading}
                                style={{ marginTop: '1rem' }}
                            >
                                Sign In
                            </Button>
                        </Form>
                    </Segment>

                </Grid.Column>
            </Grid>
        </Container>
    );
};

export default WelcomePage;