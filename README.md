# Helex

Helex ek collaborative online code editor hai (VS Code jaisa interface), jahan team ke log alag-alag locations se ek hi project par ek saath live code kar sakte hain. Har user ka cursor, naam aur changes real-time me dikhte hain.

## Features
- Login / Register (JWT authentication)
- Projects, team members aur roles (Owner, Editor, Viewer)
- Invite link se team join karna
- Multi-file editor (Monaco Editor, VS Code ka asli editor)
- Real-time sync aur colored cursors (Yjs)
- Browser me terminal aur code run (Docker sandbox)
- Project chat
- Voice/video, Git integration (roadmap me)

## Tech Stack
| Layer | Technology |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS, Monaco Editor, xterm.js |
| Live sync | Yjs, y-monaco |
| Backend | FastAPI (Python), microservices |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Cache / Pub-Sub | Redis |
| Auth | JWT, bcrypt |
| Sandbox | Docker |
| Deployment | Docker Compose, Nginx |

## Architecture
```
Frontend (React + Monaco)
       |
       v
API Gateway (:8000)
       |-- auth-service (:8001) -> auth_db
       |-- project-service (:8002) -> project_db
       |-- collab-service (:8003) -> collab_db + Redis
       |-- terminal-service (:8004) -> Docker sandbox
       |-- chat-service (:8005) -> chat_db (baad me)
```
Har service ka apna database hota hai, aur services aapas me REST ya Redis events se baat karti hain.

## Folder Structure
```
helex/
├── backend/
│   ├── api-gateway/
│   ├── auth-service/
│   ├── project-service/
│   ├── collab-service/
│   ├── terminal-service/
│   ├── chat-service/
│   ├── shared/
│   └── infra/            # docker-compose, nginx, db init
├── frontend/
├── docs/
│   ├── api-contract.md
│   └── architecture.md
├── .github/
├── .gitignore
└── README.md
```

## Prerequisites
Ye sab install hona chahiye:

| Tool | Version |
| --- | --- |
| Python | 3.10+ |
| Node.js | 18 ya 20 |
| Docker + Docker Compose | Latest |
| Git | Latest |

## Getting Started

**1. Repo clone karo**
```bash
git clone https://github.com/princehk0101/Helex.git
cd helex
```

**2. Environment files banao**
Har service me `.env.example` ko copy karke `.env` banao aur values bharo:
```bash
cp backend/auth-service/.env.example backend/auth-service/.env
cp backend/project-service/.env.example backend/project-service/.env
cp backend/collab-service/.env.example backend/collab-service/.env
cp backend/api-gateway/.env.example backend/api-gateway/.env
cp frontend/.env.example frontend/.env
```
Random SECRET_KEY banane ke liye:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
*Sab services me `SECRET_KEY` same rakho, taaki JWT sab verify kar sakein.*

**3. Database aur Redis chalao**
```bash
cd backend/infra
docker compose up -d postgres redis
```

**4. Backend service chalao (example: auth-service)**
```bash
cd backend/auth-service
python -m venv venv
# Windows
venv\Scripts\activate
# Mac / Linux
# source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```
Swagger docs: http://localhost:8001/docs
Baaki services bhi isi tarah apne port par chalao.

**5. Frontend chalao**
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173

**6. Sab kuch ek saath (Docker Compose)**
```bash
cd backend/infra
docker compose up --build
```

## Environment Variables
**Backend service (example):**
| Variable | Matlab |
| --- | --- |
| DATABASE_URL | PostgreSQL connection string |
| SECRET_KEY | JWT sign karne ki key |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token ki expiry |
| ALLOWED_ORIGINS | CORS ke liye frontend URL |
| REDIS_URL | Redis connection |

**Frontend:**
| Variable | Matlab |
| --- | --- |
| VITE_API_URL | API Gateway ka URL |
| VITE_WS_URL | WebSocket URL |

*Kabhi bhi `.env` file Git me push mat karo.*

## Git Workflow
| Branch | Kaam |
| --- | --- |
| `main` | Stable code, seedha push band |
| `develop` | Sab features yahan merge hote hain |
| `feature/<team>-<kaam>` | Naya feature, jaise feature/backend-auth |
| `fix/<team>-<bug>` | Bug fix |

**Roz ka flow:**
```bash
git checkout develop
git pull
git checkout -b feature/backend-auth
# kaam karo
git add .
git commit -m "feat(backend): add login API"
git push -u origin feature/backend-auth
```
Phir GitHub par Pull Request kholo (feature/... to develop), reviewer tag karo, 1 approval ke baad merge.

**Commit message style:**
| Prefix | Use |
| --- | --- |
| `feat:` | Naya feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `refactor:` | Code saaf karna |
| `chore:` | Setup, config |

## Team
| Role | Zimmedari |
| --- | --- |
| Backend 1 | API Gateway, Auth, Shared, Infra |
| Backend 2 | Project, Collab, Terminal services |
| Frontend 1 | Login, Dashboard, Workspace, File Explorer |
| Frontend 2 | Monaco + Yjs, Presence, Terminal UI, Chat |

## Roadmap
- [ ] Phase 1: Monaco + Yjs, 2 tabs me live sync (MVP)
- [ ] Phase 2: Auth, JWT, database
- [ ] Phase 3: Projects, members, roles, invite link
- [ ] Phase 4: File explorer aur multi-file tabs
- [ ] Phase 5: Persistence (Yjs state DB me)
- [ ] Phase 6: Presence aur cursor UI
- [ ] Phase 7: Terminal aur Docker sandbox
- [ ] Phase 8: Chat
- [ ] Phase 9: Deployment (Nginx, HTTPS)
- [ ] Phase 10: Voice/video, Git, AI assistant

## Security Notes
- Passwords sirf bcrypt hash me store hote hain
- User ka code hamesha Docker sandbox me chalta hai (memory, CPU aur network limits ke saath)
- Har API aur WebSocket par permission check
- Production me HTTPS/WSS zaroori hai

## Documentation
- [API Contract](docs/api-contract.md)
- [Architecture](docs/architecture.md)

## Contributing
1. Issue kholo ya existing issue lo
2. Branch banao
3. Chhote, saaf commits karo
4. PR kholo aur review maango
5. Merge ke baad branch delete karo

## License
Abhi decide nahi hua. (MIT, Apache-2.0 ya private rakh sakte ho.)
