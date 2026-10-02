"""Local-only static review server with MP4 byte-range seeking."""
import os,re,shutil
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
class ReviewHandler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def send_head(self):
  file=Path(self.translate_path(self.path));self._range_remaining=None
  if file.is_file() and self.headers.get('Range'):
   match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers['Range'])
   if match:
    size=file.stat().st_size;a=int(match[1]);z=min(size-1,int(match[2]) if match[2] else size-1)
    if a>=size or a>z:self.send_error(416);return None
    f=file.open('rb');f.seek(a);self._range_remaining=z-a+1;self.send_response(206);self.send_header('Content-type',self.guess_type(str(file)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {a}-{z}/{size}');self.send_header('Content-Length',str(z-a+1));self.end_headers();return f
  return super().send_head()
 def end_headers(self):self.send_header('Accept-Ranges','bytes');super().end_headers()
 def copyfile(self,source,output):
  if self._range_remaining is None:return super().copyfile(source,output)
  left=self._range_remaining
  try:
   while left:
    b=source.read(min(65536,left))
    if not b:break
    output.write(b);left-=len(b)
  except (BrokenPipeError,ConnectionResetError):pass
ThreadingHTTPServer(('127.0.0.1',8768),ReviewHandler).serve_forever()
