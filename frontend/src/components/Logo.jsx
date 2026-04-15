import React from 'react';

const Logo = ({ size = 'md', className = '' }) => {
  const sizes = {
    xs: 'h-6',
    sm: 'h-8',
    md: 'h-10',
    lg: 'h-14',
    xl: 'h-20',
  };

  return (
    <img
      src="/analiyx-logo.jpg"
      alt="Analiyx"
      className={`${sizes[size]} object-contain mix-blend-lighten ${className}`}
      data-testid="analiyx-logo"
    />
  );
};

export default Logo;
