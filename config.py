	# Config file for this amazing system

host = "0.0.0.0" # broadcast range
host_ip = "10.0.0.1" # ip_addr of interface you are currently using
port = 8088
tasks_port = 8888

tasks_enabled = 1
scoreboard_enabled = 1
hints_enabled = 1

base_modules = ['__builtins__', '__doc__', '__file__', '__name__', '__package__', 'rglobals']
accesslog = 'logs/msuctf-access.log'
errorlog = 'logs/msuctf-error.log'

