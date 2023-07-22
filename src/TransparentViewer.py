from importlib.resources import path
from PIL import Image, ImageTk
import sys
import os
import time
import yaml
import multiprocessing
import tkinter as tk
import tkinter.font as font

multiprocessing.freeze_support()
class TransparentViewer(multiprocessing.Process):
  def __refresh_image(self):
    self.__img_params["base_image"].seek(self.__img_params["cur_frame_index"])
    if self.__root.winfo_width() * self.__img_params["base_image"].height / self.__img_params["base_image"].width > self.__root.winfo_height():
      new_image_width = self.__root.winfo_height() * self.__img_params["base_image"].width / self.__img_params["base_image"].height
      new_image_height = self.__root.winfo_height()
    else:
      new_image_height = self.__root.winfo_width() * self.__img_params["base_image"].height / self.__img_params["base_image"].width
      new_image_width = self.__root.winfo_width()

    self.__canvas.delete("image")

    self.__img_params["resized_image"] = self.__img_params["base_image"].resize([int(new_image_width), int(new_image_height)], Image.Resampling.HAMMING)    
    self.__img_params["photo_image"] = ImageTk.PhotoImage(self.__img_params["resized_image"])
    self.__canvas.configure(width=self.__root.winfo_width(), height=self.__root.winfo_height())
    self.__canvas.create_image( (self.__root.winfo_width() - new_image_width) / 2,
                                (self.__root.winfo_height() - new_image_height) / 2,
                                image=self.__img_params["photo_image"], anchor=tk.NW,
                                tag="image" )

  def __refresh_text(self):
    self.__canvas.delete("text")

    if (self.__txt_params["visible"]):
      self.__canvas.create_text( self.__root.winfo_width(),
                                 self.__root.winfo_height(),
                                 text=self.__txt_params["text"],
                                 font=font.Font(size=str(self.__txt_params["font_size"]), family=self.__txt_params["font_type"], weight="bold"),
                                 anchor=tk.SE, justify=tk.RIGHT,
                                 fill=self.__txt_params["font_color"],
                                 tag="text" )

  def __refresh_canvas(self):
    self.__refresh_image()
    self.__refresh_text()

  def __show_frames(self):
    cur_time = time.time()
    offset_time_ms = int((time.time() - self.__start_time) * 1000)
    rest_time_ms = offset_time_ms % self.__img_params["total_time_ms"]

    frame_index = i = 0
    while (rest_time_ms > 0 and i < self.__img_params["base_image"].n_frames - 1):
      frame_index = i
      rest_time_ms -= self.__img_params["durations"][frame_index]
      i += 1

    self.__img_params["cur_frame_index"] = frame_index

    self.__refresh_image()
    window_duration = int(1000 / self.__win_params["refresh_rate"]) - int((cur_time - self.__prev_time) * 1000)
    min_win_duration = int(667 / self.__win_params["refresh_rate"])
    min_win_duration = 1 if min_win_duration <= 0 else min_win_duration
    if window_duration < min_win_duration:
      window_duration = min_win_duration

    self.__prev_time = cur_time
    if not self.__img_params["decimated_animation"]:
      self.__root.after(window_duration, self.__show_frames)
    else:
      self.__img_params["decimated_animation"] = False
      self.__root.after(int(1000 / self.__win_params["refresh_rate"]), self.__show_frames)

  def __initialize_duration_info(self):
    for i in range(self.__img_params["base_image"].n_frames):
      self.__img_params["base_image"].seek(i)
      self.__img_params["durations"].append(self.__img_params["base_image"].info["duration"])
      self.__img_params["total_time_ms"] += self.__img_params["durations"][i]

  def __play_animation(self):
    if self.__img_params["base_image"].n_frames > 1:
      self.__initialize_duration_info()
      self.__start_time = time.time()
      self.__show_frames()
    else:
      self.__refresh_image()

  def __save_visibility(self, visible):
    variable_cache = {}
    try:
      with open(self.__variable_cache_path, 'r') as file:
        variable_cache = yaml.safe_load(file)
    except:
      pass

    variable_cache["image_window_visible"] = visible

    try:
      with open(self.__variable_cache_path, 'w', encoding='UTF-8') as file:
        yaml.safe_dump(variable_cache, file)
    except:
      pass

  def __apply_visibility(self):
    if self.__win_params["visible_mem"]:
      if self.__win_params["visible_mem"].value:
        cur_visible = True
      else:
        cur_visible = False
    elif self.__win_params["visible"]:
        cur_visible = True
    else:
        cur_visible = False

    if cur_visible and not self.__win_params["prev_visible"]:
      self.__root.deiconify()
      self.__save_visibility(True)
      self.__win_params["prev_visible"] = True
    elif not cur_visible and self.__win_params["prev_visible"]:
      self.__root.withdraw()
      self.__save_visibility(False)
      self.__win_params["prev_visible"] = False

    self.__root.after(200, self.__apply_visibility)

  def __image_window_is_cached(self):
    variable_cache = {}
    try:
      with open(self.__variable_cache_path, 'r') as file:
        variable_cache = yaml.safe_load(file)
    except:
      pass

    return ("image_window_width" in variable_cache or "image_window_height" in variable_cache or
            "image_window_x" in variable_cache or "image_window_y" in variable_cache)

  def __createImageWindow(self):
    self.__img_params["base_image"] = Image.open(self.__img_params["path"])

    self.__root.wm_minsize(width=3, height=3)
    self.__root.title(self.__title)
    self.__root.iconbitmap(default = self.__icon)
    if self.__is_client:
      self.__root.protocol("WM_DELETE_WINDOW", self.__changeVisible)
    self.__root.bind(sequence="<Configure>", func=lambda event:self.__configureWindow(event=event))

    frame = tk.Frame(self.__root)
    frame.pack(fill = tk.BOTH)

    self.__canvas = tk.Canvas(bg=self.__transparent_color)
    self.__canvas.place(x=-2, y=-2)

    default_width = self.__win_params["default_width"]
    default_height = self.__win_params["default_height"]
    default_x = self.__win_params["default_x"]
    default_y = self.__win_params["default_y"]

    if self.__image_window_is_cached():
      width = default_width
      height = default_height
    elif default_width * self.__img_params["base_image"].height / self.__img_params["base_image"].width > default_height:
      width = default_height * self.__img_params["base_image"].width / self.__img_params["base_image"].height
      height = default_height
    else:
      height = default_width * self.__img_params["base_image"].height / self.__img_params["base_image"].width
      width = default_width

    x = default_x
    y = default_y

    self.__root.geometry(f"{int(width)}x{int(height)}+{x}+{y}")
    self.__root.update()
    self.__win_params["prev_width"] = self.__root.winfo_width()
    self.__win_params["prev_height"] = self.__root.winfo_height()

    if not self.__win_params["default_bg_visible"]:
      self.__root.wm_overrideredirect(True)
      self.__root.wm_attributes("-transparentcolor", self.__transparent_color)

    if self.__is_client:
      self.__apply_visibility()
    self.__play_animation()

    self.__root.bind(sequence="<Button-1>", func=lambda event:self.__clickWindow(event=event))
    self.__root.bind(sequence="<B1-Motion>", func=lambda event:self.__moveWindow(event=event))
    self.__root.bind(sequence="<Double-Button-1>", func=lambda event:self.__doubleclickWindow(event=event))

  def __applySettings(self, workspace):
    settings = {}
    with open(self.__setting_path, 'r', encoding='shift_jis') as file:
      settings = yaml.safe_load(file)

    self.__title = settings["image_window_title"]
    self.__transparent_color = settings["image_window_transparent_color"]
    self.__win_params["refresh_rate"] = settings["image_window_refresh_rate"]
    self.__img_params["path"] = os.path.join(workspace, settings["image_file"])
    self.__txt_params["font_color"] = settings["image_window_font_color"]
    self.__txt_params["font_size"] = settings["image_window_font_size"]
    self.__txt_params["font_type"] = settings["image_window_font_type"]
    self.__txt_params["text"] = settings["image_window_label"]

    try:
      with open(self.__variable_cache_path, 'r') as file:
        variable_cache = yaml.safe_load(file)
    except:
      pass

    if "image_window_width" in variable_cache:
      self.__win_params["default_width"] = variable_cache["image_window_width"]
    if "image_window_height" in variable_cache:
      self.__win_params["default_height"] = variable_cache["image_window_height"]
    if "image_window_x" in variable_cache:
      self.__win_params["default_x"] = variable_cache["image_window_x"]
    if "image_window_y" in variable_cache:
      self.__win_params["default_y"] = variable_cache["image_window_y"]
    if "image_bg_visible" in variable_cache:
      self.__win_params["default_bg_visible"] = variable_cache["image_bg_visible"]

    self.__txt_params["visible"] = self.__win_params["default_bg_visible"]

  def __init__(self, visible_mem=None, is_client=False, workspace="./"):
    self.__is_client = is_client
    self.__title = "立ち絵"
    self.__icon = os.path.join(workspace, "zundamon_icon1.ico")
    self.__transparent_color = "#00ff00"
    self.__mouse_position = [0, 0]
    self.__canvas = None
    self.__start_time = 0
    self.__prev_time = 0
    self.__win_params = {}
    self.__win_params["default_width"] = 400
    self.__win_params["default_height"] = 700
    self.__win_params["prev_width"] = 0
    self.__win_params["prev_height"] = 0
    self.__win_params["default_x"] = 50
    self.__win_params["default_y"] = 50
    self.__win_params["visible"] = 1
    self.__win_params["prev_visible"] = not self.__win_params["visible"]
    self.__win_params["visible_mem"] = None
    self.__win_params["default_bg_visible"] = True
    if visible_mem:
      self.__win_params["visible_mem"] = visible_mem
      self.__win_params["prev_visible"] = not visible_mem.value
    self.__win_params["refresh_rate"] = 30
    self.__img_params = {}
    self.__img_params["base_image"] = None
    self.__img_params["resized_image"] = None
    self.__img_params["photo_image"] = None
    self.__img_params["path"] = os.path.join(workspace, "Zundamon.gif")
    self.__img_params["cur_frame_index"] = 0
    self.__img_params["durations"] = []
    self.__img_params["total_time_ms"] = 0
    self.__img_params["decimated_animation"] = False
    self.__txt_params = {}
    self.__txt_params["font_color"] = "#0000ff"
    self.__txt_params["font_size"] = "11"
    self.__txt_params["font_type"] = "Helvetica"
    self.__txt_params["visible"] = "True"
    self.__txt_params["text"] = "ダブルクリックで\n背景透過/非透過を\n切り替えられます"
    self.__setting_path = os.path.join(workspace, "setting.yaml")
    self.__variable_cache_path = os.path.join(workspace, "variable_cache.yaml")
    self.__applySettings(workspace)
    super(TransparentViewer, self).__init__(daemon=True)

  def run(self):
    self.__root = tk.Tk()
    self.__createImageWindow()
    self.__root.mainloop()

  def __changeVisible(self):
    if self.__win_params["visible_mem"]:
      if self.__win_params["visible_mem"].value:
        self.__win_params["visible_mem"].value = False
      else:
        self.__win_params["visible_mem"].value = True
    elif self.__win_params["visible"]:
      self.__win_params["visible"] = False
    else:
      self.__win_params["visible"] = True

  def __clickWindow(self, event):
    self.__mouse_position[0] = event.x_root
    self.__mouse_position[1] = event.y_root

  def __moveWindow(self, event):
    moved_x = event.x_root - self.__mouse_position[0]
    moved_y = event.y_root - self.__mouse_position[1]
    self.__mouse_position[0] = event.x_root
    self.__mouse_position[1] = event.y_root
    cur_position_x = self.__root.winfo_x() + moved_x
    cur_position_y = self.__root.winfo_y() + moved_y
    self.__root.geometry(f"+{cur_position_x}+{cur_position_y}")
 
  def __doubleclickWindow(self, event=None):
    variable_cache = {}
    try:
      with open(self.__variable_cache_path, 'r') as file:
        variable_cache = yaml.safe_load(file)
    except:
      pass

    if self.__root.wm_overrideredirect():
      new_bg_visible = True
      self.__canvas.create_text( self.__root.winfo_width(),
                                 self.__root.winfo_height(),
                                 text=self.__txt_params["text"],
                                 font=font.Font(size=str(self.__txt_params["font_size"]), family=self.__txt_params["font_type"], weight="bold"),
                                 fill=self.__txt_params["font_color"],
                                 anchor=tk.SE, justify=tk.RIGHT,
                                 tag="text" )
      self.__root.wm_attributes("-transparentcolor", "")
      self.__root.wm_overrideredirect(False)
    else:
      new_bg_visible = False
      self.__canvas.delete("text")
      self.__root.wm_attributes("-transparentcolor", self.__transparent_color)
      self.__root.wm_overrideredirect(True)

    variable_cache["image_bg_visible"] = new_bg_visible
    self.__txt_params["visible"] = new_bg_visible

    try:
      with open(self.__variable_cache_path, 'w', encoding='UTF-8') as file:
        yaml.safe_dump(variable_cache, file)
    except:
      pass

  def __configureWindow(self, event=None):
    if self.__img_params["base_image"].n_frames > 1:
      self.__img_params["decimated_animation"] = True
    if self.__win_params["prev_width"] != self.__root.winfo_width() or self.__win_params["prev_height"] != self.__root.winfo_height():
      self.__refresh_canvas()
      self.__win_params["prev_width"] = self.__root.winfo_width()
      self.__win_params["prev_height"] = self.__root.winfo_height()

    variable_cache = {}
    try:
      with open(self.__variable_cache_path, 'r') as file:
        variable_cache = yaml.safe_load(file)
    except:
      pass

    variable_cache["image_window_width"] = self.__root.winfo_width()
    variable_cache["image_window_height"] = self.__root.winfo_height()
    variable_cache["image_window_x"] = self.__root.winfo_x()
    variable_cache["image_window_y"] = self.__root.winfo_y()

    try:
      with open(self.__variable_cache_path, 'w', encoding='UTF-8') as file:
        yaml.safe_dump(variable_cache, file)
    except:
      pass

if __name__ == "__main__":
  is_client = False
  for arg in sys.argv:
    if arg == "-c":
      is_client = True
      break

  manager = multiprocessing.Manager()
  visible = manager.Value('b', True)

  ui = TransparentViewer(visible=visible, is_client=is_client)
  ui.start()
  ui.join()