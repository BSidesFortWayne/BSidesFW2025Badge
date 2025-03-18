from typer import Typer
import os

app = Typer()

@app.command()
def generate_app_cache(app_directory="src/apps"):
    from src.app_directory import AppDirectory
    app_dir = AppDirectory(app_directory)
    for module_name,module in app_dir.modules.items():
        print(module, module_name)
    

    
@app.command()
def deploy_all_to_device(files: list[str] = []):
    # Use mpremote to sync src/ folder to the device root
    # Execute this shell command
    # mpremote cp src/* :

    print("Syncing files to device")
    print(files)

    os.system("mpremote cp src/* :")


def program_name(
    first_name: str,
    last_name: str,
    company: str = "",
    title: str = "",
):
    # Write to temporary JSON file
    with open("name.json", "w") as f:
        f.write(
            f"""
                {{
                    "first_name": "{first_name}",
                    "last_name": "{last_name}",
                    "company": "{company}",
                    "title": "{title}"
                }}
                """
        )
    
    # Execute this shell command
    os.system("uv run mpremote cp name.json :")

if __name__ == "__main__":
    app()
