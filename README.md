# FFProbe Visualizer

Takes a video file and spins up a DASH based server that shows the bitrate of the given file via ffprobe

## Usage

### With Python Installed

The package requires python 3 to run, once installed do the following

- `pip install -r requirements.txt`
- `python main.py [video_file.ext]`

### Using the docker image

With docker installed run:

- `docker run -v /path/to/video_file.ext:/app/video_file.ext -p 8080:8080 pxslip/ffprobe-visualizer video_file.ext`
  - `docker run` - run the given container
  - `-v /path/to/video_file.ext:/app/video_file.ext` - mount the file into the container
  - `-p 8080:8080` - bind from container to host, limit which interfaces this binds to by changing to `-v 127.0.0.1:8080:8080`
  - `pxslip/ffprobe-visualizer` - the name of the container
  - `video.mkv` - the name of the video file to analyze
    - The script is run from `/app` so the path should be relative to that directory, or absolute in the filesystem

#### Environment Variables of Note

- `PORT` - change which port the flask server binds to
- `HOST` - change the host name that the flask server binds to, if not set flask binds to loopback so is only accessible via a local machine
  - Use `0.0.0.0` to bind to all interfaces
