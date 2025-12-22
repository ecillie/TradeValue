import { useState, useEffect } from 'react';
import { getContracts } from '../services/api';
import ContractList from '../components/contracts/ContractList';
import './Contracts.css';

function Contracts() {
    const [contracts, setContracts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchContracts();
    }, []);

    const fetchContracts = async () => {
        try {
            setLoading(true);
            const data = await getContracts();
            setContracts(data);
        } catch (error) {
            console.error('Error fetching contracts:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleContractClick = (contract) => {
        console.log('Contract clicked:', contract);
        // TODO: Navigate to contract detail page or show modal
    };

    return (
        <div className="contracts-page">
            <h1>Contracts</h1>
            
            <ContractList
                contracts={contracts}
                onContractClick={handleContractClick}
                loading={loading}
            />
        </div>
    );
}

export default Contracts;
