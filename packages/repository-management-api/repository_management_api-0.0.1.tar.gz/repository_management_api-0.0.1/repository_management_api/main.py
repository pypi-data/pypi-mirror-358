import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException

from .auth import get_current_username, verifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the directory for git repositories exists
    Path("/srv/git").mkdir(parents=True, exist_ok=True)
    await verifier.init_keys()
    try:
        yield
    finally:
        await verifier.close()


app = FastAPI(lifespan=lifespan)


@app.post("/repos/{repo_name}")
async def create_repo(repo_name: str, username: str = Depends(get_current_username)):
    repo_path = f"/srv/git/{username}/{repo_name}.git"
    Path(repo_path).mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["git", "-C", repo_path, "init", "--bare"], check=True)
        subprocess.run(
            ["git", "-C", repo_path, "config", "http.receivepack", "true"], check=True
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Git error: {e}") from e
    return {"message": "Repository created", "repo": repo_name, "user": username}
