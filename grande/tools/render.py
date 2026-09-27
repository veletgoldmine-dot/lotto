import json,sys,re,subprocess,urllib.request
from PIL import Image,ImageDraw,ImageFont
M=json.load(open(sys.argv[1]));OUT=sys.argv[2]
W,H,FPS=1080,1920,30;PAD=0.2;INTRO=1.3;OUTRO=1.2
PAPER=(226,221,208);INK=(18,18,18);YEL=(255,212,0);RED=(210,36,36)
FB,FN='BlackHanSans.ttf','Nanum.ttf'
def get(u,p):urllib.request.urlretrieve(u,p);return p
def cl(x):return max(0.,min(1.,x))
def eo(x):x=cl(x);return 1-(1-x)**3
def bk(x):x=cl(x);c=1.9;return 1+(c+1)*(x-1)**3+c*(x-1)**2
def dur(p):return float(subprocess.check_output(['ffprobe','-v','0','-show_entries','format=duration','-of','csv=p=0',p]))
def tag(txt,st):
 f=ImageFont.truetype(FB,{'stamp':210,'count':230}.get(st,150));b=f.getbbox(txt);tw,th=b[2]-b[0],b[3]-b[1];p=40
 im=Image.new('RGBA',(tw+2*p,th+2*p),(0,0,0,0));d=ImageDraw.Draw(im)
 if st=='stamp':
  d.rectangle([6,6,im.width-7,im.height-7],outline=RED,width=12);d.text((p-b[0],p-b[1]),txt,font=f,fill=RED);return im.rotate(8,expand=1,resample=Image.BICUBIC)
 if st=='count':
  d.rectangle([0,int(im.height*.55),im.width,im.height-10],fill=YEL);d.text((p-b[0],p-b[1]),txt,font=f,fill=INK,stroke_width=6,stroke_fill=(250,248,240));return im
 d.rectangle([0,0,im.width,im.height],fill=YEL);d.rectangle([0,0,im.width-1,im.height-1],outline=INK,width=6);d.text((p-b[0],p-b[1]),txt,font=f,fill=INK);return im.rotate(-3,expand=1,resample=Image.BICUBIC)
def wrap(t,f,mw):
 L=[''];
 for w in t.split(' '):
  s=(L[-1]+' '+w).strip()
  if f.getlength(s)>mw and L[-1]:L.append(w)
  else:L[-1]=s
 return L
def capimg(t):
 f=ImageFont.truetype(FN,56);L=wrap(t,f,900);lh=74;im=Image.new('RGBA',(W,len(L)*lh+40),(0,0,0,0));d=ImageDraw.Draw(im)
 for i,l in enumerate(L):
  w=f.getlength(l);x=(W-w)/2;y=20+i*lh;d.rectangle([x-18,y-6,x+w+18,y+lh-10],fill=(250,248,240));d.text((x,y),l,font=f,fill=INK)
 return im
cuts=M['cuts'];t=INTRO;ev=[];aud=[]
for i,c in enumerate(cuts):
 c['im']=Image.open(get(c['img'],f'i{i}.png')).convert('RGB');a=get(c['aud'],f'a{i}.mp3');d=dur(a);aud.append((a,t))
 c['t0'],c['d']=t,d+PAD;t+=d+PAD
 S=[s.strip() for s in re.split(r'(?<=[.?!])\s+',c['cap']) if s.strip()];n=sum(map(len,S));x=c['t0']
 c['caps']=[]
 for s in S:e=x+d*len(s)/n;c['caps'].append((x,e,capimg(s)));x=e
 K=[]
 for st,txt,an in c['kw']:
  k=c['tts'].find(an) if isinstance(an,str) else -1;fr=an if isinstance(an,(int,float)) else (k/len(c['tts']) if k>=0 else 0)
  K.append([st,txt,c['t0']+max(0,d*fr-0.15)]);ev.append(('thump' if st=='stamp' else 'tick',K[-1][2]))
 for j,k in enumerate(K):k.append(K[j+1][2]-0.05 if j+1<len(K) else c['t0']+c['d']);k.append(tag(k[1],k[0]) if k[0]!='count' else None)
 c['K']=K
T=t+OUTRO
def cover(im,z):
 s=max(W/im.width,H/im.height)*z;return im.resize((int(im.width*s),int(im.height*s)),Image.BILINEAR)
for i,c in enumerate(cuts):c['big']=cover(c['im'],1.12)
fB=ImageFont.truetype(FB,250);fQ=ImageFont.truetype(FN,60)
def logo(fr,lt,q):
 d=ImageDraw.Draw(fr);s='그란데?';b=fB.getbbox(s);x=(W-(b[2]-b[0]))/2;y=H/2-200;ww=(b[2]-b[0]+60)*eo(lt/0.35)
 d.rectangle([x-30,y+120,x-30+ww,y+250],fill=YEL);
 if lt>0.1:d.text((x-b[0],y-b[1]),s,font=fB,fill=INK)
 if q and lt>0.45:
  for i,l in enumerate(wrap(q,fQ,900)):d.text(((W-fQ.getlength(l))/2,y+340+i*80),l,font=fQ,fill=INK)
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','v.mp4'],stdin=subprocess.PIPE)
N=int(T*FPS);prev=None
for n in range(N):
 t=n/FPS
 if t<INTRO or t>=T-OUTRO:
  fr=Image.new('RGB',(W,H),PAPER);logo(fr,t if t<INTRO else t-(T-OUTRO),M['title'] if t<INTRO else None);p.stdin.write(fr.tobytes());continue
 c=next(c for c in cuts if c['t0']<=t<c['t0']+c['d']);lt=t-c['t0'];i=cuts.index(c);pr=lt/c['d'];B=c['big']
 cw=int(B.width*(1.0+0.07*(pr if i%2==0 else 1-pr))/1.12);ch=int(cw*H/W);j=(n//3)%3-1
 x0=(B.width-cw)//2+j*3+int((pr-.5)*20*(1 if i%2 else -1));y0=(B.height-ch)//2+j*2
 fr=B.crop((x0,y0,x0+cw,y0+ch)).resize((W,H),Image.BILINEAR)
 if lt<0.3 and prev is not None:
  o=int(W*(1-eo(lt/0.3)));base=prev.copy();base.paste(fr,(o,0));fr=base
 sh=0
 for st,txt,a,b,im in c['K']:
  if not(a<=t<b):continue
  k=t-a;out=cl((b-t)/0.15)
  if st=='count':
   m=re.search(r'[\d,]+',txt);v=int(m.group().replace(',',''));cur=int(v*eo(k/0.6));im=tag(txt.replace(m.group(),f'{cur:,}' if ',' in m.group() else str(cur)),'count');sc=bk(k/0.25)*out
  elif st=='stamp':sc=(1+1.3*(1-eo(k/0.18)))*out;sh=int(18*(1-cl(k/0.35)))
  else:sc=bk(k/0.28)*out
  if sc<=0.02:continue
  r=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BILINEAR);cy=H*0.47 if st=='stamp' else 330
  fr.paste(r,(int(W/2-r.width/2),int(cy-r.height/2)),r)
  if st=='stamp' and k<0.07:fr=Image.blend(fr,Image.new('RGB',(W,H),'white'),0.6)
 for a,b,im in c['caps']:
  if a<=t<b:fr.paste(im,(0,1480),im)
 if sh:fr=fr.transform((W,H),Image.AFFINE,(1,0,sh*((n%2)*2-1),0,1,sh*(((n//2)%2)*2-1)))
 prev=fr;p.stdin.write(fr.tobytes())
p.stdin.close();p.wait()
subprocess.run('sox -n thump.wav synth 0.4 sine 70:30 fade 0 0.4 0.35 gain -1 && sox -n tick.wav synth 0.07 sine 1400 fade 0 0.07 0.06 gain -14',shell=True,check=1)
ins=[];fl=[];src=aud+[(e+'.wav',s) for e,s in ev]
for k,(a,s) in enumerate(src):ins+=['-i',a];fl.append(f'[{k+1}:a]adelay=delays={int(s*1000)}:all=1[s{k}]')
fl.append(''.join(f'[s{k}]' for k in range(len(src)))+f'amix=inputs={len(src)}:normalize=0[a]')
subprocess.run(['ffmpeg','-y','-v','error','-i','v.mp4']+ins+['-filter_complex',';'.join(fl),'-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(T),OUT],check=1)
print('done',OUT,round(T,1))
