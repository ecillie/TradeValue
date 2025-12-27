import { useState, useEffect, useCallback } from 'react';
import { getPlayerContracts, getPlayerStats, getPlayerContractPredictions } from '../../services/api';
import { formatCurrency, formatSeason, formatPlayerName, formatNumber } from '../../utils/helpers';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PlayerDetailModal.css';

function PlayerDetailModal({ player, isOpen, onClose }) {
    const [contracts, setContracts] = useState([]);
    const [stats, setStats] = useState([]);
    const [predictions, setPredictions] = useState([]);
    const [loadingContracts, setLoadingContracts] = useState(false);
    const [loadingStats, setLoadingStats] = useState(false);
    const [loadingPredictions, setLoadingPredictions] = useState(false);
    const [error, setError] = useState(null);
    const [showPlayoffs, setShowPlayoffs] = useState(false); // Toggle for playoffs/regular season

    const fetchPlayerData = useCallback(async () => {
        if (!player) return;

        try {
            setError(null);
            setLoadingContracts(true);
            setLoadingStats(true);
            setLoadingPredictions(true);

            // Fetch contracts, stats, and predictions in parallel
            const [contractsData, statsData, predictionsData] = await Promise.all([
                getPlayerContracts(player.id),
                getPlayerStats(player.id),
                getPlayerContractPredictions(player.id).catch(() => []) // Don't fail if predictions fail
            ]);

            setContracts(contractsData);
            setStats(statsData);
            setPredictions(predictionsData);
            console.log('Predictions data:', predictionsData); // Debug log
        } catch (err) {
            console.error('Error fetching player data:', err);
            setError('Failed to load player data');
        } finally {
            setLoadingContracts(false);
            setLoadingStats(false);
            setLoadingPredictions(false);
        }
    }, [player]);

    useEffect(() => {
        if (isOpen && player) {
            fetchPlayerData();
        }
    }, [isOpen, player, fetchPlayerData]);

    if (!isOpen || !player) return null;

    const playerName = formatPlayerName(player.firstname, player.lastname);

    // Filter stats based on toggle
    const filteredStats = stats.filter(stat => stat.playoff === showPlayoffs);
    
    // Sort by season (newest first)
    const sortedStats = [...filteredStats].sort((a, b) => {
        if (a.season !== b.season) return b.season - a.season;
        return a.team.localeCompare(b.team);
    });

    // Calculate aggregated totals
    const aggregatedTotals = filteredStats.reduce((acc, stat) => {
        acc.gp += stat.gp || 0;
        acc.goals += stat.goals || 0;
        acc.assists += stat.assists || 0;
        acc.points += stat.points || 0;
        acc.plus_minus += stat.plus_minus || 0;
        acc.pim += stat.pim || 0;
        acc.shots += stat.shots || 0;
        return acc;
    }, {
        gp: 0,
        goals: 0,
        assists: 0,
        points: 0,
        plus_minus: 0,
        pim: 0,
        shots: 0
    });

    // Calculate shooting percentage
    const shootingPct = aggregatedTotals.shots > 0 
        ? ((aggregatedTotals.goals / aggregatedTotals.shots) * 100).toFixed(1)
        : '0.0';

    // Sort contracts by start year (newest first)
    const sortedContracts = [...contracts].sort((a, b) => b.start_year - a.start_year);

    // Calculate contract aggregates
    const contractTotals = contracts.reduce((acc, contract) => {
        acc.totalValue += parseFloat(contract.total_value || 0);
        acc.totalCapHit += parseFloat(contract.cap_hit || 0);
        acc.totalDuration += contract.duration || 0;
        return acc;
    }, {
        totalValue: 0,
        totalCapHit: 0,
        totalDuration: 0
    });

    const avgCapHit = contracts.length > 0 ? contractTotals.totalCapHit / contracts.length : 0;
    const avgDuration = contracts.length > 0 ? contractTotals.totalDuration / contracts.length : 0;

    // Sort predictions by year to ensure proper display
    const sortedPredictions = [...predictions].sort((a, b) => a.year - b.year);

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{playerName}</h2>
                    <button className="modal-close" onClick={onClose}>&times;</button>
                </div>

                <div className="modal-body">
                    {/* Player Info */}
                    <div className="player-info-section">
                        <div className="info-row">
                            <span className="info-label">Team:</span>
                            <span className="info-value">{player.team}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">Position:</span>
                            <span className="info-value">{player.position}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">Age:</span>
                            <span className="info-value">{player.age}</span>
                        </div>
                    </div>

                    {/* Contracts Section */}
                    <div className="section">
                        <h3>Contracts ({contracts.length})</h3>
                        {loadingContracts ? (
                            <div className="loading">Loading contracts...</div>
                        ) : error ? (
                            <div className="error">{error}</div>
                        ) : contracts.length === 0 ? (
                            <div className="empty-state">No contracts found</div>
                        ) : (
                            <div className="contracts-table-wrapper">
                                <table className="contracts-table">
                                    <thead>
                                        <tr>
                                            <th>Season</th>
                                            <th>Team</th>
                                            <th>Duration</th>
                                            <th>Cap Hit</th>
                                            <th>Total Value</th>
                                            <th>Cap %</th>
                                            <th>Type</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {sortedContracts.map((contract) => (
                                            <tr key={contract.id}>
                                                <td>{formatSeason(contract.start_year)} - {formatSeason(contract.end_year)}</td>
                                                <td>{contract.team}</td>
                                                <td>{contract.duration} {contract.duration === 1 ? 'year' : 'years'}</td>
                                                <td>{formatCurrency(contract.cap_hit)}</td>
                                                <td>{contract.total_value ? formatCurrency(contract.total_value) : '-'}</td>
                                                <td>{(parseFloat(contract.cap_pct) * 100).toFixed(2)}%</td>
                                                <td>
                                                    <div className="contract-badges">
                                                        {contract.elc && <span className="contract-badge elc">ELC</span>}
                                                        {contract.rfa && <span className="contract-badge rfa">RFA</span>}
                                                        {!contract.elc && !contract.rfa && <span className="contract-badge ufa">UFA</span>}
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                    <tfoot>
                                        <tr className="totals-row">
                                            <td colSpan="2"><strong>Totals ({contracts.length} contracts)</strong></td>
                                            <td><strong>{avgDuration.toFixed(1)} avg years</strong></td>
                                            <td><strong>{formatCurrency(avgCapHit)} avg</strong></td>
                                            <td><strong>{formatCurrency(contractTotals.totalValue)}</strong></td>
                                            <td colSpan="2"></td>
                                        </tr>
                                    </tfoot>
                                </table>
                            </div>
                        )}
                    </div>

                    {/* Contract Predictions Chart */}
                    {sortedPredictions.length > 0 && (
                        <div className="section">
                            <h3>Actual vs Expected Cap Hit (By Year)</h3>
                            {loadingPredictions ? (
                                <div className="loading">Loading predictions...</div>
                            ) : (
                                <div className="chart-container">
                                    <ResponsiveContainer width="100%" height={400}>
                                        <BarChart
                                            data={sortedPredictions}
                                            margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                                        >
                                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                            <XAxis
                                                dataKey="year"
                                                stroke="#888"
                                                tickFormatter={(value) => value.toString()}
                                            />
                                            <YAxis
                                                tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                                                stroke="#888"
                                            />
                                            <Tooltip
                                                formatter={(value) => formatCurrency(value)}
                                                labelFormatter={(value) => `Year: ${value}`}
                                                labelStyle={{ color: '#333' }}
                                                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333', borderRadius: '4px' }}
                                            />
                                            <Legend />
                                            <Bar dataKey="actual_cap_hit" fill="#646cff" name="Actual Cap Hit" />
                                            <Bar dataKey="expected_cap_hit" fill="#10b981" name="Expected Cap Hit" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Statistics Section */}
                    <div className="section">
                        <div className="stats-header">
                            <h3>Statistics</h3>
                            <div className="season-toggle">
                                <button 
                                    className={`toggle-btn ${!showPlayoffs ? 'active' : ''}`}
                                    onClick={() => setShowPlayoffs(false)}
                                >
                                    Regular Season
                                </button>
                                <button 
                                    className={`toggle-btn ${showPlayoffs ? 'active' : ''}`}
                                    onClick={() => setShowPlayoffs(true)}
                                >
                                    Playoffs
                                </button>
                            </div>
                        </div>
                        {loadingStats ? (
                            <div className="loading">Loading statistics...</div>
                        ) : error ? (
                            <div className="error">{error}</div>
                        ) : sortedStats.length === 0 ? (
                            <div className="empty-state">No {showPlayoffs ? 'playoff' : 'regular season'} statistics found</div>
                        ) : (
                            <>
                                <div className="stats-table-wrapper">
                                    <table className="stats-table">
                                        <thead>
                                            <tr>
                                                <th>Season</th>
                                                <th>Team</th>
                                                <th>GP</th>
                                                <th>G</th>
                                                <th>A</th>
                                                <th>P</th>
                                                <th>+/-</th>
                                                <th>PIM</th>
                                                <th>S</th>
                                                <th>S%</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {sortedStats.map((stat) => (
                                                <tr key={stat.id}>
                                                    <td>{formatSeason(stat.season)}</td>
                                                    <td>{stat.team}</td>
                                                    <td>{formatNumber(stat.gp)}</td>
                                                    <td>{formatNumber(stat.goals)}</td>
                                                    <td>{formatNumber(stat.assists)}</td>
                                                    <td>{formatNumber(stat.points)}</td>
                                                    <td>{formatNumber(stat.plus_minus)}</td>
                                                    <td>{formatNumber(stat.pim)}</td>
                                                    <td>{formatNumber(stat.shots)}</td>
                                                    <td>{Number(stat.shootpct).toFixed(1)}%</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                        <tfoot>
                                            <tr className="totals-row">
                                                <td colSpan="2"><strong>Totals</strong></td>
                                                <td><strong>{formatNumber(aggregatedTotals.gp)}</strong></td>
                                                <td><strong>{formatNumber(aggregatedTotals.goals)}</strong></td>
                                                <td><strong>{formatNumber(aggregatedTotals.assists)}</strong></td>
                                                <td><strong>{formatNumber(aggregatedTotals.points)}</strong></td>
                                                <td><strong>{formatNumber(aggregatedTotals.plus_minus)}</strong></td>
                                                <td><strong>{formatNumber(aggregatedTotals.pim)}</strong></td>
                                                <td><strong>{formatNumber(aggregatedTotals.shots)}</strong></td>
                                                <td><strong>{shootingPct}%</strong></td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PlayerDetailModal;

