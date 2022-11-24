import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask,request,render_template

def definearg(value,args):
   if value in args:
      return args[value]
   else:
      return None

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
      timearea = definearg("time",request.args) # 2020-5-12/2020-5-13
      tripsf = definearg("trip",request.args) # trip = JlVj7N 
      nicksf = definearg("nick",request.args)
      try:
         start,end = [
            [int(j) for j in i.split("-")]
            for i in timearea.split("/")
         ] # [[2020,5,12],[2020,5,13]]
      except:
         start,end = [[-1,-1,-1],[9999,99,99]]

      for s in pd.read_csv("data.csv",index_col=0).itertuples():
         stime = [int(i) for i in s[1].split(" ")[0].split("-")] # [2020,5,12]
         if tripsf != None and tripsf != s[3]:
            continue
         if nicksf != None and nicksf != s[2]:
            continue

         if pd.isnull(s[3]):
            _trip = ""
         else:
            _trip = f"<i>{s[3]}</i>"
         formattxt = f"<b>{s[2]}</b> <small>{_trip}</small> <small>{s[1]}</small><br>{s[5]}<br><br>"
         if start[0]<=stime[0]<=end[0]: # if in this area
            if start[1]<=stime[1]<=end[1]:
               if start[2]<=stime[2]<=end[2]:
                  reply = reply + formattxt
   return reply

@app.route('/image')
def image():
   data = pd.read_csv("data.csv",index_col=0)
   messages_total = data.trip
   tenmost = messages_total.value_counts()[:5]
   tenmostlabel,tenmostsize = tenmost.keys(),tenmost.values 
   otherlabel,othersize = ["other"],[messages_total.count() - tenmost.count()]
   labels,sizes = list(tenmostlabel)+otherlabel,list(tenmostsize)+othersize 
   fig = plt.figure()
   plt.pie(sizes,autopct="%1.1f%%",startangle=90)
   plt.legend(labels,loc=(1,0),fontsize=10)
   fig.savefig("./static/image.png")
   info = ""
   for label,size in messages_total.value_counts().items():
      info += "<a href=\"http://43.142.118.149:5000/lookup?trip={}\">{}</a> : {}<br>".format(label,label,size)
   return '<img src="static/image.png"><br>{}'.format(info)

if __name__ == '__main__':
   app.run(host="0.0.0.0",port=5000,debug=True)
