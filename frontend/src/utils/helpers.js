// Format currency values
export const formatCurrency = (value) => {
    if (value == null || value === undefined) return '$0';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
};

// Format player name
export const formatPlayerName = (firstname, lastname) => {
    return `${firstname || ''} ${lastname || ''}`.trim();
};

// Format season year (e.g., 2023-24)
export const formatSeason = (year) => {
    if (!year) return '';
    const nextYear = (year + 1).toString().slice(-2);
    return `${year}-${nextYear}`;
};

// Format percentage
export const formatPercentage = (value, decimals = 2) => {
    if (value == null || value === undefined) return '0%';
    return `${Number(value).toFixed(decimals)}%`;
};

// Format number with commas
export const formatNumber = (value) => {
    if (value == null || value === undefined) return '0';
    return new Intl.NumberFormat('en-US').format(value);
};
