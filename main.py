import os
import re
import json
from datetime import datetime
from colorama import init, Fore, Style
init()


def extract_file_content(path, target, cut, extra_cut=0):
    """ 
        Extract a string from a file via line-by-line searching.
        'path' is the target file, 'target' the target string and 'cut'
        the amount of characters to cut after the index of the target
        string.
    """
    output = ""
    try:
        with open(path, 'r') as reader:
            for line in reader:
                found_index = line.find(target)
                if found_index > -1:
                    output = line[found_index + cut:len(line) - extra_cut]
                    break
    except Exception as e:
        pass
    return output
    
def start_protonvpn():
    """ Create JSON-output for ProtonVPN logs """
    # Vital variables
    date_time_log = []
    username = []
    version = []
    # Timeline
    timeline_events = []
    start_date = ""
    stop_date = ""
    width = 1000
    
    # Find connection log path
    programdata_path = os.getenv("PROGRAMDATA") + "\\ProtonVPN\\logs\\"
    print(Fore.YELLOW + "Testing default path: " + programdata_path + Style.RESET_ALL)
    
    # Check if exists
    # To-do: Add functionality to scan for directory containing log files instead
    if not os.path.isdir(programdata_path):
        print(Fore.RED + "Directory not found" + Style.RESET_ALL)
        return 0
    else:
        print(Fore.GREEN + "Directory found" + Style.RESET_ALL)
        
    # Check if contains logs
    log_files = os.listdir(programdata_path)
    if not log_files:
        print(Fore.RED + "Log files not found" + Style.RESET_ALL)
        return 0
    else:
        print(Fore.GREEN + "Log files found" + Style.RESET_ALL)
    
    # Extract dates and sort into array
    date_time_log = re.findall(r'\d{4}-\d{2}-\d{2}', str(log_files))
    
    # Extract client version from log files
    version_target = 'INFO = Booting ProtonVPN Service version: '
    alt = "0"
    while alt not in ["1", "2"]:
        print("Please select client version scan type\n(1) Deep: Fetch all client versions\n(2) Shallow: Fetch latest client version")
        alt = input("> ")
        
        for item in reversed(log_files):
            tmp_version = extract_file_content(programdata_path + item, version_target, len(version_target), 2)
            tmp_version = tmp_version.split(" os:")[0]
            if tmp_version and tmp_version not in version:
                version.append(tmp_version)
                if alt == "2":
                    break
    if len(version) > 0:
        print(Fore.GREEN + "Client version found" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Client version not found" + Style.RESET_ALL)
    
    # Find connects/disconnects
    # To-Do: Add support for location extraction
    found_connect = 0
    found_disconnect = 0
    conn_object = []
    conn_target = ",CONNECTED,SUCCESS,"
    conn_alt_target = "OpenVPN"
    dc_target = "Disconnected from OpenVPN management"
    
    # All logs are important so no filtering - Treat "service.txt" as latest log    
    filtered_list = log_files
    for item in filtered_list:
        
        output = ""
        try:
            with open(programdata_path + item, 'r') as reader:
                for line in reader:
                    # Check each line for sign of connection
                    if not found_connect:
                        if conn_target in line and conn_alt_target in line:
                            found_connect = 1
                            # Add to conn_object with the following structure: [["HH:MM DD Mar, YYYY", IPv4, IPv6, Location*, "HH:MM DD Mar, YYYY"], -//-]
                            tmp_conn_time, tmp_ip_details = line.split(" INFO OpenVPN")
                            # Remove trailing whitespace and convert time of connection to timeline-appropriate format
                            conn_time = datetime.strptime(tmp_conn_time[:-1], "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M:%S %d %b, %Y")
                            # Handle IP addresses
                            ip_details = tmp_ip_details.split(",")
                            ipv4 = ip_details[4].rstrip()
                            # IPv6 is not always present in ProtonVPN logs, avoid looking for it
                            ipv6 = "" 
                            
                            conn_object.extend((conn_time, ipv4, ipv6))
                            
                    # Connection has already been found, look for disconnect
                    else:
                        if dc_target in line:
                            found_connect = 0
                            tmp_dc_time = line.split(" INFO")[0]
                            dc_time = datetime.strptime(tmp_dc_time[:-1], "%Y-%m-%d %H:%M:%S.%f").strftime("%H:%M:%S %d %b, %Y")
                            # Extend conn_object to include disconnect time
                            conn_object.append(dc_time)
                            # Add to timeline_events array for further processing
                            timeline_events.append(conn_object)
                            # Clear conn_object for use in next iteration
                            conn_object = []
                            
                    # return 0
        except Exception as e:
            print(e)
        # No reset of found_connect is performed, as disconnects may appear on a different file than connects
    # End of loop    

    # Determine start date
    # Due to timeline oddities further conversion is needed
    start_date = datetime.strptime(date_time_log[0], "%Y-%m-%d").strftime("%d %b %Y")
    # Due to no "stop date" being available for extraction through the name of service.txt,
    # avoid sending one entirely    
    generate_timeline_json(timeline_events, start_date, stop_date, username, version)
    
    return 0
    
    
def start_ovpn():
    """ Create JSON-output for OVPN logs """
    # Vital variables
    date_time_log = []
    username = []
    version = []
    # Timeline
    timeline_events = []
    start_date = ""
    stop_date = ""
    width = 1000
    
    # Find connection log path
    appdata_path = os.getenv("APPDATA") + "\\OVPN\\logs\\"
    print(Fore.YELLOW + "Testing default path: " + appdata_path + Style.RESET_ALL)
    
    # Check if exists
    # To-do: Add functionality to scan for directory containing log files instead
    if not os.path.isdir(appdata_path):
        print(Fore.RED + "Directory not found" + Style.RESET_ALL)
        return 0
    else:
        print(Fore.GREEN + "Directory found" + Style.RESET_ALL)
        
    # Check if contains logs
    log_files = os.listdir(appdata_path)
    if not log_files:
        print(Fore.RED + "Log files not found" + Style.RESET_ALL)
        return 0
    else:
        print(Fore.GREEN + "Log files found" + Style.RESET_ALL)
        
    # Extract dates/times and sort into two-dimensional array
    for idx, item in enumerate(log_files):
        raw = re.search(r'\d{4}-\d{2}-\d{2}--\d{2}-\d{2}-\d{2}', item)
        date_time_log.append(raw.group().split("--"))
    
    # Extract client versions from log files
    version_target = 'Application: Version: "'
    alt = "0"
    while alt not in ["1", "2"]:
        print("Please select client version scan type\n(1) Deep: Fetch all client versions\n(2) Shallow: Fetch latest client version")
        alt = input("> ")
        
        for item in reversed(log_files):
            tmp_version = extract_file_content(appdata_path + item, version_target, len(version_target), 2)
            if tmp_version and tmp_version not in version:
                version.append(tmp_version)
                if alt == "2":
                    break
    if len(version) > 0:
        print(Fore.GREEN + "Client version found" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Client version not found" + Style.RESET_ALL)

    # Extract OVPN username        
    # To-do: Merge with client version scan to prevent unnecessary file reads
    username_target = "username 'Auth' "
    alt = "0"
    while alt not in ["1", "2"]:
        print("Please select username scan type\n(1) Deep: Fetch all usernames\n(2) Shallow: Fetch latest username")
        alt = input("> ")
    
        for item in reversed(log_files):
            tmp_user = extract_file_content(appdata_path + item, username_target, len(username_target), 2)
            # Strip newlines
            tmp_user = tmp_user.strip()
            if tmp_user and tmp_user not in username:
                username.append(tmp_user)
                if alt == "2":
                    break
    if len(username) > 0:
        print(Fore.GREEN + "Username found" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Username not found" + Style.RESET_ALL)
    
    # Find connects/disconnects
    # To-Do: Add support for location extraction
    found_connect = 0
    found_disconnect = 0
    conn_object = []
    conn_target = ",CONNECTED,SUCCESS,"
    dc_target = "MANAGEMENT: Client disconnected"
    
    # Filter list to not include client logs
    filtered_list = [x for x in log_files if not "client.log" in x]
    for item in filtered_list:
        
        output = ""
        try:
            with open(appdata_path + item, 'r') as reader:
                for line in reader:
                    # Check each line for sign of connection
                    if not found_connect:
                        if conn_target in line:
                            found_connect = 1
                            # Location should be looked after here, check the lines prior to the connection attempt for:
                            # Mon Jan 01 XX:XX:XX 2022 SENT CONTROL [SERVER URL]: 'PUSH_REQUEST' (status=1)
     
                            # Add to conn_object with the following structure: [["HH:MM DD Mar, YYYY", IPv4, IPv6, Location*, "HH:MM DD Mar, YYYY"], -//-]
                            tmp_conn_time, tmp_ip_details = line.split("MANAGEMENT")
                            # Remove trailing whitespace and convert time of connection to timeline-appropriate format
                            conn_time = datetime.strptime(tmp_conn_time[:-1], "%a %b %d %H:%M:%S %Y").strftime("%H:%M:%S %d %b, %Y")
                            # Handle IP addresses
                            ip_details = tmp_ip_details.split(",")
                            ipv4 = ip_details[4].rstrip()
                            ipv6 = ip_details[8].rstrip()
                            
                            conn_object.extend((conn_time, ipv4, ipv6))
                            
                    # Connection has already been found, look for disconnect
                    else:
                        if dc_target in line:
                            found_connect = 0
                            tmp_dc_time = line.split("MANAGEMENT")[0]
                            dc_time = datetime.strptime(tmp_dc_time[:-1], "%a %b %d %H:%M:%S %Y").strftime("%H:%M:%S %d %b, %Y")
                            # Extend conn_object to include disconnect time
                            conn_object.append(dc_time)
                            # Add to timeline_events array for further processing
                            timeline_events.append(conn_object)
                            # Clear conn_object for use in next iteration
                            conn_object = []
                            
        except Exception as e:
            print(e)
        # No reset of found_connect is performed, as disconnects may appear on a different file than connects
    # End of loop    
   
    # Determine start date
    # Due to time line oddities further conversion is needed
    start_date = datetime.strptime(date_time_log[0][0], "%Y-%m-%d").strftime("%d %b %Y")
    stop_date = datetime.strptime(date_time_log[-1][0], "%Y-%m-%d").strftime("%d %b %Y")
    
    generate_timeline_json(timeline_events, start_date, stop_date, username, version)
    
    return 0
    

def generate_timeline_json(content, start, stop, username="", version="", width=2000,):
    """ 
        Generate the JSON-file needed by make_timeline to generate a proper timeline.
    """
    data = {}
    # To-do: Modify width during runtime
    data["width"] = width
    data["start"] = start
    # Even with no stop date available, it needs to be set
    data["end"] = stop
    
    # Create callouts and eras
    # Callout - Start and IP addresses
    # Era - Start date included, but only stop is shown
    callouts = []
    # Add start and stop as callouts to make timeline more clear
    callouts.append(["Log start: " + start, start])
    # We can, however, skip setting a callout for stop
    if stop:
        callouts.append(["Log stop: " + stop, stop])
    # Add callout for version information and username
    if username:
        callouts.append(["Username: " + str(username), data["start"]])
    callouts.append(["Version: " + str(version), data["start"]])
    
    eras = []
    for item in content:
        callouts.append([item[1] + "\n" + item[2], item[0]])
        eras.append([" ", item[0], item[3]])
    data["callouts"] = callouts
    data["eras"] = eras
    
    # Dump JSON file
    json_data = json.dumps(data)
    print("\n\n")
    print(json_data)

def about():
    """ Display basic information about the project """
    string = ("Created as a part of DV2579 - Advanced Topic in Computer Forensics.\n\n"
              "The tool is a Proof-of-Concept, meaning less focus has been put on clean code.\n"
              "The tool is written for specific versions of VPN clients ProtonVPN and OVPN.\n"
              "The supported clients are ProtonVPN (version 1.6.4) and OVPN (version 1.2.7.2246). Previous, or\n"
              "newer versions may be supported - Although runtime errors may occur if log format is altered.\n\n"
              "The tool has been tested on Windows 10 Pro N, version 1703.")
    return string

def main():
    # Banner
    
    print(Fore.CYAN)
    print(Style.BRIGHT + "                        _               _    ")
    print("__   ___ __  _ __   ___| |__   ___  ___| | __")
    print("\ \ / / '_ \| '_ \ / __| '_ \ / _ \/ __| |/ /")
    print(" \ V /| |_) | | | | (__| | | |  __/ (__|   < ")
    print("  \_/ | .__/|_| |_|\___|_| |_|\___|\___|_|\_\\")
    print("      |_|                                    \n")

    print("PoC forensic analysis tool for Windows VPN clients")
    print("Written as part of DV2579 - Advanced Topic in Computer Forensics" + Style.RESET_ALL)    
    
    alt = '0'
    while alt == '0':
        print("\n\n1. Analyze OVPN client")
        print("2. Analyze ProtonVPN client")
        print("3. About")
        print("4. Exit")
        
        alt = input("> ")
        
        if alt == "1":
            print("Analyzing OVPN client .. ")
            start_ovpn()
        elif alt == "2":
            print("Analyzing ProtonVPN client .. ")
            start_protonvpn()
        elif alt == "3":
            print(about())
            alt = "0"

if __name__ == "__main__":
    main()