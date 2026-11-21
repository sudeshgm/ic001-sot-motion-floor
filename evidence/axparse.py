import re,sys
t=open(sys.argv[1]).read()
for e in t.split('<entry>')[1:]:
  i=re.search(r'<id>https?://arxiv.org/abs/([^<]+)</id>',e).group(1); d=re.search(r'<published>([^<]{10})',e).group(1); ti=' '.join(re.search(r'<title>(.*?)</title>',e,re.S).group(1).split())
  if d>='2025-06': print(d,i,ti[:120])
