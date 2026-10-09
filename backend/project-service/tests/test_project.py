import pytest
import uuid
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token
import jwt

# Generate a fake token for testing
def get_fake_token(user_id):
    return jwt.encode({"sub": str(user_id)}, "testsecret", algorithm="HS256")

def test_create_project(client):
    user_id = uuid.uuid4()
    token = get_fake_token(user_id)
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test Project"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data
    
    # Store for next test
    os.environ["TEST_PROJECT_ID"] = data["id"]
    os.environ["TEST_USER_ID"] = str(user_id)

def test_get_project(client):
    project_id = os.environ.get("TEST_PROJECT_ID")
    user_id = os.environ.get("TEST_USER_ID")
    token = get_fake_token(user_id)
    
    response = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == project_id

def test_internal_access(client):
    project_id = os.environ.get("TEST_PROJECT_ID")
    user_id = os.environ.get("TEST_USER_ID")
    
    response = client.get(f"/internal/projects/{project_id}/access?user_id={user_id}")
    assert response.status_code == 200
    assert response.json()["allowed"] == True
    assert response.json()["role"] == "OWNER"

def test_add_file_as_owner(client):
    project_id = os.environ.get("TEST_PROJECT_ID")
    user_id = os.environ.get("TEST_USER_ID")
    token = get_fake_token(user_id)
    
    response = client.post(
        f"/api/v1/projects/{project_id}/files",
        headers={"Authorization": f"Bearer {token}"},
        json={"path": "src/main.py", "is_folder": False}
    )
    assert response.status_code == 201
    assert response.json()["path"] == "src/main.py"
