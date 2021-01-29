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
  n_intervals=0
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
    for value in values:
      data = value.split('=')
      if len(data) > 1 and (data[0] == 'pkt_pts_time' or data[0] == 'pkt_size'):
        queue.put(data)
  out.close()

def runFfprobe(infile):
  global thread
  proc = Popen(
    [
      'ffprobe',
      "-show_frames",
      "-print_format",
      "compact",
      "-prefix",
      infile
    ],
    stdout=PIPE
  )
  thread = Thread(target=handleFfprobeOutput, args=(proc.stdout, q), daemon=True)
  thread.start()

@app.callback(Output('frame-graph', 'figure'), Input('interval-component', 'n_intervals'))
def updateFigure(n):
  global fig, dataFrame, interval
  if thread and thread.is_alive():
    dict = {}
    while not q.empty():
      data = q.get()
      if data[0] not in dict:
        dict[data[0]] = []
      dict[data[0]].append(data[1])
    if len(dict.keys()) > 0:
      df2 = DataFrame(data=dict)
      dataFrame = dataFrame.append(df2, ignore_index=True)
      click.echo(dataFrame)
      fig = px.box(data_frame=dataFrame, x='pkt_pts_time', y='pkt_size')
    else:
      interval.disabled = True
  return fig

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