class Logger:
    def __init__(self,client) -> None:
        self.client = client

    def log(self,message):
        print(message)
        self.client.log(message)

