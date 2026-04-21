import cv2
import mediapipe as mp
import numpy as np
import time
import sys
import os


CAT_VIDEO_PATH = "kicau-mania.mp4" 
WAVE_THRESHOLD = 1                 # NOTE: Cukup 1 kibasan (kanan atau kiri) langsung muncul
WAVE_AMPLITUDE = 0.01              # NOTE: Gerakan sangat kecil (1% lebar layar) sudah terbaca
MOUTH_COVER_DISTANCE = 0.35        # NOTE: Tangan tidak perlu menempel banget ke mulut
COVER_WAVE_WINDOW = 5.0            # NOTE: Memberi waktu lebih lama setelah tutup mulut
TRIGGER_COOLDOWN = 0.3             # NOTE: Respons lebih instan
INACTIVE_RESET_SECONDS = 1.0       # NOTE: Toleransi jika tangan berhenti sejenak agar tidak reset
PLAY_TIMEOUT = 0.5                 # NOTE: Video menutup lebih cepat jika benar-benar diam              


#  SETUP MEDIAPIPE

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_draw  = mp.solutions.drawing_utils

hands_detector = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.4  
)

face_mesh_detector = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

def find_trigger_video():
    if os.path.exists(CAT_VIDEO_PATH):
        return CAT_VIDEO_PATH
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    mp4_candidates = sorted([f for f in files if f.lower().endswith(".mp4")])
    if mp4_candidates:
        return mp4_candidates[0]
    return None

def get_hand_center(hand_landmarks):
    wrist = hand_landmarks.landmark[0]
    index_mcp = hand_landmarks.landmark[5]
    pinky_mcp = hand_landmarks.landmark[17]
    center_x = (wrist.x + index_mcp.x + pinky_mcp.x) / 3.0
    center_y = (wrist.y + index_mcp.y + pinky_mcp.y) / 3.0
    return center_x, center_y

def get_mouth_center(face_landmarks):
    upper_lip = face_landmarks.landmark[13]
    lower_lip = face_landmarks.landmark[14]
    mouth_x = (upper_lip.x + lower_lip.x) / 2.0
    mouth_y = (upper_lip.y + lower_lip.y) / 2.0
    return mouth_x, mouth_y

def is_mouth_covered(hand_centers, mouth_center, threshold=MOUTH_COVER_DISTANCE):
    if mouth_center is None or len(hand_centers) < 2:
        return False
    mouth_x, mouth_y = mouth_center
    for hand_x, hand_y in hand_centers:
        distance = np.hypot(hand_x - mouth_x, hand_y - mouth_y)
        if distance <= threshold:
            return True
    return False

class WaveDetector:
    def __init__(self):
        self.last_x = None
        self.peak_x = None
        self.direction = 0  
        self.direction_count = 0
        self.last_move_time = time.time()

    def reset(self):
        self.last_x = None
        self.peak_x = None
        self.direction = 0
        self.direction_count = 0
        self.last_move_time = time.time()

    def is_moving(self):
        return (time.time() - self.last_move_time) < PLAY_TIMEOUT

    def update(self, x_position):
        now = time.time()
        if now - self.last_move_time > INACTIVE_RESET_SECONDS:
            self.reset()

        if self.last_x is None:
            self.last_x = x_position
            self.peak_x = x_position
            return False

        delta = x_position - self.last_x
        self.last_x = x_position

        if abs(delta) > 0.005:
            self.last_move_time = now
            new_direction = 1 if delta > 0 else -1

            if self.direction != new_direction and self.direction != 0:
                amplitude = abs(x_position - self.peak_x)
                if amplitude >= WAVE_AMPLITUDE:
                    self.direction_count += 1
                self.peak_x = x_position
                
            self.direction = new_direction
            
            if self.direction == 1:
                self.peak_x = max(self.peak_x, x_position)
            else:
                self.peak_x = min(self.peak_x, x_position)

        is_wave = self.direction_count >= WAVE_THRESHOLD
        if is_wave:
            self.reset()
            
        return is_wave


#  FUNGSI UTAMA

def main():
    print("\nKICAU MANIA DETECTOR - Starting...\n")

    trigger_video_path = find_trigger_video()
    if trigger_video_path is None:
        print("ERROR: Video MP4 tidak ditemukan!")
        sys.exit(1)

    print("Memuat video ke memori... (Pre-loading)")
    cat_cap = cv2.VideoCapture(trigger_video_path)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30) 
    
    wave_detector_left = WaveDetector()
    wave_detector_right = WaveDetector()
    
    last_mouth_cover_time = 0.0
    last_trigger_time = 0.0

    is_playing = False
    last_movement_time = 0.0
    
    print("\n[READY] Aplikasi siap digunakan! Tekan Q pada jendela kamera untuk keluar.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hands_result = hands_detector.process(rgb_frame)
        face_result = face_mesh_detector.process(rgb_frame)

        hand_centers = []
        mouth_center = None

        if face_result.multi_face_landmarks:
            face_landmarks = face_result.multi_face_landmarks[0]
            mouth_center = get_mouth_center(face_landmarks)
            mx, my = int(mouth_center[0] * w), int(mouth_center[1] * h)
            # Anda bisa menghapus 2 baris cv2.circle di bawah jika tidak ingin ada titik di mulut
            cv2.circle(frame, (mx, my), 12, (255, 255, 255), 2)

        if hands_result.multi_hand_landmarks:
            for hand_landmarks in hands_result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hx, hy = get_hand_center(hand_landmarks)
                hand_centers.append((hx, hy))
                cx, cy = int(hx * w), int(hy * h)
                # Anda bisa menghapus cv2.circle di bawah jika tidak ingin ada titik di tangan
                cv2.circle(frame, (cx, cy), 12, (0, 255, 120), -1)

        hand_centers.sort(key=lambda p: p[0])
        now = time.time()

        two_hands_ready = len(hand_centers) >= 2
        mouth_cover_now = is_mouth_covered(hand_centers, mouth_center)

        if mouth_cover_now:
            last_mouth_cover_time = now
        mouth_recent = (now - last_mouth_cover_time) <= COVER_WAVE_WINDOW

        wave_now = False
        
        if len(hand_centers) > 0:
            if hand_centers[0][0] < 0.6 or len(hand_centers) == 1:
                wave_left = wave_detector_left.update(hand_centers[0][0])
            else:
                wave_left = False
                
            if len(hand_centers) >= 2:
                wave_right = wave_detector_right.update(hand_centers[1][0])
            else:
                wave_right = False
                
            wave_now = wave_left or wave_right

        can_trigger = (now - last_trigger_time) >= TRIGGER_COOLDOWN
        trigger_now = two_hands_ready and mouth_recent and wave_now and can_trigger

        # =========================================================
        # LOGIKA PEMUTAR VIDEO BEBAS FREEZE
        # =========================================================
        
        if trigger_now and not is_playing:
            is_playing = True
            last_movement_time = now
            print("=> TRIGGER AKTIF! Video ditampilkan.")
            last_trigger_time = now
            wave_detector_left.reset()
            wave_detector_right.reset()
            
            if cat_cap.isOpened():
                cat_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        if is_playing:
            if wave_detector_left.is_moving() or wave_detector_right.is_moving():
                last_movement_time = now
            
            if now - last_movement_time > PLAY_TIMEOUT:
                is_playing = False
                print("=> DIAM. Menyembunyikan video.")
                try:
                    cv2.destroyWindow("🐾 KICAU MANIA 🐾")
                    cv2.waitKey(1) 
                except:
                    pass
            else:
                ret_cat, cat_frame = cat_cap.read()
                if not ret_cat:
                    cat_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret_cat, cat_frame = cat_cap.read()
                
                if ret_cat:
                    cv2.imshow("🐾 KICAU MANIA 🐾", cat_frame)

        # =========================================================

        cv2.imshow("Kicau Mania Detector", frame)

        if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
            break

    cap.release()
    if cat_cap is not None:
        cat_cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
