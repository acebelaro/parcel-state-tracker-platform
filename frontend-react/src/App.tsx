import { BrowserRouter, Routes, Route } from 'react-router-dom'
import WelcomePage from './features/parcels/pages/welcome'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        {/* Add more routes here as needed */}
      </Routes>
    </BrowserRouter>
  )
}

export default App