import PlayerCard from './PlayerCard';
import './PlayerList.css';

function PlayerList({ players, onPlayerClick, loading = false }) {
    if (loading) {
        return <div className="loading">Loading players...</div>;
    }

    if (!players || players.length === 0) {
        return <div className="empty-state">No players found</div>;
    }

    return (
        <div className="player-list">
            {players.map((player) => (
                <PlayerCard
                    key={player.id}
                    player={player}
                    onClick={() => onPlayerClick && onPlayerClick(player)}
                />
            ))}
        </div>
    );
}

export default PlayerList;
