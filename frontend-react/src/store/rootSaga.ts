import { all } from 'redux-saga/effects';
import { authSaga } from '../features/auth/authSagas';
// Import other sagas here as your app grows (e.g., import { productSaga } from '../features/products/productSagas')

export default function* rootSaga() {
    yield all([
        authSaga(),
        // productSaga(),
    ]);
}