from core.base_exercise import BaseExercise


class LungeDetector(BaseExercise):
    
    def perform(self, landmarks):
        return self.process(landmarks)




    # Front knee should bend to ~90° at bottom, fully extended ~170° at top
    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.7

    # Landmarks
    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27
    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    # For back knee (trailing leg) — used for depth check
    # In a lunge the back knee drops toward the floor
    BACK_KNEE_DOWN_THRESHOLD = 110  # back knee bends more acutely

    def __init__(self):
        super().__init__()

    def reset(self):
        self.reps = 0
        self.stage = None

    def process(self, landmarks):

        # ── Determine which leg is the front (more visible) leg ──────────────
        left_vis = landmarks[self.LEFT_KNEE].visibility
        right_vis = landmarks[self.RIGHT_KNEE].visibility

        if left_vis >= right_vis:
            # Left leg is front leg
            front_hip, front_knee, front_ankle, front_shoulder = (
                self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE, self.LEFT_SHOULDER
            )
            back_hip, back_knee, back_ankle = (
                self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE
            )
        else:
            # Right leg is front leg
            front_hip, front_knee, front_ankle, front_shoulder = (
                self.RIGHT_HIP, self.RIGHT_KNEE, self.RIGHT_ANKLE, self.RIGHT_SHOULDER
            )
            back_hip, back_knee, back_ankle = (
                self.LEFT_HIP, self.LEFT_KNEE, self.LEFT_ANKLE
            )

        # ── Angles ────────────────────────────────────────────────────────────

        # Front knee angle (tracks rep stage)
        front_knee_angle = self.calculate_angle(
            self.get_point(landmarks, front_hip),
            self.get_point(landmarks, front_knee),
            self.get_point(landmarks, front_ankle),
        )

        # Back knee angle (trailing leg depth check)
        back_knee_angle = self.calculate_angle(
            self.get_point(landmarks, back_hip),
            self.get_point(landmarks, back_knee),
            self.get_point(landmarks, back_ankle),
        )

        # Torso upright angle (shoulder → hip → front knee)
        torso_angle = self.calculate_angle(
            self.get_point(landmarks, front_shoulder),
            self.get_point(landmarks, front_hip),
            self.get_point(landmarks, front_knee),
        )

        # Back angle (hip alignment — same landmark set)
        back_angle = self.calculate_angle(
            self.get_point(landmarks, front_shoulder),
            self.get_point(landmarks, front_hip),
            self.get_point(landmarks, back_knee),
        )

        # ── Visibility gate ───────────────────────────────────────────────────
        key_landmarks_visible = (
            landmarks[front_hip].visibility >= self.MIN_VISIBILITY
            and landmarks[front_knee].visibility >= self.MIN_VISIBILITY
            and landmarks[front_ankle].visibility >= self.MIN_VISIBILITY
            and landmarks[front_shoulder].visibility >= self.MIN_VISIBILITY
        )

        # ── Rep counting (driven by front knee angle) ─────────────────────────
        if key_landmarks_visible:
            if front_knee_angle <= self.DOWN_THRESHOLD:
                self.stage = "down"
            if front_knee_angle >= self.UP_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1

        # ── Depth status ──────────────────────────────────────────────────────
        if self.stage == "down":
            depth_status = "Good Depth" if front_knee_angle <= self.DOWN_THRESHOLD else "Too Shallow"
        elif self.stage == "up":
            depth_status = "Standing"
        else:
            depth_status = "N/A"

        # ── Body alignment (torso should stay upright ~160-180°) ──────────────
        if key_landmarks_visible:
            if torso_angle >= 160:
                body_alignment = "Upright ✅"
            elif torso_angle >= 130:
                body_alignment = "Slight Lean ⚠️"
            else:
                body_alignment = "Too Much Lean ❌"
        else:
            body_alignment = "N/A"

        # ── Hip status (hips should be level and square) ──────────────────────
        left_hip_y = landmarks[self.LEFT_HIP].y
        right_hip_y = landmarks[self.RIGHT_HIP].y
        hip_diff = abs(left_hip_y - right_hip_y)

        if key_landmarks_visible:
            if hip_diff < 0.05:
                hip_status = "Level ✅"
            elif hip_diff < 0.10:
                hip_status = "Slightly Off ⚠️"
            else:
                hip_status = "Uneven ❌"
        else:
            hip_status = "N/A"

        # ── Front knee tracking (knee should not cave inward) ─────────────────
        front_knee_x = landmarks[front_knee].x
        front_ankle_x = landmarks[front_ankle].x
        knee_drift = front_knee_x - front_ankle_x

        if key_landmarks_visible and self.stage == "down":
            if abs(knee_drift) < 0.05:
                knee_tracking = "Good Tracking ✅"
            else:
                knee_tracking = "Knee Caving ❌" if knee_drift < 0 else "Knee Drifting ⚠️"
        else:
            knee_tracking = "N/A"

        # ── Balance status (vertical alignment of shoulder over hip) ──────────
        shoulder_x = landmarks[front_shoulder].x
        hip_x = landmarks[front_hip].x
        balance_drift = abs(shoulder_x - hip_x)

        if key_landmarks_visible:
            balance_status = "Balanced ✅" if balance_drift < 0.08 else "Off Balance ⚠️"
        else:
            balance_status = "N/A"

        return {
            "reps": self.reps,
            "front_knee_angle": int(front_knee_angle),
            "back_knee_angle": int(back_knee_angle),
            "torso_angle": int(torso_angle),
            "back_angle": int(back_angle),
            "depth_status": depth_status,
            "body_alignment": body_alignment,
            "hip_status": hip_status,
            "knee_tracking": knee_tracking,
            "balance_status": balance_status,
        }