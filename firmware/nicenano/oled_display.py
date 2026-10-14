"""Owner-approved Clawdy animation, optional 128x64 SSD1306-compatible OLED."""
import busio, microcontroller
from provider_icons import OPENAI, GEMINI
addresses=[]
error=None
try:
 i=busio.I2C(microcontroller.pin.P0_20,microcontroller.pin.P0_22,frequency=100000)
 if not i.try_lock(): raise RuntimeError("I2C busy during setup")
 addresses=i.scan()
 for a in addresses:
  if a in (60,61):
   i.writeto(a,bytes([0,174,213,128,168,63,211,0,64,141,20,32,0,161,200,218,18,129,127,217,241,219,64,164,166,175]))
   i.writeto(a,bytes([0,33,0,127,34,0,7]))
   # 128x64 SSD1306 page-format framebuffer.
   frame=bytearray(1024)
   def pixel(x,y):
    if 0 <= x < 128 and 0 <= y < 64:
     frame[x+(y//8)*128] |= 1 << (y%8)
   def line(x0,y0,x1,y1):
    dx=abs(x1-x0); sx=1 if x0<x1 else -1
    dy=-abs(y1-y0); sy=1 if y0<y1 else -1
    err=dx+dy
    while True:
     pixel(x0,y0)
     if x0==x1 and y0==y1: break
     e=2*err
     if e>=dy: err+=dy; x0+=sx
     if e<=dx: err+=dx; y0+=sy
   # Clawdy drawing primitives.
   def rect(x,y,w,h,on=True):
    for yy in range(y,y+h):
     for xx in range(x,x+w):
      if on: pixel(xx,yy)
      elif 0<=xx<128 and 0<=yy<64:
       frame[xx+(yy//8)*128] &= 255 ^ (1 << (yy%8))
   # Front projection of the 45 mm model; uniform scale, four quarter-height legs.
   rect(7,40,4,9)
   rect(15,40,4,9)
   rect(31,40,4,9)
   rect(39,40,4,9)
   rect(7,31,36,9)
   rect(3,23,44,8)
   rect(7,14,36,9)
   rect(11,23,4,4,False)
   rect(35,23,4,4,False)
   line(49,10,49,55)
   for page in range(8):
    i.writeto(a,bytes([64])+frame[page*128:(page+1)*128])
 i.unlock()
except Exception as e: error=str(e)
# Small readable 5x7 capitals for status comments.
font={
"A":[14,17,17,31,17,17,17],"C":[14,17,16,16,16,17,14],
"D":[30,17,17,17,17,17,30],"E":[31,16,16,30,16,16,31],
"F":[31,16,16,30,16,16,16],"G":[14,17,16,23,17,17,15],"H":[17,17,17,31,17,17,17],
"I":[14,4,4,4,4,4,14],"K":[17,18,20,24,20,18,17],
"L":[16,16,16,16,16,16,31],"N":[17,25,25,21,19,19,17],
"O":[14,17,17,17,17,17,14],"R":[30,17,17,30,20,18,17],
"S":[15,16,16,14,1,1,30],"T":[31,4,4,4,4,4,4],
"U":[17,17,17,17,17,17,14],"W":[17,17,17,21,21,21,10],
"B":[30,17,17,30,17,17,30],"P":[30,17,17,30,16,16,16],"Y":[17,17,10,4,4,4,4],"!":[4,4,4,4,4,0,4]," ":[0]*7}
font.update({
"0":[14,17,19,21,25,17,14],"1":[4,12,4,4,4,4,14],
"2":[14,17,1,2,4,8,31],"3":[30,1,1,14,1,1,30],
"4":[2,6,10,18,31,2,2],"5":[31,16,16,30,1,1,30],
"6":[14,16,16,30,17,17,14],"7":[31,1,2,4,8,8,8],
"8":[14,17,17,14,17,17,14],"9":[14,17,17,15,1,1,14],
"-":[0,0,0,31,0,0,0],"M":[17,27,21,21,17,17,17],
"?":[14,17,1,2,4,0,4],".":[0,0,0,0,0,0,4]})
font.update({
"l":[12,4,4,4,4,4,14],"a":[0,0,14,1,15,17,15],
"w":[0,0,17,17,21,21,10],"d":[1,1,15,17,17,17,15],
"y":[0,0,17,17,15,1,14]})
def text_at(text,x,y,scale=1):
 for index,ch in enumerate(text):
  for row,bits in enumerate(font[ch]):
   for col in range(5):
    if bits & (1 << (4-col)):
     for oy in range(scale):
      for ox in range(scale): pixel(x+(index*6+col)*scale+ox,y+row*scale+oy)
def mascot(c,tick,compact=False):
 # Rigid translation preserves the 45 mm figure's proportions.
 dx=0
 dy=0
 if c=="Y": dy=(0,-1,0,1)[tick%4]
 elif c=="G": dy=(0,-2,-4,-2,0,0,0,0)[tick%8]
 elif c=="R": dx=(-1,1,-1,1,0,0,0,0)[tick%8]
 def shape(x,y,w,h,on=True):
  if compact:
   left=round(6+x*.75); top=round(16+y*.75)
   right=round(6+(x+w)*.75); bottom=round(16+(y+h)*.75)
   rect(left,top,max(1,right-left),max(1,bottom-top),on)
  else: rect(x,y,w,h,on)
 def effect_line(x0,y0,x1,y1):
  if compact: line(round(6+x0*.75),round(16+y0*.75),round(6+x1*.75),round(16+y1*.75))
  else: line(x0,y0,x1,y1)
 def block(x,y,w,h,on=True): shape(x+dx,y+dy,w,h,on)
 for x in (7,15,31,39): block(x,40,4,9)
 block(7,31,36,9); block(3,23,44,8); block(7,14,36,9)
 if c=="R":
  # Dark diagonal crosses cut into the lit face; move with its shake.
  for x in (11,35):
   for offset in range(5):
    block(x+offset,23+offset,1,1,False)
    block(x+4-offset,23+offset,1,1,False)
 elif c=="G":
  for x in (11,35):
   block(x,24,4,3,False)
   block(x+1,23,2,1,False)
 elif tick%20==19:
  block(11,25,4,1,False); block(35,25,4,1,False)
 else:
  gaze=(-1,0,1,0)[(tick//3)%4] if c=="Y" else 0
  block(11+gaze,23,4,4,False); block(35+gaze,23,4,4,False)
 if c=="Y":
  for dot in range(tick%4): rect(62+dot*8,51,3,3)
 elif c=="R" and tick%4<2:
  shape(23,3,2,5); shape(23,10,2,2)
 elif c=="G" and tick%8 in (1,2,3):
  effect_line(3,7,3,11); effect_line(1,9,5,9)
  effect_line(43,4,43,8); effect_line(41,6,45,6)
# Each pair fits the 12-character right-column limit.
PHRASES={
 "Y":(("BRAIN GO","BRRR..."),("COOKING UP","SOME CODE"),("HOLD MY","COFFEE"),("THINKING","NO SMOKE YET")),
 "G":(("NAILED IT!","SNACK TIME"),("JOB DONE","TINY FLEX"),("ALL DONE!","YOU ARE UP"),("CODE SERVED","BON APPETIT")),
 "R":(("OH CRUMBS!","SEND HELP"),("BUG PARTY","NOT INVITED"),("PLOT TWIST","IT BROKE"),("WELL THAT","WAS AWKWARD")),
 "B":(("YOUR TURN!","HUMAN!"),("NEED A NOD","HUMAN!"),("BOOP TO","PROCEED"),("WAITING ON","YOUR MAGIC")),
 "O":(("ON A BREAK","GOT SNACKS?"),("NAP MODE","DO NOT BOOP"),("NO TASKS","BIG CHILL"),("READY WHEN","YOU ARE")),
 "offline":(("HELLO?","ANYONE HOME?"),("LOST MY","HUMAN AGAIN"),("SIGNAL","WENT WALKIES"),("COME BACK","GOT PIXELS"))
}
PHRASE_SECONDS=5
font.update({"J":[7,2,2,2,18,18,12],"Q":[14,17,17,17,21,18,13],
 "V":[17,17,17,17,17,10,4],"X":[17,17,10,4,10,17,17],"Z":[31,1,2,4,8,16,31]})
def status_lines(mode,connected,phrase_index):
 options=PHRASES[mode if connected else "offline"]
 return options[phrase_index % len(options)]
def active_provider(mask,slot):
 options=[bit for bit in (1,2,4,8) if mask & bit]
 return options[slot % len(options)] if options else 0

def provider_drawing(mode,tick,connected,mask,slot):
 provider=active_provider(mask,slot) if connected else 0
 if provider in (0,1):
  mascot(mode if connected else "O",tick,compact=True)
  return
 if provider in (2,4):
  bitmap=OPENAI if provider==2 else GEMINI
  # Keep the provider mark intact; animate a small progress dot below it.
  for y in range(30):
   row=bitmap[min(35,(y*36+18)//30)]
   for x in range(30):
    if row & (1<<min(35,(x*36+18)//30)): pixel(9+x,18+y)
  label="CODEX" if provider==2 else "GEMINI"
 else:
  # Unknown provider / Cursor: neutral symbol, no invented model attribution.
  rect(16,23,17,17)
  rect(18,25,13,13,False)
  text_at("?",22,28)
  label="OTHER"
 text_at(label,(49-(len(label)*6-1))//2,51)
 if mode=="Y": pixel(9+(tick%30),60)
def comment(c,tick=0,connected=True,session_count=None,phrase_index=0,provider_mask=0):
 global error
 if not any(a in (60,61) for a in addresses): return
 try:
  for index in range(1024): frame[index]=0
  provider_drawing(c,tick,connected,provider_mask,phrase_index)
  line(49,10,49,55)
  lines=status_lines(c,connected,phrase_index)
  text_at("Clawdy",56,0,scale=2)
  for text,y in ((lines[0],24),(lines[1],38)):
   text_at(text,56,y)
  # WIP sits in the top yellow band of the two-colour OLED.
  count = str(session_count) if connected and session_count is not None else "--"
  footer = count + " WIP"
  text_at(footer,(49-(len(footer)*6-1))//2,0)
  if not i.try_lock(): return
  try:
   for addr in addresses:
    if addr in (60,61):
     i.writeto(addr,bytes([0,33,0,127,34,0,7]))
     for page in range(8): i.writeto(addr,bytes([64])+frame[page*128:(page+1)*128])
  finally: i.unlock()
 except Exception as e: error=str(e)

_tick=0
_next_frame=0
_phrase_status=None
_phrase_started=0
def update(now,mode,connected,session_count=None,provider_mask=0):
 global _tick,_next_frame,_phrase_status,_phrase_started
 status=mode if connected else "offline"
 if status!=_phrase_status:
  _phrase_status=status
  _phrase_started=now
  _next_frame=now
 if now>=_next_frame:
  phrase_index=int((now-_phrase_started)/PHRASE_SECONDS)
  comment(mode,_tick,connected,session_count,phrase_index,provider_mask=provider_mask)
  _tick+=1
  _next_frame=now+.2
