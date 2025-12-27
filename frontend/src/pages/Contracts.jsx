import { useState, useEffect } from 'react';
import { getContracts, getPlayers } from '../services/api';
import ContractList from '../components/contracts/ContractList';
import './Contracts.css';

function Contracts() {
    const [contracts, setContracts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [players, setPlayers] = useState([]);
    useEffect(() => {
        fetchContracts();
    }, []);

    const fetchContracts = async () => {
        try {
            setLoading(true);
            const data = await getContracts();
            setContracts(data);
            const playersData = await getPlayers();
            setPlayers(playersData);
        } catch (error) {
            console.error('Error fetching contracts and players:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleContractClick = (contract) => {
        console.log('Contract clicked:', contract);

    };

    return (
        <div className="contracts-page">
            <h1>Contracts</h1>
            
            <ContractList
                contracts={contracts}
                players={players}
                onContractClick={handleContractClick}
                loading={loading}
            />
        </div>
    );
}

export default Contracts;
