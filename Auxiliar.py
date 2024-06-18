from datetime import datetime

def get_current_time_formatted():
    # Get the current date and time
    now = datetime.now()
    # Format the date and time as a string in the specified format
    return now.strftime("%Y%m%d_%H%M%S")
