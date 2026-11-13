import os,json,http.client as H
from urllib.parse import urlparse
V=dict(P=100,N=320,B=330,R=500,Q=900,K=20000)
T={}
for p in V:
 t=[0]*120
 for r in range(8):
  for c in range(8):
   m=min(r,7-r)+min(c,7-c);x=V[p]
   if p=='P':x+=(6-r)*7+(c in(3,4))*(7-r)*4
   if p=='N':x+=m*9-(r==7)*15
   if p=='B':x+=m*5
   if p=='R':x+=(r==1)*20+(c in(3,4))*5
   if p=='Q':x+=m*2
   if p=='K':x+=(r==7)*20+(r==7)*(c in(1,2,6))*20-m*4*(r<6)
   t[21+c+10*r]=x
 T[p]=t
Z=(-10,-1,1,10);X=(-11,-9,9,11)
D=dict(P=(-10,-20,-11,-9),N=(-21,-19,-12,-8,8,12,19,21),B=X,R=Z,Q=Z+X,K=Z+X)
def gen(b):
 for i,p in enumerate(b):
  if p.isupper():
   for d in D[p]:
    j=i+d
    while 1:
     q=b[j]
     if q.isspace()or q.isupper():break
     if p=='P':
      if d%10==0 and q!='.':break
      if d==-20 and(i<81 or b[i-10]!='.'):break
      if d%10 and q=='.':break
     yield i,j
     if p in'PNK'or q.islower():break
     j+=d
def rot(b):return b[::-1].swapcase()
def ev(b):return sum(T[p][i]if p.isupper()else-T[p.upper()][119-i]for i,p in enumerate(b)if p.isalpha())
def chk(b):
 f=rot(b);return any(f[j]=='k'for i,j in gen(f))
class A(Exception):pass
TT={};N=0;LIM=0
def S(b,sc,d,a,be,ply,nm=1):
 global N
 N+=1
 if N>LIM:raise A
 e=TT.get(b);mv=None
 if e:
  if e[0]>=d and(e[1]==0 or e[1]==1 and e[2]>=be or e[1]==2 and e[2]<=a):return e[2]
  mv=e[3]
 a0=a;best=-99999
 if d<=0:
  best=sc
  if best>=be:return best
  a=max(a,best)
 elif nm and d>2 and sc>=be:
  v=-S(rot(b),-sc,d-3,-be,-be+1,ply+1,0)
  if v>=be:return v
 L=[]
 for i,j in gen(b):
  q=b[j]
  if q=='k':return 29000
  if d<=0 and q=='.':continue
  s=T[b[i]][j]-T[b[i]][i]
  if q!='.':s+=T[q.upper()][119-j]
  pr=b[i]=='P'and j<30
  if pr:s+=T['Q'][j]-T['P'][j]
  L.append((((i,j)==mv)*9999+s,i,j,pr))
 L.sort(reverse=1)
 bm=None;n=0
 for s,i,j,pr in L:
  nb=list(b);nb[j]='Q'if pr else b[i];nb[i]='.'
  sc2=sc+s-((i,j)==mv)*9999
  v=-S(rot(''.join(nb)),-sc2,d-1,-be,-a,ply+1)
  n+=1
  if v>best:best=v;bm=(i,j)
  if v>a:a=v
  if a>=be:break
 if d>0 and best<-28000:
  best=-29000+ply if chk(b)else 0
 TT[b]=(d,0 if a0<best<be else 1 if best>=be else 2,best,bm)
 return best
def parse(fen):
 f=fen.split();b=' '*20
 for row in f[0].split('/'):
  b+=' '+''.join('.'*int(c)if c.isdigit()else c for c in row)+' '
 b+=' '*20
 return b,f[1]=='b'
def sq(s,fl):
 i=21+ord(s[0])-97+10*(8-int(s[1]));return 119-i if fl else i
def pick(fen,legal,seen,bud):
 global N,LIM
 b,fl=parse(fen)
 if fl:b=rot(b)
 R=[]
 for u in legal:
  i=sq(u[:2],fl);j=sq(u[2:4],fl);p=b[i];nb=list(b);nb[j]=u[4].upper()if len(u)>4 else p;nb[i]='.'
  if p=='K'and abs(j-i)==2:
   k=(i+3,i+1)if j>i else(i-4,i-1);nb[k[0]]='.';nb[k[1]]='R'
  if p=='P'and abs(j-i)in(9,11)and b[j]=='.':nb[j+10]='.'
  c=rot(''.join(nb));R.append((u,c,ev(c)))
 best=R[0][0];LIM=bud;N=0
 try:
  for d in range(1,30):
   a=-99999;cur=[];bk=0
   for k,(u,c,e)in enumerate(R):
    v=0 if c in seen else-S(c,e,d-1,-99999,-a,1)
    cur.append((v,k))
    if v>a:a=v;bk=k
   R=[R[bk]]+[R[k]for v,k in sorted(cur,reverse=1)if k!=bk];best=R[0][0]
   if a>20000:break
 except A:pass
 for u,c,e in R:
  if u==best:seen.add(c);break
 return best
def main():
 u=urlparse(os.environ['MAKEFUN_ENV_URL']);c=H.HTTPConnection(u.hostname,u.port)
 def post(p,b):
  c.request('POST',p,json.dumps(b),{'content-type':'application/json'});return json.loads(c.getresponse().read())
 g=post('/game',{});cur=None;seen=set()
 while g.get('status')!='done':
  if g['status']=='your_move':
   if g['game']!=cur:cur=g['game'];seen=set();TT.clear()
   g=post('/move',{'game':cur,'move':pick(g['fen'],g['legal_moves'],seen,BUD)})
  else:g=post('/game',{})
BUD=100000
main()
