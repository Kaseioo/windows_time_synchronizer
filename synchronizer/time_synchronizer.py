import sys
from datetime import datetime
import datetime as dt
import ntplib
from ntplib import NTPException
import threading
from threading import Event
import time
import msvcrt as m
import win32api

BACKUP_TIME_SERVERS = ['ntp.iitb.ac.in', 'time.nist.gov', 'time.windows.com', 'pool.ntp.org', 'time.google.com', 'time.cloudflare.com', 'ntp.nict.jp', 'ntps1.pads.ufrj.br']

def read_time_server_list():
	"""
	Reads the list of NTP servers from a file.

	Returns:
		list: A list of NTP servers.
	"""

	try:
		with open("ntp_servers.txt", "r") as f:
			return f.read().splitlines()
	except FileNotFoundError:
		return []


def wait_for_keypress_before_exiting(exit_code):
	"""
	Waits for a keypress before exiting the program.

	Parameters:
	exit_code (int): The exit code to be passed to sys.exit().

	Returns:
	None
	"""
	m.getch()
	sys.exit(exit_code)
    
def track_elapsed_time(update_progress_event, timeout_threshold=20):
	"""
	Track the elapsed time and check for timeout while fetching timestamp from a time server.

	Args:
		update_progress_event (threading.Event): An event object used to signal the progress update.
		timeout_threshold (int, optional): The maximum number of seconds to wait for a response from the server. Defaults to 20.

	Raises:
		Exception: If the request times out after the specified timeout threshold.

	Returns:
		None
	"""
	print("Fetching timestamp..", end="")
	
	execution_counter = 0
	while not update_progress_event.is_set():
		print(".", end="", flush=True)
  
		execution_counter += 1
  
		if execution_counter >= timeout_threshold:
			print("f\n\ns{execution_counter} seconds have elapsed, and no response was received from the server. Aborting operation as the current limit is {timeout_threshold} seconds.")
			update_progress_event.set()
			raise Exception(f"Request timed out after {timeout_threshold} seconds.")
		elif execution_counter % 10 == 0:
			print(f"\n\n {execution_counter} seconds have elapsed. Still fetching timestamp..", end="", flush=True)
		else:
			time.sleep(1)

def gettime_ntp(addr, update_progress_event, should_offset_trip_delay=True):
	"""
	Fetches the current time from an NTP server.

	Args:
		addr (str): The address of the NTP server.
		update_progress_event (threading.Event): An event object used to track the progress of time fetching.
		should_offset_trip_delay (bool, optional): Whether to include round trip ping delay as an offset in the returned value. Defaults to True.

	Returns:
		float: The current time in seconds since the epoch.

	Raises:
		NTPException: If there is an error while fetching the time from the NTP server.
		Exception: If the NTP server does not respond.

	"""
	c = ntplib.NTPClient()

	elapsed_time_thread = threading.Thread(target=track_elapsed_time, args=(update_progress_event,))

	try:
		elapsed_time_thread.start()
		request = c.request(addr, version=3)
		update_progress_event.set()
	except NTPException as e:
		raise

	if request is None:
		raise Exception(f"Failed to fetch time from {addr}: server did not respond.")

	absolute_epoch = request.tx_time

	if should_offset_trip_delay:
		return absolute_epoch + request.delay
	return absolute_epoch

def update_time(epoch_time, timezone_offset):
	"""
	Update the system time based on the given epoch time and timezone offset.

	Args:
		epoch_time (float): The epoch time to update the system time to.
		timezone_offset (timedelta): The timezone offset to adjust the epoch time.

	Returns:
		None
	"""
	print(f"Trying to update system time...")

	offset = timezone_offset.total_seconds()

	if offset < 0:
		epoch_time -= offset
	else:
		epoch_time += offset

	utc_time = datetime.fromtimestamp(epoch_time)

	win32api.SetSystemTime(
		utc_time.year,
		utc_time.month,
		utc_time.weekday(),
		utc_time.day,
		utc_time.hour,
		utc_time.minute,
		utc_time.second,
		utc_time.microsecond // 1000
	)

def human_readable_timezone(offset):
	"""
	Converts a given timezone offset to a human-readable format.

	Parameters:
		offset (timedelta): The timezone offset to convert.

	Returns:
	int: The timezone offset in hours, rounded to the nearest whole number.
	"""
	timezone_hours = offset.total_seconds() / 3600
	timezone_hours_rounded = int(timezone_hours) if timezone_hours.is_integer() else timezone_hours

	return timezone_hours_rounded

if __name__ == "__main__":
	"""_summary_
 
		Acquire the current time from an NTP server and update the system time.
	
		_description_

		This script fetches the current time from an NTP server uses the win32api windows interface library to update the system time.
		A list of NTP servers is provided, and the script will attempt to fetch the time from each server in the list until it is successful.
		Once the time has been updated, the script will display the original and updated system times, as well as the system timezone so the user can verify that the time has been updated correctly.
  
		Created with Python 3.11.8 64-bit and tested on Windows 10.

		Args:
			None

		Returns:
			None
	"""
	has_updated = False
	update_progress_event = Event()
 
	time_before_update = datetime.now()
	execution_time = datetime.now()
 
	timezone = datetime.now(dt.timezone.utc).astimezone().tzinfo
	timezone_offset = timezone.utcoffset(datetime.now())
	
	server_list = read_time_server_list()
	if len(server_list) == 0:
		server_list = BACKUP_TIME_SERVERS
		print("No time servers found in ntp_servers.txt. Defaulting to hardcoded time servers instead.")
 
	print(f"Program is going to use the following time servers: {server_list}.")
 
	for server in server_list:
		print(f"Current time server: {server}")
		try:
			epoch_time = gettime_ntp(server, update_progress_event)
			print(f"\n\nAcquired time from {server}: {datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S:%f%z')}. Program will consider UTC {human_readable_timezone(timezone_offset)} to be the system timezone.")
		except Exception as e:
			epoch_time = None
			update_progress_event.set()

			print(f" Failed to fetch time from {server}: {e}")
			print(f"Trying next server...\n\n====================\n")
			continue
			
		try:
			time_before_update = datetime.now()
			update_time(epoch_time, timezone_offset)
			has_updated = True
		except Exception as e:
			print(f"Failed to update system time. Are you running this program as administrator?\n {e}")
			break

		execution_time = datetime.now() - execution_time
		break

	if not has_updated:
		print("Failed to update system time from current servers. Update ntp_servers.txt with a new line if you think a new server can work.\nPress any key to exit.")
		wait_for_keypress_before_exiting(1)
	else:
		updated_system_time = datetime.now()
  
		print("System time updated successfully.\n")
		print(f"Old system time: {time_before_update.strftime('%Y-%m-%d %H:%M:%S:%f%z')}.")
		print(f"New system time: {updated_system_time.strftime('%Y-%m-%d %H:%M:%S:%f%z')}.")
		print(f"System timezone: {timezone}, UTC {human_readable_timezone(timezone_offset)}. If this is incorrect, please change your system timezone settings.\n")
		print(f"Press any key to exit.")
  
		wait_for_keypress_before_exiting(0)

	
