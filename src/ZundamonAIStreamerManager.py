# To use this class, please install ffmpeg.
from dataclasses import dataclass
from typing import Callable
import time
import math
import threading
import queue
import ZundamonAIStreamer as zasr

streamParams = zasr.streamParams
aiParams = zasr.aiParams
streamerParams = zasr.streamerParams

@dataclass
class params(zasr.params):
  send_message_cb: Callable[[str, str, bool], None] = None
  speaker_type: int = 1
  volume: int = 100

@dataclass
class voicedAnswer():
  user_message: any = ""
  completion: any = ""
  voice: any = None

class ZundamonAIStreamerManager(threading.Thread):
  # Customized sleep for making available of running flag interruption.
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

  def __getItemCB(self, c):
    self.__send_message_cb(key="chat", name=c.author.name, message=c.message)
    pass

  def __get_volume_cb(self):
    return self.__volume

  # callback for getting answer of ChatGPT
  # The voice generated by ZundamonGenerator is given.
  def __speak(self):
    while self.__running:
      while self.__running and self.__voiced_answers_queue.empty():
        self.__interruptibleSleep(0.1)
      voiced_answer = self.__voiced_answers_queue.get()
      user_message = voiced_answer.user_message
      completion = voiced_answer.completion
      voice = voiced_answer.voice

      self.__send_message_cb(key="ask", name=user_message.extern.author.name, message=user_message.message)
      self.__interruptibleSleep(1)
      # Play the voice by VoicePlayer of ZundamonAIStreamer
      self.__player = None
      self.__player = zasr.VoicePlayer(voice, get_volume_cb=self.__get_volume_cb)
      self.__interruptibleSleep(1)
      self.__player.start()
      self.__send_message_cb(key="answer", message=completion.choices[0]["message"]["content"])    
      
      # Wait finishing Playng the voice.
      self.__player.join()
      del self.__player
      self.__player = None
      self.__interruptibleSleep(0.1)

  # callback for getting answer of ChatGPT
  # The voice generated by ZundamonGenerator is given.
  def __answerWithVoiceCB(self, user_message, completion, voice):
    while self.__running and self.__voiced_answers_queue.full():
      self.__interruptibleSleep(0.1)
    self.__voiced_answers_queue.put(voicedAnswer(user_message=user_message, completion=completion, voice=voice))

  @property
  def volume(self):
    return self.__volume
  @volume.setter
  def volume(self, volume):
    self.__volume = volume

  def __init__(self, params):
    self.__send_message_cb = params.send_message_cb
    self.__player = None
    self.__volume = params.volume

    # Set params of getting messages from stream source.
    params.stream_params.get_item_cb=self.__getItemCB

    # Create ZundamonVoiceGenerator
    params.streamer_params.voice_generator=zasr.ZundamonGenerator(speaker=params.speaker_type)
    params.streamer_params.answer_with_voice_cb=self.__answerWithVoiceCB

    # Create ZundamonAIStreamer instance.
    # 'voice_generator=' is omittable for English generator.
    self.ai_streamer =zasr.ZundamonAIStreamer(params)

    self.__voiced_answers_queue = queue.Queue(2)
    self.__speaker_thread = threading.Thread(target=self.__speak, daemon=True)

    super(ZundamonAIStreamerManager, self).__init__(daemon=True)


  def run(self):
    self.__running = True

    # Wake up internal thread to get chat messages from stream and play VoiceVox voices of reading ChatGPT answers aloud.
    self.ai_streamer.start()

    self.__speaker_thread.start()
  
  def disconnect(self):
    self.__running=False

    # Finish generating gTTS voices.
    # Internal thread will stop soon.
    self.ai_streamer.disconnect()

    # terminating internal thread.
    self.ai_streamer.join()

