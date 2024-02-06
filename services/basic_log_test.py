import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
classes_dir = os.path.join(current_dir, '..', 'classes')
sys.path.insert(0, classes_dir)
from imports import *

logger = aws_logger()
for i in range(10, 16):
    log_message = f"Log message {i}"
    print(f"Sending log message: {log_message}")

    ret, error = logger.add_log(log_message)
    print(ret)


# logger = aws_logger()
# ret, error = logger.add_log(log_message)