from core import msg_worker
import time

msg_worker('N', 2, 1)
time.sleep(5)
msg_worker('Q', 2, 1)
time.sleep(5)
msg_worker('F', 2, 1)

