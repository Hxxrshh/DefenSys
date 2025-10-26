import React from 'react';
import './LoadingSkeleton.css';

const LoadingSkeleton = ({ type = 'card', count = 1 }) => {
  const renderSkeleton = () => {
    switch (type) {
      case 'card':
        return (
          <div className="skeleton-card">
            <div className="skeleton-header">
              <div className="skeleton-circle"></div>
              <div className="skeleton-line skeleton-line-title"></div>
            </div>
            <div className="skeleton-body">
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line skeleton-line-short"></div>
            </div>
          </div>
        );
      
      case 'stat':
        return (
          <div className="skeleton-stat">
            <div className="skeleton-circle skeleton-icon"></div>
            <div className="skeleton-stat-content">
              <div className="skeleton-line skeleton-line-number"></div>
              <div className="skeleton-line skeleton-line-label"></div>
            </div>
          </div>
        );
      
      case 'table-row':
        return (
          <tr className="skeleton-table-row">
            <td><div className="skeleton-line"></div></td>
            <td><div className="skeleton-line skeleton-line-short"></div></td>
            <td><div className="skeleton-line skeleton-line-short"></div></td>
            <td><div className="skeleton-line skeleton-line-short"></div></td>
            <td><div className="skeleton-line skeleton-line-short"></div></td>
          </tr>
        );
      
      case 'chart':
        return (
          <div className="skeleton-chart">
            <div className="skeleton-line skeleton-line-title"></div>
            <div className="skeleton-chart-body">
              <div className="skeleton-bars">
                {[70, 85, 60, 90, 75].map((height, i) => (
                  <div 
                    key={i} 
                    className="skeleton-bar" 
                    style={{ height: `${height}%` }}
                  ></div>
                ))}
              </div>
            </div>
          </div>
        );
      
      default:
        return <div className="skeleton-line"></div>;
    }
  };

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <React.Fragment key={index}>
          {renderSkeleton()}
        </React.Fragment>
      ))}
    </>
  );
};

export default LoadingSkeleton;
