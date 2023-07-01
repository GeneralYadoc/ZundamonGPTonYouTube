from dataclasses import dataclass
import ZundamonAIStreamerManager as zm
import sys
import os
import math
import time
import yaml
import queue
import subprocess
import tkinter as tk
import tkinter.font as font

@dataclass
class messageSlot():
  message: str
  refresh: bool

class ZundamonAIStreamerUI:
  def __createStartWindow(self):
    self.__root.geometry('336x120')
    self.__root.title('なんでもこたえてくれるずんだもん')

    self.__clearStartWindow()
    self.__widgits_start["video_id_label"] = tk.Label(text='Video ID')
    self.__widgits_start["video_id_label"].place(x=30, y=15)
    self.__widgits_start["video_id_entry"] = tk.Entry(width=32)
    self.__widgits_start["video_id_entry"].place(x=90, y=15)

    self.__widgits_start["api_key_label"] = tk.Label(text='API Key')
    self.__widgits_start["api_key_label"].place(x=30, y=48)
    self.__widgits_start["api_key_entry"] = tk.Entry(width=32)
    self.__widgits_start["api_key_entry"].place(x=90, y=48)

    self.__widgits_start["button"] = tk.Button(self.__root, text="すたーと", command=self.__start)
    self.__widgits_start["button"].place(x=143, y=80)

  def __clearStartWindow(self):
    for widgit in self.__widgits_start.values():
      widgit.destroy()
    self.__widgits_start.clear()

  def __createMainWindow(self):
    self.__root.geometry('336x120')
    self.__root.title('めいんういんどう')
    self.__root.iconbitmap(default = self.__icon)

    self.__clearMainWindow()
    self.__widgits_main["buttonChat"] = tk.Button(self.__root, text="ちゃっと", width="6", command=lambda:self.__changeVisible("chat"))
    self.__widgits_main["buttonChat"].place(x=30, y=20)

    self.__widgits_main["buttonAsk"] = tk.Button(self.__root, text="しつもん", width="6", command=lambda:self.__changeVisible("ask"))
    self.__widgits_main["buttonAsk"].place(x=104, y=20)

    self.__widgits_main["buttonAnswer"] = tk.Button(self.__root, text="こたえ", width="6", command=lambda:self.__changeVisible("answer"))
    self.__widgits_main["buttonAnswer"].place(x=178, y=20)

    self.__widgits_main["buttonPortrait"] = tk.Button(self.__root, text="立ち絵", width="6", command=self.__changeVisiblePortrait)
    self.__widgits_main["buttonPortrait"].place(x=252, y=20)

    self.__widgits_main["volumeLabel"] = tk.Label(text='volume')
    self.__widgits_main["volumeLabel"].place(x=27, y=70)
    self.__widgits_main["scaleVolume"] = tk.Scale( self.__root,
                                                   variable = tk.DoubleVar(),
                                                   command = self.__changeVolume,
                                                   orient=tk.HORIZONTAL,
                                                   sliderlength = 20,
                                                   length = 200,
                                                   from_ = 0,
                                                   to = 500,
                                                   resolution=5,
                                                   tickinterval=250 )

    self.__widgits_main["scaleVolume"].set(self.__initial_volume)
    self.__widgits_main["scaleVolume"].place(x=72, y=50)

    self.__widgits_main["volumeEntry"] = tk.Entry(width=3, justify=tk.RIGHT)
    self.__widgits_main["volumeEntry"].bind(sequence="<Return>", func=self.__scaleVolume)
    self.__widgits_main["volumeEntry"].place(x=282, y=70)

    self.__receiveMessage()

  def __clearMainWindow(self):
    for widgit in self.__widgits_main.values():
      widgit.destroy()
    self.__widgits_main.clear()

  def __createMessageWindow(self, key):
    window = tk.Toplevel()
    window.title(self.__sub_window_settings[key]["title"])
    window.geometry(self.__sub_window_settings[key]["window_size"])
    window.protocol("WM_DELETE_WINDOW", lambda:self.__changeVisible(key))
    
    frame = tk.Frame(window)
    frame.pack(fill = tk.BOTH)

    text = tk.Text( frame,
                    bg=self.__sub_window_settings[key]["window_color"],
                    fg=self.__sub_window_settings[key]["font_color"],
                    selectbackground=self.__sub_window_settings[key]["window_color"],
                    selectforeground=self.__sub_window_settings[key]["font_color"],
                    width=800,
                    height=100,
                    bd="0",
                    padx=self.__sub_window_settings[key]["window_padx"],
                    pady=self.__sub_window_settings[key]["window_pady"],
                    font=font.Font( size=self.__sub_window_settings[key]["font_size"],
                                    family=self.__sub_window_settings[key]["font_type"],
                                    weight="bold" ),
                    state="disabled" )


    self.__sub_windows[key] = {
      "visible" : False,
      "body" : window,
      "text" : text,
      "mouse_position" : [0, 0],
      "message_queue" : queue.Queue(1000)
    }
    self.__sub_windows[key]["body"].bind(sequence="<Button-1>", func=lambda event:self.__clickWindow(key=key, event=event))
    self.__sub_windows[key]["body"].bind(sequence="<B1-Motion>", func=lambda event:self.__moveWindow(key=key, event=event))
    self.__sub_windows[key]["body"].bind(sequence="<Double-Button-1>", func=lambda event:self.__doubleclickWindow(key=key, event=event))
    self.__sub_windows[key]["text"].pack()
    self.__sub_windows[key]["body"].withdraw()

  def __interruptibleSleep(self, time_sec):
    counter = math.floor(time_sec / 0.10)
    frac = time_sec - (counter * 0.10)
    for i in range(counter):
      if not self.__running:
        break
      time.sleep(0.10)
    if not self.__running:
      return
    time.sleep(frac)

  def __sendMessageCore(self, key, message, refresh):
    message_queue = self.__sub_windows[key]["message_queue"]
    if not message_queue.full():
      slot = messageSlot(message=message, refresh=refresh)
      message_queue.put(slot)

  def __sendMessage(self, key, name="", message=""):
    rendering_method = self.__sub_window_settings[key]["rendering_method"]
    display_name = self.__sub_window_settings[key]["display_name"]

    if display_name == 'True':
      message = f"[{name}] {message}"

    if rendering_method == "incremental":
      for i in range(len(message)):
        refresh = True if i == 0  else False
        self.__sendMessageCore(key, message[i : i+1], refresh)
        self.__interruptibleSleep(0.10)
    else:
      refresh = True if rendering_method == "refresh" else False
      if not refresh:
        message = f"\n{message}\n"
      self.__sendMessageCore(key, message, refresh)

  def __showMessage(self, text, message, refresh):
    text.configure(state="normal")
    try:
      pos = text.index('end')
    except:
      return
    
    if refresh:
      text.delete('1.0', 'end')
      pos = text.index('end')
    
    text.insert(pos, message)
    text.see("end")
    text.configure(state="disabled")
 
  def __receiveMessage(self):
    for key in self.__sub_windows.keys():
      message_queue = self.__sub_windows[key]["message_queue"]
      text = self.__sub_windows[key]["text"]
      while not message_queue.empty():
        slot = message_queue.get()
        self.__showMessage(text, slot.message, slot.refresh)

    self.__root.after(ms=33, func=self.__receiveMessage)

  def __init__(self, workspace="./"):
    self.__running = False
    self.__variable_cache_path = os.path.join(workspace, "variable_cache.yaml")
    self.__setting_path = os.path.join(workspace, "setting.yaml")

    variable_cache = {}
    try:
      with open(self.__variable_cache_path, 'r') as file:
        variable_cache = yaml.safe_load(file)
    except:
      variable_cache["video_id"] = ""
      variable_cache["api_key"] = ""
    
    with open(self.__setting_path, 'r', encoding='shift_jis') as file:
      settings = yaml.safe_load(file)

    self.__voicevox_path = settings['voicevox_path']

    self.__sub_window_settings = {}
    self.__sub_window_settings["chat"] = {}
    self.__sub_window_settings["chat"]["display_user_name"] = settings["display_user_name_on_chat_window"]
    self.__sub_window_settings["chat"]["title"] = settings["chat_window_title"]
    self.__sub_window_settings["chat"]["window_size"] = settings["chat_window_size"]
    self.__sub_window_settings["chat"]["window_padx"] = settings["chat_window_padx"]
    self.__sub_window_settings["chat"]["window_pady"] = settings["chat_window_pady"]
    self.__sub_window_settings["chat"]["window_color"] = settings["chat_window_color"]
    self.__sub_window_settings["chat"]["font_color"] = settings["chat_font_color"]
    self.__sub_window_settings["chat"]["font_size"] = settings["chat_font_size"]
    self.__sub_window_settings["chat"]["font_type"] = settings["chat_font_type"]
    self.__sub_window_settings["chat"]["rendering_method"] = settings["chat_rendering_method"]
    self.__sub_window_settings["chat"]["display_name"] = settings["display_user_name_on_chat_window"]

    self.__sub_window_settings["ask"] = {}
    self.__sub_window_settings["ask"]["display_user_name"] = settings["display_user_name_on_ask_window"]
    self.__sub_window_settings["ask"]["title"] = settings["ask_window_title"]
    self.__sub_window_settings["ask"]["window_size"] = settings["ask_window_size"]
    self.__sub_window_settings["ask"]["window_padx"] = settings["ask_window_padx"]
    self.__sub_window_settings["ask"]["window_pady"] = settings["ask_window_pady"]
    self.__sub_window_settings["ask"]["window_color"] = settings["ask_window_color"]
    self.__sub_window_settings["ask"]["font_color"] = settings["ask_font_color"]
    self.__sub_window_settings["ask"]["font_size"] = settings["ask_font_size"]
    self.__sub_window_settings["ask"]["font_type"] = settings["ask_font_type"]
    self.__sub_window_settings["ask"]["rendering_method"] = settings["ask_rendering_method"]
    self.__sub_window_settings["ask"]["display_name"] = settings["display_user_name_on_ask_window"]

    self.__sub_window_settings["answer"] = {}
    self.__sub_window_settings["answer"]["title"] = settings["answer_window_title"]
    self.__sub_window_settings["answer"]["window_size"] = settings["answer_window_size"]
    self.__sub_window_settings["answer"]["window_padx"] = settings["answer_window_padx"]
    self.__sub_window_settings["answer"]["window_pady"] = settings["answer_window_pady"]
    self.__sub_window_settings["answer"]["window_color"] = settings["answer_window_color"]
    self.__sub_window_settings["answer"]["font_color"] = settings["answer_font_color"]
    self.__sub_window_settings["answer"]["font_size"] = settings["answer_font_size"]
    self.__sub_window_settings["answer"]["font_type"] = settings["answer_font_type"]
    self.__sub_window_settings["answer"]["rendering_method"] = settings["answer_rendering_method"]
    self.__sub_window_settings["answer"]["display_name"] = False

    stream_params = zm.streamParams(
      video_id = variable_cache["video_id"],
    )

    ai_params = zm.aiParams(
      api_key = variable_cache["api_key"],
      model = settings["model"],
      system_role = settings["system_role"],
      max_tokens_per_request = settings["max_tokens_per_request"],
      interval_sec = settings["ask_interval_sec"]
    )

    volume = (lambda v: 0 if v < 0 else 500 if v > 500 else v)(settings['volume'])

    self.__zm_streamer_params = zm.params( stream_params=stream_params,
                                           ai_params=ai_params,
                                           speaker_type = settings["speaker_type"],
                                           volume=volume,
                                           send_message_cb=self.__sendMessage )

    self.__manager = None
    self.__root = tk.Tk()
    self.__root.resizable(False, False)
    self.__root.protocol("WM_DELETE_WINDOW", self.__close)
    self.__initial_volume = volume
    self.__icon = os.path.join(workspace, "zundamon_icon1.ico")
    self.__widgits_start = {}
    self.__widgits_main = {}
    self.__sub_windows = {}
    self.__image_command_path = os.path.join(workspace, "TransparentViewer.exe")
    self.__image_command_args = "-c"
    self.__portrait_window_process = None
    self.__portrait_image_file = settings["image_file"]
    self.__portrait_visible_file_path = os.path.join(workspace, "viewer_visible.txt")
    try:
      os.remove(self.__portrait_visible_file_path)
    except:
      pass
    self.__createStartWindow()

  def __start(self):
    self.__running = True

    variables = {}
    if self.__widgits_start["video_id_entry"].get() == "":
      variables["video_id"] = self.__zm_streamer_params.stream_params.video_id
    else:
      variables["video_id"] = self.__widgits_start["video_id_entry"].get()
      self.__zm_streamer_params.stream_params.video_id = variables["video_id"]
    if self.__widgits_start["api_key_entry"].get() == "":
      variables["api_key"] = self.__zm_streamer_params.ai_params.api_key
    else:
      variables["api_key"] = self.__widgits_start["api_key_entry"].get()
      self.__zm_streamer_params.ai_params.api_key = variables["api_key"]

    file = open(self.__variable_cache_path, 'w', encoding='UTF-8')
    yaml.safe_dump(variables, file)
    file.close()

    self.__root.title("めいんういんどう")
    self.__clearStartWindow()
    self.__createMainWindow()
    self.__createMessageWindow(key = "chat")
    self.__createMessageWindow(key = "ask")
    self.__createMessageWindow(key = "answer")

    visible_file_generated = False

    while (not visible_file_generated):
      try:
        file = open(self.__portrait_visible_file_path, mode='w')
      except:
        continue
      file.write("false")
      file.close()
      visible_file_generated = True

    self.__portrait_window_process = subprocess.Popen(f"{self.__image_command_path} {self.__image_command_args} {self.__portrait_image_file}")

    self.__manager = zm.ZundamonAIStreamerManager(self.__zm_streamer_params)
    self.__manager.start()

  def __changeVolume(self, event=None):
    volume = int(self.__widgits_main["scaleVolume"].get())
    self.__widgits_main["volumeEntry"].delete(0, tk.END)
    self.__widgits_main["volumeEntry"].insert(0, str(volume))
    if self.__manager:
      self.__manager.volume = volume

  def __scaleVolume(self, event=None):
    volume_str = self.__widgits_main["volumeEntry"].get()
    try:
      volume = int(volume_str)
    except:
      return
    
    volume = (lambda v: 0 if v < 0 else 500 if v > 500 else v)(volume)
    
    self.__widgits_main["volumeEntry"].delete(0, tk.END)
    self.__widgits_main["volumeEntry"].insert(0, str(volume))

    self.__widgits_main["scaleVolume"].set(volume)

  def __changeVisible(self, key):
    if self.__sub_windows[key]["visible"]:
      self.__sub_windows[key]["visible"] = False
      self.__sub_windows[key]["body"].withdraw()
    else:
      self.__sub_windows[key]["visible"] = True
      self.__sub_windows[key]["body"].deiconify()

  def __changeVisiblePortrait(self):
    try:
      file = open(self.__portrait_visible_file_path, mode='r')
    except:
      self.__root.after(ms=33, func=self.__changeVisiblePortrait)
      return
    
    visible_str = file.readline().splitlines()[0]
    visible = True if visible_str == "true" else False

    try:
      file = open(self.__portrait_visible_file_path, mode='w')
    except:
      self.__root.after(ms=33, func=self.__changeVisiblePortrait)
      return

    visible = not visible
    file.write("true" if visible else "false")
    file.close()
  
  def __clickWindow(self, key, event):
    self.__sub_windows[key]["mouse_position"][0] = event.x_root
    self.__sub_windows[key]["mouse_position"][1] = event.y_root

  def __moveWindow(self, key, event):
    moved_x = event.x_root - self.__sub_windows[key]["mouse_position"][0]
    moved_y = event.y_root - self.__sub_windows[key]["mouse_position"][1]
    self.__sub_windows[key]["mouse_position"][0] = event.x_root
    self.__sub_windows[key]["mouse_position"][1] = event.y_root
    cur_position_x = self.__sub_windows[key]["body"].winfo_x() + moved_x
    cur_position_y = self.__sub_windows[key]["body"].winfo_y() + moved_y
    self.__sub_windows[key]["body"].geometry(f"+{cur_position_x}+{cur_position_y}")
    pass
  
  def __doubleclickWindow(self, key, event=None):
    self.__sub_windows[key]["body"].wm_overrideredirect(not self.__sub_windows[key]["body"].wm_overrideredirect())

  def __close(self):
    self.__running = False

    if self.__portrait_window_process:
      self.__portrait_window_process.kill()
    if self.__manager:
      self.__manager.disconnect()
      self.__manager.join()
    self.__root.destroy()
    try:
      os.remove(self.__portrait_visible_file_path)
    except:
      pass

  def mainloop(self):
    self.__root.mainloop()

if __name__ == "__main__":
  ui = ZundamonAIStreamerUI(workspace=os.path.abspath(os.path.dirname(sys.argv[0])))
  ui.mainloop()
