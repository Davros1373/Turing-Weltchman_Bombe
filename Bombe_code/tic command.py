import os

#os.system("ticcmd")
os.system("ticcmd --energize")
os.system("ticcmd --exit-safe-start")

os.system("ticcmd --step-mode 2")
os.system("ticcmd --max-speed 700000")
os.system("ticcmd --starting-speed 700000")

#os.system("ticcmd --position-relative 1612") # 1 rotation at step-mode 4 1600/26=61.538
											 # 26*61=1586, 26*62=1612 

os.system("ticcmd --position-relative 462")
