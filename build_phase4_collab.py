import os
import json

base_dir = r"d:\Helex"

files = {
    "backend/collab-service/.env.example": """PORT=8003
DATABASE_URL=postgresql://helex_admin:helex_secret@localhost:5432/collab_db
SECRET_KEY=default-secret-key-helex-dev-12345
PROJECT_SERVICE_URL=http://localhost:8002
""",
    
    "backend/collab-service/src/index.js": """const express = require('express');
const { Server } = require('@hocuspocus/server');
const { Database } = require('@hocuspocus/extension-database');
const { Pool } = require('pg');
const jwt = require('jsonwebtoken');
const axios = require('axios');
const dotenv = require('dotenv');

dotenv.config();

const PORT = process.env.PORT || 8003;
const SECRET_KEY = process.env.SECRET_KEY;
const PROJECT_SERVICE_URL = process.env.PROJECT_SERVICE_URL || "http://localhost:8002";

// Setup Postgres
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Initialize DB Table
const initDB = async () => {
  const query = `
    CREATE TABLE IF NOT EXISTS documents (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      project_id UUID NOT NULL,
      file_path TEXT NOT NULL,
      yjs_state BYTEA,
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(project_id, file_path)
    );
  `;
  await pool.query(query);
  console.log("Database initialized");
};
initDB().catch(console.error);

// Hocuspocus Server
const server = Server.configure({
  port: PORT,

  async onAuthenticate(data) {
    const token = data.requestParameters.get('token');
    if (!token) throw new Error("Missing token");
    
    let decoded;
    try {
      decoded = jwt.verify(token, SECRET_KEY);
    } catch (e) {
      throw new Error("Invalid token");
    }
    const userId = decoded.sub;

    // documentName format: {projectId}:{filePath}
    const parts = data.documentName.split(':');
    if (parts.length < 2) throw new Error("Invalid document name format. Expected projectId:filePath");
    const projectId = parts[0];
    const filePath = parts.slice(1).join(':');

    // Call project-service internal API for access check
    try {
      const response = await axios.get(`${PROJECT_SERVICE_URL}/internal/projects/${projectId}/access?user_id=${userId}`);
      if (!response.data.allowed) {
        throw new Error("No access to project");
      }
      
      const role = response.data.role; // OWNER, EDITOR, VIEWER
      
      return {
        user: { id: userId, role: role },
        projectId,
        filePath
      };
    } catch (error) {
      throw new Error("Access check failed or forbidden");
    }
  },

  async onStoreDocument(data) {
    if (data.context.user.role === "VIEWER") {
      return; // Viewers cannot save
    }
    
    const { projectId, filePath } = data.context;
    
    // Save to Postgres
    const query = `
      INSERT INTO documents (project_id, file_path, yjs_state, updated_at) 
      VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
      ON CONFLICT (project_id, file_path) 
      DO UPDATE SET yjs_state = $3, updated_at = CURRENT_TIMESTAMP
    `;
    await pool.query(query, [projectId, filePath, data.documentState]);
  },

  extensions: [
    new Database({
      fetch: async ({ context }) => {
        const { projectId, filePath } = context;
        const result = await pool.query(
          "SELECT yjs_state FROM documents WHERE project_id = $1 AND file_path = $2",
          [projectId, filePath]
        );
        if (result.rows.length > 0 && result.rows[0].yjs_state) {
          return result.rows[0].yjs_state;
        }
        return null;
      },
    }),
  ],
});

const app = express();

app.get('/health', (req, res) => {
  res.send({ status: "ok", service: "collab-service" });
});

// Pass the Express instance to Hocuspocus so it can attach the WebSocket handler to it
server.handle(app);

app.listen(PORT, () => {
  console.log(`Collab service listening on port ${PORT}`);
});
"""
}

for rel_path, content in files.items():
    file_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)

# update package.json scripts
import json
pkg_path = os.path.join(base_dir, "backend/collab-service/package.json")
if os.path.exists(pkg_path):
    with open(pkg_path, "r") as f:
        data = json.load(f)
    data["scripts"] = {
        "start": "node src/index.js",
        "dev": "nodemon src/index.js"
    }
    with open(pkg_path, "w") as f:
        json.dump(data, f, indent=2)

import shutil
shutil.copy(os.path.join(base_dir, "backend/collab-service/.env.example"), os.path.join(base_dir, "backend/collab-service/.env"))

print("Collab service scaffolded.")
