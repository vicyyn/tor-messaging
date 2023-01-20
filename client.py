#/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
from cell import Cell
from logger import Logger
from peer import Peer
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class Client:
    def __init__(self) -> None:
        self.layers = []

        window = tk.Tk()
        self.window = window
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
        init_button = tk.Button(buttons_frame, text="Create Circuit" , command=self.create_circuit)
        init_button.pack(side="left", padx=5, pady=5)
        refresh_button = tk.Button(buttons_frame, text="Refresh", command=self.refresh)
        refresh_button.pack(side="left", padx=5, pady=5)
        buttons_frame.pack(side="top",fill="x")

        self.circuit = []

        treeview = ttk.Treeview(window)
        treeview.pack(side="top",expand=True, fill="both")
        treeview["columns"] = ("peer_address", "ip")
        treeview.heading("peer_address", text="Peer address")
        treeview.heading("ip", text="IP")
        treeview.bind('<Double-1>', self.pop_window)
        treeview.pack(side="top",expand=True, fill="both")

        log_text = tk.Text(window,state="disabled")
        log_text.pack(side="bottom",fill="x")

        self.treeview = treeview
        self.address_label_text = address_label_text
        self.ip_label_text = ip_label_text
        self.peers_label_text = peers_label_text
        self.log_text = log_text
        self.messages_log = None

        self.peer = Peer("localhost",8000,10,Logger(self))
        window.mainloop()

    def pop_window(self,event):
        address = self.get_address_from_selection(0)

        messaging_box = tk.Toplevel(self.window)
        tk.Label(messaging_box, text='address : ' + address).pack()

        bottom_frame = tk.Frame(messaging_box)

        send_button = tk.Button(bottom_frame, text="Send Message", command=self.send_message)
        send_button.pack(side="right", padx=5, pady=5)

        left_label = tk.Label(bottom_frame, text="message : ",justify="center")
        left_label.pack(side="left", padx=5, pady=5)

        self.message_input = tk.Entry(bottom_frame)
        self.message_input.pack(side="left", padx=5, pady=5)

        bottom_frame.pack(side="bottom",fill="x")

        self.messages_log = tk.Text(messaging_box,state="disabled")
        self.messages_log.pack(side="top",fill="x")
        self.fill_messages_log(address)

    def fill_messages_log(self,address):
        self.messages_log.delete(1.0,tk.END)
        for message in self.peer.messages.get(address,[]):
            self.messages_log.configure(state="normal")
            self.messages_log.insert("end", str(message) + "\n")
            self.log_text.configure(state="disabled")
        self.log_text.see("end")


    def log(self,message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", str(message) + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")
        self.refresh_gui()

    def create_circuit(self):
        address = self.get_address_from_selection(0)
        self.circuit.append(address)
        self.peer.create_circuit("satoshi",address)
        self.peer.log(self.circuit)
    
    def send_message(self):
        address = self.get_address_from_selection(0)
        sock = self.peer.get_peers_sockets()[self.circuit[0]]
        message = bytes(self.message_input.get(),'utf-8')

        for key in reversed(self.peer.layers):
            aes = self.peer.get_aes_from_key(key)
            message = aes.encrypt(pad(message,16))

        cell = Cell("NA","message", {"from":self.peer.address,"message":message,"next":self.circuit[1:] + [address]} )
        self.peer.send_cell(cell,sock)
        self.peer.add_message(self.message_input.get(),address,self.peer.address)
        self.log(self.peer.messages)
        self.fill_messages_log(address)

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
            self.ip_label_text.set("IP : " + str(self.peer.get_socket().getsockname()))
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

if __name__ == "__main__":
    Client()
