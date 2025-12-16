Import("env")

# Print message immediately when script is loaded
print("Hello cool dudes normal")

# Ensure ArduinoJson dependency is installed
import subprocess
import os

# Also hook into the build process to ensure it runs
def before_build(source, target, env):
    print("Hello cool dudes before build")

# Hook into the build process before compilation starts
env.AddPreAction("$BUILD_DIR/${PROGNAME}.elf", before_build)

