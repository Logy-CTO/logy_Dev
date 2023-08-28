import tkinter as tk
from tkinter import ttk
from tkinter import Canvas
import numpy as np
from scipy.spatial.transform import Rotation as R
from helpers import shutdown, sendToSteamVR
import cv2
from PIL import Image,ImageTk
from queue import Queue
#use_steamvr = True

class InferenceWindow(tk.Frame):
    def __init__(self, root, params,queue=None, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        
        self.params = params
        params.gui = self       #uhh is this a good idea?
        self.root = root
        self.queue = queue
        #-----
        self.canvas = Canvas(root, width=640, height=480)
        self.canvas.pack()
        #-----
        # calibrate rotation
        self.calib_rot_var = tk.BooleanVar(value=self.params.calib_rot)
        self.calib_flip_var = tk.BooleanVar(value=self.params.flip)
       
        frame1 = tk.Frame(self.root)
        frame1.pack()
        self.calibrate_rotation_frame(frame1)

        self.put_separator()

        # calibrate tilt
        self.calib_tilt_var = tk.BooleanVar(value=self.params.calib_tilt)
      
        frame2 = tk.Frame(self.root)
        frame2.pack()
        self.calibrate_tilt_frame(frame2)

        self.put_separator()

        # calibrate scale
        self.calib_scale_var = tk.BooleanVar(value=self.params.calib_scale)
       

        frame3 = tk.Frame(self.root)
        frame3.pack()
        self.calibrate_scale_frame(frame3)

        self.put_separator()

        # recalibrate
        tk.Button(self.root, text='Recalibrate (automatically recalibrates checked values above)', 
                    command=self.autocalibrate).pack()
                    
        # pause tracking
        tk.Button(self.root, text='Pause/Unpause tracking', 
                    command=self.pause_tracking).pack()
                  
        
        # show the Profile 1 profile 2 text:
        if params.advanced:
            frame_profile = tk.Frame(self.root)
            frame_profile.pack()
            tk.Label(frame_profile, text=" ", width = 20).pack(side='left')
            tk.Label(frame_profile, text="Profile 1", width = 10).pack(side='left')
            tk.Label(frame_profile, text=" ", width = 5).pack(side='left')
            tk.Label(frame_profile, text="Profile 2", width = 10).pack(side='left')
            tk.Label(frame_profile, text=" ", width = 5).pack(side='left')
            tk.Label(frame_profile, text=" ", width = 5).pack(side='left')

        # smoothing
        if params.advanced:
            frame4 = tk.Frame(self.root)
            frame4.pack()
            self.change_smooothing_frame(frame4)

        # smoothing
        frame4_2 = tk.Frame(self.root)
        frame4_2.pack()
        self.change_add_smoothing_frame(frame4_2)

        # smoothing
        if params.advanced:
            frame4_1 = tk.Frame(self.root)
            frame4_1.pack()
            self.change_cam_lat_frame(frame4_1)

        # rotate image 
        frame5 = tk.Frame(self.root)
        frame5.pack()
        self.change_image_rotation_frame(frame5)
        
        # neck offset
        if params.advanced:
            frame6 = tk.Frame(self.root)
            frame6.pack()
            self.change_neck_offset_frame(frame6)
        
        #frametime log
        self.log_frametime_var = tk.BooleanVar(value=self.params.log_frametime)
       

        # exit
        tk.Button(self.root, text='Press to exit', command=self.params.ready2exit).pack()

        root.protocol("WM_DELETE_WINDOW", self.params.ready2exit) # when press x
    #--------
    def show_frame_on_canvas(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def update(self):
        while not self.queue.empty():
            img = self.queue.get()
            self.show_frame_on_canvas(img)
        self.root.after(1000//60, self.update)  # 60fps로 업데이트   
    #--------     
    def change_neck_offset_frame(self,frame):
        tk.Label(frame, text="HMD to neck offset:", width = 20).pack(side='left')
        
        text1 = tk.Entry(frame, width = 5)
        text1.pack(side='left')
        text1.insert(0, self.params.hmd_to_neck_offset[0])
        
        text2 = tk.Entry(frame, width = 5)
        text2.pack(side='left')
        text2.insert(0, self.params.hmd_to_neck_offset[1])
        
        text3 = tk.Entry(frame, width = 5)
        text3.pack(side='left')
        text3.insert(0, self.params.hmd_to_neck_offset[2])

        tk.Button(frame, text='Update', command=lambda *args: self.params.change_neck_offset(float(text1.get()),float(text2.get()),float(text3.get()))).pack(side='left')

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
       
    def change_smooothing_frame(self, frame):
        
        tk.Label(frame, text="Smoothing window:", width = 20).pack(side='left')
        smoothingtext1 = tk.Entry(frame, width = 10)
        smoothingtext1.pack(side='left')
        smoothingtext1.insert(0, self.params.smoothing_1)

        tk.Button(frame, text='Update', command=lambda *args: self.params.change_smoothing(float(smoothingtext1.get()),1)).pack(side='left')
        
        if self.params.advanced:
            smoothingtext2 = tk.Entry(frame, width = 10)
            smoothingtext2.pack(side='left')
            smoothingtext2.insert(0, self.params.smoothing_2)

            tk.Button(frame, text='Update', command=lambda *args: self.params.change_smoothing(float(smoothingtext2.get()),2)).pack(side='left')
        
        tk.Button(frame, text='Disable', command=lambda *args: self.params.change_smoothing(0.0)).pack(side='left')


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


def make_inference_gui(_params, root=None, _queue=None):
    
    root = tk.Tk()
    InferenceWindow(root,_params,_queue).pack(side="top", fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    
    print("hehe")