# Demo 03 — audio-only finishing record

The user approved the visual story and requested one audio-only pass to match the accepted Demo 01/02 level. This pass used the already encoded [visually approved MP4](renders/motif-demo-03-calendar-approval.mp4); it did not change the narration file, individual SFX levels, scene events, artwork, frame timing, or video stream.

## Diagnosis

| Source measured with FFmpeg loudnorm analysis | Integrated loudness | True peak |
| --- | ---: | ---: |
| Demo 03 raw local Kokoro `af_nova` WAV | −27.10 LUFS | −9.86 dBTP |
| Demo 03 original encoded mix | −24.43 LUFS | −9.87 dBTP |
| Demo 02 accepted encoded mix | −16.25 LUFS | −3.00 dBTP |

Demo 03's audio plan placed the raw Kokoro WAV directly at volume 1; Demo 02's plan used a prepared `narration-master.wav`. The absent preparation stage accounts for the level mismatch. The encoded Demo 03 mix was already assembled, so applying a single gain to that **combined** mix retained the intended narration-to-SFX relationship.

## Exact finishing operation

From the repository root:

```bash
ffmpeg -hide_banner -y \
  -i videos/motif-calendar-reel/renders/motif-demo-03-calendar-approval.mp4 \
  -map 0:v:0 -map 0:a:0 -map_metadata 0 \
  -c:v copy -af 'volume=8.2dB' -c:a aac -b:a 192k \
  -movflags +faststart \
  videos/motif-calendar-reel/renders/motif-demo-03-calendar-approval-audio-finished.mp4
```

The 360 × 640 mobile copy uses its already encoded video stream and the finished full-resolution AAC stream:

```bash
ffmpeg -hide_banner -y \
  -i videos/motif-calendar-reel/renders/motif-demo-03-calendar-approval-mobile.mp4 \
  -i videos/motif-calendar-reel/renders/motif-demo-03-calendar-approval-audio-finished.mp4 \
  -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart \
  videos/motif-calendar-reel/renders/motif-demo-03-calendar-approval-audio-finished-mobile.mp4
```

## Encoded result

| File | Integrated loudness | True peak | Duration |
| --- | ---: | ---: | ---: |
| Full finished MP4 | −16.24 LUFS | −1.68 dBTP | 12.80 s |
| Mobile finished MP4 | −16.24 LUFS | −1.68 dBTP | 12.80 s |

FFmpeg's `loudnorm` analysis supplied these encoded-file measurements. The original and finished 1080 × 1920 H.264 video streams have the same SHA-256 packet hash, `acb75267855e38c202efe71023c30a2fdb1c8215d64e41c62500c40625043e32`; the mobile video streams also match each other at `684bacb240f63498a2f519c1ffa43c309cb20c70d7b98cbca65f9293c0c36391`. All 384 full-resolution frames and the 12.80-second timing are preserved. The measured level now matches Demo 02 within 0.01 LU. This establishes technical level consistency, not a subjective judgment of narration or SFX quality.
