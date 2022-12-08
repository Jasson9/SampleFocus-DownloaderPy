import cloudscraper
from bs4 import BeautifulSoup
import requests
import re
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.font as tkfont
import tkinter.filedialog as dialog
import os
import pathlib
import sys
import json

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

# default configuration
defconfig = {
    "overwrite": 0,
    "directory": "None",
    "ontop": 0,
    "linkname": 1,
    "autoopen": 0
}


# to make sure resource loaded after bundled to exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# get appdata directory for each platform
def getdatadir() -> pathlib.Path:
    home = pathlib.Path.home()
    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


# set the directory of configuration file
datadir = getdatadir() / "Sample Focus Downloader"

try:
    datadir.mkdir(parents=True)
except FileExistsError:
    pass


# save configuration file
def saveconf():
    with open(os.path.join(datadir, 'config.json'), 'w') as f:
        json.dump(config, f)


# load configuration file, occur when starting the app
def loadconf():
    with open(os.path.join(datadir, 'config.json')) as t:
        return json.loads(t.read())


try:
    open(os.path.join(datadir, 'config.json'))
except FileNotFoundError:
    with open(os.path.join(datadir, 'config.json'), 'w') as g:
        json.dump(defconfig, g)

config = loadconf()
root = tk.Tk("Sample Focus Preview Downloader", className="Sample Focus Downloader")
root.iconbitmap(resource_path("SampleFocus.ico"))
root.geometry("450x475")
root.resizable(width=False, height=False)
winstat = tk.IntVar()
overwriteval = tk.IntVar()
linknameval = tk.IntVar()
autoopenval = tk.IntVar()


# check directory, useful when directory haven't been set
def chkdir():
    if config['directory'] == 'None':
        try:
            os.mkdir('downloaded')
        except FileExistsError:
            pass
        return os.path.join(os.getcwd(), 'downloaded')
    else:
        return config['directory']


# Download and return filename, if an exception occured return [error, errormessage]
def download(link: str):
    try:
        soup = BeautifulSoup(scraper.get(link).text, features="html.parser")
        url = soup.find('body').find('meta', {"itemprop": "contentUrl"}).get('content')
        if config['linkname'] == 1:
            filename = str(re.search("/.*./.*./(.*.)", link).groups()[0]).replace('-', ' ') + '.mp3'
        else:
            filename = re.search("mp3/(.*.mp3)", url).group(1)
        get = requests.get(url, allow_redirects=True)
        downdir = chkdir()
        if config['overwrite'] == 0:
            dirs = os.listdir(downdir)
            for item in dirs:
                if item == filename:
                    raise Exception(f"Same filename : {filename}")
        open(os.path.join(downdir, filename), 'wb').write(get.content)
    except Exception as e:
        return ['Error', str(e)]
    return filename


# Handler/Command for Always on top
def toggleontop(start=False):
    if start:
        val = config['ontop']
        winstat.set(val)
    else:
        val = winstat.get()
    if 1 == val:
        root.attributes('-topmost', True)
    elif 0 == val:
        root.attributes('-topmost', False)
    config['ontop'] = val
    saveconf()
    return winstat


# Handler/Command to toggle Overwwrite file
def toggleoverwrite(start=False):
    if start:
        overwriteval.set(config['overwrite'])
    else:
        config['overwrite'] = overwriteval.get()
        saveconf()


# Handler/Command to toggle use name from url given
def togglelinkname(start=False):
    if start:
        linknameval.set(config['linkname'])
    else:
        config['linkname'] = linknameval.get()
        saveconf()


# Handler/Command to toggle automatic open
def toggleautoopen(start=False):
    if start:
        autoopenval.set(config['autoopen'])
    else:
        config['autoopen'] = autoopenval.get()
        saveconf()


def instruction(dir):
    return '1. open sample focus from browser \n' \
           '2. copy the sample page url that you want to download \n' \
           '3. paste the url into the input box below\n' \
           '4. click the download button \n\n' \
           f'Download directory : {dir}'


Helv22 = tkfont.Font(family="Helvetica", size=18)
Helv16 = tkfont.Font(family="Helvetica", size=12)
checkboxes = tkfont.Font(size=12)
entry = tk.Entry(root, width=60)
title = tk.Label(root,
                 text="Sample Focus Preview Downloader",
                 font=Helv22
                 )
insttext = tk.StringVar()
insttext.set(instruction(chkdir()))

instlabel = tk.Label(root,
                     textvariable=insttext,
                     font=Helv16,
                     anchor=tk.W,
                     justify='left',
                     wraplength=400
                     )

ontop = tk.Checkbutton(root, text='Always on top',
                       variable=winstat,
                       command=toggleontop,
                       font=checkboxes
                       )

overwrite = tk.Checkbutton(root, text='Overwrite same audio name',
                           variable=overwriteval,
                           command=toggleoverwrite,
                           font=checkboxes
                           )

autoopen = tk.Checkbutton(root, text='Automatically open folder after download',
                          variable=autoopenval,
                          command=toggleautoopen,
                          font=checkboxes
                          )

linkname = tk.Checkbutton(root, text='Use filename from the url',
                          variable=linknameval,
                          command=togglelinkname,
                          font=checkboxes
                          )


# hander/command at download button / when pressing Enter
def callback(self=None):
    if entry.get() == '':
        messagebox.showerror("Error", 'Url Not specified')
    else:
        name = download(entry.get())
        if name[0] == 'Error':
            messagebox.showerror("Error", "Error Message: \n" + name[1])
        else:
            if config['autoopen'] == 1:
                cdir = str(chkdir()).replace("/", "\\")
                os.popen(f'explorer /select, "{os.path.join(cdir, name)}"')
            else:
                messagebox.showinfo("Downloaded", name + ' downloaded')
    entry.delete(0, tk.END)


def opdir():
    if config['directory'] == 'None':
        curdir = os.getcwd()
        os.startfile(os.path.join(curdir, 'downloaded'))
    else:
        os.startfile(config['directory'])


def chdir():
    selectdir = dialog.askdirectory()
    if selectdir != '':
        config['directory'] = selectdir
        saveconf()
        insttext.set(instruction(chkdir()))


downbutton = tk.Button(
    text="Download",
    width=8,
    height=2,
    fg="Black",
    command=callback
)

opendir = tk.Button(
    text="open directory",
    width=12,
    height=2,
    bg="gray",
    command=opdir
)
opendir.place(x=25, y=50)

changedir = tk.Button(
    text="change directory",
    width=12,
    height=2,
    bg="gray",
    command=chdir,
)

# Bind Enter button to download
root.bind('<Return>', callback)

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    toggleontop(start=True)
    toggleoverwrite(start=True)
    togglelinkname(start=True)
    toggleautoopen(start=True)
    title.pack()
    opendir.pack()
    changedir.pack()
    instlabel.pack()
    ontop.pack(anchor='w')
    overwrite.pack(anchor='w')
    autoopen.pack(anchor='w')
    linkname.pack(anchor='w')
    entry.pack()
    downbutton.pack()
    root.mainloop()
