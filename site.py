import re
import time
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from multiprocessing import Process
from flask import Flask,request,render_template

def definearg(value,args):
   if value in args:
      return args[value]
   else:
      return None

def getime(inttime):
   t = time.localtime(inttime)
   return [
      t.tm_year,
      t.tm_mon,
      t.tm_mday,
      t.tm_hour,
      t.tm_min,
      t.tm_sec
   ]

def striter(i):
   return [str(j) for j in i]

def updateimages():
   data = pd.read_csv("data.csv",index_col=0)
   messages_total = data.trip
   tenmost = messages_total.value_counts()[:5]
   tenmostlabel,tenmostsize = tenmost.keys(),tenmost.values 
   otherlabel,othersize = ["other"],[messages_total.count() - tenmost.count()]
   labels,sizes = list(tenmostlabel)+otherlabel,list(tenmostsize)+othersize 
   plt.title("YC Users Messages")
   plt.pie(sizes,autopct="%1.1f%%",startangle=90)
   plt.legend(labels,loc=(1,0),fontsize=10)
   plt.savefig("./static/image.png")
   plt.clf()

   st = pd.Series(
      ["/".join(striter(time.localtime(i)[0:3])) for i in data["time"]]
   ).value_counts().sort_index().to_dict()
   x,y = st.keys(),st.values()
   plt.title("YC Activity")
   plt.plot(x,y)
   plt.savefig("./static/image_c.png")

app = Flask(__name__)

@app.route('/')
def home():
   messages = len(pd.read_csv("data.csv"))
   return ("<b>Link:</b><br>/lookup,/image<br>" \
      f"<br><b>Messages:</b><br>{messages}<br>" \
      "<br><b>Examples:</b><br>/lookup?time=2022-11-19/2022-11-21" \
      "<br>/lookup?time=all&nick=light<br>" \
      "/lookup?trip=a/Jz/a")

@app.route('/lookup',methods=['POST', 'GET'])
def lookup():
   reply = ""
   if request.method == "GET":
      timesf = definearg("time",request.args) # 2020-5-12/2020-5-13
      tripsf = definearg("trip",request.args) # trip = JlVj7N 
      nicksf = definearg("nick",request.args)

      if tripsf:
         tripsf = tripsf.replace(" ","+")

      start = end = getime(time.time())[0:4]
      if timesf:
         if timesf == "all":
            start,end = [-1,-1,-1],[99999,99999,99999]
            
         ifsftime = re.findall(r"^([0-9]+)/([0-9]+)/([0-9]+)$",timesf)
         if ifsftime:
            start = end = [int(i) for i in list(ifsftime[0])]

      for s in pd.read_csv("data.csv",index_col=0).itertuples():
         stime = getime(s[1])[0:4]
         if tripsf != None and tripsf != s[3]:
            continue
         if nicksf != None and nicksf != s[2]:
            continue

         if pd.isnull(s[3]):
            _trip = ""
         else:
            _trip = f"<i>{s[3]}</i>"
         formattxt = f"<b>{s[2]}</b> <small>{_trip}</small> <small>{'/'.join([str(i) for i in getime(s[1])[:4]])} {':'.join([str(i) for i in getime(s[1])[3:7]])}</small><br>{s[5]}<br><br>"
         if start[0]<=stime[0]<=end[0]: # if in this area
            if start[1]<=stime[1]<=end[1]:
               if start[2]<=stime[2]<=end[2]:
                  reply = reply + formattxt
   return reply

@app.route('/image')
def image():
   Process(target=updateimages).start()
   data = pd.read_csv("data.csv",index_col=0).trip
   info = ""
   for label,size in data.value_counts().items():
      info += "<a href=\"http://43.142.118.149:5000/lookup?trip={}\">{}</a> : {}<br>".format(label,label,size)
   return '<img src="static/image.png"><br><img src="static/image_c.png"><br>%s' % info

if __name__ == '__main__':
   app.run(host="0.0.0.0",port=5000,debug=True)
