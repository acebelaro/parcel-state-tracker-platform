import React from 'react';
import { Container, Grid } from 'semantic-ui-react';
import ImageBanner from '../components/imageBanner';
import LoginOrRegister from '../components/loginOrRegister';

export const WelcomePage: React.FC = () => {

    return (
        <Container style={{ marginTop: '2rem', marginBottom: '2rem' }}>
            <Grid centered columns={1}>
                <Grid.Column mobile={16} tablet={12} computer={10}>
                    <ImageBanner />
                    <LoginOrRegister />
                </Grid.Column>
            </Grid>
        </Container>
    );
};

export default WelcomePage;