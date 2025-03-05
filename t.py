import streamlink

url = "https://videolamborghini-meride-tv.akamaized.net/video/folder2/Lambo_40MB_APP_lamborghini/Lambo_40MB_APP_lamborghini.m3u8"
output_file = "lamborghini_video.mp4"

# Get available streams
streams = streamlink.streams(url)

if "best" in streams:
    stream = streams["best"]
    with open(output_file, "wb") as f:
        with stream.open() as stream_fd:
            while True:
                data = stream_fd.read(1024)  # Read in chunks (1KB)
                if not data:
                    break
                f.write(data)

    print(f"Download complete: {output_file}")
else:
    print("No suitable stream found.")
