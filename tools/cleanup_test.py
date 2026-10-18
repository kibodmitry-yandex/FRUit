import ctypes
user32 = ctypes.windll.user32
for h in (25300672, 22744080):
    user32.PostMessageW(h, 0x0010, 0, 0)  # WM_CLOSE
print("closed test windows 25300672, 22744080")
