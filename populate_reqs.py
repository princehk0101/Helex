import os

base_dir = r"d:\Helex"

reqs = {
    "backend/api-gateway/requirements.txt": "fastapi\nuvicorn[standard]\nhttpx\npyjwt\npython-dotenv\n",
    "backend/auth-service/requirements.txt": "fastapi\nuvicorn[standard]\nsqlalchemy\npsycopg2-binary\nalembic\npyjwt\npasslib[bcrypt]\npython-dotenv\n",
    "backend/project-service/requirements.txt": "fastapi\nuvicorn[standard]\nsqlalchemy\npsycopg2-binary\nalembic\nhttpx\npython-dotenv\n",
    "backend/collab-service/requirements.txt": "fastapi\nuvicorn[standard]\nsqlalchemy\npsycopg2-binary\nredis\nwebsockets\npython-dotenv\n",
    "backend/terminal-service/requirements.txt": "fastapi\nuvicorn[standard]\nwebsockets\ndocker\npython-dotenv\n"
}

for rel_path, content in reqs.items():
    file_path = os.path.join(base_dir, rel_path)
    with open(file_path, "w") as f:
        f.write(content)

print("Requirements populated.")
