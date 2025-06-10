import yaml
import os

DEFAULT_CONFIG_PATH = '/workspaces/rootzengine/model-config.yaml'
DEFAULT_GDRIVE_MOUNT_PATH = '/mnt/gdrive' # Default if not in model-config.yaml

def load_config(config_path=DEFAULT_CONFIG_PATH):
    """Loads the YAML configuration file."""
    if not os.path.exists(config_path):
        print(f"Warning: Config file not found at {config_path}. Using default project structure on GDrive.")
        # Define a default structure that will be created on GDrive
        return {
            'gdrive_base_path': DEFAULT_GDRIVE_MOUNT_PATH,
            'project_root_on_gdrive': 'RootzEngine', # Name of the main project folder on GDrive
            'mp3_raw_folder': 'data/mp3_raw',       # Relative to project_root_on_gdrive
            'mp3_enriched_folder': 'data/mp3_enriched', # Relative to project_root_on_gdrive
            'mp3_trash_folder': 'data/mp3_trash',     # Relative to project_root_on_gdrive
            'output_folder': 'output'                 # Relative to project_root_on_gdrive
        }
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Ensure essential keys are present, falling back to defaults if necessary
    config.setdefault('gdrive_base_path', DEFAULT_GDRIVE_MOUNT_PATH)
    config.setdefault('project_root_on_gdrive', 'RootzEngine')
    config.setdefault('mp3_raw_folder', 'data/mp3_raw')
    config.setdefault('mp3_enriched_folder', 'data/mp3_enriched')
    config.setdefault('mp3_trash_folder', 'data/mp3_trash')
    config.setdefault('output_folder', 'output')
    return config

def get_project_paths(config):
    """
    Constructs absolute paths for project directories on the mounted Google Drive.
    Example: /mnt/gdrive/RootzEngine/data/mp3_raw
    """
    gdrive_mount_point = config['gdrive_base_path']
    project_root_name = config['project_root_on_gdrive']
    
    base_project_path_on_gdrive = os.path.join(gdrive_mount_point, project_root_name)
    
    paths = {
        'project_root': base_project_path_on_gdrive,
        'raw': os.path.join(base_project_path_on_gdrive, config['mp3_raw_folder']),
        'enriched': os.path.join(base_project_path_on_gdrive, config['mp3_enriched_folder']),
        'trash': os.path.join(base_project_path_on_gdrive, config['mp3_trash_folder']),
        'output': os.path.join(base_project_path_on_gdrive, config['output_folder'])
    }
    return paths

def ensure_project_paths_exist(project_paths):
    """
    Checks if project paths exist on the mounted GDrive and creates them if not.
    This should be called after GDrive is confirmed to be mounted.
    """
    print("Ensuring project paths exist on Google Drive via mount point...")
    for key, path in project_paths.items():
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                print(f"Created directory: {path} (for '{key}')")
            except Exception as e:
                print(f"Error creating directory {path}: {e}. Please check mount point and permissions.")
                # Depending on severity, you might want to raise an error here
        else:
            print(f"Path {path} (for '{key}') already exists.")

if __name__ == '__main__':
    config = load_config()
    print("\\nLoaded Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
        
    project_paths = get_project_paths(config)
    print("\\nConstructed Project Paths (absolute on VM):")
    for key, value in project_paths.items():
        print(f"  {key}: {value}")

    print("\\nAttempting to ensure paths exist (will create if GDrive is mounted and paths don't exist):")
    # IMPORTANT: This will attempt to create directories on your mounted Google Drive.
    # Ensure your Google Drive is mounted at the 'gdrive_base_path' (e.g., /mnt/gdrive)
    # before running this directly for testing.
    if os.path.exists(config['gdrive_base_path']):
        ensure_project_paths_exist(project_paths)
    else:
        print(f"Error: Google Drive base path '{config['gdrive_base_path']}' does not exist on this system.")
        print("Please mount your Google Drive first.")
    
    # Example of how other modules would get paths:
    # raw_mp3_folder = project_paths['raw']
    # print(f"\\nRaw MP3s will be read from: {raw_mp3_folder}")