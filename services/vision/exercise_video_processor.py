import threading
import os
import cv2
from streamlit_webrtc import VideoProcessorBase
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from detectors.squats import SquatDetector
from detectors.bench_press import BenchPressDetector
from detectors.biceps_curl import BicepCurl
from detectors.lunges import LungeDetector
from detectors.shoulder_press import ShoulderPress
from services.config.workout_config import POSE_CONNECTIONS
import numpy as np
import mediapipe as mp
import av



class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._landmarker_lock = threading.Lock()
        self._latest_metrics= None
        self._exercise_type="squats"

        model_path=os.path.join(os.getcwd(),"ml_models","pose_landmarker_full.task")
        base_option= python.BaseOptions(model_asset_path=model_path)


        options= vision.PoseLandmarkerOptions(
            base_options=base_option,
            running_mode= vision.RunningMode.IMAGE,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            output_segmentation_masks=False

        )

        self._landmarker=vision.PoseLandmarker.create_from_options(options)


        self.detectors={
                "squats": SquatDetector(),
                "bench_press" : BenchPressDetector(),
                "biceps_curl" : BicepCurl(),
                "lunges": LungeDetector(),
                "shoulder_press": ShoulderPress(),

        }

    def set_latest_metrics(self, metrics):
        with self._lock:
            self._latest_metrics = metrics.copy()


    def get_latest_metrics(self):
        with self._lock:
            return None if self._latest_metrics is None else self._latest_metrics.copy()
        
    _EXERCISE_KEY_MAP = {
        "Squats": "squats",
        "Push-ups": "bench_press",
        "Biceps Curls (Dumbbell)": "biceps_curl",
        "Shoulder Press": "shoulder_press",
        "Lunges": "lunges",
    }

    def set_exercise(self,exercise_type):
        with self._lock:
            self._exercise_type = self._EXERCISE_KEY_MAP.get(
                exercise_type, exercise_type.lower().replace(" ", "_")
            )

    def get_exercise(self):
        with self._lock:
            return self._exercise_type
        

    def _draw_skeleton(self,img,landmarks):
        h,w=img.shape[:2]

        for start_idx, end_idx in POSE_CONNECTIONS:
            p1= landmarks[start_idx]
            p2= landmarks[end_idx]

            if p1.visibility > 0.7 and p2.visibility > 0.7:
                cv2.line(
                     img,
                    (int(p1.x*w),int(p1.y*h)),
                    (int(p2.x*w),int(p2.y*h)),
                    (0,255,0),
                    8

                )

        for lm in landmarks:
            if lm.visibility>0.7:
                cv2.circle(
                    img,
                    (int(lm.x*w),int(lm.y*h)),
                    8,
                    (255,0,0),
                    -1

                )

        return img
    
    def _draw_no_pose_warnings(self,img):
        cv2.putText(
            img,
            "NO POSE DETECTED",
            (30,50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
            cv2.LINE_AA
        )


        cv2.putText(
            img,
            "PLEASE FACE THE CAMERA",
            (30,100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
            cv2.LINE_AA
        )

    def _draw_overlays(self,img,metrics,ex_type):
        ex_type_lower = ex_type.lower()
        if ex_type_lower=="squats":
            self._draw_squats_overlays(img,metrics)
        elif ex_type_lower=="bench_press":
            self._draw_benchpress_overlays(img,metrics)
        elif ex_type_lower=="biceps_curl":
            self._draw_bicepcurl_overlays(img,metrics)
        elif ex_type_lower=="shoulder_press":
            self._draw_shoulderpress_overlays(img,metrics)
        elif ex_type_lower=="lunges":
            self._draw_lunges_overlays(img,metrics)

    def _draw_squats_overlays(self,img,metrics):
        h,_=img.shape[:2]
        cv2.putText(
            img,
            f"DEPTH:{metrics['depth_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
        )


    def _draw_benchpress_overlays(self, img, metrics):
        h, _ = img.shape[:2]
        cv2.putText(
            img,
            f"EXT:{metrics['extension_status']} | ARCH:{metrics['back_arch_status']}",
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )


    
    def _draw_bicepcurl_overlays(self,img,metrics):
        h,_=img.shape[:2]
        cv2.putText(
            img,
            f"SWING:{metrics['swing_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
        )


    def _draw_shoulderpress_overlays(self,img,metrics):
        h,_=img.shape[:2]
        cv2.putText(
            img,
            f"EXT:{metrics['extension_status']} | BACK:{metrics['back_arch_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
        )


    def _draw_lunges_overlays(self,img,metrics):
        h,_=img.shape[:2]
        cv2.putText(
            img,
            f"BALANCE:{metrics['balance_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
        )

    def recv(self,frame):
        image= frame.to_ndarray(format="bgr24")
        image= cv2.flip(image,1)

        try:
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
            )

            with self._landmarker_lock:
                result= self._landmarker.detect(mp_image)

            if result.pose_landmarks:
                landmarks=result.pose_landmarks[0]
                self._draw_skeleton(image,landmarks)

                ex_type=self.get_exercise()
                detector= self.detectors.get(ex_type)

                if detector:
                    try:
                        metrics= detector.process(landmarks)
                        self._draw_overlays(image,metrics,ex_type)
                        self.set_latest_metrics(metrics)
                    except Exception as e:
                        cv2.putText(image, f"DETECTOR ERR: {str(e)[:50]}", (30,150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
            else:
                self._draw_no_pose_warnings(image)

        except Exception as e:
            cv2.putText(image, f"RECV ERR: {str(e)[:60]}", (30,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        return av.VideoFrame.from_ndarray(image,format="bgr24")                             
