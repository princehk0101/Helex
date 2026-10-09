# Helex - Skills aur Tech Stack Guide

Ye document Helex project par kaam karne wali team ke liye tech stack aur zaroori skills ki detail deta hai.

## 1. Final Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | React, Vite, Tailwind CSS, Monaco Editor, xterm.js, Zustand, React Query |
| **Live sync** | Yjs, y-monaco, y-websocket |
| **Backend** | Python, FastAPI, Pydantic, httpx |
| **Database** | PostgreSQL, SQLAlchemy, Alembic |
| **Cache / events** | Redis (pub/sub) |
| **Auth** | JWT, bcrypt |
| **Real-time** | WebSocket |
| **Sandbox** | Docker |
| **Deploy** | Docker Compose, Nginx, Let’s Encrypt, Linux VPS |
| **Tools** | Git, GitHub, Postman/Swagger, VS Code/Antigravity |
| **Testing** | pytest, Vitest, Playwright |

## 2. Skills: Backend Team

| Skill | Kitna zaroori | Kahan use hoga |
| --- | --- | --- |
| Python basics (functions, classes, async/await) | Bahut | Poora backend |
| FastAPI (routes, dependencies, Pydantic) | Bahut | Har service |
| SQL + PostgreSQL (tables, joins, indexes) | Bahut | Sab databases |
| SQLAlchemy + Alembic | Bahut | Models aur migrations |
| REST API design (status codes, errors) | Bahut | API contract |
| Auth (JWT, password hashing, roles) | Bahut | auth-service, permissions |
| WebSocket | Bahut | Collab, terminal, chat |
| Git/GitHub (branch, PR, merge conflict) | Bahut | Team kaam |
| Docker + Docker Compose | Bahut | Infra, sandbox |
| Microservices basics | Medium | Architecture |
| Redis | Medium | Presence, events |
| Linux commands | Medium | Deploy, debugging |
| Security basics (CORS, path traversal) | Medium | Poora backend |
| Testing (pytest) | Medium | Quality |
| Nginx + HTTPS | Kam | Production |
| CRDT/Yjs ka concept | Kam | collab-service |

## 3. Skills: Frontend Team

| Skill | Kitna zaroori | Kahan use hoga |
| --- | --- | --- |
| HTML, CSS, JavaScript (ES6+) | Bahut | Sab kuch |
| React (components, hooks, props, state) | Bahut | Poora UI |
| Async JS (fetch, promises, async/await) | Bahut | API calls |
| Tailwind CSS | Medium | Styling |
| Monaco Editor | Bahut | Editor |
| Yjs + y-monaco | Bahut | Live sync |
| WebSocket (browser side) | Bahut | Live features |
| State management (Zustand/Context) | Medium | Tabs, user, files |
| React Query / Axios | Medium | Server data |
| React Router | Medium | Pages |
| xterm.js | Medium | Terminal UI |
| Git/GitHub | Bahut | Team kaam |
| TypeScript | Optional | Bade project me |

## 4. Dono ke liye Common Skills
- Git aur GitHub workflow (branch, PR, review)
- API contract padhna aur likhna
- Postman ya Swagger se API test karna
- Debugging (error message padhna, logs dekhna)
- Documentation likhna
- Teamwork: chhote PR, regular sync call

## 5. Priority: Pehle kya seekhein

**Pehle 2 hafte (must):**
- *Backend:* Python + FastAPI basics, SQL
- *Frontend:* JavaScript + React basics
- *Dono:* Git/GitHub

**Phir 2 hafte:**
- *Backend:* SQLAlchemy, JWT auth, Docker basics
- *Frontend:* React hooks, API calls, Tailwind

**Phir project ke saath-saath (just-in-time):**
- WebSocket, Yjs, Monaco, Redis, xterm.js, Nginx
*(Sab kuch pehle seekhne ki zarurat nahi. Project banate-banate seekhna sabse tez hota hai.)*

## 6. Ek member me kitna load

| Member | Top 5 skills jo chahiye |
| --- | --- |
| **Backend 1** | FastAPI, PostgreSQL, JWT/Auth, Docker, Microservices |
| **Backend 2** | WebSocket, Redis, Yjs concept, Docker sandbox, Linux |
| **Frontend 1** | React, Tailwind, React Router, API integration, UI design |
| **Frontend 2** | Monaco, Yjs, WebSocket, xterm.js, State management |

## 7. Free Resources (Search Keywords)
- **Python:** “Python for beginners” (CodeWithHarry, freeCodeCamp)
- **FastAPI:** Official docs ka Tutorial - User Guide (best hai)
- **SQL:** “PostgreSQL tutorial for beginners”
- **React:** Official react.dev Learn section
- **Git:** “Git and GitHub for beginners”
- **Docker:** “Docker tutorial for beginners” (TechWorld with Nana)
- **Yjs:** Official docs docs.yjs.dev

## 8. Self-Check: Aap ready ho ya nahi?
Ye 8 cheezein kar paate ho to project shuru kar sakte ho:
1. [x] Python me function, class, list/dict likh sakte ho
2. [x] Ek simple FastAPI endpoint bana sakte ho
3. [x] SQL me table banakar data insert/select kar sakte ho
4. [x] Git se branch banakar PR khol sakte ho
5. [x] React me ek component banakar button click se state badal sakte ho
6. [x] `fetch` se API call kar sakte ho
7. [x] Docker container chala sakte ho
8. [x] Error message padhkar Google/AI se fix dhundh sakte ho

---

**Meri Suggestion:**
Is project me bahut naye concepts hain. Shuru me:
- **MVP pehle:** sirf Monaco + Yjs live sync + login.
- Terminal, chat, microservices ka split baad me.
- AI ko teacher ki tarah use karo: code ke saath “line by line samjhao” bhi bolo.
