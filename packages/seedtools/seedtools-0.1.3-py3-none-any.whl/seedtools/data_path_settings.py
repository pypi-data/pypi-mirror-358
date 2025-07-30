import os 
from dotenv import load_dotenv,find_dotenv,set_key
from pathlib import Path


env_path =  os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)


def return_data_path():
    return os.getenv("DATA_PATH")


def configure_data_path(new_path,create_new_path=True):
    if os.path.exists(new_path):
         set_key(env_path,"DATA_PATH",new_path)
         print(f"Path setted to : {new_path}")

    elif not os.path.exists(new_path) and  create_new_path:
        Path(new_path).mkdir(parents=True,exist_ok=True)
        set_key(env_path,"DATA_PATH",new_path)
        print(f"Path setted to : {new_path}")
        
    else:
        print("Path not found ... please create that path first")
            
        
        
def reset_path():
    """
    os.sep =>  cross platform sep for windows // and for mac \
        
    """
    default_path =  os.path.join(os.path.expanduser("~"), ".data")  # c:/users/<name>/data
    configure_data_path(default_path)
    
    