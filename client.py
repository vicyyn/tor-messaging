#/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from peer import Peer

class Client:
    def __init__(self) -> None:
        self.peer = Peer("localhost",8000,20)

        window = tk.Tk()
        window.geometry("800x400")
        window.title("tor-messaging client")
        window.config(background="#121212")

        info_frame = tk.Frame(window)
        name_label = tk.Label(info_frame, text="Name:")
        name_label.pack(side="left", padx=5, pady=5)
        address_label = tk.Label(info_frame, text="Address:")
        address_label.pack(side="left", padx=5, pady=5)
        ip_label = tk.Label(info_frame, text="IP:")
        ip_label.pack(side="left", padx=5, pady=5)
        info_frame.pack(side="top",fill="x")

        buttons_frame = tk.Frame(window)
        ping_button = tk.Button(buttons_frame, text="Ping")
        ping_button.pack(side="left", padx=5, pady=5)
        send_button = tk.Button(buttons_frame, text="Send message")
        send_button.pack(side="left", padx=5, pady=5)
        init_button = tk.Button(buttons_frame, text="Initialize circuit")
        init_button.pack(side="left", padx=5, pady=5)
        buttons_frame.pack(side="top",fill="x")

        treeview = ttk.Treeview(window)
        treeview["columns"] = ("peer_address", "ip")
        treeview.heading("peer_address", text="Peer address")
        treeview.heading("ip", text="IP")
        treeview.pack(side="bottom",expand=True, fill="both")

        for index , address in enumerate(self.peer.get_peers_addresses()):
            treeview.insert("", "end", text=str(index+1), values=(address,self.peer.peers_sockets[address].getsockname()))

        window.mainloop()

Client()


