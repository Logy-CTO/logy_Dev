import tkinter as tk
import sys
import pickle
import cv2
import PIL.Image
import PIL.ImageTk

from sys import platform

import os
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, BooleanVar, IntVar
from PIL import Image, ImageTk

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\홍택수SSD\Downloads\logyproject-main\assets\frame2")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
window.geometry("350x322")
window.configure(bg = "#FFFFFF")

canvas = Canvas(window, bg="#FFFFFF", height=322, width=350, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)


def set_advanced(window, param):
    param["switch_advanced"] = True
    window.quit()

# ----------------카메라 인터페이스 추가, 크기 : 320, 240(07/30 국현우)---------------


def show_camera_frame():
    global camera, canvas, window
    _, frame = camera.read()
    if frame is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))

        # 현재 canvas의 가로 및 세로 크기를 가져옵니다
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # 이미지의 가로 및 세로 크기를 가져옵니다
        image_width = photo.width()
        image_height = photo.height()

        # 이미지를 중앙에 배치하기 위한 좌표 계산
        x = (canvas_width - image_width) // 2
        y = (canvas_height - image_height) // 2

        canvas.create_image(x, y, image=photo, anchor=tk.NW)
        canvas.photo = photo

    window.after(10, show_camera_frame)
# --------------------------------------------------------------


def getparams():

    global camera, canvas, window  # 카메라 인터페이스 구현을 위한 전역변수설정(07/30 국현우)
    try:
        param = pickle.load(open("params.p", "rb"))
    except:
        param = {}

    if "camid" not in param:
        param["camid"] = '0'
    if "imgsize" not in param:
        param["imgsize"] = 640
    if "neckoffset" not in param:
        param["neckoffset"] = [0.0, -0.2, 0.1]
    if "prevskel" not in param:
        param["prevskel"] = False
    if "waithmd" not in param:
        param["waithmd"] = False
    if "rotateclock" not in param:
        param["rotateclock"] = False
    if "rotatecclock" not in param:
        param["rotatecclock"] = False
    if "rotate" not in param:
        param["rotate"] = None
    if "camlatency" not in param:
        param["camlatency"] = 0.05
    if "smooth" not in param:
        param["smooth"] = 0.5
    if "feetrot" not in param:
        param["feetrot"] = False
    if "calib_scale" not in param:
        param["calib_scale"] = True
    if "calib_tilt" not in param:
        param["calib_tilt"] = True
    if "calib_rot" not in param:
        param["calib_rot"] = True
    if "use_hands" not in param:
        param["use_hands"] = False
    if "ignore_hip" not in param:
        param["ignore_hip"] = False
    if "camera_settings" not in param:
        param["camera_settings"] = False
    if "camera_width" not in param:
        param["camera_width"] = 640
    if "camera_height" not in param:
        param["camera_height"] = 480
    if "model_complexity" not in param:
        param["model_complexity"] = 1
    if "smooth_landmarks" not in param:
        param["smooth_landmarks"] = True
    if "min_tracking_confidence" not in param:
        param["min_tracking_confidence"] = 0.5
    if "static_image" not in param:
        param["static_image"] = False
    if "min_tracking_confidence" not in param:
        param["min_tracking_confidence"] = 0.5
    if "backend" not in param:
        param["backend"] = 1
    if "backend_ip" not in param:
        param["backend_ip"] = "127.0.0.1"
    if "backend_port" not in param:
        param["backend_port"] = 9000
    if "advanced" not in param:
        param["advanced"] = False
    if "webui" not in param:
        param["webui"] = False
    if "switch_advanced" not in param: ##추가 8/14 홍택수
        param["switch_advanced"] = False

    window = tk.Tk()

    def on_close():
        window.destroy()
        sys.exit("INFO: Exiting... You can close the window after 10 seconds.")

    window.protocol("WM_DELETE_WINDOW", on_close)

    if param["advanced"]:

        camwidth = tk.Entry(width=20)
        camwidth.pack_forget()
        camwidth.insert(0, param["camera_width"])

        camheight = tk.Entry(width=20)
        camheight.pack_forget()
        camheight.insert(0, param["camera_height"])

    if not param["advanced"]:
        tk.Label(text="Camera IP or ID:", width=50).pack()
        camid = tk.Entry(width=20)
        camid.pack()
        camid.insert(0, param["camid"])

        tk.Label(text="Camera width:", width=50).pack()
        camwidth = tk.Entry(width=20)
        camwidth.pack()
        camwidth.insert(0, param["camera_width"])

        tk.Label(text="Camera height:", width=50).pack()
        camheight = tk.Entry(width=20)
        camheight.pack()
        camheight.insert(0, param["camera_height"])

    if not param["advanced"]:

        # ---- 카메라 인터페이스 GUI (07/30 국현우) ----
        canvas = tk.Canvas(window, width="320", height="240")
        canvas.pack()

        # Open the camera
        camera = cv2.VideoCapture(0)

        # Display the camera frame in the tkinter window
        show_camera_frame()

        

    if param["advanced"]:

        # ----------------------8/14 홍택수 수정/gui2 section--------------------------------

        image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
        image_1 = canvas.create_image(175.0, 161.0, image=image_image_1)

        canvas.create_text(85.0, 31.0, anchor="nw", text="DISABLE HIP TRACKER", fill="#FFFFFF", font=("Roboto Medium", 14 * -1))
        canvas.create_text(85.0, 87.0, anchor="nw", text="DEV: SPAWN TRAKER FOR HANDS", fill="#FFFFFF", font=("Roboto Medium", 14 * -1))
        canvas.create_text(85.0, 143.0, anchor="nw", text="DEV: PREVIEW SKELETON IN VR", fill="#FFFFFF", font=("Roboto Medium", 14 * -1))
        canvas.create_text(34.0, 206.0, anchor="nw", text="steam VR", fill="#FFFFFF", font=("Inter", 16 * -1))
        canvas.create_text(185.0, 207.0, anchor="nw", text="VRchatOSC", fill="#FFFFFF", font=("Inter", 16 * -1))

        def create_toggle_switch(window, canvas, x, y, param_key, param, scale=0.65):
            toggle_status = BooleanVar()
            toggle_status.set(param[param_key])

            original_on_image = Image.open(relative_to_assets("toggle_on.png"))
            original_off_image = Image.open(relative_to_assets("toggle_off.png"))

            on_image_resized = original_on_image.resize((round(original_on_image.width * scale), round(original_on_image.height * scale)), Image.LANCZOS)
            off_image_resized = original_off_image.resize((round(original_off_image.width * scale), round(original_off_image.height * scale)), Image.LANCZOS)

            toggle_on_image = ImageTk.PhotoImage(on_image_resized)
            toggle_off_image = ImageTk.PhotoImage(off_image_resized)

            toggle_switch = canvas.create_image(x, y, image=toggle_off_image if not toggle_status.get() else toggle_on_image, anchor="nw")

            def toggle_action(event):
                toggle_status.set(not toggle_status.get())
                param[param_key] = toggle_status.get()

                if toggle_status.get():
                    canvas.itemconfigure(toggle_switch, image=toggle_on_image)
                else:
                    canvas.itemconfigure(toggle_switch, image=toggle_off_image)

            canvas.tag_bind(toggle_switch, "<Button-1>", toggle_action)

            return toggle_switch, toggle_status


        toggle_switch_1, varignorehip = create_toggle_switch(window, canvas, x=32, y=28, param_key="ignore_hip", param=param)
        toggle_switch_2, varusehands = create_toggle_switch(window, canvas, x=32, y=83, param_key="use_hands", param=param)
        toggle_switch_3, varprevskel = create_toggle_switch(window, canvas, x=32, y=138, param_key="prevskel", param=param)


    '''
    backend_frame = tk.Frame(window)
    backend_selection_frame = tk.Frame(backend_frame)
    backend_options_frame = tk.Frame(backend_frame)
    varbackend = tk.IntVar(value=param["backend"])
    '''

    ''' ##아래와 사유 동일 
    def show_hide_backend_options():
        if varbackend.get() == 2:
            backend_options_frame.pack(side=tk.BOTTOM)
        else:
            backend_options_frame.pack_forget()
    '''

    ''' ##VRChatOSC 추가 UI 사유로 더미데이터 구현 중 8/14 홍택수
    tk.Label(backend_options_frame, text="IP/port:").pack(side=tk.LEFT)
    backend_ip = tk.Entry(backend_options_frame, width=15)
    backend_ip.insert(0, param["backend_ip"])
    backend_ip.pack(side=tk.LEFT)
    backend_port = tk.Entry(backend_options_frame, width=5)
    backend_port.insert(0, param["backend_port"])
    backend_port.pack(side=tk.LEFT)
    '''

    '''
    show_hide_backend_options()
    backend_frame.pack()
    '''
    def create_image_radio_button(window, canvas, on_image_path, off_image_path, x, y, variable, value):
        on_image = ImageTk.PhotoImage(Image.open(relative_to_assets(on_image_path)))
        off_image = ImageTk.PhotoImage(Image.open(relative_to_assets(off_image_path)))

        def toggle_image(event):
            if variable.get() != value:
                variable.set(value)
                update_radio_buttons()

        radio_button = canvas.create_image(x, y, image=off_image, anchor="center")
        canvas.tag_bind(radio_button, '<Button-1>', toggle_image)

        return radio_button

    def update_radio_buttons():
        canvas.itemconfigure(radio_button_steam_vr, image=(on_image if varbackend.get() == 1 else off_image))
        canvas.itemconfigure(radio_button_vrchat_osc, image=(on_image if varbackend.get() == 2 else off_image))

    varbackend = IntVar(value=1)
    on_image = ImageTk.PhotoImage(Image.open(relative_to_assets("check_on.png")))
    off_image = ImageTk.PhotoImage(Image.open(relative_to_assets("check_off.png")))
    
    param["switch_advanced"] = False
    if param["advanced"]:
        radio_button_steam_vr = create_image_radio_button(window, canvas, "check_on.png", "check_off.png", 125, 215, varbackend, 1)
        radio_button_vrchat_osc = create_image_radio_button(window, canvas, "check_on.png", "check_off.png", 295, 214, varbackend, 2)   
        update_radio_buttons()

        button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        button_1 = Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: set_advanced(window, param), relief="flat")
        button_1.place(x=32.0, y=262.0, width=287.0, height=40.0)
    else:
        tk.Button(text='SETTING', command=lambda *args: set_advanced(window, param)).pack()
        tk.Button(text='SAVE AND CONTINUE', command=window.quit).pack()
    
    window.mainloop()
# ----------------------------------------------------------"

    cameraid = '0'
    # hmd_to_neck_offset = [0.0, -0.2, 0.1]

    dont_wait_hmd = False  # bool(varhmdwait.get())

    # camera_latency = 0.05
    # smoothing = True
    feet_rotation = False

    ignore_hip = False
    camera_height = camheight.get()
    camera_width = camwidth.get()

    '''##VRChatOSC 추가 버튼 관련 숨김 8/14 홍택수
    backend = int(varbackend.get())
    backend_ip_set = backend_ip.get()
    backend_port_set = int(backend_port.get())
    '''

    webui = False

    if param["advanced"]:
        maximgsize = 640

        preview_skeleton = bool(varprevskel.get())  ##수정 8/14 홍택수
        use_hands = bool(varusehands.get())  ##수정 8/14 홍택수

        mp_smoothing = True
        model_complexity = 1
        min_tracking_confidence = 0.5
        static_image = False

    else:
        maximgsize = 640

        preview_skeleton = False
        use_hands = False

        mp_smoothing = True
        model_complexity = 1
        min_tracking_confidence = 0.5
        static_image = False

    switch_advanced = param["switch_advanced"]

    advanced = param["advanced"]

    param = {}
    param["camid"] = '0'
    param["imgsize"] = maximgsize
    param["neckoffset"] = [0.0, -0.2, 0.1]
    param["prevskel"] = preview_skeleton
    param["waithmd"] = dont_wait_hmd
    param["smooth"] = 0.5
    param["camlatency"] = 0.05
    param["feetrot"] = False
    param["use_hands"] = use_hands
    param["ignore_hip"] = False
    param["camera_settings"] = False
    param["camera_height"] = camera_height
    param["camera_width"] = camera_width
    param["model_complexity"] = model_complexity
    param["smooth_landmarks"] = mp_smoothing
    param["static_image"] = static_image
    param["min_tracking_confidence"] = min_tracking_confidence
    
    '''##VRChatOSC 추가 버튼 관련 숨김(param값) 8/14 홍택수
    param["backend"] = backend
    param["backend_ip"] = backend_ip_set
    param["backend_port"] = backend_port_set
    '''

    param["webui"] = False

    if switch_advanced:
        param["advanced"] = not advanced
    else:
        param["advanced"] = advanced

    pickle.dump(param, open("params.p", "wb"))

    window.destroy()

    if switch_advanced:
        return None
    else:
        return param


if __name__ == "__main__":
    print(getparams())