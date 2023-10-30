import tkinter as tk
import sys
import pickle
import cv2
import PIL.Image
import PIL.ImageTk
import subprocess as sp
import pymysql
from tkinter import messagebox
from inference_gui import make_inference_gui

from sys import platform

import os
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, BooleanVar, IntVar, Entry, messagebox
from PIL import Image, ImageTk

conn = pymysql.connect(host = '113.131.111.147', user = 'root', password = 'vrlogy12@', db = 'vrlogydb', charset = 'utf8')

def on_close():
    window.destroy()

def check_username_password(username,password):
    cur = conn.cursor() # 데이터베이스에 SQL문을 실행하거나 실행된 결과를 돌려받는 통로
    
    # Id, Password 확인
    check_id_sql = "SELECT password FROM member_info where username = %s"
    cur.execute(check_id_sql, (username,)) 
    id_result = cur.fetchone()  # 하나의 행을 가져옴
    # 라이센스 유무 확인
    check_is_purchased_sql = "select is_purchased from license, member_info where member_id = username AND username = %s"
    cur.execute(check_is_purchased_sql, (username,))
    license_result = cur.fetchone()
    
        
    if id_result is not None:
        if id_result[0] == password:
            if license_result is not None and license_result[0] == 1:
                messagebox.showinfo("로그인 성공", "로그인을 성공하였습니다.")
                pass
                return  make_inference_gui

            elif license_result is not None and license_result[0] != 1:
                messagebox.showerror("라이센스 구매", "라이센스가 없습니다. 홈페이지에서 구매해주시길 바랍니다.")
                return getparams()
            else:
                messagebox.showerror("라이센스 오류", "라이센스가 없습니다. 홈페이지에서 구매해주시길 바랍니다.")
                return getparams()
        else:
            messagebox.showerror("로그인 실패", "로그인에 실패하였습니다.")
            return getparams() 
    else:
        messagebox.showerror("로그인 실패", "해당 아이디가 존재하지 않습니다.")
        return getparams()

button_image_1 = None
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH_FRAME0 =  Path("C:/dev/assets/frame0")
ASSETS_PATH_FRAME2 =  Path("C:/dev/assets/frame2")


def relative_to_assets_frame0(path: str) -> Path:
    return ASSETS_PATH_FRAME0 / Path(path)


def relative_to_assets_frame2(path: str) -> Path:
    return ASSETS_PATH_FRAME2 / Path(path)


def set_advanced(window, param):
    param["switch_advanced"] = True
    window.quit()

window = Tk()

window.geometry("485x499")
window.configure(bg="#FFFFFF")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=499,
    width=485,
    bd=0,
    highlightthickness=0,
    relief="ridge",
)
canvas.place(x=0, y=0)

window.minsize(width = 485, height = 499)
window.maxsize(width = 485, height = 499)

is_window_opened = False  # 초기에 창이 닫혀 있는 상태로 설정
setting_window = None

varbackend = tk.IntVar(value = 1)
port = 9000



def getparams():
    global camera, window, canvas # 카메라 인터페이스 구현을 위한 전역변수설정(07/30 국현우)
    try:
        param = pickle.load(open("params.p", "rb"))
    except:
        param = {}

    if "camid" not in param:
        param["camid"] = 0
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
    if "switch_advanced" not in param:  ##추가 8/14 홍택수
        param["switch_advanced"] = False     
    if "member_id" not in param:
        param["member_id"] = ""
    if "member_pw" not in param:
        param["member_pw"] = ""
    if "db_flag" not in param:
        param["db_flag"] = 0
        

    window.protocol("WM_DELETE_WINDOW", on_close)

    # =============================================8/15 강창범 수정=============================================

    image_image_1 = PhotoImage(file=relative_to_assets_frame0("image_1.png"))
    image_1 = canvas.create_image(274.0, 266.0, image=image_image_1)

    #=========================================[8/29 강창범]이미지 수정===========================================
    def center_image(canvas, image):
        canvas.update()  # 캔버스 업데이트하여 실제 크기를 반영
        canvas_width = canvas.winfo_width()
        image_width = image.width()
        x_position = (canvas_width - image_width) / 2
        y_position = -80
        return x_position, y_position
    image_image_2 = relative_to_assets_frame0("image_2.png")
    original_image = Image.open(image_image_2)
    resized_image = original_image.resize((360, 400))  # 원하는 크기로 이미지 크기 조절
    image_a = ImageTk.PhotoImage(resized_image)
    # 이미지를 캔버스의 위쪽 가운데에 배치
    image_2 = canvas.create_image(center_image(canvas, image_a), anchor="nw", image=image_a)
    #==========================================================================================================

    canvas.create_text(
        231.0,
        415.0,
        anchor="nw",
        text="Steam VR을 실행한 뒤  클릭해주세요.",
        fill="#FF3333",
        font=("SourceSansPro Bold", -11),
    )

    """------------------------------camera_ID/IP------------------------------"""
    canvas.create_text(
        50.0,
        240.0,
        anchor="nw",
        text="Camera IP or ID",
        fill="#E7EFFF",
        font=("SourceSansPro Bold", 18 * -1),
    )
    entry_image_1 = PhotoImage(file=relative_to_assets_frame0("entry_1.png"))
    entry_bg_1 = canvas.create_image(335.5, 244.0, image=entry_image_1)
    # [8/28 강창범] camera_id param 수정
    camera_id = Entry(bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
    camera_id.place(x=209.0, y=222.0, width=253.0, height=42.0)

    """------------------------------username------------------------------"""
    canvas.create_text(
        50.0,
        305.0,
        anchor="nw",
        text="Email",
        fill="#E7EFFF",
        font=("SourceSansPro Bold", 18 * -1),
    )
    entry_image_2 = PhotoImage(file=relative_to_assets_frame0("entry_2.png"))
    entry_bg_2 = canvas.create_image(335.5, 310.0, image=entry_image_2)
    member_id = Entry(bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
    member_id.place(x=209.0, y=288.0, width=253.0, height=42.0)

    """------------------------------password------------------------------"""
    canvas.create_text(
        50.0,
        372.0,
        anchor="nw",
        text="Password",
        fill="#E7EFFF",
        font=("SourceSansPro Bold", 18 * -1),
    )

    entry_image_3 = PhotoImage(file=relative_to_assets_frame0("entry_3.png"))
    entry_bg_3 = canvas.create_image(335.5, 377.0, image=entry_image_3)
    member_pw = Entry(bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0, show = '*')
    member_pw.place(x=209.0, y=355.0, width=253.0, height=42.0)

    if param["advanced"]:
        
        camera_id.insert(0, param["camid"])
        member_id.pack_forget()
        member_id.insert(0, param["member_id"])

        member_pw.pack_forget()
        member_pw.insert(0, param["member_pw"])

    if not param["advanced"]:
        camera_id.insert(0, param["camid"])

        member_id.insert(0, param["member_id"])

        member_id.insert(0, param["member_pw"])

    # ==========================================================================================

    ##gui2 버그 해결 8/31 홍택수 (~352)
    button_image_1 = PhotoImage(file=relative_to_assets_frame2("button_1.png"))
    image_image_3 = PhotoImage(file=relative_to_assets_frame2("image_1.png"))
   
    def create_toggle_switch(window, canvas, x, y, param_key, param, scale=0.65):
        toggle_status = BooleanVar()
        toggle_status.set(param[param_key])

        original_on_image = Image.open(relative_to_assets_frame2("toggle_on.png"))
        original_off_image = Image.open(relative_to_assets_frame2("toggle_off.png"))

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
   
   
    def on_new_window_close():
            global is_window_opened
            is_window_opened = False  
           
   
    def open_setting_window():  
        global varbackend, port, ip
        global is_window_opened, setting_window  # 전역 변수로 창이 열려 있는지 여부를 추적
            #9/4 홍택수 backend param수정
        if is_window_opened and setting_window is not None and setting_window.winfo_exists():
            # 창이 이미 열려 있을 때
            messagebox.showinfo("Info", "The window is already open")
        else:
            # 창이 열려 있지 않을 때
            is_window_opened = True
            setting_window = tk.Toplevel(window)
            setting_window.protocol("WM_DELETE_WINDOW", on_new_window_close)
           
            # 창 크기 고정
            setting_window.minsize(width = 350, height = 322)
            setting_window.maxsize(width = 350, height = 340)
           
            # 아래부터 창 내용을 구성
            canvas = tk.Canvas(
                setting_window,
                bg="#FFFFFF",
                height=322,
                width=350,
                bd=0,
                highlightthickness=0,
                relief="ridge",
            )
            canvas.place(x=0, y=0)
            canvas.pack()

        canvas.create_image(175.0, 161.0, image=image_image_3)
        canvas.create_text(85.0, 31.0, anchor="nw", text="DISABLE HIP TRACKER", fill="#FFFFFF", font=("Roboto Medium", 14 * -1))
        canvas.create_text(85.0, 87.0, anchor="nw", text="Calculate Calorie", fill="#FFFFFF", font=("Roboto Medium", 14 * -1))
        canvas.create_text(85.0, 143.0, anchor="nw", text="DEV: PREVIEW SKELETON IN VR", fill="#FFFFFF", font=("Roboto Medium", 14 * -1))
        canvas.create_text(34.0, 206.0, anchor="nw", text="steam VR", fill="#FFFFFF", font=("Inter", 16 * -1))
        canvas.create_text(185.0, 207.0, anchor="nw", text="VRchatOSC", fill="#FFFFFF", font=("Inter", 16 * -1))

        toggle_switch_1, varignorehip = create_toggle_switch(window, canvas, x=32, y=28, param_key="ignore_hip", param=param)
        toggle_switch_2, varusehands = create_toggle_switch(window, canvas, x=32, y=83, param_key="use_hands", param=param)
        toggle_switch_3, varprevskel = create_toggle_switch(window, canvas, x=32, y=138, param_key="prevskel", param=param)

        backend_frame = tk.Frame(setting_window)
        backend_options_frame = tk.Frame(setting_window)

        def show_hide_backend_options():
            if varbackend.get() == 2:
                backend_options_frame.pack(side=tk.BOTTOM)
            else:
                backend_options_frame.pack_forget()  
        tk.Radiobutton(setting_window, variable = varbackend, value = 1, command = show_hide_backend_options).place(x=115, y=200)
        tk.Radiobutton(setting_window,  variable = varbackend, value = 2, command = show_hide_backend_options).place(x=280, y=200)

        #9/4 홍택수 backend param수정
        tk.Label(backend_options_frame, text="IP/port:").pack(side = tk.LEFT)
       
        backend_ip = tk.Entry(backend_options_frame, width=20)
        backend_ip.pack(side=tk.LEFT)
       
        backend_port = tk.Entry(backend_options_frame, width=10)
        backend_port.pack(side=tk.LEFT)
       
        if not param["advanced"]:
            backend_ip.insert(0, param["backend_ip"])
            backend_port.insert(0, param["backend_port"])

        show_hide_backend_options()
        backend_frame.pack()
       
        ##버튼 수정 및 이벤트 처리 8/22 홍택수
        button_2 = canvas.create_image(175.5, 282.0, image=button_image_1, anchor="center")

        # 버튼 클릭 액션 정의   9/5 backend_port 해결
        def button2_action(event):
            ip = backend_ip.get()
            param["backend_ip"] = ip

            port = backend_port.get()
            param["backend_port"] = port

            # 원래 button_1의 command=lambda: set_advanced(setting_window, param)
            setting_window.destroy()

        # 버튼 이벤트 처리기 (버튼 클릭 시 동작하게 함)
        canvas.tag_bind(button_2, "<Button-1>", button2_action)
   
        setting_window.mainloop()
       
    # """==================================setting===================================="""
    button_image_3 = PhotoImage(file=relative_to_assets_frame0("button_1.png"))
    button_3 = Button(
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=open_setting_window,
        relief="flat",
    )
    button_3.place(x=20.0, y=434.0, width=170.0, height=50.0)

    # Button(text='SETTING', command=lambda *args: set_advanced(window, param)).pack()
    button_image_2 = PhotoImage(file=relative_to_assets_frame0("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=window.quit,
        relief="flat",
    )
    button_2.place(x=201.0, y=434.0, width=269.0, height=50.0)
    window.mainloop()
    
    # ----------------------------------------------------------"
    
    username = member_id.get()
    password = member_pw.get()
    check_username_password(username, password)
    camid = camera_id.get()
    

    # cameraid = "0"
    # hmd_to_neck_offset = [0.0, -0.2, 0.1]

    dont_wait_hmd = False  # bool(varhmdwait.get())

    # camera_latency = 0.05
    # smoothing = True
    feet_rotation = False

    ## param 수정 8/24 홍택수
    # ignore_hip = param["ignore_hip"]
    # prevskel = param["prevskel"]
    # use_hands = param["use_hands"]

    # [8/28 강창범] param camera_id 수정
    
    
    #9/4 홍택수 backend param수정
    backend = int(varbackend.get())
    backend_ip_set = param["backend_ip"]
    backend_port_set = param["backend_port"]
    webui = False

    # ===================[9/1 강창범] param[ignore_hip, use_hands, prevskel] 수정==================
    if param["advanced"]:
        maximgsize = 640
        #prevskel = False  ##param 수정 8/24 홍택수
        #use_hands = False  ##param 수정 8/24 홍택수
        #ignore_hip = False
        mp_smoothing = True
        model_complexity = 1
        min_tracking_confidence = 0.5
        static_image = False

    else:
        maximgsize = 640
        ignore_hip = param["ignore_hip"]
        prevskel = param["prevskel"]
        use_hands = param["use_hands"]
        mp_smoothing = True
        model_complexity = 1
        min_tracking_confidence = 0.5
        static_image = False

    switch_advanced = param["switch_advanced"]
    advanced = param["advanced"]

    param = {}
    param["camid"] = camid
    param["imgsize"] = maximgsize
    param["neckoffset"] = [0.0, -0.2, 0.1]
    param["prevskel"] = prevskel # preview_skeleton
    param["waithmd"] = dont_wait_hmd
    param["smooth"] = 0.5
    param["camlatency"] = 0.05
    param["feetrot"] = False
    param["use_hands"] = use_hands
    param["ignore_hip"] = ignore_hip
    param["camera_settings"] = False
    param["camera_width"] = 640
    param["camera_height"] = 480
    param["member_id"] = username
    param["member_pw"] = password
    param["model_complexity"] = model_complexity
    param["smooth_landmarks"] = mp_smoothing
    param["static_image"] = static_image
    param["min_tracking_confidence"] = min_tracking_confidence
    ##VRChatOSC 추가 버튼 관련 숨김(param값) 8/14 홍택수
    #9/4 홍택수 backend param수정
    param["backend"] = backend
    param["backend_ip"] = backend_ip_set
    param["backend_port"] = backend_port_set
    param["webui"] = False
    
    on_close()

    if switch_advanced:
        param["advanced"] = not advanced
    else:
        param["advanced"] = advanced

    if switch_advanced:
        return None
    else:
        return param
    
    


if __name__ == "__main__":
    print(getparams())