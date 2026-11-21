W,H=160,128
g=[['"']*W for _ in range(H)]
def R(x0,x1,y0,y1,c):
    for y in range(max(0,y0),min(H-1,y1)+1):
        for x in range(max(0,x0),min(W-1,x1)+1):
            g[y][x]=c
# borders
R(0,1,0,127,'T'); R(0,159,0,1,'T'); R(156,159,0,127,'T')
# rails / south border
R(0,159,124,126,'H'); R(0,159,127,127,'f')
# ---------- creek ----------
R(42,159,36,37,'W')          # north wall face (south-facing stone)
R(42,43,36,127,'W')          # west lip
R(44,51,38,127,'~'); R(44,159,38,43,'~')
R(52,53,44,127,'W'); R(52,159,44,45,'W')
R(44,46,88,99,'g'); R(42,43,92,93,'s')   # secret shoal + stair
# ---------- roads & walks ----------
R(38,41,2,123,'.')           # west bank path (north part grove overwritten below)
R(38,159,34,35,'.')          # outer (north) walk
R(42,159,32,33,'"')          # verge
R(54,55,46,123,'.'); R(54,159,46,47,'.')   # inner walk
def road(x0,x1,y0,y1,rx0,rx1,ry0,ry1):
    R(x0,x1,y0,y1,'.'); R(rx0,rx1,ry0,ry1,'=')
road(38,159,24,31, 42,159,26,29)      # Parkway Blvd
road(54,159,60,67, 56,159,62,65)      # Philadelphia St
road(0,159,78,87, 0,159,80,85)        # Market St / Carlisle Ave
road(38,159,104,111, 42,159,106,109)  # King St
R(54,159,122,123,'.')                 # rail-side lane / platform
road(54,61,46,123, 56,59,48,123)      # Water St
road(80,87,46,123, 82,85,48,123)      # Beaver St
road(104,113,24,123, 106,111,26,123)  # George St
road(132,139,46,123, 134,137,48,123)  # Duke St
# restore creek-crossing structures
R(104,113,36,45,'B'); R(42,53,78,87,'B'); R(42,53,104,111,'B'); R(42,53,62,65,'B'); R(42,53,124,126,'H')
# road-end barriers
R(0,1,78,87,'x'); R(158,159,78,87,'x'); R(158,159,24,31,'x'); R(158,159,60,67,'x'); R(158,159,104,111,'x')
# ---------- FAIRGROUNDS ----------
R(2,35,2,75,'"')
R(36,37,2,77,'f'); R(36,37,63,64,'*')         # east fence + back gate
R(2,35,76,77,'f'); R(14,15,72,77,'*'); R(20,21,72,77,'*'); R(16,19,72,77,'m')  # main gate
R(2,15,3,15,'R'); R(2,7,16,19,'f'); R(8,15,16,19,'m')            # barns + pens
R(18,33,5,15,'E')                               # Memorial Hall
R(6,29,20,29,'G')                               # grandstand
cx,cy=17.5,42.5
for y in range(30,56):
    for x in range(2,34):
        o=((x-cx)/16.0)**2+((y-cy)/13.0)**2
        i=((x-cx)/12.0)**2+((y-cy)/9.0)**2
        if o<=1.0 and i>1.0: g[y][x]='o'
R(16,19,40,44,'*')                              # judges' stand
R(2,35,56,75,'m'); R(16,19,50,55,'m')           # midway + crossing
R(3,13,58,61,'#'); R(3,13,64,67,'#'); R(3,13,70,71,'#')
R(23,34,58,68,'#'); R(22,34,71,73,'#')
# ---------- PENN PARK ----------
R(2,35,88,121,'"')
R(2,37,88,89,'f'); R(16,19,88,89,'g'); R(36,37,88,121,'f'); R(36,37,106,109,'g'); R(0,37,122,123,'f')
R(16,19,90,121,'g'); R(2,35,104,107,'g')
R(13,22,100,109,'.'); R(16,19,102,106,'*')
R(4,11,92,99,'~'); R(24,31,92,98,'#'); R(30,35,113,119,'#')
R(2,7,114,120,'T'); R(6,7,116,117,'g'); R(4,5,116,117,'*')
# ---------- NORTH BAND ----------
R(38,41,2,21,'T'); R(40,40,10,21,'g'); R(39,40,8,9,'*')             # grove + secret glade
R(42,63,2,23,'.'); R(44,61,10,21,'X'); R(54,61,3,8,'#'); R(42,43,2,4,'*')
R(64,135,2,23,'+')
R(64,65,2,23,'f'); R(134,135,2,23,'f'); R(64,135,22,23,'f')
R(66,133,10,11,'^')
R(107,110,12,23,'g'); R(106,111,10,11,'s')
R(70,129,12,13,'g'); R(70,73,10,11,'s'); R(126,129,10,11,'s'); R(70,129,8,9,'g')
R(105,112,18,23,'*'); R(107,110,18,23,'g')
R(114,121,14,19,'L')
R(76,87,2,7,'g'); R(78,85,3,6,'+'); R(81,82,3,6,'*')
R(116,125,1,7,'V')
R(90,93,10,11,'*')
R(66,69,2,3,'*')
R(136,155,2,23,'"'); R(136,155,10,11,'^'); R(146,147,10,11,'s')
R(137,145,12,21,'#'); R(148,155,13,21,'#'); R(146,147,12,23,'g'); R(140,155,2,9,'.'); R(152,153,3,4,'*')
# ---------- DOWNTOWN ----------
R(62,79,48,57,'M'); R(62,79,58,59,'.'); R(60,61,48,59,'.')
R(88,103,48,59,'"'); R(90,101,48,59,'C')
R(114,131,48,59,'"'); R(116,129,48,59,'Y')
R(140,155,48,59,'"'); R(142,153,50,57,'F'); R(142,153,58,59,'.')
R(60,79,68,77,'#'); R(78,79,68,77,'a'); R(60,61,68,77,'.')
R(88,95,68,77,'#')
R(96,103,68,77,'p'); R(96,103,68,69,'T'); R(98,101,68,69,'p')
R(114,121,68,77,'p'); R(114,121,68,69,'T'); R(116,119,68,69,'p')
R(122,131,68,77,'K'); R(140,155,68,77,'Q')
for (a,b) in [(60,79),(88,95),(122,131),(140,155)]:
    R(a,b,88,90,'"'); R(a,b,91,92,'a')
R(62,71,93,99,'#'); R(62,71,100,103,'k'); R(72,79,93,103,'#'); R(60,61,93,103,'"')
R(88,95,93,103,'#')
R(96,103,88,95,'p'); R(96,103,96,103,'#')
R(114,121,88,95,'p'); R(114,121,96,103,'#')
R(122,131,93,103,'P')
R(140,155,93,103,'h')
R(60,79,112,121,'"'); R(62,79,112,121,'h')
R(88,103,112,121,'"'); R(90,101,112,121,'C')
R(114,131,112,121,'"'); R(114,129,112,121,'D')
R(140,155,112,121,'h')
R(121,122,122,123,'S')
R(154,155,88,90,'*')    # SE alley secret
for y in range(0,128):
    if g[y][157] not in '=x~H' and not (122<=y<=123):
        for x in range(156,160):
            if g[y][x] not in '~H': g[y][x]='T'
R(156,159,122,123,'T')
# ---------- downsample ----------
pri='S*MCYFQKPDVLGERXh#B^~WHoxfapkTsg=.m+"'
def pick(cells):
    return min(cells,key=lambda c: pri.index(c) if c in pri else 99)
out=[]
for cy2 in range(H//2):
    row=''
    for cx2 in range(W//2):
        cells=[g[cy2*2+dy][cx2*2+dx] for dy in (0,1) for dx in (0,1)]
        row+=pick(cells)
    out.append(row)
h1='x=    '+''.join(str((i*2)//100) if i%5==0 else ' ' for i in range(80))
h2='      '+''.join(str((i*2)//10%10) if i%5==0 else ' ' for i in range(80))
h3='      '+''.join(str((i*2)%10) if i%5==0 else ' ' for i in range(80))
print(h1);print(h2);print(h3)
for i,r in enumerate(out):
    print('y%3d  %s'%(i*2,r))

import collections
walk=set('.="gpakmBSo+s*')
start=(121,122)
seen={start};dq=collections.deque([start])
while dq:
    x,y=dq.popleft()
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx,ny=x+dx,y+dy
        if 0<=nx<W and 0<=ny<H and (nx,ny) not in seen and g[ny][nx] in walk:
            seen.add((nx,ny));dq.append((nx,ny))
pts={'market apron':(70,58),'square':(108,82),'fair midway':(17,60),'grandstand front':(17,31),'judges stand':(17,45),
'memorial hall front':(25,16),'barn yard':(10,17),'penn park monument':(17,101),'hobo camp':(4,116),'park pond side':(13,95),
'cemetery gate':(108,22),'soldiers circle':(80,5),'chapel front':(120,8),'vault':(91,11),'gatehouse front':(117,20),
'NE overlook':(150,5),'factory yard':(50,22),'factory back secret':(42,3),'grove secret':(39,8),'shoal secret':(45,95),
'SE alley secret':(154,89),'fair back gate':(36,63),'theater front':(126,104),'courthouse front':(147,78),'hotel front':(122,60)}
for k,(x,y) in pts.items(): print(k, (x,y), g[y][x], 'OK' if (x,y) in seen else 'UNREACHABLE')
import json
json.dump([''.join(r) for r in g],open('grid.json','w'))
