import { useState } from 'react';
import { predictContractValue } from '../services/api';
import Button from '../components/common/Button';
import { formatCurrency } from '../utils/helpers';
import './Predictions.css';

function Predictions() {
    const [formData, setFormData] = useState({
        position: 'forward',
        gp: '',
        goals: '',
        assists: '',
        points: '',
        plus_minus: '',
        pim: '',
        shots: '',
        shootpct: '',
    });
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setPrediction(null);

        // Validate required fields
        const requiredFields = ['gp', 'goals', 'assists', 'points', 'plus_minus', 'pim', 'shots', 'shootpct'];
        const missingFields = requiredFields.filter(field => !formData[field]);
        
        if (missingFields.length > 0) {
            setError(`Please fill in all fields: ${missingFields.join(', ')}`);
            return;
        }

        try {
            setLoading(true);
            const playerData = {
                position: formData.position,
                gp: Number(formData.gp),
                goals: Number(formData.goals),
                assists: Number(formData.assists),
                points: Number(formData.points),
                plus_minus: Number(formData.plus_minus),
                pim: Number(formData.pim),
                shots: Number(formData.shots),
                shootpct: Number(formData.shootpct),
            };

            const result = await predictContractValue(playerData);
            setPrediction(result);
        } catch (err) {
            console.error('Prediction error:', err);
            setError('Failed to make prediction. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="predictions-page">
            <h1>Contract Value Prediction</h1>
            
            <div className="predictions-container">
                <div className="prediction-form-card">
                    <h2>Enter Player Statistics</h2>
                    <form onSubmit={handleSubmit} className="prediction-form">
                        <div className="form-group">
                            <label htmlFor="position">Position</label>
                            <select
                                id="position"
                                name="position"
                                value={formData.position}
                                onChange={handleChange}
                                className="form-input"
                            >
                                <option value="forward">Forward</option>
                                <option value="defenseman">Defenseman</option>
                                <option value="goalie">Goalie</option>
                            </select>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="gp">Games Played</label>
                                <input
                                    type="number"
                                    id="gp"
                                    name="gp"
                                    value={formData.gp}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="goals">Goals</label>
                                <input
                                    type="number"
                                    id="goals"
                                    name="goals"
                                    value={formData.goals}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="assists">Assists</label>
                                <input
                                    type="number"
                                    id="assists"
                                    name="assists"
                                    value={formData.assists}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="points">Points</label>
                                <input
                                    type="number"
                                    id="points"
                                    name="points"
                                    value={formData.points}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="plus_minus">Plus/Minus</label>
                                <input
                                    type="number"
                                    id="plus_minus"
                                    name="plus_minus"
                                    value={formData.plus_minus}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="pim">Penalty Minutes</label>
                                <input
                                    type="number"
                                    id="pim"
                                    name="pim"
                                    value={formData.pim}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="shots">Shots</label>
                                <input
                                    type="number"
                                    id="shots"
                                    name="shots"
                                    value={formData.shots}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="shootpct">Shooting %</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    id="shootpct"
                                    name="shootpct"
                                    value={formData.shootpct}
                                    onChange={handleChange}
                                    className="form-input"
                                    required
                                />
                            </div>
                        </div>

                        {error && <div className="error-message">{error}</div>}

                        <Button
                            type="submit"
                            variant="primary"
                            disabled={loading}
                            className="submit-button"
                        >
                            {loading ? 'Predicting...' : 'Predict Contract Value'}
                        </Button>
                    </form>
                </div>

                {prediction && (
                    <div className="prediction-result-card">
                        <h2>Prediction Result</h2>
                        <div className="prediction-result">
                            <div className="predicted-cap-hit">
                                {formatCurrency(prediction.predicted_cap_hit || prediction.predicted_pv)}
                            </div>
                            {prediction.confidence && (
                                <div className="prediction-confidence">
                                    Confidence: {prediction.confidence}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Predictions;

