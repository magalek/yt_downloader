from pytube import YouTube
from youtubesearchpython import VideosSearch
import dearpygui.dearpygui as dpg
import pickle
import os
from pathlib import Path
#from firebase_integration import Firebase
from moviepy.editor import *
import subprocess
import requests
from version_parser import Version
import signal

#firebase = Firebase()

version = '1.0.1'
new_version_available = False

if os.path.exists(str(Path.home()) + "/downloader_data.dat"):
    with open(str(Path.home()) + "/downloader_data.dat", 'rb') as fp:
        downloader_data = pickle.load(fp)
        #print(downloader_data)
else:
    downloader_data = {"download_path":"", "history":[]}

def build_history():
    history = "DOWNLOAD HISTORY\n"
    history_reversed = downloader_data["history"].copy()
    history_reversed.reverse()
    for idx, record in enumerate(history_reversed):
        history = history + str(idx) + ". " + record['title'] + " | " + record['path'] + "\n"
    return history

def save_data():
    # if firebase.initialized:
    #     firebase.write(downloader_data)

    with open(str(Path.home()) + "/downloader_data.dat", 'wb') as fp:
        pickle.dump(downloader_data, fp)

def DownloadTrack(title):
    if "youtube.com/watch" not in title:
        videosSearch = VideosSearch(title)

        results = videosSearch.result()['result']

        yt_video_id = results[0]['id']
        
        print(results[0]['title'])
        print(yt_video_id)
        
        # link of the video to be downloaded 
        link="https://www.youtube.com/watch?v=" + yt_video_id
    else:
        link = title
        print("downloading: " + link)

    try: 
        yt = YouTube(link) 
        #dpg.set_value("Label", "Downloading " + results[0]['title'] + "...")
        dpg.set_value("Label", "Downloading " + yt.title + "...")
        
        # response = urllib.request.urlopen(yt.streams[0].url)

        # chunk = response.read(16 * 1024)

        

        stream = yt.streams.get_audio_only()
        save_path = dpg.get_value("__path_input")
        downloaded_file = stream.download(save_path)
        audio = AudioFileClip(downloaded_file)
        

        base, ext = os.path.splitext(downloaded_file)
        new_file = base + '.mp3'
        audio.write_audiofile(new_file)
        audio.close()
        os.remove(downloaded_file)
        
        dpg.set_value("Label", "Download completed.")

        downloader_data["history"].append({'title':yt.title, 'path':save_path})
        save_data()
        dpg.set_value("history", build_history())
        dpg.set_value("__input_text", "")
    except Exception as inst: 
        print("Error")
        print(inst)
        dpg.set_value("Label", "Download failed.")
    
def check_for_updates():
    url = 'https://api.github.com/repos/magalek/yt_downloader/releases/latest'

    response = requests.get(url)

    json = response.json()
    release_version = json['name']
    currentVersion = Version(version)
    remoteVersion = Version(release_version)
    new_version_available = remoteVersion > currentVersion
    print(currentVersion)
    print(remoteVersion)
    print("NEW VERSION " + str(new_version_available))
    return new_version_available

def update_module():
    subprocess.Popen("downloader.exe", start_new_session=True)
    dpg.stop_dearpygui()
    dpg.destroy_context()
    sys.exit()

def main():


    #firebase.initialize(os.getlogin())

    update_available = check_for_updates()

    dpg.create_context()

    dpg.create_viewport(width=1000, height=600, title="YT Downloader " + version)

    dpg.setup_dearpygui()

    def update():
        update_module()

    def print_input_text():
        name = dpg.get_value("__input_text")
        print(name)
        DownloadTrack(name)

    def file_dialog_ok_callback(sender, app_data):
        downloader_data["download_path"] = app_data['file_path_name']
        save_data()
        print(downloader_data["download_path"])
        dpg.set_value("__path_input", app_data['file_path_name'])

    def file_dialog_cancel_callback(sender, app_data):
        print('Cancel was clicked.')
        print("Sender: ", sender)
        print("App Data: ", app_data)

    dpg.add_file_dialog(
        directory_selector=True, show=False, callback=file_dialog_ok_callback, tag="file_dialog_id",
        cancel_callback=file_dialog_cancel_callback, width=700 ,height=400)

    width, height, channels, data = dpg.load_image("C:\Projects\Python\http-server\html\img\cat-spinning.gif")

    with dpg.texture_registry(show=True):
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="texture_tag")

    with dpg.window(autosize=True, pos=[0, 0]) as win1:    
        dpg.add_button(label="Select download path", callback=lambda: dpg.show_item("file_dialog_id"))
        dpg.add_input_text(tag="__path_input", height= 60, label="Download path", default_value=downloader_data["download_path"])
        dpg.add_input_text(tag="__input_text", height= 60, label="Video name")
        dpg.add_button(label="Download",callback=print_input_text, height=30)
        dpg.add_text(tag="Label")
        if update_available:
            dpg.add_button(label="Update",callback=update, height=30)
        dpg.add_image("texture_tag")
            
        
    with dpg.window(autosize=True, pos=[500, 0], ) as win2:    
        dpg.add_text(tag="history", default_value=build_history())


    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main() 
