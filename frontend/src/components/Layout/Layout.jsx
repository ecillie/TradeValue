import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

function Layout({ children }) {
    const location = useLocation();

    const isActive = (path) => {
        return location.pathname === path ? 'active' : '';
    };

    return (
        <div className="layout">
            <nav className="navbar">
                <Link to="/" className="navbar-brand">
                    <h1>TradeValue</h1>
                </Link>
                <div className="nav-links">
                    <Link to="/" className={isActive('/')}>
                        Home
                    </Link>
                    <Link to="/players" className={isActive('/players')}>
                        Players
                    </Link>
                    <Link to="/contracts" className={isActive('/contracts')}>
                        Contracts
                    </Link>
                    <Link to="/predictions" className={isActive('/predictions')}>
                        Predictions
                    </Link>
                </div>
            </nav>
            <main className="main-content">
                {children}
            </main>
        </div>
    );
}

export default Layout;
