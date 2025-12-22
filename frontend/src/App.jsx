import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Homepage from './pages/Homepage';
import Players from './pages/Players';
import Contracts from './pages/Contracts';
import Predictions from './pages/Predictions';
import './App.css';

function App() {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Homepage />} />
                    <Route path="/players" element={<Players />} />
                    <Route path="/contracts" element={<Contracts />} />
                    <Route path="/predictions" element={<Predictions />} />
                </Routes>
            </Layout>
        </Router>
    );
}

export default App;