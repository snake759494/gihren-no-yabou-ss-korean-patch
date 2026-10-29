VARS=[]
exec(open('route_bisect.py',encoding='utf8').read())
print('faction',to_faction()); e.run(60); e.cmd('save faction','SAVED'); e.shot('../shots/kf.png')
e.press(C,4,10); e.run(300)
for i in range(3): e.press(START,4,120)
for i in range(22): e.run(600)
e.cmd('save movie_end','SAVED')
fs=[]
for i in range(48):
    e.press(C,4,100)
    if i%3==2: f=f'../shots/k{i//3:02d}.png'; e.shot(f); fs.append(f)
e.cmd('save strat','SAVED')
grid(fs,'../shots/kg.png')
