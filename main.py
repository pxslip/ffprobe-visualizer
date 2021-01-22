import distutils.spawn
import subprocess
import click
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

dataFrame = None
currentStdout = {}

@click.command()
@click.argument('infile', nargs=1)
def visualizer(infile):
  if distutils.spawn.find_executable('ffprobe') == None:
    click.echo('ffmpeg, and specifically ffprobe must be installed to use this program')
    exit(1)

  click.echo(infile)

  proc = subprocess.Popen(["ffprobe", "-show_frames", "-print_format", "compact", "-prefix", infile], stdout=subprocess.PIPE)
  for line in proc.stdout:
    values = line.decode('utf-8').split('|')
    dictionary = {}
    for value in values:
      data = value.split('=')


if __name__ == '__main__':
  visualizer()