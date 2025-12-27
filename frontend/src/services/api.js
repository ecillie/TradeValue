import axios from 'axios'
import { BASE_URL } from '../config/constants'

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    timeout: 10000,
    withCredentials: false,
})

// Handle API errors consistently
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// Players API
export const getPlayers = async () => {
    const response = await api.get('/api/players');
    return response.data;
};

export const getPlayerById = async (id) => {
    const response = await api.get(`/api/players/${id}`);
    return response.data;
};

export const searchPlayers = async (params = {}) => {
    const response = await api.get('/api/players/search', { params });
    return response.data;
};

// Contracts API
export const getContracts = async () => {
    const response = await api.get('/api/players/contracts');
    return response.data;
};

export const getContractById = async (id) => {
    const response = await api.get(`/api/players/contracts/${id}`);
    return response.data;
};

export const getPlayerContracts = async (playerId) => {
    const response = await api.get(`/api/players/${playerId}/contracts`);
    return response.data;
};

// Stats API
export const getPlayerStats = async (playerId, params = {}) => {
    const response = await api.get(`/api/players/${playerId}/stats`, { params });
    return response.data;
};

export const getPlayerStatsBySeason = async (playerId, season) => {
    return getPlayerStats(playerId, { season });
};

// ML/Prediction API
export const predictContractValue = async (playerData) => {
    const response = await api.post('/api/ml/predict', playerData);
    return response.data;
};

export const getPlayerContractPredictions = async (playerId) => {
    const response = await api.get(`/api/players/${playerId}/contract-predictions`);
    return response.data;
};

export default api