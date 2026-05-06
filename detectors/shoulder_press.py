import math
from core.base_exercise import BaseExercise


class ShoulderPress(BaseExercise):

    def perform(self, landmarks):
        return self.process(landmarks)

    UP_THRESHOLD = 150       # arm extended overhead (large angle)
    DOWN_THRESHOLD = 90      # arm back at start position (small angle)
    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    LEFT_KNEE = 25
    RIGHT_HIP = 24
    RIGHT_KNEE = 26

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = None

    def process(self, landmarks) -> dict:
        left_vis = landmarks[self.LEFT_ELBOW].visibility
        right_vis = landmarks[self.RIGHT_ELBOW].visibility

        if left_vis >= right_vis:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE

        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        key_landmarks_visible = (
            landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY
            and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
        )

        if key_landmarks_visible:
            if elbow_angle >= self.UP_THRESHOLD and self.stage != "up":
                self.stage = "up"
            if elbow_angle <= self.DOWN_THRESHOLD and self.stage == "up":
                self.stage = "down"
                self.reps += 1

        if elbow_angle >= self.UP_THRESHOLD:
            shoulder_status = "OVERHEAD"
            extension_status = "FULLY EXTENDED"
        elif elbow_angle >= 120:
            shoulder_status = "NEARLY EXTENDED"
            extension_status = "NEARLY EXTENDED"
        elif elbow_angle >= self.DOWN_THRESHOLD:
            shoulder_status = "MID PRESS"
            extension_status = "PRESSING"
        else:
            shoulder_status = "START POSITION"
            extension_status = "AT START"

        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        if back_angle >= 160:
            back_arch_status = "GOOD"
        elif back_angle >= 140:
            back_arch_status = "SLIGHT BEND"
        else:
            back_arch_status = "BENT"

        return {
            "reps": self.reps,
            "elbow_angle": int(elbow_angle),
            "shoulder_status": shoulder_status,
            "extension_status": extension_status,
            "swing_status": "N/A",
            "back_angle": int(back_angle),
            "back_arch_status": back_arch_status,
        }
