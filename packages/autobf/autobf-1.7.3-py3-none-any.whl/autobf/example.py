import autobf as bf
Xc,Yc=bf.Xc,bf.Yc
def goEnemy():
    global isGetMission
    bf.zoom2max()
    if bf.checkColorByXY(x=553,y=656):
        #背對問號
        bf.keyDown('left',0.5)
        bf.slide('w',2);bf.slide('a',2)
        bf.close2Color(color=(241, 234, 41))
        if isGetMission:bf.getMission(p1=(1400,510))
        isGetMission = False
        bf.slide('d',5); bf.slide('s',12)
    else:
        #面向問號
        bf.slide('w',4);bf.slide('d',1)
        if bf.checkColorByXY(x=1124,y=93):
            bf.slide('w',3);bf.slide('d',1)
            bf.close2Color(color=(241, 234, 41))
            bf.getMission(p1=(1400,510))
            print('1')
            bf.slide('a',5);bf.slide('s',3);bf.slide('a',9)
        elif bf.checkColorByXY(x=1132,y=96):
            bf.slide('w',3);bf.slide('d',1)
            bf.close2Color(color=(241, 234, 41))
            bf.getMission(p1=(1400,510))
            print('2')
            bf.slide('a',5);bf.slide('s',2);bf.slide('a',8)
        else:
            bf.close2Color(color=(241, 234, 41))
            bf.getMission(p1=(1400,510))
            bf.slide('a',12)
            bf.slide('w',2)
            print('3')
def getXYDist(x,y,color):#1590,918
    pix = np.array(pyautogui.pixel(x,y))
    dist = np.linalg.norm(pix-np.array(color),axis=-1)
    print(f"於({x},{y})處 pix={pix}和目標顏色{color}距離={dist}")
    return dist

def fight():
    for i in range(33):
        print('fight:',i)
        bf.instinctOn()
        time.sleep(0.6)
        bf.shotEnemy(a='', b='v', c='')
        if bf.aimEnemy():
            if bf.getXYDist(1590,918,(180,180,180))>50:
                bf.press('v')
            else:bf.press('4');bf.click();bf.press('2')
        press('e')
        for j in range(150):bf.click()
        if bf.isComplete(targetImgPath='goal.png', p1=(740,596)):
            return True
    return False
    
isGetMission = False
def work():
    global isGetMission
    while True:
        bf.reset()
        if bf.getXYDist(925,962,(131, 226, 247))>30:bf.press('2')
        goEnemy()
        isGetMission = fight()
        
        
if __name__ == '__main__':
    bf.click(Xc,Yc)
    bf.zoom2max()
#     bf.click(bf.Xc,bf.wYc)
#     work()