import json,sys,re,random,subprocess,urllib.request
from PIL import Image,ImageDraw,ImageFont,ImageFilter
M=json.load(open(sys.argv[1]));OUT=sys.argv[2]
W,H,FPS=1080,1920,30;PAD=0.25;INTRO=1.4;OUTRO=1.4;TR=0.5
PAPER=(226,221,208);INK=(18,18,18);YEL=(255,212,0);RED=(200,34,34);CREAM=(250,247,238)
FB,FN='BlackHanSans.ttf','Nanum.ttf'
def get(u,p):urllib.request.urlretrieve(u,p);return p
def cl(x):return max(0.,min(1.,x))
def eo(x):x=cl(x);return 1-(1-x)**3
def dur(p):return float(subprocess.check_output(['ffprobe','-v','0','-show_entries','format=duration','-of','csv=p=0',p]))
def jag(R,n,a):
 v=0;o=[]
 for _ in range(n):v=max(-a,min(a,v+R.uniform(-a*.6,a*.6)));o.append(v)
 return o
def torn(R,w,h,m,a=9,s=14):
 # 네 변이 찢긴 종이 외곽선(여백 m 안쪽)
 t=[(m+x,m+a+d) for x,d in zip(range(0,w+1,s),jag(R,w//s+1,a))]
 r=[(m+w-a+d,m+y) for y,d in zip(range(0,h+1,s),jag(R,h//s+1,a))]
 b=[(m+x,m+h-a+d) for x,d in zip(range(w,-1,-s),jag(R,w//s+1,a))]
 l=[(m+a+d,m+y) for y,d in zip(range(h,-1,-s),jag(R,h//s+1,a))]
 return t+r+b+l
def paper(txt,st,seed):
 R=random.Random(seed);bg,fg,sz={'stamp':(RED,CREAM,190),'count':(YEL,INK,220)}.get(st,(YEL,INK,140))
 f=ImageFont.truetype(FB,sz);b=f.getbbox(txt);tw,th=b[2]-b[0],b[3]-b[1];px,py,m=56,46,40;w,h=tw+2*px,th+2*py
 im=Image.new('RGBA',(w+2*m,h+2*m),(0,0,0,0));outer=torn(R,w,h,m,12);inner=[(x+R.uniform(-2,2),y+R.uniform(-2,2)) for x,y in torn(R,w-14,h-14,m+7,8)]
 sh=Image.new('L',im.size,0);ImageDraw.Draw(sh).polygon([(x+8,y+12) for x,y in outer],fill=110);sh=sh.filter(ImageFilter.GaussianBlur(9))
 im.paste((0,0,0,255),(0,0),sh);d=ImageDraw.Draw(im);d.polygon(outer,fill=CREAM+(255,));d.polygon(inner,fill=bg+(255,))
 d.text((m+px-b[0],m+py-b[1]),txt,font=f,fill=fg)
 rot={'stamp':-5}.get(st,R.uniform(-4,4));return im.rotate(rot,expand=1,resample=Image.BICUBIC)
def wrap(t,f,mw):
 L=['']
 for w in t.split(' '):
  s=(L[-1]+' '+w).strip()
  if f.getlength(s)>mw and L[-1]:L.append(w)
  else:L[-1]=s
 return L
def capimg(t):
 f=ImageFont.truetype(FN,56);L=wrap(t,f,900);lh=74;im=Image.new('RGBA',(W,len(L)*lh+40),(0,0,0,0));d=ImageDraw.Draw(im)
 for i,l in enumerate(L):
  w=f.getlength(l);x=(W-w)/2;y=20+i*lh;d.rectangle([x-18,y-6,x+w+18,y+lh-10],fill=CREAM);d.text((x,y),l,font=f,fill=INK)
 return im
cuts=M['cuts'];t=INTRO;ev=[];aud=[]
for i,c in enumerate(cuts):
 c['im']=Image.open(get(c['img'],f'i{i}.png')).convert('RGB');a=get(c['aud'],f'a{i}.mp3');d=dur(a);aud.append((a,t))
 c['t0'],c['d']=t,d+PAD;t+=d+PAD
 S=[s.strip() for s in re.split(r'(?<=[.?!])\s+',c['cap']) if s.strip()];n=sum(map(len,S));x=c['t0'];c['caps']=[]
 for s in S:e=x+d*len(s)/n;c['caps'].append((x,e,capimg(s)));x=e
 K=[]
 for st,txt,an in c['kw']:
  k=c['tts'].find(an) if isinstance(an,str) else -1;fr=an if isinstance(an,(int,float)) else (k/len(c['tts']) if k>=0 else 0)
  K.append([st,txt,c['t0']+max(0,d*fr-0.15)]);ev.append(('thump' if st=='stamp' else 'tick',K[-1][2]))
 for j,k in enumerate(K):k+=[K[j+1][2]-0.05 if j+1<len(K) else c['t0']+c['d'],paper(k[1],k[0],i*10+j),i*10+j]
 c['K']=K;R=random.Random(i);c['edge']=jag(R,H//16+2,26)
T=t+OUTRO
def cover(im,z):s=max(W/im.width,H/im.height)*z;return im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
for c in cuts:c['big']=cover(c['im'],1.08)
def rip(prev,new,p,edge):
 # 찢긴 세로 가장자리가 오른쪽→왼쪽으로 지나가며 새 종이가 덮는다
 X=W*(1-eo(p));pts=[(X+edge[k],k*16) for k in range(len(edge))]
 poly=pts+[(W+40,H+40),(W+40,-40)];fr=prev.copy()
 sh=Image.new('L',(W,H),0);ImageDraw.Draw(sh).polygon([(x-18,y) for x,y in pts]+[(W+40,H+40),(W+40,-40)],fill=120);sh=sh.filter(ImageFilter.GaussianBlur(14))
 fr.paste((0,0,0),(0,0),sh);ImageDraw.Draw(fr).polygon([(x-9,y) for x,y in pts]+[(W+40,H+40),(W+40,-40)],fill=CREAM)
 m=Image.new('L',(W,H),0);ImageDraw.Draw(m).polygon(poly,fill=255);fr.paste(new,(0,0),m);return fr
fB=ImageFont.truetype(FB,250);fQ=ImageFont.truetype(FN,60);LG=paper('그란데?','stamp',999)
def logo(lt,q):
 fr=Image.new('RGB',(W,H),PAPER);s=1+0.25*(1-eo(lt/0.2));r=LG.resize((int(LG.width*s*1.3),int(LG.height*s*1.3)),Image.BICUBIC)
 if lt>0.05:fr.paste(r,((W-r.width)//2,H//2-160-r.height//2),r)
 if q and lt>0.4:
  d=ImageDraw.Draw(fr)
  for i,l in enumerate(wrap(q,fQ,900)):d.text(((W-fQ.getlength(l))/2,H//2+120+i*80),l,font=fQ,fill=INK)
 return fr
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','v.mp4'],stdin=subprocess.PIPE)
N=int(T*FPS);prev=None
for n in range(N):
 t=n/FPS
 if t<INTRO:fr=logo(t,M['title']);prev=fr;p.stdin.write(fr.tobytes());continue
 if t>=T-OUTRO:
  lt=t-(T-OUTRO);fr=logo(lt,None) if lt>=TR else rip(prev,logo(lt,None),lt/TR,cuts[0]['edge']);p.stdin.write(fr.tobytes());continue
 c=next(c for c in cuts if c['t0']<=t<c['t0']+c['d']);lt=t-c['t0'];i=cuts.index(c);pr=lt/c['d'];B=c['big']
 z=1.0+0.06*(pr if i%2==0 else 1-pr);cw=int(B.width/z);ch=int(cw*H/W)
 x0=(B.width-cw)//2;y0=(B.height-ch)//2;fr=B.crop((x0,y0,x0+cw,y0+ch)).resize((W,H),Image.BILINEAR)
 if lt<TR:fr=rip(prev,fr,lt/TR,c['edge'])
 for st,txt,a,b,im,sd in c['K']:
  if not(a<=t<b):continue
  k=t-a;out=cl((b-t)/0.2)
  if st=='count':
   m=re.search(r'[\d,]+',txt);v=int(m.group().replace(',',''));cur=int(v*eo(k/0.7));im=paper(txt.replace(m.group(),f'{cur:,}' if ',' in m.group() else str(cur)),'count',sd)
  e=eo(k/0.3);sc=(1.12-0.12*e) if st=='stamp' else 1.0;dy=int((1-e)*140+(1-out)*60)
  r=im if sc==1 else im.resize((int(im.width*sc),int(im.height*sc)),Image.BICUBIC)
  if out<1 or e<1:
   al=r.getchannel('A').point(lambda v,q=min(e*1.5,1)*out:int(v*q));r=r.copy();r.putalpha(al)
  cy=H*0.46 if st=='stamp' else 340;fr.paste(r,(int(W/2-r.width/2),int(cy-r.height/2)+dy),r)
 for a,b,im in c['caps']:
  if a<=t<b:fr.paste(im,(0,1480),im)
 prev=fr;p.stdin.write(fr.tobytes())
p.stdin.close();p.wait()
subprocess.run('sox -n thump.wav synth 0.35 sine 90:40 fade 0 0.35 0.3 gain -4 && sox -n tick.wav synth 0.12 pinknoise fade 0 0.12 0.1 highpass 1500 gain -16',shell=True,check=1)
ins=[];fl=[];src=aud+[(e+'.wav',s) for e,s in ev]
for k,(a,s) in enumerate(src):ins+=['-i',a];fl.append(f'[{k+1}:a]adelay=delays={int(s*1000)}:all=1[s{k}]')
fl.append(''.join(f'[s{k}]' for k in range(len(src)))+f'amix=inputs={len(src)}:normalize=0[a]')
subprocess.run(['ffmpeg','-y','-v','error','-i','v.mp4']+ins+['-filter_complex',';'.join(fl),'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(T),OUT],check=1)
print('done',OUT,round(T,1))
