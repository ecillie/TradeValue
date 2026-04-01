import { useEffect, useState } from 'react';
import { getPlayerContracts, getPlayerStats, getPlayerContractPredictions } from '../../services/api';
import { formatPlayerName, formatCurrency, formatSeason, formatPercentage } from '../../utils/helpers';
import Button from '../common/Button';
import './PlayerDetailModal.css';

function PlayerDetailModal({ player, isOpen, onClose }) {
    const [contracts, setContracts] = useState([]);
    const [stats, setStats] = useState([]);
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!isOpen || !player?.id) {
            return;
        }

        let cancelled = false;

        const load = async () => {
            setLoading(true);
            setError(null);
            try {
                const [contractsData, statsData, predictionsData] = await Promise.all([
                    getPlayerContracts(player.id),
                    getPlayerStats(player.id),
                    getPlayerContractPredictions(player.id).catch(() => []),
                ]);
                if (!cancelled) {
                    setContracts(Array.isArray(contractsData) ? contractsData : []);
                    setStats(Array.isArray(statsData) ? statsData : []);
                    setPredictions(Array.isArray(predictionsData) ? predictionsData : []);
                }
            } catch (e) {
                if (!cancelled) {
                    setError(e?.message || 'Failed to load player details');
                    setContracts([]);
                    setStats([]);
                    setPredictions([]);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        load();
        return () => {
            cancelled = true;
        };
    }, [isOpen, player?.id]);

    useEffect(() => {
        const onKeyDown = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [isOpen, onClose]);

    if (!isOpen || !player) {
        return null;
    }

    const fullName = formatPlayerName(player.firstname, player.lastname);

    return (
        <div
            className="player-detail-modal-backdrop"
            role="presentation"
            onClick={onClose}
        >
            <div
                className="player-detail-modal-panel"
                role="dialog"
                aria-modal="true"
                aria-labelledby="player-detail-modal-title"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="player-detail-modal-header">
                    <div>
                        <h2 id="player-detail-modal-title">{fullName}</h2>
                        <p className="player-detail-modal-meta">
                            {player.team} · {player.position} · Age {player.age}
                        </p>
                    </div>
                    <Button type="button" variant="secondary" onClick={onClose} aria-label="Close">
                        Close
                    </Button>
                </div>

                <div className="player-detail-modal-body">
                    {loading && <div className="player-detail-modal-status">Loading…</div>}
                    {error && <div className="player-detail-modal-error">{error}</div>}

                    {!loading && !error && (
                        <>
                            <section className="player-detail-modal-section">
                                <h3>Contracts ({contracts.length})</h3>
                                {contracts.length === 0 ? (
                                    <p className="player-detail-modal-empty">No contracts</p>
                                ) : (
                                    <div className="player-detail-modal-table-wrap">
                                        <table className="player-detail-modal-table">
                                            <thead>
                                                <tr>
                                                    <th>Team</th>
                                                    <th>Years</th>
                                                    <th>Duration</th>
                                                    <th>Cap hit</th>
                                                    <th>Total value</th>
                                                    <th>Type</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {contracts.map((c) => (
                                                    <tr key={c.id}>
                                                        <td>{c.team}</td>
                                                        <td>
                                                            {c.start_year}–{c.end_year}
                                                        </td>
                                                        <td>{c.duration}</td>
                                                        <td>{formatCurrency(Number(c.cap_hit))}</td>
                                                        <td>
                                                            {c.total_value != null
                                                                ? formatCurrency(Number(c.total_value))
                                                                : '—'}
                                                        </td>
                                                        <td>
                                                            {[c.rfa && 'RFA', c.elc && 'ELC']
                                                                .filter(Boolean)
                                                                .join(', ') || '—'}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </section>

                            <section className="player-detail-modal-section">
                                <h3>Basic stats ({stats.length})</h3>
                                {stats.length === 0 ? (
                                    <p className="player-detail-modal-empty">No stats</p>
                                ) : (
                                    <div className="player-detail-modal-table-wrap">
                                        <table className="player-detail-modal-table">
                                            <thead>
                                                <tr>
                                                    <th>Season</th>
                                                    <th>Playoff</th>
                                                    <th>Team</th>
                                                    <th>GP</th>
                                                    <th>G</th>
                                                    <th>A</th>
                                                    <th>Pts</th>
                                                    <th>+/-</th>
                                                    <th>SO%</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {stats.map((s) => (
                                                    <tr key={s.id}>
                                                        <td>{formatSeason(s.season)}</td>
                                                        <td>{s.playoff ? 'Yes' : 'No'}</td>
                                                        <td>{s.team}</td>
                                                        <td>{s.gp}</td>
                                                        <td>{s.goals}</td>
                                                        <td>{s.assists}</td>
                                                        <td>{s.points}</td>
                                                        <td>{s.plus_minus}</td>
                                                        <td>{formatPercentage(Number(s.shootpct))}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </section>

                            {predictions.length > 0 && (
                                <section className="player-detail-modal-section">
                                    <h3>Contract predictions (by year)</h3>
                                    <div className="player-detail-modal-table-wrap">
                                        <table className="player-detail-modal-table">
                                            <thead>
                                                <tr>
                                                    <th>Year</th>
                                                    <th>Actual cap hit</th>
                                                    <th>Expected cap hit</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {predictions.map((row) => (
                                                    <tr key={`${row.contract_id}-${row.year}`}>
                                                        <td>{row.year}</td>
                                                        <td>
                                                            {formatCurrency(row.actual_cap_hit)}
                                                            {row.is_slide ? ' (ELC slide)' : ''}
                                                        </td>
                                                        <td>{row.is_slide ? '—' : formatCurrency(row.expected_cap_hit)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </section>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

export default PlayerDetailModal;
