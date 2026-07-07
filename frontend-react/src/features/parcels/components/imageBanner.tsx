import { Segment } from 'semantic-ui-react';
import welcomeBanner from '../../../assets/welcome-banner.jpg'; // Adjust path based on your folder depth

export default function ImageBanner() {
    return (
        <Segment basic style={{ padding: 0, overflow: 'hidden', borderRadius: '8px' }}>
            <img
                src={welcomeBanner}
                alt="ParcelSafe Welcome Banner"
                style={{ width: '100%', height: 'auto', display: 'block' }}
            />
        </Segment>
    );
}
