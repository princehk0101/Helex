import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { email, password });
      localStorage.setItem('token', res.data.access_token);
      navigate('/workspace');
    } catch (err) {
      alert('Login failed');
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-900 text-white">
      <form onSubmit={handleLogin} className="flex flex-col gap-4 p-8 bg-gray-800 rounded-lg">
        <h2 className="text-2xl mb-4">Login to Helex</h2>
        <input 
          type="email" 
          placeholder="Email" 
          className="p-2 text-black rounded"
          value={email} onChange={e => setEmail(e.target.value)} 
        />
        <input 
          type="password" 
          placeholder="Password" 
          className="p-2 text-black rounded"
          value={password} onChange={e => setPassword(e.target.value)} 
        />
        <button type="submit" className="bg-blue-600 p-2 rounded hover:bg-blue-500">Login</button>
      </form>
    </div>
  );
}
