# This is the configuration file for setting up simulation servers.
# The servers should provide an OGC processes api which will be retrieved
# on the fly to provide all existing processes via this api.
import os

platforms = {}

platforms["cut"] = {
  "url":      os.environ.get("MODEL_PLATFORM_URL", "https://api-processes.cut.hcu-hamburg.de"),
  "user":     os.environ.get("MODEL_PLATFORM_USER", "cut"),
  "password": os.environ.get("MODEL_PLATFORM_PASSWORD", "cut"),
  "timeout":  60 * 30
}

