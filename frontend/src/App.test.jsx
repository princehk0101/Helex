import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  it('renders the welcome message', () => {
    render(<App />);
    const headingElement = screen.getByText(/Welcome to Helex/i);
    expect(headingElement).toBeInTheDocument();
  });
});
