from app_directory import AppDirectory
app_dir = AppDirectory("apps")
for module_name,module in app_dir.modules.items():
    print(module, module_name)

app_dir.save_app_directory_cache()

reload_app_dir = AppDirectory(
    "apps"
)