import tkinter as tk
from tkinter import ttk
from tkinter import Canvas
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, BooleanVar
import numpy as np
from scipy.spatial.transform import Rotation as R
from helpers import shutdown, sendToSteamVR
import cv2
from PIL import Image,ImageTk
#use_steamvr = True
from pathlib import Path
import os

OUTPUT_PATH = Path(__file__).parent

ASSETS_PATH_FRAME1 = Path("c:/vlogy/logy_Dev/assets/frame1")

def relative_to_assets_frame1(path: str) -> Path:
    return ASSETS_PATH_FRAME1 / Path(path)

### 9/1 홍택수 ###
#####토글####
def create_toggle_switch( canvas, command=None, x=0, y=0, scale=0.71):
    # 토글 상태 변수 및 이미지 로드
    toggle_status = BooleanVar()
    toggle_status.set(False)

    original_on_image = Image.open(relative_to_assets_frame1("toggle_on.png"))
    original_off_image = Image.open(relative_to_assets_frame1("toggle_off.png"))

    # 이미지 크기 조절
    on_image_resized = original_on_image.resize((round(original_on_image.width * scale), round(original_on_image.height * scale)), Image.LANCZOS)
    off_image_resized = original_off_image.resize((round(original_off_image.width * scale), round(original_off_image.height * scale)), Image.LANCZOS)

    toggle_on_image = ImageTk.PhotoImage(on_image_resized)
    toggle_off_image = ImageTk.PhotoImage(off_image_resized)

    # 토글 이미지 생성 및 위치 설정
    toggle_switch = canvas.create_image(x, y, image=toggle_off_image, anchor="nw")

    # 토글 동작 함수
    def toggle_action(event):
        if command:  # command가 지정되었을 경우 실행합니다.
            command()

        if toggle_status.get():
            canvas.itemconfigure(toggle_switch, image=toggle_off_image)
            toggle_status.set(False)
        else:
            canvas.itemconfigure(toggle_switch, image=toggle_on_image)
            toggle_status.set(True)

    canvas.tag_bind(toggle_switch,"<Button-1>",toggle_action)

    return toggle_switch

class InferenceWindow(tk.Frame):
    def __init__(self, root, params, *args, **kwargs):
        super().__init__(root)  
        
        self.params = params
        params.gui = self       #uhh is this a good idea?
        self.root = root
        self.root.geometry("528x209")
        self.root.minsize(width = 528, height = 209)
        self.root.maxsize(width = 528, height = 209)

        ### 9/1 홍택수 ( ~73 ) ### 

        self.canvas = Canvas(
            bg = "#FFFFFF",
            height = 209,
            width = 528,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.canvas.pack()

        self.image_image_1 = PhotoImage(
            file=relative_to_assets_frame1("image_1.png"))
        self.image_1 = self.canvas.create_image(
            0.0,
            0.0,
            anchor=tk.NW,
            image=self.image_image_1
        )

        self.canvas.create_text(
            180.0,
            22.0,
            anchor="nw",
            text="PAUSE/UNPAUSE TRACKING",
            fill="#FFFFFF",
            font=("Roboto Medium", 14 * -1)
        )
        #-----
        # calibrate rotation
        self.calib_rot_var = tk.BooleanVar(value=self.params.calib_rot)
        self.calib_flip_var = tk.BooleanVar(value=self.params.flip)

        frame1 = tk.Frame(self.root)
        frame1.pack()
        self.calibrate_rotation_frame(frame1)

        # calibrate tilt
        self.calib_tilt_var = tk.BooleanVar(value=self.params.calib_tilt)
    
        frame2 = tk.Frame(self.root)
        frame2.pack()
        self.calibrate_tilt_frame(frame2)

        # calibrate scale
        self.calib_scale_var = tk.BooleanVar(value=self.params.calib_scale)

        frame3 = tk.Frame(self.root)
        frame3.pack()
        self.calibrate_scale_frame(frame3)

        self.smoothing_1 = 0.5   
        self.smoothing_2 = 0.5
        self.ready2exit = self.ready_to_exit

        ### 9/1 홍택수 ( ~114 ) ### 
        # recalibrate
        self.button_image_1 = PhotoImage(
            file=relative_to_assets_frame1("button_1.png"))
        button_1 = Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.autocalibrate,  # 원하는 기능을 수행할 함수를 지정합니다.
            relief="flat"
        )
        button_1.place(
            x=20.0,
            y=60.0,
            width=488.0,
            height=50.0
        )

        ### 9/1 홍택수 ###
        # pause tracking
        toggle_switch_button = create_toggle_switch(self.canvas,x=130.0,y=13.0,scale=0.71,
                                            command=self.pause_tracking) 
        
        #frametime log
        self.log_frametime_var = tk.BooleanVar(value=self.params.log_frametime)
       
        ### 9/1 홍택수 ( ~192 ) ### 
        # exit
        self.button_image_2 = PhotoImage(
            file=relative_to_assets_frame1("button_2.png"))
        self.button_2 = Button(
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.params.ready2exit,
            relief="flat"
        )
        self.button_2.place(
            x=20.0,
            y=130.0,
            width=488.0,
            height=50.0
        )

        root.protocol("WM_DELETE_WINDOW", self.params.ready2exit) # when press x

        # smoothing_1 and smoothing_2 속성 추가, 초기값으로 임시로 0을 설정했습니다. 

    def ready_to_exit(self):  # 메소드 이름 변경
        self.gui.root.destroy()

    camera_latency = 0   # TODO: Set an appropriate initial value for camera latency

    hmd_to_neck_offset=[0,0,0]
    
    def change_log_frametime(self):
        self.params.log_frametime = self.log_frametime_var.get()
        if self.params.log_frametime:
            print("INFO: Enabled frametime logging")
        else:
            print("INFO: Disabled frametime logging")

    def set_scale_var(self):
        self.scale_var.set(self.params.posescale)


    def change_rot_auto(self):
        self.params.calib_rot = self.calib_rot_var.get()
        print(f"Mark rotation to{'' if self.params.calib_rot else ' NOT'} be automatically calibrated")
        
    def change_rot_flip(self):
        self.params.flip = self.calib_flip_var.get()
        print("changed flip to: ", self.params.flip)


    def calibrate_rotation_frame(self, frame):
       
        self.change_rot_auto()
       

    def change_tilt_auto(self):
        self.params.calib_tilt = self.calib_tilt_var.get()
        print(f"Mark tilt to{'' if self.params.calib_tilt else ' NOT'} be automatically calibrated")

    
    def calibrate_tilt_frame(self, frame):
        
        self.change_tilt_auto()
        
    def change_scale_auto(self):
        self.params.calib_scale = self.calib_scale_var.get()
        print(f"Mark scale to{'' if self.params.calib_scale else ' NOT'} be automatically calibrated")


    def calibrate_scale_frame(self, frame):
        
        self.change_scale_auto()
       
    def change_cam_lat_frame(self, frame):

        tk.Label(frame, text="Camera latency:", width = 20).pack(side='left')
        lat = tk.Entry(frame, width = 10)
        lat.pack(side='left')
        lat.insert(0, self.params.camera_latency)

        tk.Button(frame, text='Update', command=lambda *args: self.params.change_camera_latency(float(lat.get()))).pack(side='left')
        
    def change_add_smoothing_frame(self, frame):

      
        self.params.change_additional_smoothing(0.7)
       
    def change_image_rotation_frame(self, frame):
        self.params.change_img_rot(0)  # 기본값으로 0도 회전 설정


    def autocalibrate(self):

        use_steamvr = True if self.params.backend == 1 else False

        if use_steamvr:
            array = sendToSteamVR("getdevicepose 0")        #get hmd data to allign our skeleton to

            if array is None or len(array) < 10:
                shutdown(self.params)

            headsetpos = [float(array[3]),float(array[4]),float(array[5])]
            headsetrot = R.from_quat([float(array[7]),float(array[8]),float(array[9]),float(array[6])])
            
            neckoffset = headsetrot.apply(self.params.hmd_to_neck_offset)   #the neck position seems to be the best point to allign to, as its well defined on 
                                                            #the skeleton (unlike the eyes/nose, which jump around) and can be calculated from hmd.   

        if self.params.calib_tilt:
            try:
                feet_middle = (self.params.pose3d_og[0] + self.params.pose3d_og[5])/2
            except:
                print("INFO: No pose detected, try to autocalibrate again.")
                return
        
            print(feet_middle)
        
            ## roll calibaration
            
            value = np.arctan2(feet_middle[0],-feet_middle[1]) * 57.295779513
            
            print("INFO: Precalib z angle: ", value)
          
            for j in range(self.params.pose3d_og.shape[0]):
                self.params.pose3d_og[j] = self.params.global_rot_z.apply(self.params.pose3d_og[j])
                
            feet_middle = (self.params.pose3d_og[0] + self.params.pose3d_og[5])/2
            value = np.arctan2(feet_middle[0],-feet_middle[1]) * 57.295779513
            
            print("INFO: Postcalib z angle: ", value)
                
            ##tilt calibration
                
            value = np.arctan2(feet_middle[2],-feet_middle[1]) * 57.295779513
            
            print("INFO: Precalib x angle: ", value)
           
        
            for j in range(self.params.pose3d_og.shape[0]):
                self.params.pose3d_og[j] = self.params.global_rot_x.apply(self.params.pose3d_og[j])
                
            feet_middle = (self.params.pose3d_og[0] + self.params.pose3d_og[5])/2
            value = np.arctan2(feet_middle[2],-feet_middle[1]) * 57.295779513
            
            print("INFO: Postcalib x angle: ", value)

        if use_steamvr and self.params.calib_rot:
            feet_rot = self.params.pose3d_og[0] - self.params.pose3d_og[5]
            value = np.arctan2(feet_rot[0],feet_rot[2])
            value_hmd = np.arctan2(headsetrot.as_matrix()[0][0],headsetrot.as_matrix()[2][0])
            print("INFO: Precalib y value: ", value * 57.295779513)
            print("INFO: hmd y value: ", value_hmd * 57.295779513)  
            
            value = value - value_hmd
            
            value = -value
   
            print("INFO: Calibrate to value:", value * 57.295779513) 
            

            for j in range(self.params.pose3d_og.shape[0]):
                self.params.pose3d_og[j] = self.params.global_rot_y.apply(self.params.pose3d_og[j])
            
            feet_rot = self.params.pose3d_og[0] - self.params.pose3d_og[5]
            value = np.arctan2(feet_rot[0],feet_rot[2])
            
            print("INFO: Postcalib y value: ", value * 57.295779513)

        if use_steamvr and self.params.calib_scale:
            #calculate the height of the skeleton, calculate the height in steamvr as distance of hmd from the ground.
            #divide the two to get scale 
            skelSize = np.max(self.params.pose3d_og, axis=0)-np.min(self.params.pose3d_og, axis=0)
            self.params.posescale = headsetpos[1]/skelSize[1]

            self.set_scale_var()

        self.params.recalibrate = False


    def put_separator(self): 
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x')
        
    def pause_tracking(self):
        if not self.params.paused:
            print("INFO: Pose estimation paused")
        else:
            print("INFO: Pose estimation unpaused") 
        self.params.paused = not self.params.paused

def make_inference_gui(_params):
    root = tk.Tk()
    #root.geometry("528X209")
    InferenceWindow(root, _params).pack(side="top", fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    make_inference_gui()