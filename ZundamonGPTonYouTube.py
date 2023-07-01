# To use this script, please install VOICEVOX and ffmpeg.
import sys
import os
import ZundamonAIStreamerUI as zui

ui = zui.ZundamonAIStreamerUI(workspace=os.path.abspath(os.path.dirname(sys.argv[0])))
ui.mainloop()
