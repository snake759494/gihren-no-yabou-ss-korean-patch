import os
os.makedirs('../shots',exist_ok=True)
TAG=globals().get('TAG','x')
exec(open('r_strat.py',encoding='utf8').read())
e.press(R,4,90); e.shot(f'../shots/sp_{TAG}0.png')
for i in range(4):
    e.press(DOWN,30,30); e.shot(f'../shots/sp_{TAG}{i+1}.png')
