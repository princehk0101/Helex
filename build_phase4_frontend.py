import os

base_dir = r"d:\Helex"

files = {
    "frontend/src/App.jsx": """import React from 'react';
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
""",
    
    "frontend/src/pages/Login.jsx": """import React, { useState } from 'react';
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
""",

    "frontend/src/pages/Workspace.jsx": """import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import { MonacoBinding } from 'y-monaco';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8003';
// For testing Phase 4 MVP
const PROJECT_ID = 'test-project-123';
const FILE_PATH = 'src/main.py';

export default function Workspace() {
  const editorRef = useRef(null);
  const navigate = useNavigate();
  const [error, setError] = useState('');
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
    }
  }, [navigate]);

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    const token = localStorage.getItem('token');
    
    // Initialize Yjs
    const ydoc = new Y.Doc();
    const provider = new WebsocketProvider(
      WS_URL,
      `${PROJECT_ID}:${FILE_PATH}`,
      ydoc,
      { params: { token } }
    );

    provider.on('status', event => {
      if (event.status === 'connected') {
        console.log('Yjs connected');
      } else if (event.status === 'disconnected') {
        console.log('Yjs disconnected');
      }
    });

    provider.on('connection-error', () => {
      setError('Connection failed. Are you authorized?');
    });

    const ytext = ydoc.getText('monaco');
    const binding = new MonacoBinding(
      ytext,
      editor.getModel(),
      new Set([editor]),
      provider.awareness
    );

    // Provide random username/color for awareness (will be fetched from /me later)
    const colors = ['#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', '#03a9f4', '#00bcd4', '#009688', '#4caf50', '#8bc34a', '#cddc39', '#ffeb3b', '#ffc107', '#ff9800', '#ff5722', '#795548', '#9e9e9e', '#607d8b'];
    provider.awareness.setLocalStateField('user', {
      name: `User ${Math.floor(Math.random() * 100)}`,
      color: colors[Math.floor(Math.random() * colors.length)]
    });

    return () => {
      binding.destroy();
      provider.destroy();
      ydoc.destroy();
    };
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      <div className="p-4 bg-gray-800 flex justify-between">
        <h1 className="text-xl font-bold">Helex Workspace</h1>
        {error && <span className="text-red-500">{error}</span>}
        <button onClick={() => { localStorage.clear(); navigate('/login'); }} className="text-sm text-gray-400 hover:text-white">Logout</button>
      </div>
      <div className="flex-1">
        <Editor
          height="100%"
          defaultLanguage="python"
          theme="vs-dark"
          onMount={handleEditorDidMount}
        />
      </div>
    </div>
  );
}
""",
    
    "frontend/.env": """VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8003
"""
}

for rel_path, content in files.items():
    file_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)

# We need to remove the App.test.jsx since it tests the old App.jsx which is gone now
try:
    os.remove(os.path.join(base_dir, "frontend/src/App.test.jsx"))
except:
    pass

print("Phase 4 frontend basic setup done.")
