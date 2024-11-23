import React from 'react';

const Card = ({ children }) => {
  return (
    <div className="border rounded shadow-md p-4 bg-white">
      {children}
    </div>
  );
};

Card.Header = ({ children }) => <div className="border-b pb-2 mb-2">{children}</div>;
Card.Title = ({ children }) => <h2 className="text-xl font-bold">{children}</h2>;
Card.Content = ({ children }) => <div>{children}</div>;

export default Card;
