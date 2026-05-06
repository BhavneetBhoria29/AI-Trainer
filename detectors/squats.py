from core.base_exercise import BaseExercise 

class SquatDetector(BaseExercise):
    def perform(self, landmarks):
        return self.process(landmarks)




    DOWN_THRESHOLD=100
    UP_THRESHOLD=160
    MIN_VISIBILITY=0.7

    LEFT_HIP=23
    LEFT_KNEE=25
    LEFT_ANKLE=27
    RIGHT_HIP=24
    RIGHT_KNEE=26
    RIGHT_ANKLE=28
    LEFT_SHOULDER=11
    RIGHT_SHOULDER=12



    def __init__(self):
        super().__init__()
        

    def reset(self):
        self.reps=0
        self.stage=None

    def process(self,landmarks):
        
        left_knee_angle= self.calculate_angle(
            self.get_point(landmarks,self.LEFT_HIP),
            self.get_point(landmarks,self.LEFT_KNEE),
            self.get_point(landmarks,self.LEFT_ANKLE)
        )

        right_knee_angle= self.calculate_angle(
            self.get_point(landmarks,self.RIGHT_HIP),
            self.get_point(landmarks,self.RIGHT_KNEE),
            self.get_point(landmarks,self.RIGHT_ANKLE)
        )
        left_vis=landmarks[self.LEFT_KNEE].visibility
        right_vis=landmarks[self.RIGHT_KNEE].visibility 


        if left_vis >= right_vis:
            knee_angle= left_knee_angle
            hip_idx,knee_idx,ankle_idx,shoulder_idx=self.LEFT_HIP,self.LEFT_KNEE,self.LEFT_ANKLE,self.LEFT_SHOULDER
        else:
            knee_angle= right_knee_angle
            hip_idx,knee_idx,ankle_idx,shoulder_idx=self.RIGHT_HIP,self.RIGHT_KNEE,self.RIGHT_ANKLE,self.RIGHT_SHOULDER



        back_angle=self.calculate_angle(
            self.get_point(landmarks,shoulder_idx),
            self.get_point(landmarks,hip_idx),
            self.get_point(landmarks,knee_idx)
        )

        key_landmark_visible= landmarks[hip_idx].visibility>=self.MIN_VISIBILITY and landmarks[knee_idx].visibility>=self.MIN_VISIBILITY and landmarks[ankle_idx].visibility>=self.MIN_VISIBILITY and landmarks[shoulder_idx].visibility>=self.MIN_VISIBILITY


        if key_landmark_visible:
            if knee_angle <= self.DOWN_THRESHOLD:
                self.stage="down"
            if knee_angle >= self.UP_THRESHOLD and self.stage=="down":
                self.stage="up"
                self.reps+=1

        if self.stage=="down":
            depth_status="Good Depth" if knee_angle<=self.DOWN_THRESHOLD else "Too Shallow"
        elif self.stage=="up":
            depth_status="Standing"
        else:
            depth_status="N/A"

        if key_landmark_visible:
            if back_angle >= 150:
                body_alignment = "Upright ✅"
            elif back_angle >= 120:
                body_alignment = "Slight Lean ⚠️"
            else:
                body_alignment = "Leaning ❌"
        else:
            body_alignment = "N/A"

        hip_y = landmarks[hip_idx].y
        knee_y = landmarks[knee_idx].y
        if key_landmark_visible:
            hip_status = "At Depth ✅" if hip_y >= knee_y else "Above Parallel"
        else:
            hip_status = "N/A"

        ankle_x = landmarks[ankle_idx].x
        shoulder_x = landmarks[shoulder_idx].x
        if key_landmark_visible:
            balance_status = "Balanced ✅" if abs(shoulder_x - ankle_x) < 0.12 else "Off Balance ⚠️"
        else:
            balance_status = "N/A"

        return {
            "reps": self.reps,
            "knee_angle": int(knee_angle),
            "front_knee_angle": int(knee_angle),
            "back_angle": int(back_angle),
            "torso_angle": int(back_angle),
            "depth_status": depth_status,
            "body_alignment": body_alignment,
            "hip_status": hip_status,
            "balance_status": balance_status,
        }

