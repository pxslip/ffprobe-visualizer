import distutils.spawn
from subprocess import PIPE, Popen
import asyncio
import click
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from pandas import DataFrame
from threading  import Thread
from queue import Queue, Empty

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
dataFrame = DataFrame()
q = Queue()
interval = dcc.Interval(
  id='interval-component',
  interval=1*2000, # in milliseconds
  n_intervals=0,
)
thread = None
fig = px.box()

def startDashServer():
  global interval
  app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='frame-graph',
        figure=fig
    ),
    interval
  ])
  app.run_server(debug=True)

def handleFfprobeOutput(out, queue: Queue):
  for line in iter(out.readline, b''):
    values = line.decode('utf-8').split('|')
    if values[0].lower() == 'frame':
      queue.put(values)
      # for value in values:
      #   data = value.split('=')
      #   if len(data) > 1 and (data[0] == 'pkt_pts_time' or data[0] == 'pkt_size'):
      #     queue.put(data)
  out.close()

def runFfprobe(infile):
  global thread
  proc = Popen(
    [
      'ffprobe',
      "-show_frames",
      "-print_format",
      "compact",
      "-select_streams",
      "v",
      "-hide_banner",
      # "-prefix",
      infile
    ],
    stdout=PIPE
  )
  thread = Thread(target=handleFfprobeOutput, args=(proc.stdout, q), daemon=True)
  thread.start()

@app.callback(Output('frame-graph', 'figure'), Output('interval-component', 'disabled'), Input('interval-component', 'n_intervals'))
def updateFigure(n):
  global fig, dataFrame
  disabled = False
  dict = {}
  while not q.empty():
    values = q.get()
    for value in values:
      data = value.split('=')
      if len(data) > 1:
        key = data[0]
        value = data[1]
        if key not in dict:
          dict[key] = []
        if key == 'pkt_pts_time':
          value = float(value)
        elif key == 'pkt_size':
          value = int(value) / 1000
        dict[key].append(value)
  if len(dict.keys()) > 0:
    df2 = DataFrame(data=dict)
    dataFrame = dataFrame.append(df2, ignore_index=True)
    fig = px.bar(data_frame=dataFrame, x='pkt_pts_time', y='pkt_size', hover_data=dict.keys())
  else:
    disabled = True
  click.echo(dataFrame)
  return (fig, disabled)

@click.command()
@click.argument('infile', nargs=1)
def main(infile):
  if distutils.spawn.find_executable('ffprobe') == None:
    click.echo('ffmpeg, and specifically ffprobe must be installed to use this program')
    exit(1)
  runFfprobe(infile)
  startDashServer()

if __name__ == '__main__':
  main()