import './Button.css';

function Button({ children, onClick, variant = 'primary', disabled = false, type = 'button', className = '', ...props }) {
    return (
        <button
            className={`btn btn-${variant} ${className}`}
            onClick={onClick}
            disabled={disabled}
            type={type}
            {...props}
        >
            {children}
        </button>
    );
}

export default Button;

