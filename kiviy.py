from kivymd.app import MDApp
from kivy.properties import StringProperty, NumericProperty
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from marquee import Marquee
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
import cv2
import time
import datetime
import os
import threading

from tkinter.filedialog import askopenfilename,askdirectory
from tkinter import Tk
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '200')
Config.write()

def direxist(dir):
    if os.path.isdir(dir) != True:
        os.mkdir(dir)
        return dir
    else:
        a  = f'{dir}(1)'
        return direxist(a)

class Marquee():
    pass

class Completed(MDScreen):
    pass
class Extracting(MDScreen):
    pass

class SelectFileScreen(MDScreen):
    def get_image_one(self):
        Tk().withdraw() # avoids window accompanying tkinter FileChooser
        filename = askopenfilename(
            #initialdir = f"{os.getcwd()}",
            initialdir = "/",
            title = "Select a File",
            filetypes=[
                    ("all video format", ".mp4"),
                    ("all video format", ".webm"),
                    ("all video format", ".mkv"),
                    ("all video format", ".avi")
                ]
        )
        if filename != '':
            MDApp.get_running_app().app_filepath = filename
            self.manager.transition.direction = 'left'
            self.manager.current = 'exdir'
class ExtractDir(MDScreen):
    def get_exdir(self):
        Tk().withdraw() 
        dirname = askdirectory(
            initialdir = "/",
            title = "Select a directory to extract",
        )
        if dirname != '':
            MDApp.get_running_app().extract_dir = dirname
            self.manager.transition.direction = 'left'
            self.manager.current = 'getf'
class GetFramesScreen(MDScreen):
    #Base dir for windows
    #base_dir_for_frames = StringProperty(f"{os.path.join(os.path.expanduser('~'), 'Desktop')}")
    def get_frames(self):  # this is run on the main thread
        self.manager.transition.direction = 'right'
        self.manager.current = 'extracting'
        threading.Thread(target=self.get_frames_thread, daemon=True).start()

    def get_frames_thread(self):  # this is run on a new thread
        start_time = time.time()
        MDApp.get_running_app().file_name = str(os.path.basename(MDApp.get_running_app().app_filepath))
        saved_frame_dir = os.path.join(MDApp.get_running_app().extract_dir,os.path.basename(MDApp.get_running_app().app_filepath)).replace('.','_').replace('\01', '01')
        b = direxist(saved_frame_dir)
        vidcap = cv2.VideoCapture(MDApp.get_running_app().app_filepath)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        MDApp.get_running_app().fps = str(int(fps))
        frame_count = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
        capduration = int(frame_count / fps)
        video_time = str(datetime.timedelta(seconds=capduration))
        MDApp.get_running_app().video_duration = str(video_time)
        success, frame = vidcap.read()
        cont = 1
        remainin_frames = frame_count 
        n_extracted_frames = 0
        while success:
            if cont == 1 or cont % int(fps) == 0:
                seconds1 = (vidcap.get(cv2.CAP_PROP_POS_MSEC)) / (1000)
                rounded_sec = round(seconds1)
                video_time2 = str(datetime.timedelta(seconds=rounded_sec))
                x = video_time2.replace(':', '.')
                formatted = f"frame{cont}_{x}.jpg"
                dd = os.path.join(str(b), formatted)
                cv2.imwrite(dd, frame)
                MDApp.get_running_app().pb = str(cont)
                n_extracted_frames += 1
            success, frame = vidcap.read()
            remainin_frames -= 1
            progressbar_value = 1-(remainin_frames/frame_count)
            MDApp.get_running_app().pb2 = progressbar_value
            cont += 1
        end_time = round(time.time() - start_time)
        print("frame count:"+str(frame_count))
        print("count: " +str(cont))
        MDApp.get_running_app().extracted_total = str(n_extracted_frames)
        MDApp.get_running_app().time_taken = str(datetime.timedelta(seconds=end_time))
        MDApp.get_running_app().saved_path = str(b)
        Clock.schedule_once(self.go_to_completed)  # run the switch to the completed Screen back on the main thread

    def go_to_completed(self, dt):  # this is run on the main thread
        self.manager.transition.direction = 'right'
        self.manager.current = 'completed'

   
class GetframesApp(MDApp):
    app_filepath = StringProperty('Not Set')
    pb = StringProperty('-')
    extract_dir = StringProperty('-')
    extracted_total = StringProperty('-')
    time_taken = StringProperty('-')
    saved_path = StringProperty('-')
    file_name = StringProperty('-')
    fps = StringProperty('-')
    video_duration = StringProperty('-')

    pb2 = NumericProperty(0)
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"
        sm = ScreenManager()
        sm.add_widget(SelectFileScreen(name='file'))
        sm.add_widget(ExtractDir(name = 'exdir'))
        sm.add_widget(GetFramesScreen(name='getf'))
        sm.add_widget(Extracting(name = 'extracting'))
        sm.add_widget(Completed(name = 'completed'))
        
        return sm

GetframesApp().run()