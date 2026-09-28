"""쇼츠 썸네일 (1080x1920). render_epN.json의 "thumb" 설정을 읽는다.

사용법: python3 tools/thumb.py render_ep1.json thumb_ep1.jpg
"thumb": {"cut": 컷 번호(0부터), "lines": ["윗줄", "아랫줄"]}
폰트(BlackHanSans.ttf)는 render.py와 같은 폴더에 둔다.
"""
import json,sys,random,urllib.request
from PIL import Image,ImageDraw,ImageFont,ImageFilter
M=json.load(open(sys.argv[1]));OUT=sys.argv[2];T=M['thumb']
W,H=1080,1920;INK=(18,18,18);YEL=(255,212,0);RED=(200,34,34);CREAM=(250,247,238)
def jag(R,n,a):
 v=0;o=[]
 for _ in range(n):v=max(-a,min(a,v+R.uniform(-a*.6,a*.6)));o.append(v)
 return o
def torn(R,w,h,m,a=9,s=14):
 t=[(m+x,m+a+d) for x,d in zip(range(0,w+1,s),jag(R,w//s+1,a))]
 r=[(m+w-a+d,m+y) for y,d in zip(range(0,h+1,s),jag(R,h//s+1,a))]
 b=[(m+x,m+h-a+d) for x,d in zip(range(w,-1,-s),jag(R,w//s+1,a))]
 l=[(m+a+d,m+y) for y,d in zip(range(h,-1,-s),jag(R,h//s+1,a))]
 return t+r+b+l
def paper(txt,bg,fg,sz,rot,seed,maxw=1000):
 # render.py의 종이 조각과 같은 모양. 폭이 넘치면 글자를 줄인다
 R=random.Random(seed)
 while True:
  f=ImageFont.truetype('BlackHanSans.ttf',sz);b=f.getbbox(txt);tw,th=b[2]-b[0],b[3]-b[1];px,py,m=50,40,40
  if tw+2*px+2*m<=maxw or sz<60:break
  sz-=6
 w,h=tw+2*px,th+2*py;im=Image.new('RGBA',(w+2*m,h+2*m),(0,0,0,0))
 outer=torn(R,w,h,m,12);inner=[(x+R.uniform(-2,2),y+R.uniform(-2,2)) for x,y in torn(R,w-14,h-14,m+7,8)]
 sh=Image.new('L',im.size,0);ImageDraw.Draw(sh).polygon([(x+8,y+12) for x,y in outer],fill=130);sh=sh.filter(ImageFilter.GaussianBlur(9))
 im.paste((0,0,0,255),(0,0),sh);d=ImageDraw.Draw(im);d.polygon(outer,fill=CREAM+(255,));d.polygon(inner,fill=bg+(255,))
 d.text((m+px-b[0],m+py-b[1]),txt,font=f,fill=fg)
 return im.rotate(rot,expand=1,resample=Image.BICUBIC)
urllib.request.urlretrieve(M['cuts'][T['cut']]['img'],'thumb_bg.png')
bg=Image.open('thumb_bg.png').convert('RGB');s=max(W/bg.width,H/bg.height)
bg=bg.resize((int(bg.width*s),int(bg.height*s)),Image.LANCZOS);x0,y0=(bg.width-W)//2,(bg.height-H)//2;fr=bg.crop((x0,y0,x0+W,y0+H))
# 글자 뒤 위쪽을 살짝 어둡게 해서 작은 화면에서도 읽히게
g=Image.new('L',(1,H));[g.putpixel((0,y),int(150*max(0,1-y/900))) for y in range(H)];fr.paste((0,0,0),(0,0),g.resize((W,H)))
y=170
for i,l in enumerate(T['lines']):
 p=paper(l,YEL if i==0 else CREAM,INK,200 if i==0 else 230,(-3,2)[i%2],i);fr.paste(p,((W-p.width)//2,y),p);y+=p.height-30
st=paper('그란데?',RED,CREAM,150,-6,99);fr.paste(st,((W-st.width)//2,H-st.height-170),st)
fr.save(OUT,quality=92);print('saved',OUT)
