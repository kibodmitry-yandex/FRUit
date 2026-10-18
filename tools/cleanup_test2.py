import ctypes
user32 = ctypes.windll.user32
user32.PostMessageW(10228838, 0x0010, 0, 0)  # WM_CLOSE тестовое окно 4 вкладок
print("closed test window 10228838")
