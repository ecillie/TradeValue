import ContractCard from './ContractCard';
import './ContractList.css';

function ContractList({ contracts, players, onContractClick, loading = false }) {
    if (loading) {
        return <div className="loading">Loading contracts...</div>;
    }

    if (!contracts || contracts.length === 0) {
        return <div className="empty-state">No contracts found</div>;
    }

    const playerMap = {};
    players.forEach(player => {
        playerMap[player.id] = player;
    });

    return (
        <div className="contract-list">
            {contracts.map((contract) => {
                const player = contract.player || playerMap[contract.player_id];
                return (
                    <ContractCard
                        key={contract.id}
                        contract={contract}
                        player={player}
                        onClick={() => onContractClick && onContractClick(contract)}
                    />
                );
            })}
        </div>
    );
}

export default ContractList;
