import Card from '../common/Card';
import { formatCurrency, formatSeason, formatPlayerName } from '../../utils/helpers';
import './ContractCard.css';

function ContractCard({ contract, player, onClick }) {
    if (!contract) return null;

    const playerName = player ? formatPlayerName(player.firstname, player.lastname) : 'Unknown Player';

    return (
        <Card onClick={onClick} className="contract-card">
            <div className="contract-card-header">
                <h3>{playerName}</h3>
                <span className="contract-team">{contract.team}</span>
            </div>
            <div className="contract-card-main">
                <div className="contract-cap-hit">
                    {formatCurrency(contract.cap_hit)}
                </div>
                <div className="contract-duration">
                    {formatSeason(contract.start_year)} - {formatSeason(contract.end_year)} ({contract.duration} years)
                </div>
            </div>
            <div className="contract-card-details">
                {contract.rfa && <span className="contract-badge rfa">RFA</span>}
                {contract.elc && <span className="contract-badge elc">ELC</span>}
                {contract.total_value && (
                    <span className="contract-total-value">
                        Total: {formatCurrency(contract.total_value)}
                    </span>
                )}
            </div>
        </Card>
    );
}

export default ContractCard;
