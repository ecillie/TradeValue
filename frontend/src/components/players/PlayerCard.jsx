import Card from '../common/Card';
import { formatPlayerName } from '../../utils/helpers';
import './PlayerCard.css';

function PlayerCard({ player, onClick }) {
    if (!player) return null;

    const fullName = formatPlayerName(player.firstname, player.lastname);

    return (
        <Card onClick={onClick} className="player-card">
            <div className="player-card-header">
                <h3>{fullName}</h3>
                <span className="player-team">{player.team}</span>
            </div>
            <div className="player-card-info">
                <div className="player-position">{player.position}</div>
                <div className="player-age">Age: {player.age}</div>
            </div>
        </Card>
    );
}

export default PlayerCard;
