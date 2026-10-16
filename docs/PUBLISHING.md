# Posting approved reels with Buffer

`scripts/motif_publish.py` sends a finished reel to [Buffer](https://buffer.com),
which posts it to Instagram Reels, TikTok, YouTube Shorts and the other channels
connected to the Buffer account. Nothing is posted until a human has approved
the exact render.

## How it fits the loop

```bash
python scripts/motif_reel.py run --brief BRIEF --out RUNS --render ...   # ends at REVIEW_REQUIRED
# Mayowa watches RUNS/<slug>-finished/renders/review.mp4 on a phone
python scripts/motif_publish.py approve RUNS/<slug> --by Mayowa          # records who approved which file (sha256)
python scripts/motif_publish.py publish RUNS/<slug> --dry-run            # checks key + channels, prints the posts
python scripts/motif_publish.py publish RUNS/<slug>                      # into Buffer's queue
```

`publish` refuses a reel with no approval, a render that changed after it was
approved (sha256 mismatch), a run whose quality gate failed, and a second post
to a channel it already went to (`--again` overrides). Each publish is
written to `reel-record.json` (`publish` entries and a `publish` stage).

When it goes out:

| flag | Buffer mode | result |
|---|---|---|
| (none) | `addToQueue` | next open slot in the channel's Buffer posting schedule |
| `--draft` | `saveToDraft` | a draft in Buffer; nothing goes out until someone schedules it there |
| `--next` | `shareNext` | front of the queue |
| `--at 2026-10-20T17:00:00-04:00` | `customScheduled` | that exact time |
| `--now` | `shareNow` | immediately |

The caption is the brief's hook line and CTA, unless the brief has a `post`
block: `{"caption": ..., "title": ..., "hashtags": [...]}` (`title` is the
YouTube title, default the brief's `title`). Per-network settings: Instagram
and Facebook post as a Reel shared to the feed; YouTube uses the title,
category Education, public.

## One-time setup (Mayowa)

1. **Buffer API key.** In Buffer, go to Settings → API
   (<https://publish.buffer.com/settings/api>) and create a key. The free plan
   allows one key and 250 requests a day, plenty for this.
2. **Connect the channels** you want Motif to post to in Buffer
   (Instagram must be a business or creator account; YouTube and TikTok are
   connected the usual way).
3. **A video host.** Buffer only takes video by public https URL and fetches
   it when the post goes out, so the render must stay online until then.
   Create a free [Cloudinary](https://cloudinary.com) account and copy the
   **API environment variable** from its dashboard (it looks like
   `cloudinary://<api_key>:<api_secret>@<cloud_name>`). Renders over 100 MB
   need `--video-url` with your own host instead.
4. **Save the credentials** on the machine that runs Motif, never in the repo.
   Either environment variables:

   ```bash
   export BUFFER_API_KEY=...
   export CLOUDINARY_URL=cloudinary://...
   export MOTIF_BUFFER_CHANNELS=<channel id>,<channel id>
   ```

   or `~/.config/motif/publish.json` (`chmod 600` it):

   ```json
   {"api_key": "...", "channels": ["<channel id>"],
    "cloudinary": {"cloud_name": "...", "api_key": "...", "api_secret": "..."}}
   ```

   `MOTIF_PUBLISH_CONFIG` points at a different file.
5. **Find the channel ids** with `python scripts/motif_publish.py channels`
   and put the ones Motif should post to in `channels`.
6. **First test:** `publish RUNS/<slug> --draft` on an approved reel, then
   check the drafts in Buffer before using the queue.

## Notes

- Buffer's API is a GraphQL endpoint at `https://api.buffer.com` with a
  bearer key ([docs](https://developers.buffer.com)). A Buffer API key has full
  access to the account; keep it out of the repo, logs and chat.
- Buffer fetches the video at post time; deleting it from Cloudinary before
  then breaks the post.
- The thumbnail is the frame at 1 s (`thumbnailOffset`, Instagram/TikTok/Pinterest).
