TAG=globals().get('TAG','x')
e.cmd('save space','SAVED')
k=0
for d,n in ((DOWN,4),(LEFT,4),(UP,3),(RIGHT,8)):
    for i in range(n):
        e.press(d,40,40); e.shot(f'../shots/w_{TAG}{k:02d}.png'); k+=1
print('shots',k)
