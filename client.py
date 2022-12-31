#/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from peer import Peer

class Client:
    def __init__(self) -> None:
        self.peer = Peer("localhost",8000,10)

        window = tk.Tk()
        window.geometry("800x400")
        window.title("tor-messaging client")
        window.config(background="#121212")

        info_frame = tk.Frame(window)
        name_label = tk.Label( info_frame, text="Name : " + "Nader",justify="center")
        name_label.pack(side="left", padx=5, pady=5)
        address_label = tk.Label(info_frame, text="Address : " + self.peer.get_address(),justify="center")
        address_label.pack(side="left", padx=5, pady=5)
        ip_label = tk.Label(info_frame, text="IP : " + str(self.peer.get_socket().getsockname()),justify="center")
        ip_label.pack(side="left", padx=5, pady=5)
        info_frame.pack( side="top",fill="x")

        buttons_frame = tk.Frame(window)
        ping_button = tk.Button(buttons_frame, text="Ping")
        ping_button.pack(side="left", padx=5, pady=5)
        send_button = tk.Button(buttons_frame, text="Send message")
        send_button.pack(side="left", padx=5, pady=5)
        init_button = tk.Button(buttons_frame, text="Initialize circuit")
        init_button.pack(side="left", padx=5, pady=5)
        refresh_button = tk.Button(buttons_frame, text="Refresh", command=self.refresh)
        refresh_button.pack(side="left", padx=5, pady=5)
        buttons_frame.pack(side="top",fill="x")

        treeview = ttk.Treeview(window)
        treeview["columns"] = ("peer_address", "ip")
        treeview.heading("peer_address", text="Peer address")
        treeview.heading("ip", text="IP")
        treeview.pack(side="bottom",expand=True, fill="both")
        self.treeview = treeview

        for index , address in enumerate(self.peer.get_peers_addresses()):
            treeview.insert("", "end", text=str(index+1), values=(address,self.peer.get_peers_sockets()[address].getsockname()))

        window.mainloop()

    def refresh(self):
        self.peer.get_peers(10)
        self.update_table()

    def update_table(self):
        self.treeview.delete(*self.treeview.get_children())
        for index , address in enumerate(self.peer.get_peers_addresses()):
            self.treeview.insert("", "end", text=str(index+1), values=(address,self.peer.get_peers_sockets()[address].getsockname()))

    # def handle_input(self,request):
    #         pattern = r"^\(([^,]+),([^)]+)\) : (.*)$"
    #         match = re.search(pattern, request)
    #         if not match:
    #             return
    #         message = match.group(1)
    #         address = match.group(2)
    #         data = match.group(3)

    #         if message == "peers":
    #             print(self.peers_publickeys)
    #             print(self.peers_sockets)
    #         elif message == "ping":
    #             for address in self.peers_sockets:
    #                 current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    #                 self.send_request(self.peers_sockets[address],"ping",{"time":current_time})
    #                 print("pinged:",address)
    #         elif message == "message":
    #             address = address if address in self.peers_sockets else self.get_random_address()
    #             print(address)
    #             current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    #             self.send_request(self.peers_sockets[address],"message",{"time":current_time,"message":self.peers_publickeys[address].encrypt(request.encode(),
    #                 padding.OAEP(
    #                     mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #                     algorithm=hashes.SHA256(),
    #                     label=None
    #                 ))
    #             })
    #             print("messaged:",address)

Client()


