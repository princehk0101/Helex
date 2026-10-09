import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Workspace from './pages/Workspace';
import Login from './pages/Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/workspace" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/workspace" element={<Workspace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
