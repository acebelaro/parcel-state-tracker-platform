# load_config.py
# import yaml
import os

# Access the current PlatformIO build environment execution context
Import("env")

# 🛠️ Automatically install pyyaml inside PlatformIO's environment if missing
try:
    import yaml
except ImportError:
    print("📦 [Config Script] 'yaml' package missing. Installing pyyaml dynamically...")
    env.Execute("$PYTHONEXE -m pip install pyyaml")
    import yaml # Retry importing after installation

config_file = os.path.join(env["PROJECT_DIR"], "app_config.yaml")

if os.path.exists(config_file):
    print(f"🛠️ [Config Script] Parsing variables from {config_file}...")
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        
        if config:
            for key, value in config.items():
                # If the value is a string, wrap it in double quotes so C++ reads it as a literal string
                if isinstance(value, str):
                    env.Append(CPPDEFINES=[(key, env.StringifyMacro(value))])
                else:
                    # For integers, floats, or hex keys, pass them raw
                    env.Append(CPPDEFINES=[(key, value)])
else:
    print("⚠️ [Config Script] app_config.yaml not found! Skipping macro injections.")