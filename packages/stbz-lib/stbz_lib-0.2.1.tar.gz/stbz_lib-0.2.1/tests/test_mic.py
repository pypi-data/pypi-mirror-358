import time

from stbz_lib import mic_block, mic_unblock

mic_block()
print("麥克風已被靜音")
time.sleep(10)

mic_unblock()
print("麥克風已取消靜音")
