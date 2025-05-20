import socket
import tkinter as tk
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor

# Function to resolve domain name to IP address
def resolve_domain_to_ip(domain_name):
    try:
        ip_address = socket.gethostbyname(domain_name)
        return ip_address
    except socket.gaierror:
        return None

# Function to scan a single port and return the port with its service name
def scan_port(target_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Timeout for connection attempt
    result = sock.connect_ex((target_ip, port))
    sock.close()

    # If the port is open, return the port and its service name
    if result == 0:
        try:
            service_name = socket.getservbyport(port)  # Get service name for the port
        except OSError:
            service_name = "Unknown Service"  # If no service name is found
        return port, service_name
    return None

# Function to scan multiple ports using ThreadPoolExecutor (multithreading)
def scan_ports(target_ip, start_port, end_port):
    open_ports = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(lambda port: scan_port(target_ip, port), range(start_port, end_port + 1))
        open_ports = [result for result in results if result is not None]
    return open_ports

# Function triggered by the "Start Scan" button
def start_scan():
    target = entry_target.get()
    start_port = int(entry_start_port.get())
    end_port = int(entry_end_port.get())

    # Check if the target is a domain name or IP address
    if '.' in target:  # Simple check to see if it's an IP or domain name
        # If it is a domain name, resolve it to an IP
        target_ip = resolve_domain_to_ip(target)
        if target_ip is None:
            messagebox.showerror("Invalid Domain", "Could not resolve domain name to IP address.")
            return
    else:
        # Otherwise, assume it's an IP address
        target_ip = target
        try:
            socket.inet_aton(target_ip)  # Validate IP address format
        except socket.error:
            messagebox.showerror("Invalid IP", "Please enter a valid IP address.")
            return

    # Disable the button to prevent multiple scans running at once
    btn_scan.config(state=tk.DISABLED)

    # Display loading message while scanning
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Scanning...\n")

    # Perform the port scan in the background
    open_ports = scan_ports(target_ip, start_port, end_port)

    # Display the results
    result_text.delete(1.0, tk.END)
    if open_ports:
        result_text.insert(tk.END, f"Open ports on {target_ip}:\n")
        for port, service in open_ports:
            result_text.insert(tk.END, f"Port {port} ({service}) is open\n")
    else:
        result_text.insert(tk.END, "No open ports found.\n")

    # Enable the button again
    btn_scan.config(state=tk.NORMAL)

# Creating the main window for Evil Eye
root = tk.Tk()
root.title("Evil Eye - Port Scanner")

# Creating and placing the labels, entry fields, and button
tk.Label(root, text="Target IP Address / Domain Name:").grid(row=0, column=0, padx=10, pady=10)
entry_target = tk.Entry(root, width=20)
entry_target.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Start Port:").grid(row=1, column=0, padx=10, pady=10)
entry_start_port = tk.Entry(root, width=20)
entry_start_port.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="End Port:").grid(row=2, column=0, padx=10, pady=10)
entry_end_port = tk.Entry(root, width=20)
entry_end_port.grid(row=2, column=1, padx=10, pady=10)

btn_scan = tk.Button(root, text="Start Scan", command=start_scan)
btn_scan.grid(row=3, column=0, columnspan=2, pady=20)

# Text box to display results
result_text = tk.Text(root, height=10, width=40)
result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
