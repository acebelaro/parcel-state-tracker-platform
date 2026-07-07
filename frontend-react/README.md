


```

src/
├── assets/                 # Global static assets (images, logos, fonts)
├── components/             # Global reusable UI components (Buttons, Inputs, Spinners)
│   ├── Button/
│   │   ├── Button.tsx
│   │   └── Button.module.css
│   └── ProtectedRoute.tsx
├── config/                 # Global configurations (API base URLs, constants)
├── features/               # Domain-driven features (The core of your app)
│   ├── auth/               # Everything related to Authentication
│   │   ├── components/     # Auth-specific UI (LoginForm, RegisterForm)
│   │   ├── pages/          # Auth pages (LoginPage, RegisterPage)
│   │   ├── authSlice.ts    # Redux Reducers & Actions for auth
│   │   └── authSagas.ts    # Redux Sagas for async login/logout api calls
│   │
│   ├── parcels/            # Everything related to Parcel Tracking
│   │   ├── components/     # TelemetryGauge, ParcelCard, ThresholdForm
│   │   ├── pages/          # DashboardPage, ParcelDetailsPage
│   │   ├── parcelSlice.ts  # Redux slice for parcel state
│   │   └── parcelSagas.ts  # Redux Sagas for fetching live telemetry/alerts
│   │
│   └── users/              # User/Profile management feature
│
├── layouts/                # Main layout wrappers (e.g., DashboardLayout, MinimalLayout)
├── routes/                 # App routing configuration (AppRoutes.tsx)
├── store/                  # Redux Global Store Setup
│   ├── index.ts            # Configures configureStore, binds rootReducer & SagaMiddleware
│   ├── rootReducer.ts      # Combines all feature slices (authSlice, parcelSlice)
│   └── rootSaga.ts         # Combines all feature sagas (authSagas, parcelSagas)
├── types/                  # Global TypeScript interfaces/types (User, Parcel, Telemetry)
├── App.tsx                 # Root component providing Store and Router
└── main.tsx                # Application entry point

```