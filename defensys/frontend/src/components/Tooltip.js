import React, { useState } from 'react';
import './Tooltip.css';

const Tooltip = ({ text, children, position = 'top' }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div 
      className="tooltip-wrapper"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div className={`custom-tooltip tooltip-${position}`}>
          <div className="tooltip-arrow"></div>
          <div className="tooltip-content">{text}</div>
        </div>
      )}
    </div>
  );
};

export default Tooltip;
