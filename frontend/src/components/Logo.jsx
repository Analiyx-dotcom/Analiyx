import React from 'react';

const Logo = ({ size = 'md', showText = true, className = '' }) => {
  const sizes = {
    xs: 'h-6',
    sm: 'h-8',
    md: 'h-10',
    lg: 'h-14',
    xl: 'h-20',
  };

  return (
    <div className={`flex items-center gap-2 ${className}`} data-testid="analiyx-logo">
      <img
        src="/analiyx-logo.jpg"
        alt="Analiyx"
        className={`${sizes[size]} object-contain`}
      />
    </div>
  );
};

export default Logo;
