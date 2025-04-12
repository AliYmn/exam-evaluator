import os

import IPython
from traitlets.config import Config

c = Config()

BANNER = r"""

Available Commands:

- %debug          : Enter debug mode
- %history       : Show command history
- %rerun         : Re-run previous command
- %reset         : Reset namespace

"""

# Persistent location for history file - keeping it under libs
HISTORY_DIR = "/app/libs/.ipython_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

# Basic settings
c.InteractiveShell.colors = "LightBG"
c.InteractiveShell.confirm_exit = False
c.TerminalIPythonApp.display_banner = True

# History settings
c.HistoryManager.enabled = True
c.HistoryManager.db_cache_size = 10000
c.HistoryManager.hist_file = os.path.join(HISTORY_DIR, "history.sqlite")
c.InteractiveShell.history_length = 10000
c.InteractiveShell.history_load_length = 10000

# Auto-reload settings
c.InteractiveShellApp.extensions = ["autoreload"]
c.InteractiveShellApp.exec_lines = ["%autoreload 2"]

# Editor and additional features
c.InteractiveShell.editor = "nano"
c.InteractiveShellApp.extensions.append("storemagic")

# Auto-completion settings
c.IPCompleter.greedy = True
c.IPCompleter.use_jedi = True

# Pretty printing settings
c.PlainTextFormatter.max_width = 120
c.PlainTextFormatter.float_precision = "%g"

print(BANNER)
IPython.start_ipython(config=c)
