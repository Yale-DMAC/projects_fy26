from asnake.client import ASnakeClient
import yaml
from pathlib import Path

def load_config():
    """Loads the conn.yml file - where relevant passwords, URLs, and usernames are kept."""

    yaml_file = Path(__file__).resolve().parent / "conn.yml"

    with yaml_file.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
    
def connect(env):
    """User calls for this function indicating either production or test for the relevant environment. 
    Returns an API connection using asnake that can be used to make API calls."""

    global client
    config = load_config()
    
    try:
        client = ASnakeClient(baseurl=config.get(env), username=config.get('username'), password=config.get('password'))
        client.authorize()
        return True
    except:
        return False
    