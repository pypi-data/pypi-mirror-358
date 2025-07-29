import argparse
import os

# **********************************************************************************************
def control_by_hand():
    import cv2
    import mediapipe as mp
    import pyautogui
    import numpy as np
    import datetime
    from time import sleep
    from shapely.geometry import Point
    from shapely.geometry.polygon import Polygon
    import os
    import copy
    import serial
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    def batMusic():
        ser.write(b'batloa\r')

    def tatMusic():
        ser.write(b'tatloa\r')

    def phanhoi():
        print(ser.readline().decode().strip())

    def isInside(points, centroid):
        polygon = Polygon(points)
        centroid = Point(centroid)
        return polygon.contains(centroid)

    def distance(point_1, point_2):
        """Calculate l2-norm between two points

        import math
        import numpy as np

            xa, ya = 1, 3
            xb, yb = 2, -2

            res1 = math.hypot(xa - xb, ya - yb)
            print(f"Khoang cach 1: {res1:.2f}")

            res2 = distance((xa, ya), (xb, yb))
            print(f"Khoang cach 2: {res2:.2f}")

            res3 = distance([xa, ya], [xb, yb])
            print(f"Khoang cach 3: {res3:.2f}")

            a = np.array([4, 9])
            b = np.array([2, -17])
            distance_E = np.linalg.norm(a - b)
            print("Khoang cach Euclidean:", distance_E)
        """
        dist = sum([(i - j) ** 2 for i, j in zip(point_1, point_2)]) ** 0.5
        return dist

    # Thiết lập kết nối Serial với Arduino
    ser = serial.Serial(port='COM4', baudrate=9600, timeout=0.2)

    # Lấy device đầu ra
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )

    # Cast về interface IAudioEndpointVolume
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    volRange=volume.GetVolumeRange()  # phạm vi âm lương

    minVol = volRange[0]
    maxVol = volRange[1]

    smooth = 12
    plocX, plocY = 0, 0  # Tọa độ chuột trước đó
    clocX, clocY = 0, 0  # Tọa độ chuột hiện tại
    fingers_number = [4, 8, 12, 16, 20]  # Các chỉ số landmark của các đầu ngón tay
    kt_udxc_lancuoi = None
    kt_udxc_sau = 0.5
    kt_udVolume_lancuoi = None
    music_active = False  # Trạng thái của biểu tượng Music
    volume_active = False
    myassistant_active = False  # Trạng thái của biểu tượng My Assistant
    isExit = False  # Biến để kiểm tra xem có thoát chương trình hay không
    isShutdown = False

    # Chiều cao và chiều rộng màn hinh.
    screen_width, screen_height = pyautogui.size()
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,       # False để xử lý video/live-stream
        max_num_hands=1,               # Số tay tối đa phát hiện
        min_detection_confidence=0.65,  # Ngưỡng tin cậy khi phát hiện
        min_tracking_confidence=0.5    # Ngưỡng tin cậy khi theo dõi
    )

    cap = cv2.VideoCapture(0)  # 0 là camera mặc định
    # Xác định kích thước camera
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # print(f"Kich thuoc camera: {frame_width}x{frame_height}")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Khong the doc video")
            break
        # Đảo ngược hình ảnh theo chiều ngang để hiển thị đúng hướng
        image = cv2.flip(image, 1)
        h, w, _ = image.shape
        image_deepcopy = copy.deepcopy(image)  # Lưu bản sao của hình ảnh để vẽ các hình khác

        points1 = [[185, 0], [185, 155], [485, 155], [485, 0], [185, 0]]
        for i in range(len(points1) - 1):
            cv2.line(image, tuple(points1[i]), tuple(points1[i + 1]), (0, 255, 255), 2)

        cv2.rectangle(image, (235, 40), (435, 125), (0, 255, 0), 2)  # Viền chữ nhật
        cv2.putText(image, "My Computer", (260, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        # Vẽ hình chữ nhật Music
        music_color = (0, 0, 255) if music_active else (255, 0, 0)  # Đỏ nếu active, xám nếu không
        cv2.rectangle(image, (110, 200), (190, 280), music_color, -1)  # Hình chữ nhật Music
        cv2.putText(image, "Music", (125, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, music_color, 2)

        # Vẽ hình chữ nhật My Assistant
        myassistant_color = (0, 0, 255) if myassistant_active else (255, 0, 0)  # Đỏ nếu active, xám nếu không
        cv2.rectangle(image, (290, 200), (370, 270), myassistant_color, -1)  # Viền chữ nhật
        cv2.putText(image, "My Assistant", (280, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, myassistant_color, 2)

        # Vẽ hình chữ nhật Exit
        Exit_color = (255, 0, 0) if isExit else (0, 0, 255)  # Đỏ nếu active, xám nếu không
        cv2.rectangle(image, (470, 200), (550, 280), Exit_color, -1)
        cv2.putText(image, "Exit", (495, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, Exit_color, 2)
        # Vẽ hình tròn giữa Music và My Assistant
        volume_color = (0, 0, 255) if volume_active else (255, 0, 0)  # Đỏ nếu active, xám nếu không
        circle1_center = (int((190 + 290) / 2), int((280 + 200) / 2))
        cv2.circle(image, circle1_center, 40, volume_color, -1)
        cv2.putText(image, "Volume", (circle1_center[0] - 30, circle1_center[1] + 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, volume_color, 2)
        cv2.circle(image, (45, 320),30, volume_color, -1)
        cv2.putText(image, "Vol_deactive", (25, 370), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, volume_color, 2)

        # Vẽ hình tròn giữa Exit và My Assistant
        circle2_center = (int((370 + 470) / 2), int((280 + 200) / 2))
        cv2.circle(image, circle2_center, 40, (0, 0, 255), -1)
        cv2.putText(image, "shutdown", (400, 290), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        points2 = [[110, 200], [110, 280], [190, 280], [190, 200], [190, 200]]
        points3 = [[290, 200], [290, 280], [370, 280], [370, 200], [290, 200]]
        points4 = [[470, 200], [470, 280], [550, 280], [550, 200], [470, 200]]

        # Chuyển đổi màu sắc từ BGR sang RGB
        image_rgb = cv2.cvtColor(image_deepcopy, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # Vẽ các landmark của tay nếu có
        if results.multi_hand_landmarks:
            myHand = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(
                image,
                myHand,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0,0,255), thickness=2)
            )

            lm_List = []
            for id, lm in enumerate(myHand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_List.append([id, cx, cy])
                cv2.putText(image, str(id), (cx+10, cy+10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
            if len(lm_List) != 0:
                
                # Lấy tọa độ ngón trỏ.
                x1, y1 = lm_List[8][1], lm_List[8][2]
                centroid = (x1, y1)  # Tọa độ ngón trỏ làm tâm
                p4 = [lm_List[4][1], lm_List[4][2]]
                cv2.circle(image, (x1, y1), 10, (255, 0, 0), -1)

                # Xác định sự co duỗi của các ngón tay.
                fingers = [] # [1, 0, 0, 0, 0] # Ngón cái duỗi, các ngón còn lại co
                # Ngón cái
                if lm_List[4][1] < lm_List[3][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                # Xác định các ngón tay còn lại
                for id,  finger_id in enumerate(fingers_number):
                    if id == 0:
                        continue
                    if lm_List[finger_id][2] < lm_List[finger_id - 2][2]:
                        fingers.append(1)
                        # print(f"Ngón {id + 1} duỗi")
                    else:
                        fingers.append(0)
                        # print(f"Ngón {id + 1} co")
                # print(f"Trạng thái các ngón tay: {fingers}")
                normal_distance = distance(lm_List[5][1:], lm_List[7][1:])
                lClick_distance = distance(lm_List[3][1:], lm_List[5][1:]) + 40

    # ***************************************************************************************************************************
                if isInside(points1, centroid):

                    # chuyển tọa độ ngón trỏ trên hình chữ nhật để tương ứng với màn hình máy tính.
                    if kt_udxc_lancuoi is None or ((datetime.datetime.utcnow() - kt_udxc_lancuoi).total_seconds() > kt_udxc_sau):
                        kt_udxc_lancuoi = datetime.datetime.utcnow()
                        x_c = np.interp(x1, (235, 435), (0, screen_width))
                        y_c = np.interp(y1, (40, 125), (0, screen_height))

                    # Làm mượt chuyển động chuột.
                    clocX = plocX + (x_c - plocX) / smooth
                    clocY = plocY + (y_c - plocY) / smooth

                    # chỉ ngón trỏ có chế độ di chuyển chuột.
                    if fingers[1] == 1:
                        if abs(plocX - x_c) > 10 or abs(plocY - y_c) > 10:
                            pyautogui.moveTo(clocX, clocY)
                            plocX, plocY = clocX, clocY
                    if fingers[1] == 1 and lClick_distance < normal_distance:
                        pyautogui.click(button='left')
                        sleep(0.7)  # Thêm độ trễ để tránh click liên tục
                if fingers.count(0) == 5:
                    pyautogui.doubleClick(button='left')
                    sleep(0.7)  # Thêm độ trễ để tránh double click liên tục
    # *****************************************************************************************************************************

                if music_active == False and myassistant_active == False and volume_active == False:

                    if isInside(points2, centroid) and fingers[1] == 1 and lClick_distance < normal_distance and not music_active:
                        music_active = True
                        batMusic()
                        sleep(3)
                        phanhoi()
                elif music_active == True and myassistant_active == False and volume_active == False:
                    if isInside(points2, centroid) and fingers[1] == 1 and lClick_distance < normal_distance and music_active:
                        music_active = False
                        tatMusic()
                        sleep(3)
                        phanhoi()
    # *****************************************************************************************************************************
                if music_active == False and myassistant_active == False and volume_active == False:
                    if isInside(points3, centroid) and fingers[1] == 1 and lClick_distance < normal_distance and not myassistant_active:
                        myassistant_active = True
                        print("Kich hoat My Assistant")
                        os.system("start a.bat")
                elif music_active == False and myassistant_active == True and volume_active == False:
                    if isInside(points3, centroid) and fingers[1] == 1 and lClick_distance < normal_distance and myassistant_active:
                        music_active = False

    # *****************************************************************************************************************************
                if music_active == False and myassistant_active == False and volume_active == False:
                    if isInside(points4, centroid) and fingers[1] == 1 and lClick_distance < normal_distance:
                        isExit = True
                        print("Thoat chuong trinh")
                        break
    # *****************************************************************************************************************************
                if music_active == False and myassistant_active == False and volume_active == False:
                    # Kiểm tra nếu ngón trỏ nằm trong hình tròn Volume
                    if distance(centroid, circle1_center) <= 40 and fingers[1] == 1 and lClick_distance < normal_distance and not volume_active:
                        volume_active = True
                        sleep(3)
                        print("Volume control activated")

                        x4, y4 = lm_List[4][1:]
                        x8, y8 = lm_List[8][1:]
                        cvx, cvy = (x4 + x8) // 2, (y4 + y8) // 2
                        cv2.circle(image, (x4, y4), 7, (255, 0, 255), -1)
                        cv2.circle(image, (x8, y8), 7, (255, 0, 255), -1)
                        cv2.circle(image, (cvx, cvy), 7, (255, 0, 255), -1)
                        cv2.line(image, (x4, y4), (x8, y8), (255, 0, 255), 2)

                        length = distance(lm_List[4][1:], lm_List[8][1:])
                        vol = np.interp(length,(35,170),(minVol,maxVol))
            
                        volume.SetMasterVolumeLevel(vol, None)
                        if length <= 35:
                            cv2.circle(image, (cvx, cvy), 7, (0, 255, 0), -1)
                elif music_active == False and myassistant_active == False and volume_active == True:
                    if distance(centroid, circle1_center) <= 40 and fingers[1] == 1 and lClick_distance < normal_distance and volume_active:
                        sleep(3)
                        volume_active = False
                        print("Volume control no activated")
                if volume_active:
                    if kt_udVolume_lancuoi is None or ((datetime.datetime.utcnow() - kt_udVolume_lancuoi).total_seconds() > 0.6):
                        kt_udVolume_lancuoi = datetime.datetime.utcnow()
                        x4, y4 = lm_List[4][1:]
                        x8, y8 = lm_List[8][1:]
                        cvx, cvy = (x4 + x8) // 2, (y4 + y8) // 2
                        cv2.circle(image, (x4, y4), 7, (255, 0, 255), -1)
                        cv2.circle(image, (x8, y8), 7, (255, 0, 255), -1)
                        cv2.circle(image, (cvx, cvy), 7, (255, 0, 255), -1)
                        cv2.line(image, (x4, y4), (x8, y8), (255, 0, 255), 2)

                        length = distance(lm_List[4][1:], lm_List[8][1:])
                        vol = np.interp(length,(35,170),(minVol,maxVol))
            
                        volume.SetMasterVolumeLevel(vol, None)
                        if length <= 35:
                            cv2.circle(image, (cvx, cvy), 7, (0, 255, 0), -1)
                if volume_active == True and distance(p4, [45, 320]) <= 30:
                    volume_active = False

                if music_active == False and myassistant_active == False and volume_active == False:
                    if distance(centroid, circle2_center) <= 40 and fingers[1] == 1 and lClick_distance < normal_distance:
                        isShutdown = True
                        print("Tat may tinh.")
                        # os.system("shutdown /s /t 5")
                        break
                    
        vol_Per = volume.GetMasterVolumeLevelScalar()
        vol_Per = vol_Per * 100
        volBar = np.interp(vol_Per,(0, 100),(135,35))
        cv2.putText(image,f"vol {str(int(vol_Per))}%", (525, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        # Vẽ hình chữ nhật volume
        cv2.rectangle(image, (545, 35), (575, 135), (0, 255, 0), 2)
        cv2.rectangle(image, (545, int(volBar)), (575, 135), (0, 255, 0), -1)
        # Hiển thị kết quả
        cv2.imshow('Control_by_hand', image)
        cv2.setWindowProperty('Control_by_hand', cv2.WND_PROP_TOPMOST, 1)
        key = cv2.waitKey(5)
        # Lưu hình ảnh khi nhấn phím 's'
        if key == ord('s'):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hand_control_{timestamp}.png"
            filename = os.path.join(r"D:\Duan\20publish_pypi\tests", filename)
            if cv2.imwrite(filename, image):
                print(f"Hinh anh da duoc luu: {filename}")

        if key & 0xFF == 27:  # Nhấn 'Esc' để thoát
            break

    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyAllWindows()


    '''
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    # 1. Lấy device đầu ra
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )

    # 2. Cast về interface IAudioEndpointVolume
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    min_db, max_db = volume.GetVolumeRange()[:2]
    print(f"Volume range: {min_db:.2f} dB to {max_db:.2f} dB")
    # 3. Đọc mức âm lượng hiện tại (dB)
    current_db = volume.GetMasterVolumeLevel()
    print(f"Current master volume: {current_db:.2f} dB")

    # 4. Thiết lập âm lượng theo dB
    volume.SetMasterVolumeLevel(-25.0, None)    # Giảm xuống -5 dB
    current_db = volume.GetMasterVolumeLevel()
    print(f"Current master volume: {current_db:.2f} dB")

    # 5. Đọc/Thiết lập âm lượng theo tỷ lệ 0.0–1.0
    current_level = volume.GetMasterVolumeLevelScalar()  # 0.0–1.0
    print(f"Current master volume level: {current_level:.2f} (0.0–1.0)")
    volume.SetMasterVolumeLevelScalar(0.57, None)         # 57%
    current_level = volume.GetMasterVolumeLevelScalar()
    print(f"Current master volume level: {current_level:.2f} (0.0–1.0)")

    # 6. Đọc/Thiết lập mute
    is_muted = volume.GetMute()
    volume.SetMute(1, None)     # Mute
    volume.SetMute(0, None)     # Unmute
    '''
# ***********************************************************************************************

def clean_temp_files(temp_folder):
    if temp_folder and os.path.exists(temp_folder):
        for root, dirs, files in os.walk(temp_folder, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete file {file_path}: {e}")
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    # Only remove empty directories
                    os.rmdir(dir_path)
                    print(f"Deleted directory: {dir_path}")
                except Exception as e:
                    print(f"Failed to clean {temp_folder}: {e}")

# ******************Begin program cipher password************************************************************

def password_cipher():
    import os

    def xor_encrypt(plaintext: bytes, key: bytes) -> bytes:
        return bytes(p ^ key[i % len(key)] for i, p in enumerate(plaintext))
    
    def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    # cùng phép XOR, vì tính chất đảo ngược
        return xor_encrypt(ciphertext, key)

    FLAG_ENCRYPT = 0b0001
    FLAG_DECRYPT = 0b0010
    OPTION = 0b0000

    print("Chon 1 trong 2:")
    print("M. Ma hoa")
    print("G. Giai ma")
    choice = input("Nhap lua chon cua ban: ").lower()

    while choice not in ['m', 'g']:
            choice = input("Nhap M de ma hoa, G de giai ma: ").lower()
    if choice == 'm':
        OPTION |= FLAG_ENCRYPT
    else:
        OPTION |= FLAG_DECRYPT
    # Thuc hien ma hoa ********************************************************************************
    if OPTION & FLAG_ENCRYPT:
        key = os.getenv("keypass").encode('utf-8')
        if not key:
            print("Bien moi truong keypass khong ton tai.")
            return

        plaintext = input("Nhap van ban can ma hoa: ").encode('utf-8')

        add_note = input("Nhap them ghi chu cho password: ")

        ciphertext = xor_encrypt(plaintext, key)
        print(f"Van ban da ma hoa: {ciphertext}")

        # Đọc đường dẫn từ dòng số 2 trong tệp config.txt
        config_file = "config.txt"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    password_dir = lines[1].strip()  # Lấy dòng số 2 và loại bỏ khoảng trắng
                else:
                    print("Tệp config.txt không có đủ dòng.")
                    return
        else:
            print(f"Tệp cấu hình '{config_file}' không tồn tại.")
            return
        # Kiểm tra và tạo thư mục nếu chưa tồn tại
        if not os.path.exists(password_dir):
            os.makedirs(password_dir)
            print(f"Đã tạo thư mục: {password_dir}")
        else:
            print(f"Thư mục đã tồn tại: {password_dir}")
        # Sử dụng đường dẫn để lưu tệp
        file_path = os.path.join(password_dir, "ciphertext.txt")
        file_path_note = os.path.join(password_dir, "ciphertext_note.txt")

        with open(file_path, "ab") as f:
            f.write(ciphertext + b'\n')
        print(f"Van ban da duoc ghi vao tep '{file_path}'.")
        with open(file_path_note, "a") as f:
            f.write(f"{add_note}\n")
        print(f"Ghi chu da duoc ghi vao tep '{file_path_note}'.")

    # Ket thuc ma hoa *******************************************************************************
    # Thuc hien giai ma ****************************************************************************

    if OPTION & FLAG_DECRYPT:
        key = os.getenv("keypass").encode('utf-8')
        if not key:
            print("Bien moi truong keypass khong ton tai.")
            return
        line_number = input("Nhap so dong can giai ma: ")
        try:
            line_number = int(line_number)
        except ValueError:
            print("So dong khong hop le. Vui long nhap mot so nguyen.")
            return
        # Đọc đường dẫn từ dòng số 2 trong tệp config.txt
        config_file = "config.txt"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    password_dir = lines[1].strip()  # Lấy dòng số 2 và loại bỏ khoảng trắng
                else:
                    print("Tệp config.txt không có đủ dòng.")
                    return
        else:
            print(f"Tệp cấu hình '{config_file}' không tồn tại.")
            return
        
        # Sử dụng đường dẫn để đọc tệp
        file_path = os.path.join(password_dir, "ciphertext.txt")
        file_path_note = os.path.join(password_dir, "ciphertext_note.txt")
        try:
            with open(file_path, "rb") as f:
                lines = f.readlines()
            if line_number <= 0 or line_number > len(lines):
                print("So dong vuot qua pham vi cua tep.")
                return
            ciphertext = lines[line_number - 1].strip()
            plaintext = xor_decrypt(ciphertext, key)
            print(f"VAN BAN DA GIAI MA: {plaintext.decode('utf-8')}")
        except FileNotFoundError:
            print(f"Tep '{file_path}' khong ton tai.")
        except Exception as e:
            print(f"Loi khi doc tep: {e}")

    # ket thuc giai ma ****************************************************************************

# ******************End program cipher password********************************************************

def main():
    parser = argparse.ArgumentParser(
        prog="cli",
        usage="mo CMD va nhan cli --help",
        description="Chuong trinh dieu khien may tinh bang dong lenh.\n"
                    "Chuong trinh duoc viet boi Tran Dinh Thuong.\n"
                    "Email: qbquangbinh@gmail.com"
    )
    parser.add_argument("--name", "-n", help="Your name", default="Tran Dinh Thuong")
    parser.add_argument("--shutdown", "-s", action="store_true", help="Shutdown the computer")
    parser.add_argument("--restart", "-r", action="store_true", help="Restart the computer")
    parser.add_argument("--sleep", "-sl", action="store_true", help="Put the computer to sleep")
    parser.add_argument("--version", "-v", action="version", version="mycli 1.0.6", help="Show version information")
    parser.add_argument("--youtube", "-y", action="store_true", help="Open YouTube in the default web browser")
    parser.add_argument("--clean", "-c", action="store_true", help="Clean temporary files")
    parser.add_argument("--deepclean", "-dc", action="store_true", help="Xoa tat ca các tep va thu muc trong thu muc Downloads")
    parser.add_argument("--control_hand", "-ch", action="store_true", help="Dieu khien may tinh bang cu chi tay.")
    parser.add_argument("--cipher", "-ci", action="store_true", help="Ma hoa van ban bang XOR cipher.")
    args = parser.parse_args()
    print(f"Hello, {args.name}!")
    if args.shutdown:
        os.system("shutdown /s /t 0")
    elif args.restart:
        os.system("shutdown /r /t 0")
    elif args.sleep:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 1,1,1")
    elif args.youtube:
        os.system("start https://www.youtube.com")
    elif args.clean:
        temp_folder = os.path.join(os.getenv('SystemRoot'), 'TEMP')
        print("-" * 50)
        print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            clean_temp_files(temp_folder)
        else:
            print("Bo qua viec xoa tep tam thoi.")
        print("-" * 50)
        
        temp_folder = os.getenv("TEMP")
        print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            clean_temp_files(temp_folder)
        else:
            print("Bo qua viec xoa tep tam thoi.")
        print("-" * 50)
        
        temp_folder = os.getenv("TMP")
        print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            clean_temp_files(temp_folder)
        else:
            print("Bo qua viec xoa tep tam thoi.")
        print("-" * 50)
    elif args.deepclean:
        temp_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        print("-" * 50)
        print(f"Xac nhan xoa cac tep va thu muc tam thoi tai thu muc: {temp_folder}")
        print("Nhan y de xoa, nhan n de bo qua.")
        user_input = input("Ban co muon xoa khong? (y/n): ").lower()
        while user_input not in ['y', 'n']:
            user_input = input("Nhap y de xoa, nhap n de bo qua: ").lower()
        if user_input == 'y':
            clean_temp_files(temp_folder)
        else:
            print("Bo qua viec xoa tep tam thoi.")
        print("-" * 50)
    elif args.control_hand:
        control_by_hand()
    elif args.cipher:
        password_cipher()

if __name__ == "__main__":
    main()