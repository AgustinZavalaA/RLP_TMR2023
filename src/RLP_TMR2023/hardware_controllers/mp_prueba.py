import threading
import time


def background_task(param, seconds=2):
    print("Running in the background with parameter:", param)
    time.sleep(seconds)
    print("Done with the background task")


def start_background_task(param, seconds=2):
    thread = threading.Thread(target=background_task, args=(param, seconds))
    thread.daemon = True
    thread.start()


# Main loop to wait for user input
while True:
    user_input = input("Enter something: ")
    print("You entered:", user_input)
    if user_input:
        start_background_task(user_input, int(user_input))
