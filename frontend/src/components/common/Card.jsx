import './Card.css';

function Card({ children, className = '', onClick, ...props }) {
    const cardClasses = `card ${onClick ? 'card-clickable' : ''} ${className}`;
    
    return (
        <div className={cardClasses} onClick={onClick} {...props}>
            {children}
        </div>
    );
}

export default Card;
