import os
import json
import subprocess
import sys
import time

try:
    import psutil
except ImportError:
    psutil = None

API_KEY_CONFIG_PATH = ["mcpServers", "klaviyo", "env", "PRIVATE_API_KEY"]
IS_WINDOWS = os.name == "nt"


class Client:
    def __init__(
        self,
        app_name,
        config_path_mac,
        config_path_windows,
        app_path_mac,
        app_path_windows,
    ):
        self.app_name = app_name
        self.config_path = config_path_windows if IS_WINDOWS else config_path_mac
        self.app_path = app_path_windows if IS_WINDOWS else app_path_mac

    def set_api_key_in_config(self, api_key):
        with open(self.config_path, "r") as f:
            config = json.load(f)

        # Ensure the path exists
        d = config
        for key in API_KEY_CONFIG_PATH[:-1]:
            if key not in d or not isinstance(d[key], dict):
                d[key] = {}
            d = d[key]

        d[API_KEY_CONFIG_PATH[-1]] = api_key
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def remove_api_key_from_config(self):
        with open(self.config_path, "r") as f:
            config = json.load(f)

        d = config
        for key in API_KEY_CONFIG_PATH[:-1]:
            d = d.get(key, {})

        if API_KEY_CONFIG_PATH[-1] in d:
            del d[API_KEY_CONFIG_PATH[-1]]

        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def is_running(self):
        if psutil:
            for proc in psutil.process_iter(["name"]):
                try:
                    if proc.info["name"] and self.app_name in proc.info["name"]:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        else:
            if IS_WINDOWS:
                out = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {self.app_name}.exe"],
                    capture_output=True,
                    text=True,
                )
                return f"{self.app_name}.exe" in out.stdout
            else:
                out = subprocess.run(
                    ["pgrep", "-x", self.app_name], capture_output=True
                )
                return out.returncode == 0

    def quit(self):
        if IS_WINDOWS:
            subprocess.run(["taskkill", "/F", "/IM", f"{self.app_name}.exe"])
        else:
            # Use AppleScript to quit app gracefully
            subprocess.run(
                ["osascript", "-e", f'tell application "{self.app_name}" to quit']
            )

    def launch(self):
        if IS_WINDOWS:
            subprocess.Popen([self.app_name])
        else:
            # Use 'open' to launch the app on macOS
            subprocess.Popen(["open", "-a", self.app_name])

    def run(self):
        # TODO: ensure this works on Windows, then remove this
        if IS_WINDOWS:
            print("This script does not yet support Windows.")
            exit(1)

        if len(sys.argv) < 2:
            print(
                "Must pass the name of the environment variable with your Klaviyo API key as the first argument."
            )
            exit(1)

        api_key_env = sys.argv[1]
        api_key = os.environ.get(api_key_env)
        if not api_key:
            print(f"Environment variable {api_key_env} not set.")
            exit(1)

        self.set_api_key_in_config(api_key)
        print("API key set in config.")

        # If app is running, quit it and wait for it to exit
        if self.is_running():
            print(
                f"{self.app_name} is already running. Quitting it to reload config..."
            )
            self.quit()
            # Wait for it to fully exit
            while self.is_running():
                time.sleep(1)
            print(f"{self.app_name} has exited.")

        print(f"Launching {self.app_name}...")
        self.launch()
        # Wait for app to exit
        time.sleep(5)
        try:
            print(f"Waiting for {self.app_name} to exit...")
            while self.is_running():
                time.sleep(2)
        finally:
            print(f"{self.app_name} exited. Cleaning up config...")
            self.remove_api_key_from_config()
            print("API key removed from config.")


def run_claude():
    client = Client(
        app_name="Claude",
        config_path_mac=os.path.expanduser(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        ),
        app_path_mac="/Applications/Claude.app",
        config_path_windows=os.path.expanduser(
            "~\AppData\Roaming\Claude\claude_desktop_config.json"
        ),
        app_path_windows=os.path.expanduser(
            r"~\AppData\Local\Programs\Claude\Claude.exe"
        ),
    )
    client.run()


def run_cursor():
    client = Client(
        app_name="Cursor",
        config_path_mac=os.path.expanduser("~/.cursor/mcp.json"),
        app_path_mac="/Applications/Cursor.app",
        config_path_windows=os.path.expanduser("~\AppData\Roaming\Cursor\mcp.json"),
        app_path_windows=os.path.expanduser(
            r"~\AppData\Local\Programs\Cursor\Cursor.exe"
        ),
    )
    client.run()
