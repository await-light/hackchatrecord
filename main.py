import json
import time
import random
import pandas as pd
from websocket import create_connection

class Client:
	def __init__(self):
		self._ws = create_connection("wss://hack.chat/chat-ws")
		if self._ws.status == 101:
			print("Able to run.")
			self.csvdata = self.loadfile()
			self.record()

	def loadfile(self):
		try:
			return pd.read_csv("data.csv")
		except pd.errors.EmptyDataError:
			return pd.DataFrame(
				[]
			)

	def updatefile(self):
		self.csvdata.to_csv("data.csv",index=True)

	def record(self):
		self._ws.send(
			json.dumps(
				{
					"cmd":"join",
					"nick":f"light{random.randint(999,10000)}",
					"channel":"your-channel"
				}
			)
		)
		while True:
			jsondata = json.loads(self._ws.recv())
			cmd = jsondata["cmd"]
			if cmd != "chat":
				continue
			rv = pd.Series(
				jsondata,
				index=["time","nick","trip","uType","text"]
			)
			rv["time"] = time.strftime(
				"%Y-%m-%d %H:%M:%S",
				time.localtime(rv["time"]/1000)
			)
			print(rv.to_string())
			self.csvdata = pd.concat(
				[
					self.csvdata,
					rv.to_frame().T
				],
				ignore_index=True
			)
			self.updatefile()

if __name__ == '__main__':
	Client()
