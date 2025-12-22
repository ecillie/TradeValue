import { Link } from 'react-router-dom';
import Button from '../components/common/Button';
import './Homepage.css';

function Homepage() {
    return (
        <div className="homepage">
            <div className="homepage-hero">
                <h1>NHL Contract Value Prediction</h1>
                <p className="hero-subtitle">
                    Analyze player contracts and predict contract values using machine learning
                </p>
                <div className="hero-actions">
                    <Link to="/players">
                        <Button variant="primary">Browse Players</Button>
                    </Link>
                    <Link to="/predictions">
                        <Button variant="secondary">Make Prediction</Button>
                    </Link>
                </div>
            </div>

            <div className="homepage-features">
                <div className="feature-card">
                    <h2>Player Database</h2>
                    <p>Browse through NHL players, their statistics, and contract information</p>
                    <Link to="/players">
                        <Button variant="primary">View Players</Button>
                    </Link>
                </div>
                <div className="feature-card">
                    <h2>Contract Analysis</h2>
                    <p>Explore contract details including cap hits, duration, and total value</p>
                    <Link to="/contracts">
                        <Button variant="primary">View Contracts</Button>
                    </Link>
                </div>
                <div className="feature-card">
                    <h2>Predictions</h2>
                    <p>Use our ML model to predict contract values based on player statistics</p>
                    <Link to="/predictions">
                        <Button variant="primary">Try Prediction</Button>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default Homepage;