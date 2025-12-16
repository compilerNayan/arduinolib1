Import("env")

# Print message immediately when script is loaded
print("Hello cool dudes")

# Ensure ArduinoJson dependency is installed
import subprocess
import os

def ensure_dependency():
    try:
        # Check if ArduinoJson is already installed
        libdeps_dir = os.path.join(env.subst("$PROJECT_DIR"), ".pio", "libdeps", env.subst("$PIOENV"))
        arduinojson_path = os.path.join(libdeps_dir, "ArduinoJson")
        
        if not os.path.exists(arduinojson_path):
            print("Installing ArduinoJson dependency...")
            result = subprocess.run(
                ["pio", "pkg", "install", "--library", "bblanchon/ArduinoJson@^7.2.0"],
                cwd=env.subst("$PROJECT_DIR"),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("ArduinoJson installed successfully")
            else:
                print(f"Warning: Could not install ArduinoJson: {result.stderr}")
    except Exception as e:
        print(f"Warning: Could not check/install ArduinoJson: {e}")

# Ensure dependency is available
ensure_dependency()

# Also hook into the build process to ensure it runs
def before_build(source, target, env):
    print("Hello cool dudes")

# Hook into the build process before compilation starts
env.AddPreAction("$BUILD_DIR/${PROGNAME}.elf", before_build)

