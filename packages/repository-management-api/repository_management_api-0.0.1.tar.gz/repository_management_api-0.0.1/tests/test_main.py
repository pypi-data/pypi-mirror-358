import configparser
import os
import shutil


async def test_create_repo(async_client):
    repo_name = "myrepo"
    user = "testuser"
    repo_dir = f"/srv/git/{user}/{repo_name}.git"
    # Ensure the repo directory does not exist before the test
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    # Call the API to create the repository
    response = await async_client.post(f"/repos/{repo_name}")
    # Check that the response is successful
    assert response.status_code == 200
    # Verify the repo directory was created
    assert os.path.isdir(repo_dir)
    # Check for expected bare repo files
    assert os.path.exists(os.path.join(repo_dir, "HEAD"))
    assert os.path.exists(os.path.join(repo_dir, "config"))
    # Verify the git config has http.receivepack set to true
    config = configparser.ConfigParser()
    config.read(os.path.join(repo_dir, "config"))
    assert config.has_section("http")
    assert config.get("http", "receivepack") == "true"
    # Clean up the created repo directory after the test
    shutil.rmtree(f"/srv/git/{user}")
