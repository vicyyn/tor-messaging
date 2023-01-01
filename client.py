#/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from logger import Logger
from peer import Peer

class Client:
    def __init__(self) -> None:
        window = tk.Tk()
        window.geometry("800x400")
        window.title("tor-messaging client")
        window.config(background="#121212")

        info_frame = tk.Frame(window)
        address_label_text = tk.StringVar()
        address_label_text.set("Address : ")
        address_label = tk.Label(info_frame, textvariable=address_label_text,justify="center")
        address_label.pack(side="left", padx=5, pady=5)
        ip_label_text = tk.StringVar()
        ip_label_text.set("IP : ")
        ip_label = tk.Label(info_frame, textvariable=ip_label_text,justify="center")
        ip_label.pack(side="left", padx=5, pady=5)
        peers_label_text = tk.StringVar()
        peers_label_text.set("Peers : ")
        peers_label = tk.Label(info_frame, textvariable=peers_label_text,justify="center")
        peers_label.pack(side="left", padx=5, pady=5)
        info_frame.pack( side="top",fill="x")

        buttons_frame = tk.Frame(window)
        ping_button = tk.Button(buttons_frame, text="Ping",command=self.ping)
        ping_button.pack(side="left", padx=5, pady=5)
        send_button = tk.Button(buttons_frame, text="Send message", command=self.send_message)
        send_button.pack(side="left", padx=5, pady=5)
        init_button = tk.Button(buttons_frame, text="Initialize circuit" , command=self.initialize_circuit)
        init_button.pack(side="left", padx=5, pady=5)
        refresh_button = tk.Button(buttons_frame, text="Refresh", command=self.refresh)
        refresh_button.pack(side="left", padx=5, pady=5)
        buttons_frame.pack(side="top",fill="x")


        treeview = ttk.Treeview(window)
        treeview["columns"] = ("peer_address", "ip")
        treeview.heading("peer_address", text="Peer address")
        treeview.heading("ip", text="IP")
        treeview.pack(side="top",expand=True, fill="both")

        log_text = tk.Text(window,state="disabled")
        log_text.pack(side="bottom",fill="x")

        self.treeview = treeview
        self.address_label_text = address_label_text
        self.ip_label_text = ip_label_text
        self.peers_label_text = peers_label_text
        self.log_text = log_text

        self.peer = Peer("localhost",8000,10,Logger(self))
        window.mainloop()

    def log(self,message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
        self.refresh_gui()

    def initialize_circuit(self):
        addresses = self.get_addresses_from_selection()
        self.circuit = addresses
        self.peer.log(addresses)
        self.peer.initialize_circuit("SATOSHI",{"next":addresses})

    def send_message(self):
        message = "Hello World!"
        message = message.encode()
        self.peer.log(message)

        for address in self.circuit:
            self.peer.log(address)
            self.peer.log(self.peer.get_peer_publickey(address))
            message = self.peer.encrypt_with_publickey(message,self.peer.get_peer_publickey(address))
            self.peer.log(len(message))

        self.peer.log(message)
        self.peer.log(self.circuit)

        address = self.get_address_from_selection(0)
        sock = self.peer.get_peers_sockets()[address]
        self.peer.send_message("SATOSHI",message,sock)

    def ping(self):
        address = self.get_address_from_selection(0)
        sock = self.peer.get_peers_sockets()[address]
        self.peer.ping(sock)
        self.refresh_gui()

    def refresh(self):
        self.log("refresh")
        self.peer.get_peers(10)
        self.refresh_gui()

    def refresh_gui(self):
        self.update_table()
        self.update_labels()

    def update_table(self):
        try:
            self.treeview.delete(*self.treeview.get_children())
            for index , address in enumerate(self.peer.get_peers_addresses()):
                self.treeview.insert("", "end", text=str(index+1), values=(address,self.peer.get_peers_sockets()[address].getsockname()))
        except:
            pass

    def update_labels(self):
        try:
            self.peers_label_text.set("peers : " + str(len(self.peer.get_peers_addresses())))
            self.address_label_text.set("Address : " + self.peer.get_address())
            self.ip_label_text.set("IP : " + str(len(self.peer.get_socket().getsockname())))
        except:
            pass

    def get_addresses_from_selection(self):
        selections = self.treeview.selection()
        res = []
        for i in range(len(selections)):
            res.append(self.get_address_from_selection(i))
        return res

    def get_address_from_selection(self,number):
        try:
            selection = self.treeview.selection()
            item = self.treeview.item(selection[number])
            address = item['values'][0]
            return address
        except:
            return None

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
