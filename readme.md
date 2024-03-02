# Windows Time Synchronizer

This is a simple Python script that synchronizes the system clock on Windows with an NTP (Network Time Protocol) server.

## Project Releases

If you prefer to use a pre-built executable file instead of running the Python script, you can download the latest release from the [Releases](https://github.com/kaseioo/windows-time-synchronizer/releases) page.

1. Go to the [Releases](https://github.com/kaseioo/windows-time-synchronizer/releases) page.

2. Download the latest version of the executable file (`windows-time-synchronizer.exe`).

3. Double-click the downloaded file to run it.

The executable file provides a convenient way to synchronize the system clock without the need to install Python or any dependencies. You can also create a `ntp_servers.txt` file in the same directory as the executable to specify the desired NTP servers.

Note: The executable file is built from the same source code as the Python script, so it offers the same functionality.

If you encounter any issues or have any questions, please refer to the [Issues](https://github.com/kaseioo/windows-time-synchronizer/issues) page or contact the project maintainer.

# Development

## Prerequisites

- Python 3.x
- pip package manager

## Installation

1. Clone the repository:

	```shell
	git clone https://github.com/kaseioo/windows-time-synchronizer.git
	```

2. Install the required dependencies:

	```shell
	pip install -r requirements.txt
	```

## Usage

1. Open a terminal or command prompt.

2. Navigate to the project directory:

	```shell
	cd windows-time-synchronizer
	```

2.1. (Optional) Modify the `ntp_servers.txt` file to include the desired NTP servers. If no servers are specified, the script will use the default hardcoded NTP servers.

	```shell
	notepad ntp_servers.txt
	```

	Each line in the file should contain the address of an NTP server, e.g.:

	```text
	time.windows.com
	time.nist.gov
	```

3. Run the script:

	```shell
	python time_synchronizer.py
	```

	The script will automatically synchronize the system clock with an NTP server.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request. Feel free to contact me if you have any questions. Otherwise, you can also fork the repository and use the code as you see fit.

## License

This project relies on the `ntplib` library, which is licensed under the MIT License. The rest of the code is licensed under the BSD 3-Clause License. See the [LICENSE](LICENSE) file for details.