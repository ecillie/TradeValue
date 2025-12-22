import { useState, useEffect } from 'react';
import { getPlayers, searchPlayers } from '../services/api';
import PlayerList from '../components/players/PlayerList';
import Button from '../components/common/Button';
import './Players.css';

function Players() {
    const [players, setPlayers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterTeam, setFilterTeam] = useState('');
    const [filterPosition, setFilterPosition] = useState('');

    useEffect(() => {
        fetchPlayers();
    }, []);

    const fetchPlayers = async () => {
        try {
            setLoading(true);
            const data = await getPlayers();
            setPlayers(data);
        } catch (error) {
            console.error('Error fetching players:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        try {
            setLoading(true);
            const params = {};
            if (searchTerm) params.name = searchTerm;
            if (filterTeam) params.team = filterTeam;
            if (filterPosition) params.position = filterPosition;

            const data = await searchPlayers(params);
            setPlayers(data);
        } catch (error) {
            console.error('Error searching players:', error);
        } finally {
            setLoading(false);
        }
    };

    const handlePlayerClick = (player) => {
        console.log('Player clicked:', player);
        // TODO: Navigate to player detail page or show modal
    };

    return (
        <div className="players-page">
            <h1>Players</h1>
            
            <div className="players-filters">
                <div className="filter-group">
                    <input
                        type="text"
                        placeholder="Search by name..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="filter-input"
                    />
                </div>
                <div className="filter-group">
                    <input
                        type="text"
                        placeholder="Filter by team..."
                        value={filterTeam}
                        onChange={(e) => setFilterTeam(e.target.value)}
                        className="filter-input"
                    />
                </div>
                <div className="filter-group">
                    <input
                        type="text"
                        placeholder="Filter by position..."
                        value={filterPosition}
                        onChange={(e) => setFilterPosition(e.target.value)}
                        className="filter-input"
                    />
                </div>
                <Button onClick={handleSearch} variant="primary">
                    Search
                </Button>
                <Button onClick={fetchPlayers} variant="secondary">
                    Reset
                </Button>
            </div>

            <PlayerList
                players={players}
                onPlayerClick={handlePlayerClick}
                loading={loading}
            />
        </div>
    );
}

export default Players;
