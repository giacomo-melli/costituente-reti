import sys, numpy as np
from PIL import Image
im=Image.open(sys.argv[1]).convert('L'); a=np.array(im); h,w=a.shape
dark=a<128; rows=dark.sum(1)
ink=np.where(rows>w*0.01)[0]
top,bot=ink[0],ink[-1]
# header line: first text block then gap
hdr_end=top
i=top
while i<h and rows[i]>w*0.005: i+=1
hdr_end=i
body=dark[hdr_end:bot]
col=body.sum(0)
lo,hi=int(w*0.4),int(w*0.6)
g=lo+int(np.argmin(np.convolve(col[lo:hi],np.ones(21),'same')))
Image.fromarray(a[hdr_end:bot+10, :g]).save(sys.argv[2]+'_L.png')
Image.fromarray(a[hdr_end:bot+10, g:]).save(sys.argv[2]+'_R.png')
print(top,hdr_end,bot,g)
