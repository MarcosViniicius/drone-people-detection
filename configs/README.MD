# Stream Configuration Examples

## Local RTMP Server Setup

### ⚠️ Important: HLS Requires Active RTMP Transmission

**HLS streams only work when you are actively transmitting to the RTMP server!**

The nginx-rtmp server generates HLS files (.m3u8 and .ts) in real-time from your RTMP transmission. Without an active RTMP stream, there are no HLS files to process.

**Workflow:**
```
1. Start nginx-rtmp server
2. Start transmitting (OBS/ffmpeg) → RTMP server
3. Wait 5-10 seconds for HLS files to generate
4. Process the HLS stream
```

### Directory Structure

The nginx-rtmp server automatically generates HLS stream files in:
```
nginx-rtmp-stream/
├── stream/              # HLS files generated here (.m3u8, .ts)
│   └── live/            # Stream name (created when streaming)
│       ├── index.m3u8   # HLS playlist
│       └── *.ts         # Video segments
```

**Important**: This directory is managed by nginx and should not be edited manually.

### 1. Start the RTMP server

```bash
cd nginx-rtmp-stream
docker compose up -d
```

### 2. Stream from OBS Studio

**Settings → Stream:**
- Service: Custom
- Server: `rtmp://localhost:1935/live`
- Stream Key: (leave empty or use any name)

### 3. Test stream URL

The stream will be available at:
- RTMP: `rtmp://localhost:1935/live`
- HLS: `http://localhost:8081/live/.m3u8`

**Note**: HLS files (.m3u8 and .ts segments) are automatically generated in `nginx-rtmp-stream/stream/live/` when you start streaming.

### 4. Monitor Stream Files

Check if HLS files are being generated:
```bash
# Windows (PowerShell)
Get-ChildItem nginx-rtmp-stream\stream\live\

# Linux/Mac
ls nginx-rtmp-stream/stream/live/
```

You should see:
- `index.m3u8` - HLS playlist
- `*.ts` - Video segment files (updated continuously)

## External Stream Examples

### YouTube Live

```
https://www.youtube.com/watch?v=VIDEO_ID
```

Note: You may need youtube-dl or yt-dlp for YouTube streams.

### Twitch

```
https://www.twitch.tv/CHANNEL_NAME
```

### Generic RTMP

```
rtmp://streaming-server.com:1935/live/stream-key
```

### Generic HLS

```
http://streaming-server.com/path/to/stream.m3u8
```

### IP Camera (RTSP)

```
rtsp://username:password@camera-ip:554/stream
```

Note: OpenCV supports RTSP, but performance may vary.

## Configuration Tips

### For Low Latency Streams

```json
"stream": {
  "dimensions": {
    "width": 1280,
    "height": 720
  }
}
```

Use smaller dimensions for faster processing.

### For High Quality Detection

```json
"stream": {
  "dimensions": {
    "width": 1920,
    "height": 1080
  }
}
```

Larger dimensions provide better detection but require more processing power.

### Inference Parameters for Streams

For real-time streams, consider adjusting:

```json
"inference_parameters": {
  "conf": 0.3,
  "iou": 0.45,
  "classes": [0],
  "verbose": false
}
```

- Higher `conf` reduces false positives
- Lower `conf` detects more people but may have false positives
- Adjust based on your use case

## Network Streams Troubleshooting

### Connection Issues

1. **Firewall**: Ensure ports 1935 (RTMP) and 8081 (HLS) are open
2. **Network**: Check your internet connection
3. **Server**: Verify the streaming server is online
4. **URL**: Test the stream URL in VLC or another player first

### Performance Issues

1. **Reduce resolution**: Lower `stream.dimensions`
2. **Use lighter model**: Switch to `yolo11n.pt` or `yolo11s.pt`
3. **Close other apps**: Free up system resources
4. **Check CPU/GPU**: Monitor system resource usage

### Buffering or Lag

1. **Network bandwidth**: Ensure stable internet connection
2. **Server load**: The streaming server may be overloaded
3. **Local processing**: Your system may not be fast enough
   - Reduce resolution
   - Use a lighter YOLO model
   - Close unnecessary applications

## File Locations

### HLS Stream Files (nginx-rtmp)
```
nginx-rtmp-stream/stream/live/
├── index.m3u8           # HLS playlist (auto-generated)
└── *.ts                 # Video segments (auto-updated)
```
**Note**: These files are managed by nginx. Do not edit or delete while streaming.

### Processed Stream Recordings
```
data/output/videos/
├── live_recordings/     # Recorded processed streams
│   └── stream_recording_YYYYMMDD_HHMMSS.mp4
└── stats/              # Stream statistics
    └── stats_stream_YYYYMMDD_HHMMSS.txt
```

### Configuration
```
configs/
└── config.json         # Stream settings
    └── stream.hls_stream_directory: "./nginx-rtmp-stream/stream"
    └── stream.recording_directory: "./data/output/videos/live_recordings"
```

## Complete Workflow

### For Internal HLS Stream (Recommended)

1. **Start nginx server**: 
   ```bash
   cd nginx-rtmp-stream
   docker compose up -d
   ```

2. **Verify server is running**:
   ```bash
   docker compose ps
   # Should show nginx container as "Up"
   ```

3. **Start streaming with OBS Studio**:
   - Settings → Stream → Service: Custom
   - Server: `rtmp://localhost:1935/live`
   - Stream Key: (leave empty or any name)
   - Click "Start Streaming"

4. **Wait 5-10 seconds** for HLS files to be generated

5. **Verify HLS files exist**:
   ```bash
   # Windows (PowerShell)
   Get-ChildItem nginx-rtmp-stream\stream\live\
   
   # Should see: index.m3u8 and *.ts files
   ```

6. **Run detection**: 
   ```bash
   python main.py
   ```
   - Option 1 (Livestream)
   - Option 1 (Internal stream)
   - Option 2 (HLS) ← Choose this!

7. **Enable recording** (optional): Answer 'y' to save processed video

8. **Monitor processing**: View live detection window and terminal stats

9. **Stop processing**: Press 'Q' key

10. **Check recordings**: Find in `data/output/videos/live_recordings/`

11. **Stop streaming in OBS**: Click "Stop Streaming"

12. **Stop server** (when done):
    ```bash
    cd nginx-rtmp-stream
    docker compose down
    ```

### For Internal RTMP Stream (Direct)

1-3. Same as above (start server and OBS)

4. **Run detection immediately** (no need to wait):
   - Option 1 (Livestream)
   - Option 1 (Internal stream)
   - Option 1 (RTMP) ← Direct processing!

5-10. Same as HLS workflow

### Troubleshooting: "Unable to open stream"

**Error**: `Error when loading first segment` or `Stream timeout`

**Cause**: No active RTMP transmission

**Solution**:
1. Make sure OBS (or ffmpeg) is **actively streaming**
2. Check OBS status bar shows "Live" or "Streaming"
3. Wait 5-10 seconds after starting transmission
4. Verify HLS files exist in `nginx-rtmp-stream/stream/live/`
5. If files don't exist, check nginx logs:
   ```bash
   cd nginx-rtmp-stream
   docker compose logs nginx
   ```
