import React from 'react';
import { Loader2 } from 'lucide-react';

const Button = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  type = 'button',
  icon: Icon,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-hover focus:ring-primary shadow-lg shadow-primary/20 hover:shadow-primary/40',
    secondary: 'bg-secondary text-background hover:bg-opacity-90 focus:ring-secondary',
    outline: 'border-2 border-border bg-transparent text-text-primary hover:border-primary hover:text-primary focus:ring-primary',
    ghost: 'bg-transparent text-text-secondary hover:bg-surface-hover hover:text-text-primary focus:ring-surface-hover',
    danger: 'bg-error text-white hover:bg-opacity-90 focus:ring-error shadow-lg shadow-error/20',
  };

  const sizes = {
    sm: 'text-sm px-3 py-1.5 gap-1.5',
    md: 'text-base px-5 py-2.5 gap-2',
    lg: 'text-lg px-8 py-3.5 gap-2.5',
  };

  return (
    <button
      type={type}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      onClick={onClick}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="animate-spin w-5 h-5" />}
      {!isLoading && Icon && <Icon className="w-5 h-5" />}
      {children}
    </button>
  );
};

export default Button;
