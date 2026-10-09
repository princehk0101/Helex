import React, { useEffect, useRef, useState } from 'react';
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
