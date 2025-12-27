import { useState } from 'react';
import { predictContractValue } from '../services/api';
import Button from '../components/common/Button';
import { formatCurrency } from '../utils/helpers';
import './Predictions.css';

function Predictions() {
    const [formData, setFormData] = useState({
        position: 'forward',
        // Skater fields
        icetime: '',
        games_played: '',
        i_f_points: '',
        i_f_goals: '',
        i_f_primary_assists: '',
        i_f_secondary_assists: '',
        i_f_x_goals: '',
        i_f_shots_on_goal: '',
        i_f_unblocked_shot_attempts: '',
        on_ice_x_goals_percentage: '',
        shots_blocked_by_player: '',
        i_f_takeaways: '',
        i_f_giveaways: '',
        i_f_penalties: '',
        penalties_drawn: '',
        i_f_o_zone_shift_starts: '',
        i_f_d_zone_shift_starts: '',
        i_f_neutral_zone_shift_starts: '',
        // Goalie fields
        x_goals: '',
        goals: '',
        unblocked_shot_attempts: '',
        blocked_shot_attempts: '',
        x_rebounds: '',
        rebounds: '',
        x_freeze: '',
        act_freeze: '',
        x_on_goal: '',
        on_goal: '',
        x_play_stopped: '',
        play_stopped: '',
        x_play_continued_in_zone: '',
        play_continued_in_zone: '',
        x_play_continued_outside_zone: '',
        play_continued_outside_zone: '',
        flurry_adjusted_x_goals: '',
        low_danger_shots: '',
        medium_danger_shots: '',
        high_danger_shots: '',
        low_danger_x_goals: '',
        medium_danger_x_goals: '',
        high_danger_x_goals: '',
        low_danger_goals: '',
        medium_danger_goals: '',
        high_danger_goals: '',
        gp: '',
        wins: '',
        losses: '',
        ot_losses: '',
        shutouts: '',
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

    const getRequiredFields = () => {
        if (formData.position === 'goalie') {
            return [
                'icetime', 'x_goals', 'goals', 'unblocked_shot_attempts', 
                'blocked_shot_attempts', 'x_rebounds', 'rebounds', 
                'x_freeze', 'act_freeze', 'x_on_goal', 'on_goal',
                'x_play_stopped', 'play_stopped', 
                'x_play_continued_in_zone', 'play_continued_in_zone',
                'x_play_continued_outside_zone', 'play_continued_outside_zone',
                'flurry_adjusted_x_goals', 'low_danger_shots', 'medium_danger_shots',
                'high_danger_shots', 'low_danger_x_goals', 'medium_danger_x_goals',
                'high_danger_x_goals', 'low_danger_goals', 'medium_danger_goals',
                'high_danger_goals', 'gp', 'wins', 'losses', 'ot_losses', 'shutouts'
            ];
        }
        // For skaters
        return [
            'icetime', 'games_played', 'i_f_points', 'i_f_goals', 
            'i_f_primary_assists', 'i_f_secondary_assists', 'i_f_x_goals',
            'i_f_shots_on_goal', 'i_f_unblocked_shot_attempts', 
            'on_ice_x_goals_percentage', 'shots_blocked_by_player',
            'i_f_takeaways', 'i_f_giveaways', 'i_f_penalties', 'penalties_drawn',
            'i_f_o_zone_shift_starts', 'i_f_d_zone_shift_starts', 'i_f_neutral_zone_shift_starts'
        ];
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setPrediction(null);

        // Validate required fields
        const requiredFields = getRequiredFields();
        const missingFields = requiredFields.filter(field => !formData[field] && formData[field] !== 0);
        
        if (missingFields.length > 0) {
            setError(`Please fill in all required fields: ${missingFields.join(', ')}`);
            return;
        }

        try {
            setLoading(true);
            // Convert all numeric fields
            const playerData = { ...formData };
            Object.keys(playerData).forEach(key => {
                if (key !== 'position' && playerData[key] !== '') {
                    playerData[key] = Number(playerData[key]);
                }
            });

            const result = await predictContractValue(playerData);
            setPrediction(result);
        } catch (err) {
            console.error('Prediction error:', err);
            setError(err.response?.data?.detail || 'Failed to make prediction. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const renderSkaterFields = () => (
        <>
            <div className="form-section">
                <h3>Usage & Games</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="icetime">Ice Time (seconds)</label>
                        <input
                            type="number"
                            id="icetime"
                            name="icetime"
                            value={formData.icetime}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="games_played">Games Played</label>
                        <input
                            type="number"
                            id="games_played"
                            name="games_played"
                            value={formData.games_played}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Scoring Production</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="i_f_points">Individual Points</label>
                        <input
                            type="number"
                            id="i_f_points"
                            name="i_f_points"
                            value={formData.i_f_points}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="i_f_goals">Individual Goals</label>
                        <input
                            type="number"
                            id="i_f_goals"
                            name="i_f_goals"
                            value={formData.i_f_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="i_f_primary_assists">Primary Assists</label>
                        <input
                            type="number"
                            id="i_f_primary_assists"
                            name="i_f_primary_assists"
                            value={formData.i_f_primary_assists}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="i_f_secondary_assists">Secondary Assists</label>
                        <input
                            type="number"
                            id="i_f_secondary_assists"
                            name="i_f_secondary_assists"
                            value={formData.i_f_secondary_assists}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Expected Goals & Shooting</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="i_f_x_goals">Individual Expected Goals</label>
                        <input
                            type="number"
                            step="0.01"
                            id="i_f_x_goals"
                            name="i_f_x_goals"
                            value={formData.i_f_x_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="i_f_shots_on_goal">Shots on Goal</label>
                        <input
                            type="number"
                            id="i_f_shots_on_goal"
                            name="i_f_shots_on_goal"
                            value={formData.i_f_shots_on_goal}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="i_f_unblocked_shot_attempts">Unblocked Shot Attempts</label>
                        <input
                            type="number"
                            id="i_f_unblocked_shot_attempts"
                            name="i_f_unblocked_shot_attempts"
                            value={formData.i_f_unblocked_shot_attempts}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="on_ice_x_goals_percentage">On-Ice xGoals % (0-1)</label>
                        <input
                            type="number"
                            step="0.0001"
                            id="on_ice_x_goals_percentage"
                            name="on_ice_x_goals_percentage"
                            value={formData.on_ice_x_goals_percentage}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Defensive Metrics</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="shots_blocked_by_player">Shots Blocked</label>
                        <input
                            type="number"
                            id="shots_blocked_by_player"
                            name="shots_blocked_by_player"
                            value={formData.shots_blocked_by_player}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="i_f_takeaways">Takeaways</label>
                        <input
                            type="number"
                            id="i_f_takeaways"
                            name="i_f_takeaways"
                            value={formData.i_f_takeaways}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="i_f_giveaways">Giveaways</label>
                        <input
                            type="number"
                            id="i_f_giveaways"
                            name="i_f_giveaways"
                            value={formData.i_f_giveaways}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Discipline</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="i_f_penalties">Penalties Taken</label>
                        <input
                            type="number"
                            id="i_f_penalties"
                            name="i_f_penalties"
                            value={formData.i_f_penalties}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="penalties_drawn">Penalties Drawn</label>
                        <input
                            type="number"
                            id="penalties_drawn"
                            name="penalties_drawn"
                            value={formData.penalties_drawn}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Zone Starts</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="i_f_o_zone_shift_starts">Offensive Zone Starts</label>
                        <input
                            type="number"
                            id="i_f_o_zone_shift_starts"
                            name="i_f_o_zone_shift_starts"
                            value={formData.i_f_o_zone_shift_starts}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="i_f_d_zone_shift_starts">Defensive Zone Starts</label>
                        <input
                            type="number"
                            id="i_f_d_zone_shift_starts"
                            name="i_f_d_zone_shift_starts"
                            value={formData.i_f_d_zone_shift_starts}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="i_f_neutral_zone_shift_starts">Neutral Zone Starts</label>
                        <input
                            type="number"
                            id="i_f_neutral_zone_shift_starts"
                            name="i_f_neutral_zone_shift_starts"
                            value={formData.i_f_neutral_zone_shift_starts}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>
        </>
    );

    const renderGoalieFields = () => (
        <>
            <div className="form-section">
                <h3>Usage</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="icetime">Ice Time (seconds)</label>
                        <input
                            type="number"
                            id="icetime"
                            name="icetime"
                            value={formData.icetime}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Basic Statistics</h3>
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
                        <label htmlFor="wins">Wins</label>
                        <input
                            type="number"
                            id="wins"
                            name="wins"
                            value={formData.wins}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="losses">Losses</label>
                        <input
                            type="number"
                            id="losses"
                            name="losses"
                            value={formData.losses}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="ot_losses">OT Losses</label>
                        <input
                            type="number"
                            id="ot_losses"
                            name="ot_losses"
                            value={formData.ot_losses}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="shutouts">Shutouts</label>
                        <input
                            type="number"
                            id="shutouts"
                            name="shutouts"
                            value={formData.shutouts}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Goals & Expected Goals</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="goals">Goals Against</label>
                        <input
                            type="number"
                            step="0.01"
                            id="goals"
                            name="goals"
                            value={formData.goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="x_goals">Expected Goals Against</label>
                        <input
                            type="number"
                            step="0.01"
                            id="x_goals"
                            name="x_goals"
                            value={formData.x_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="flurry_adjusted_x_goals">Flurry Adjusted xGoals</label>
                        <input
                            type="number"
                            step="0.01"
                            id="flurry_adjusted_x_goals"
                            name="flurry_adjusted_x_goals"
                            value={formData.flurry_adjusted_x_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Shot Attempts</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="unblocked_shot_attempts">Unblocked Shot Attempts</label>
                        <input
                            type="number"
                            id="unblocked_shot_attempts"
                            name="unblocked_shot_attempts"
                            value={formData.unblocked_shot_attempts}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="blocked_shot_attempts">Blocked Shot Attempts</label>
                        <input
                            type="number"
                            id="blocked_shot_attempts"
                            name="blocked_shot_attempts"
                            value={formData.blocked_shot_attempts}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="x_on_goal">Expected Shots on Goal</label>
                        <input
                            type="number"
                            step="0.01"
                            id="x_on_goal"
                            name="x_on_goal"
                            value={formData.x_on_goal}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="on_goal">Shots on Goal</label>
                        <input
                            type="number"
                            id="on_goal"
                            name="on_goal"
                            value={formData.on_goal}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Danger Zone Statistics</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="low_danger_shots">Low Danger Shots</label>
                        <input
                            type="number"
                            id="low_danger_shots"
                            name="low_danger_shots"
                            value={formData.low_danger_shots}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="medium_danger_shots">Medium Danger Shots</label>
                        <input
                            type="number"
                            id="medium_danger_shots"
                            name="medium_danger_shots"
                            value={formData.medium_danger_shots}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="high_danger_shots">High Danger Shots</label>
                        <input
                            type="number"
                            id="high_danger_shots"
                            name="high_danger_shots"
                            value={formData.high_danger_shots}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="low_danger_x_goals">Low Danger xGoals</label>
                        <input
                            type="number"
                            step="0.01"
                            id="low_danger_x_goals"
                            name="low_danger_x_goals"
                            value={formData.low_danger_x_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="medium_danger_x_goals">Medium Danger xGoals</label>
                        <input
                            type="number"
                            step="0.01"
                            id="medium_danger_x_goals"
                            name="medium_danger_x_goals"
                            value={formData.medium_danger_x_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="high_danger_x_goals">High Danger xGoals</label>
                        <input
                            type="number"
                            step="0.01"
                            id="high_danger_x_goals"
                            name="high_danger_x_goals"
                            value={formData.high_danger_x_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="low_danger_goals">Low Danger Goals</label>
                        <input
                            type="number"
                            id="low_danger_goals"
                            name="low_danger_goals"
                            value={formData.low_danger_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="medium_danger_goals">Medium Danger Goals</label>
                        <input
                            type="number"
                            id="medium_danger_goals"
                            name="medium_danger_goals"
                            value={formData.medium_danger_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="high_danger_goals">High Danger Goals</label>
                        <input
                            type="number"
                            id="high_danger_goals"
                            name="high_danger_goals"
                            value={formData.high_danger_goals}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Rebounds</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="x_rebounds">Expected Rebounds</label>
                        <input
                            type="number"
                            step="0.01"
                            id="x_rebounds"
                            name="x_rebounds"
                            value={formData.x_rebounds}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="rebounds">Rebounds</label>
                        <input
                            type="number"
                            id="rebounds"
                            name="rebounds"
                            value={formData.rebounds}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h3>Puck Control</h3>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="x_freeze">Expected Freezes</label>
                        <input
                            type="number"
                            step="0.01"
                            id="x_freeze"
                            name="x_freeze"
                            value={formData.x_freeze}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="act_freeze">Actual Freezes</label>
                        <input
                            type="number"
                            id="act_freeze"
                            name="act_freeze"
                            value={formData.act_freeze}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="x_play_stopped">Expected Plays Stopped</label>
                        <input
                            type="number"
                            step="0.01"
                            id="x_play_stopped"
                            name="x_play_stopped"
                            value={formData.x_play_stopped}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="play_stopped">Plays Stopped</label>
                        <input
                            type="number"
                            id="play_stopped"
                            name="play_stopped"
                            value={formData.play_stopped}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="x_play_continued_in_zone">Expected Plays Continued In Zone</label>
                        <input
                            type="number"
                            step="0.01"
                            id="x_play_continued_in_zone"
                            name="x_play_continued_in_zone"
                            value={formData.x_play_continued_in_zone}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="play_continued_in_zone">Plays Continued In Zone</label>
                        <input
                            type="number"
                            id="play_continued_in_zone"
                            name="play_continued_in_zone"
                            value={formData.play_continued_in_zone}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="x_play_continued_outside_zone">Expected Plays Continued Outside Zone</label>
                        <input
                            type="number"
                            step="0.01"
                            id="x_play_continued_outside_zone"
                            name="x_play_continued_outside_zone"
                            value={formData.x_play_continued_outside_zone}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="play_continued_outside_zone">Plays Continued Outside Zone</label>
                        <input
                            type="number"
                            id="play_continued_outside_zone"
                            name="play_continued_outside_zone"
                            value={formData.play_continued_outside_zone}
                            onChange={handleChange}
                            className="form-input"
                            required
                        />
                    </div>
                </div>
            </div>
        </>
    );

    return (
        <div className="predictions-page">
            <h1>Contract Value Prediction</h1>
            
            <div className="predictions-container">
                <div className="prediction-form-card">
                    <h2>Enter Player Advanced Statistics</h2>
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

                        {formData.position === 'goalie' ? renderGoalieFields() : renderSkaterFields()}

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
                                {formatCurrency(prediction.predicted_cap_hit)}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Predictions;