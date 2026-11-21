# Lists the central directory of the remote KITTI tracking velodyne zip via HTTP Range requests (reads only a few MB).
import io, zipfile, urllib.request, collections, sys
URL="https://s3.eu-central-1.amazonaws.com/avg-kitti/data_tracking_velodyne.zip"
class R(io.RawIOBase):
    def __init__(s,u):
        s.u=u; s.pos=0; s.n=0
        req=urllib.request.Request(u,method='HEAD'); s.size=int(urllib.request.urlopen(req).headers['Content-Length'])
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.pos
    def seek(s,o,w=0):
        s.pos = o if w==0 else (s.pos+o if w==1 else s.size+o); return s.pos
    def read(s,n=-1):
        if n<0: n=s.size-s.pos
        if n==0: return b''
        end=min(s.pos+n,s.size)-1
        req=urllib.request.Request(s.u,headers={'Range':f'bytes={s.pos}-{end}'})
        d=urllib.request.urlopen(req).read(); s.pos+=len(d); s.n+=len(d); return d
    def readinto(s,b):
        d=s.read(len(b)); b[:len(d)]=d; return len(d)
r=R(URL); z=zipfile.ZipFile(io.BufferedReader(r,buffer_size=1<<20))
agg=collections.defaultdict(lambda:[0,0,0])
for i in z.infolist():
    p=i.filename.split('/')
    key='/'.join(p[:-1])
    a=agg[key]; a[0]+=1; a[1]+=i.compress_size; a[2]+=i.file_size
with open('kitti_tracking_velodyne_zip_listing.tsv','w') as f:
    f.write('dir\tfiles\tcompressed_bytes\tuncompressed_bytes\n')
    for k in sorted(agg): f.write(f'{k}\t{agg[k][0]}\t{agg[k][1]}\t{agg[k][2]}\n')
print('bytes fetched for listing:', r.n, 'entries:', len(z.infolist()), 'compress types:', set(i.compress_type for i in z.infolist()))
for k in sorted(agg):
    if k.endswith(('0019','0020')) and 'training' in k: print(k, agg[k])
