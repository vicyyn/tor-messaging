#/usr/bin/python3

import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
from logger import Logger
from peer import Peer

class Client:
    def __init__(self) -> None:
        window = tk.Tk()

        self.log_text = tk.Text(window,state="disabled")
        self.log_text.pack(side="bottom",fill="x")

        self.peer = Peer("localhost",8000,10,Logger(self))

        window.geometry("800x400")
        window.title("tor-messaging client")
        window.config(background="#121212")

        info_frame = tk.Frame(window)

        self.name_label = tk.Label( info_frame, text="Name : " + "Nader",justify="center")
        self.name_label.pack(side="left", padx=5, pady=5)

        self.address_label = tk.Label(info_frame, text="Address : " + self.peer.get_address(),justify="center")
        self.address_label.pack(side="left", padx=5, pady=5)

        self.ip_label = tk.Label(info_frame, text="IP : " + str(self.peer.get_socket().getsockname()),justify="center")
        self.ip_label.pack(side="left", padx=5, pady=5)

        self.peers_label_text = tk.StringVar()
        self.peers_label_text.set("peers : " + str(len(self.peer.get_peers_addresses())))
        self.peers_label = tk.Label(info_frame, textvariable=self.peers_label_text,justify="center")
        self.peers_label.pack(side="left", padx=5, pady=5)

        info_frame.pack( side="top",fill="x")

        buttons_frame = tk.Frame(window)
        ping_button = tk.Button(buttons_frame, text="Ping",command=self.ping)
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

        threading.Thread(target=self.auto_refresh,args=()).start()
        window.mainloop()

    def log(self,message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.configure(state="disabled")

    def ping(self):
        selection = self.treeview.selection()
        item = self.treeview.item(selection[0])
        address = item['values'][0]
        sock = self.peer.get_peer_socket(address)
        self.peer.ping(sock)

    def auto_refresh(self):
        while True:
            self.refresh()
            time.sleep(10)

    def refresh(self):
        self.peer.get_peers(10)
        self.update_table()
        self.update_labels()

    def update_table(self):
        self.treeview.delete(*self.treeview.get_children())
        for index , address in enumerate(self.peer.get_peers_addresses()):
            self.treeview.insert("", "end", text=str(index+1), values=(address,self.peer.get_peers_sockets()[address].getsockname()))

    def update_labels(self):
        self.peers_label_text.set("peers : " + str(len(self.peer.get_peers_addresses())))

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


if __name__ == "__main__":
    Client()


