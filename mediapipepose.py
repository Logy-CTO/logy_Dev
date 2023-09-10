print("Importing libraries...")
import os
import sys
sys.path.append(os.getcwd())    #embedable python doesnt find local modules without this line
import time
import threading
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, BooleanVar
from helpers import  CameraStream, shutdown, mediapipeTo3dpose, get_rot_mediapipe, get_rot_hands,  get_rot,sendToSteamVR
from scipy.spatial.transform import Rotation as R
from backends import DummyBackend, SteamVRBackend, VRChatOSCBackend
import webui
from pathlib import Path
import parameters
from PIL import Image,ImageTk
import tkinter as tk
from helpers import shutdown, sendToSteamVR
import mediapipe as mp


OUTPUT_PATH = Path(__file__).parent

ASSETS_PATH_FRAME1 = Path("./frame1")

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
        self.canvas_width = 640  # Or whatever size you want.
        self.canvas_height = 480 
        

        # Update canvas with video frames.
       
        #-----

        ### 9/1 홍택수 ( ~73 ) ### 

        self.canvas = Canvas(
            bg = "#FFFFFF",
            height = 756,
            width = 529,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.pack()

        self.image_image_1 = PhotoImage(
            file=relative_to_assets_frame1("image_1.png"))
        self.image_1 = self.canvas.create_image(
            264.0,
            378.0,
            image=self.image_image_1
        )
       
        self.canvas.create_text(
            87.0,
            574.0,
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
            x=21.0,
            y=621.0,
            width=488.0,
            height=50.0
        )

        
        ### 9/1 홍택수 ###
        # pause tracking
        toggle_switch_button = create_toggle_switch(self.canvas,x=33,y=567,scale=0.71,
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
            x=21.0,
            y=682.0,
            width=488.0,
            height=50.0
        )

       
 
        root.protocol("WM_DELETE_WINDOW", self.params.ready2exit) # when press x
 
        
    def update_image(self, img):
        image_pil_format = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        self.image_tkinter_format = ImageTk.PhotoImage(image=image_pil_format)

        # Clear the canvas and put a new image on it.
        self.canvas.delete("all")
        self.canvas.create_image(264.0, 278.0, image=self.image_tkinter_format, anchor='nw')
        self.root.after(15, self.update_from_main)

    def update_from_main(self):
        # 여기서 OpenCV로부터 이미지를 가져와 update_image 메서드를 호출합니다.
        # 예: img = capture_from_opencv()
        # self.update_image(img)
        
        if hasattr(self, 'update_func'):
            self.update_func()
        self.root.update_idletasks()
        self.root.update()

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
    
    
def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    use_steamvr = True
    
    print("INFO: Reading parameters...")

    params = parameters.Parameters()
    
    if params.webui:
        webui_thread = threading.Thread(target=webui.start_webui, args=(params,), daemon=True)
        webui_thread.start()
    else:
        print("INFO: WebUI disabled in parameters")

    backends = { 0: DummyBackend, 1: SteamVRBackend, 2: VRChatOSCBackend }
    backend = backends[params.backend]()
    backend.connect(params)

    if params.exit_ready:
        sys.exit("INFO: Exiting... You can close the window after 10 seconds.")

    print("INFO: Opening camera...")

    camera_thread = CameraStream(params)

    #making gui

    
    print("INFO: Starting pose detector...")

    #create our detector. These are default parameters as used in the tutorial. 
    pose = mp_pose.Pose(model_complexity=params.model, 
                        min_detection_confidence=0.5, 
                        min_tracking_confidence=params.min_tracking_confidence, 
                        smooth_landmarks=params.smooth_landmarks, 
                        static_image_mode=params.static_image)

    

    #Main program loop:

    rotation = 0
    i = 0

    prev_smoothing = params.smoothing
    prev_add_smoothing = params.additional_smoothing

    while True:
        # Capture frame-by-frame
        if params.exit_ready:
            shutdown(params)
            
        if prev_smoothing != params.smoothing or prev_add_smoothing != params.additional_smoothing:
            print(f"INFO: Changed smoothing value from {prev_smoothing} to {params.smoothing}")
            print(f"INFO: Changed additional smoothing from {prev_add_smoothing} to {params.additional_smoothing}")

            prev_smoothing = params.smoothing
            prev_add_smoothing = params.additional_smoothing

            backend.onparamchanged(params)

        #wait untill camera thread captures another image
        if not camera_thread.image_ready:     
            time.sleep(0.001)
            continue

        #some may say I need a mutex here. I say this works fine.
        
        #if set, rotate the image
        if params.rotate_image is not None:       
            img = cv2.rotate(img, params.rotate_image)
            
        if params.mirror:
            img = cv2.flip(img,1)

        #if set, ensure image does not exceed the given size.
        if max(img.shape) > params.maximgsize:        
            ratio = max(img.shape)/params.maximgsize
            img = cv2.resize(img, (int(img.shape[1]/ratio),int(img.shape[0]/ratio)))
        
        if params.paused:
            
            continue
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        #print(image.shape)
        
        t0 = time.time()
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.    copied from the tutorial
        img.flags.writeable = False
        results = pose.process(img)
        img.flags.writeable = True

        if results.pose_world_landmarks:        #if any pose was detected
            
            pose3d = mediapipeTo3dpose(results.pose_world_landmarks.landmark)   #convert keypoints to a format we use
            
            #do we need this with osc as well?
           
            pose3d[:,0] = -pose3d[:,0]      #flip the points a bit since steamvrs coordinate system is a bit diffrent
            pose3d[:,1] = -pose3d[:,1]

            pose3d_og = pose3d.copy()
            params.pose3d_og = pose3d_og
            
            for j in range(pose3d.shape[0]):        #apply the rotations from the sliders
                pose3d[j] = params.global_rot_z.apply(pose3d[j])
                pose3d[j] = params.global_rot_x.apply(pose3d[j])
                pose3d[j] = params.global_rot_y.apply(pose3d[j])
            
            if not params.feet_rotation:
                rots = get_rot(pose3d)          #get rotation data of feet and hips from the position-only skeleton data
            else:
                rots = get_rot_mediapipe(pose3d)
                
            if params.use_hands:
                hand_rots = get_rot_hands(pose3d)
            else:
                hand_rots = None
                
            
            #pose3d[0] = [1,0,1]
            #rots = (rots[0], R.from_euler('ZXY',[i/17,i/11,i/10]).as_quat(),rots[2])   #for testing rotation conversions
            #i+=1
            
            if not backend.updatepose(params, pose3d, rots, hand_rots):
                continue
        
        
        #print(f"Inference time: {time.time()-t0}\nSmoothing value: {smoothing}\n")        #print how long it took to detect and calculate everything
        inference_time = time.time() - t0
        
        if params.log_frametime:
            print(f"INFO: Inference time: {inference_time}")
        
               #convert back to bgr and draw the pose
        mp_drawing.draw_landmarks(
            img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        img = cv2.putText(img, f"{inference_time:1.3f}, FPS:{int(1/inference_time)}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
        
    
        

if __name__ == "__main__":
    main()