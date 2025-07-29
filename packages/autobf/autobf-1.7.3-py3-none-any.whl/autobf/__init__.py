import numpy as np
import pyautogui
import pydirectinput
import time
# import keyboard
import cv2
import pygetwindow as gw
Xc=int(1920/2)
Yc=int(1080/2)
import threading
import pyperclip
timeUp = False
mode = 0
def _timer(hours, minutes=0, seconds=0):
    global timeUp
    total_seconds = hours * 3600 + minutes * 60 + seconds
    while total_seconds:
        hrs, remainder = divmod(total_seconds, 3600)
        mins, secs = divmod(remainder, 60)
        print(f"{hrs:02d}:{mins:02d}:{secs:02d}", end="\r")
        time.sleep(1)
        total_seconds -= 1
    print("時間到！")
    timeUp = True
    
def timerStart(hours, minutes=0, seconds=0):
    global timeUp
    timeUp = False
    timeThread=threading.Thread(target=_timer,args=(hours,minutes,seconds,))
    timeThread.start()
 
def get_window_size(title='Roblox'):
    '''
    獲取所有符合標題的視窗
    '''
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        print(f"找不到標題為 '{title}' 的視窗。")
        return
    for window in windows:
        if window.title == title:
            width, height = window.width, window.height
#             print(f"視窗 '{window.title}' 的大小為: {width}x{height}")
            return width, height
        
def detectMode():
    global mode
    '''
    mode=1 全螢幕
    mode=2 左大右小
    '''
    try:
        w,h=get_window_size()
        if w==1936 and h==1048: mode=1;setCenterXY(int(1920/2),int(1080/2));return 1
        if w==1294 and h==1039: mode=2;setCenterXY();return 2
        mode = 0
        print('''非預設視窗大小：
        1.設定螢幕解析度為 1920x1080
        2.底下為兩種可接受之roblox視窗大小：
           mode=1:全螢幕，roblox視窗 1294x1039
           mode=2:螢幕左大右小，roblox視窗 1294x1039(左)，python IDE視窗放右邊 
    ''')
    except:print('要先開啟roblox...')
    return 0

def setCenterXY(x=639,y=530):#預設值為螢幕左大右小
    global Xc,Yc
    Xc=x;Yc=y
    
def row(x,y,dx=0,dy=0,button='right',delay=0.2):
    '''
    在 (x,y) 處，按下滑鼠 button 鍵後拖曳 dx,dy
    '''
    pydirectinput.mouseDown(x,y,button=button);time.sleep(delay)
    pydirectinput.moveTo(x+dx,y+dy);    time.sleep(delay)
    pydirectinput.mouseUp(button=button)

def zoom(scroll=-200,repeat=1):
    '''
    使用滑鼠滾輪縮放
    scroll:捲動方向 正值為往前捲，負值為往後捲
    repeat:重覆捲動次數
    '''
    for i in range(repeat):    pyautogui.scroll(scroll)
    
def zoom2max(scroll=-500,repeat=10,dy=100):
    '''
    拉最遠並把視角放到頭頂
    '''
    global Xc,Yc
    for i in range(repeat):    pyautogui.scroll(scroll)
    row(Xc,Yc,dy=dy)
#     row(Xc,Yc,dy=50)
def checkAndClick(x,y,color,tolorance=30,double=False):
    pydirectinput.moveTo(x,y)
    while True:
        a=np.array(pyautogui.pixel(x,y))
        dist = np.linalg.norm(a-np.array(color), axis=-1)
        if dist<=tolorance:
            print(f"於({x},{y})執行點擊，dist={dist}")
            break
    if double: pydirectinput.doubleClick()
    else:      pydirectinput.click()
    
def click(x=None,y=None,repeat=1,delay=0,center=False):
    '''
    點擊 x,y 重複 repeat 次，每次延遲 delay 秒
    '''
    if center:x=Xc;y=Yc
    try:
        if x==None:
            for i in range(repeat):pydirectinput.click();time.sleep(delay)
        else:
            for i in range(repeat):pydirectinput.click(x,y);pydirectinput.click(x+1,y+1);time.sleep(delay)
    except:print("except while click()...")
    
def slide(key='down',repeat=1):
    '''
    按q滑行，由 key 指定方向， 重複repeat次
    '''
    for i in range(repeat):
        pydirectinput.keyDown(key)
        pydirectinput.press('q')
        pydirectinput.keyUp(key)
        
def jumpSlide(key,j_repeat,s_repeat):
    '''
    跳躍滑行
    '''
    press('space',j_repeat)
    slide(key,s_repeat)
    
def keyDown(key,duration=2):
    '''
    按下 key , 等待 duration 秒後放開
    '''
    pydirectinput.keyDown(key);time.sleep(duration);pydirectinput.keyUp(key)
    
def press(key,repeat=1,delay=0):
    '''
    按 key ，重覆repeat次，每次等的delay秒
    '''
    for i in range(repeat):pydirectinput.press(key);time.sleep(delay)
    
def reset(delay=8):
    '''
    重設色角色 esc + r + enter
    '''
    pydirectinput.press('esc');time.sleep(1)
    pydirectinput.press('r');time.sleep(1)
    pydirectinput.press('enter')
    time.sleep(delay)
    
def findColorsYX(color,tolorance=0,image=[]):
    '''
    給定 image ，在上面找到和 color 相近顏色的座標
    並回傳座標陣列[(y1,x1),(y2,x2)...]，tolorance 為容忍範圍
    '''
    if len(image)==0:image = pyautogui.screenshot()
    image=np.array(image)
    a=np.array(image)
    b=np.array(color)
    dist = np.linalg.norm(a-b, axis=-1)
    return np.argwhere(dist <= tolorance)

def countColor(color,region=(0,0, 40, 20),tolorance=0,image=[]):
    '''
    計算 region 裡面 color 出現的次數
    region=(0,0, 40, 20) 左上角座標(0,0) 寬=40 高=20
    tolorance=0， 距離容忍值
    '''
    if len(image)==0:image = pyautogui.screenshot()
    x,y,w,h=region
    image=np.array(image)
    a=np.array(image)[y:y+h,x:x+w]
    b=np.array(color)
    dist = np.linalg.norm(a-b, axis=-1)
    return len(np.argwhere(dist <= tolorance))

def isHit(tolorance=20, min_hits=5, image=None):
    '''
    判斷是否擊中敵人
    參數說明：
        region:     (x, y, w, h)，偵測區域的左上角座標與寬高
        tolorance:  顏色距離容忍值，像素顏色距離在此範圍內才算命中
        min_hits:   至少有幾個符合顏色的像素才算「擊中」
        image:      numpy array 或 PIL Image，若無則自動截圖
    回傳：
        若目標顏色像素數（任一顏色達標） >= min_hits，回傳 True，否則 False
    '''
    # 預設目標顏色（可依遊戲調整）
    region=(334, 668, 40, 40)
    targets = [
        (231, 230, 231),
        (250, 238, 132),
        (255, 126, 49),
        (192, 3, 212)
    ]
    if image is None:    image = pyautogui.screenshot()
    img = np.asarray(image)
    x, y, w, h = region
    crop = img[y:y+h, x:x+w, :3]                      # 取區域 RGB
    targets_arr = np.array(targets).reshape(-1, 1, 1, 3)  # (N,1,1,3)
    dist = np.linalg.norm(crop - targets_arr, axis=-1)    # (N,h,w)
    count_per_target = np.sum(dist <= tolorance, axis=(1,2))  # (N,)
    return np.any(count_per_target >= min_hits)


def checkColorByXY(x,y,color=(241,234,41),
                   color_tolorance=25,
                   XY_tolorance=8,image=[]):
    '''
    找出螢幕上所有顏色類似 color 的像素所在位置，看是否有接近 (x,y) 的
    若有則回傳真
    '''
    if len(image)==0:image = pyautogui.screenshot()
    image=np.array(image)
    a=findColorsYX(color,color_tolorance,image)
#     print(a)
    if len(a)>0:
        dist = np.linalg.norm(a-np.array([y,x]), axis=-1)
#         print("===============")
#         print(dist)
        ps = np.argwhere(dist <= XY_tolorance)
#         print("===============")
#         print(a[ps])
        if len(ps)>0:return True
        else :return False
    return False

def findColorsInSizeYX(color,tolorance=0,size=300,image=[]):
    '''
    給定 image ，在上面找到和 color 相近顏色的座標
    [(y1,x1),(y2,x2)...]
    並回傳座標陣列，tolorance 為容忍範圍
    size為上下左右搜與範圍
    '''
    global Xc,Yc
    if len(image)==0:image = pyautogui.screenshot()
    image=np.array(image)
    a=image[Yc-size:Yc+size,Xc-size:Xc+size]
    b=np.array(color)
    dist = np.linalg.norm(a-b, axis=-1)
    base = np.array([Yc-size,Xc-size])
    ret = np.argwhere(dist <= tolorance) + base
    return ret



def findNearestColor(color,tolorance=0,LOW=0):
    '''
    找到離角色(螢幕中心)最近的指定顏色 color
    LOW:距離下限
    '''
    global Xc,Yc
    a = findColorsYX(color,tolorance=tolorance)
    if len(a)>0:
        b = np.array([Yc,Xc])
        dist=np.linalg.norm(a-b,axis=-1)
        a=a[np.argwhere(dist>LOW)]
        if len(a)>0:
            i = np.argmin(np.linalg.norm(a-b,axis=-1))
            y,x=a[i][0]
            return x,y
    return -1,-1

def switchOn(switch='1'):
    global mode
    detectMode()
    '''
    預設有 1 2 3 4 個
    mode=1 全螢幕
    檢查若技能未開啟則開啟它
    1: (x,y)=(861,962),pixel=(129, 226, 247)
    2: (x,y)=(929,962),pixel=(129, 225, 246)
    3: (x,y)=(991,962),pixel=(130, 226, 248)
    4: (x,y)=(1055,962),pixel=(130, 226, 248)
    j: (x,y)=(903,907),pixel=(133, 232, 254)
    e: (x,y)=(960,906),pixel=(127, 222, 243)
    r: (x,y)=(1014,906),pixel=(127, 222, 243)
    mode=2 左大右小
    檢查若技能未開啟則開啟它
    1: (x,y)=(544,960),pixel=(129, 226, 247)
    2: (x,y)=(606,960),pixel=(129, 225, 246)
    3: (x,y)=(672,960),pixel=(130, 226, 248)
    4: (x,y)=(737,960),pixel=(130, 226, 248)
    j: (x,y)=(587,908),pixel=(133, 232, 254)
    e: (x,y)=(640,908),pixel=(127, 222, 243)
    r: (x,y)=(690,908),pixel=(127, 222, 243)
    '''
    if mode==1:
        XYs={'1':(861,962),'2':(929,962),
             '3':(991,962),'4':(1055,962),
             'j':(903,907),'e':(960,906),'r':(1014,906)}
    elif mode==2:
        XYs={'1':(544,960),'2':(606,960),
             '3':(672,960),'4':(737,960),
             'j':(587,908),'e':(640,908),'r':(690,908)}
    
    x,y=XYs[switch]
    check=checkColorByXY(x,y,color=(130, 227, 249),
                         color_tolorance=30,XY_tolorance=2)
    if not check:press(switch) ;return True
    return False
   
def getMission(mission=1):
#     ,baseX=1400,baseY=510,dy=50
    '''
    取得任務
    mission=1,2,3...
    baseX,basY :任務1所在座標
    dy：往下一個任務的y位移值
    '''
    global mode,Xc,Yc
    detectMode()
    baseX=1400;baseY=510;dy=50
    if mode==2:baseX=1157
    click(Xc,Yc,delay=2)
    click(baseX,baseY+dy*(mission-1));time.sleep(2)
#     click(1448,562);time.sleep(2)
    row(Xc,Yc)
    click(baseX,baseY);time.sleep(2)
    click(baseX,baseY);time.sleep(2)
    
def aimEnemy(LOW=0):
    '''
    在見聞色下找到最近的敵人(紅色)瞄準一下
    LOW：可以瞄準的最短距離，此值越大可以瞄準越遠的敵人
    '''
    x,y = findNearestColor((255,0,0),LOW=LOW)
    if x>0:
        print(f'瞄準：{x},{y}',)
        row(x,y,dy=-1,delay=0)
        row(x,y,dy=1,delay=0)
#         click(x,y);
        return True
    return False

def shotEnemy(a='4',b='',c='1'):
    '''
    在見聞色下找到最近的敵人
    開 a 欄位做射擊,a='1'or'2'or'3'or'4'
    使用 b 招,     b='z'or'x'or'c'or'v'
    切換回 c 欄位   c='1'or'2'or'3'or'4'
    '''
    x,y = findNearestColor((255,0,0))
    if x>0:
        print(f'射擊：{x},{y}',)
        if a!='':press(a);
        row(x,y,dy=1,delay=0)
        click(x,y);
        if b!='':press(b)
        if c!='':press(c)
        return True
    return False

def isComplete(targetImgPath='goal.png',p1=(740,596)):
    '''
    檢查螢幕中是否有 goal.png 來判斷任務是否完成
    若任務已完成就開啟邏盤，p1為縮小對話框的座標
    '''
    mode=detectMode()
    try:
        x,y=pyautogui.locateCenterOnScreen(targetImgPath,confidence=0.92)
        click(x,y,delay=1)
        if mode==2:    click(459,582)
        elif mode==1:  click(740,596)
        print('mission complete!')
        return True
    except:return False
    
def close2Color(color=(241, 234, 41),size=300,tolorance=25,
                distTH=10,
                offsetX=15,offsetY=60,
                repeat=200):
    '''
    以角色為中心搜與方圓 size內的指定顏色(color)
    並接近指定顏色所在位置
    tolorance：顏色容忍值
    distTH：距離容忍值
    offsetX:X方向偏移值
    offsetY:Y方向偏移值
    '''
    global Xc,Yc
    for i in range(repeat):
        ps=findColorsInSizeYX(color,tolorance=tolorance,size=size)
        if(len(ps)>0):
            y,x=ps[0]
            y+=offsetY
            x+=offsetX
            print(f'接近目標顏色{color} 位置：({x},{y})')
            if i%4==0:
                if x>Xc+distTH:press('d')
                elif x<Xc-distTH:press('a')
                elif y>Yc+distTH:press('s')
                elif y<Yc-distTH:press('w')
                else:return True
            elif i%4==1:
                if x<Xc-distTH:press('a')
                elif y>Yc+distTH:press('s')
                elif y<Yc-distTH:press('w')
                elif x>Xc+distTH:press('d')
                else:return True
            elif i%4==2:
                if y>Yc+distTH:press('s')
                elif y<Yc-distTH:press('w')
                elif x>Xc+distTH:press('d')
                elif x<Xc-distTH:press('a')
                else:return True
            elif i%4==2:
                if y<Yc-distTH:press('w')
                elif x>Xc+distTH:press('d')
                elif x<Xc-distTH:press('a')
                elif y>Yc+distTH:press('s')
                else:return True
            
        else:print(f'找不到指定顏定{color}');break
    return False
def getXYDist(x,y,color):#1590,918
    '''
    於(x,y)處的顏色和目標顏色的差異
    '''
    pix = np.array(pyautogui.pixel(x,y))
    dist = np.linalg.norm(pix-np.array(color),axis=-1)
    print(f"於({x},{y})處 pix={pix}和目標顏色{color}距離={dist}")
    return dist

def buyRandomFruit():
    '''
    目前只適用 mode=2
    買隨機水果，定位點可能需要調整
    '''
    click(Xc,Yc)
    print(Xc,Yc)
    time.sleep(1)
    check=checkColorByXY(1150,505,color=(255, 255, 255))
    if check:
        print('OK')
        row(1150,505)
        click(1150,505)
        time.sleep(1.5)
        click(1150,505)
        time.sleep(1.5)
        click(1150,505)
        time.sleep(1)
        check=checkColorByXY(573,579,color=(255, 255, 255))
        if check:
            print('時間未到')
            return False
        click(1150,505)
        return True
    return False

def putDownFruit(isFruitOnHand=True):
    '''
    目前只適用 mode=2
    放下水果，，定位點可能需要調整
    '''
    if not isFruitOnHand: press('5')
    time.sleep(1)
    click(Xc,Yc)
    time.sleep(1)
    row(1176,565)
    time.sleep(1)
    click(1176,565)
    time.sleep(1)
    click(1176,565)
#1176,565,color=(255, 255, 255)

def storeFruit():
    '''
    目前只適用 mode=2
    儲存水果，定位點可能需要調整
    '''
    press('5')
    time.sleep(1)
    click(Xc,Yc)
    time.sleep(1)
    row(1157,633)
    click(1157,633)
    time.sleep(1)
    click(Xc,Yc)
    #check if fruit repeat
    check=checkColorByXY(1173,683,color=(255, 255, 255))
    if check:
        row(1173,683);
        click()
        return False
    return True

def closePopUp():
    '''
    目前只適用 mode=2
    關閉誤按完成或展開問題，定位點可能需要調整
    '''
    check=checkColorByXY(866,467,color=(255, 255, 255))
    if check:print('縮小彈出視窗');click(866,467)
    
def openPopUp():
    '''
    目前只適用 mode=2
    展開問題，定位點可能需要調整
    '''
    check=checkColorByXY(235,495,color=(255, 255, 255))
    if check:print('點開任務');click(235,495)
    
def quitJob():
    '''
    目前只適用 mode=2
    放棄目前任務，定位點可能需要調整
    '''
#     237,496,color=(255, 255, 255)
    click(237,496)
    time.sleep(1)
    click(455,587)
    time.sleep(1)
    click(455,587)
def switchSever(join='navy',repeat=5):
    for i in range(repeat):
        row(1252,67,dy=1)
        pyautogui.click(1252,67);time.sleep(2);row(639,530,dy=1)
        zoom(scroll=-200,repeat=50)
        time.sleep(1)
        click(883,615);time.sleep(2)
        check=checkColorByXY(686,611,color=(255, 255, 255))
        if check:
            print('傳送失敗');click(686,611);time.sleep(1);click(1252,67)
            continue
        else:
            for i in range(20):
                check=checkColorByXY(718,292,color=(255, 255, 255))
                if check:
                    if join=='navy':
                        click(805,479)
                        print('加入海軍')
                    else:
                        click(535,452)
                        print('加入海盜')
                    return True
                time.sleep(1)
    return False    
def homePoint(x=83,y=458,delay=8):
    '''
    目前只適用 mode=2
    按下home point (x,y) 並等待 delay 秒
    '''
    check = checkColorByXY(x,y,(255,255,255))
    if not check: print("can't find home point. Is (x,y) correct?")
    else:
        click(x,y)
        for i in range(delay):
            print('wait for ',delay-i, 'sec')
            time.sleep(1)
        return True
    return False

mode = detectMode()
'''
外掛練等已海軍為主
0-10:海軍新手
15-30:叢林
30-60:海盜村
60-90:沙漠
100:中島
90-120:冰凍村
120-150:海上堡壘
150-200:天空之境
190-275:監獄
225-300:斗獸場
225-300:岩漿村
374-450:水下城
450-575:空島上層
625-700:噴泉城
'''
code={}
code['海軍新手']='''
import autobf as bf
import time
print(\'\'\'
===============
海軍新手村前置作業：
1.開啟「快速模式」
2.櫃檯(ON)
3.輸入法切換至 ENG(純英文)
4.視窗位置：左大(遊戲視窗)，右小(PYTHON IDE)
5.螢幕解析度調整為：1920x1080
================
\'\'\')
bf.setCenterXY(x=639,y=530)
bf.click(center=True)
def fight():
    notHit = 0
    for i in range(720):
        if bf.isComplete():return
        bf.click()
#         for j in range(80):bf.click()
        if not bf.isHit():notHit+=1
        else:notHit=0
        if notHit>40:break
        print('notHit=',notHit)
    bf.closePopUp()
    
def resetUntilOK():
    bf.click(center=True)
    while True:
        bf.reset()
        bf.switchOn('1')
        isGetMission=True
        check=bf.checkColorByXY(232,523,color=(255, 255, 255))
        if check:isGetMission=False
        bf.zoom2max()
        check=bf.checkColorByXY(525,73,color=(241, 234, 56))
        if check:
            print('1.黃色問號在左前，港口在左.')
            bf.slide('w',3)
            if not bf.close2Color(offsetX=5,offsetY=40,distTH=7):continue
            if isGetMission:bf.getMission(1)
            bf.press('d',4);bf.slide('w',4);
            bf.press('d',4);bf.press('w',4);
            bf.press('d',2)
            return
        check=bf.checkColorByXY(581,108,color=(241, 234, 55))
        if check:
            print('2.黃色問號在正前，港口在左.')
            bf.slide('d');bf.slide('w',3);
            bf.slide('a');bf.press('a',5)
            if not bf.close2Color(offsetX=5,offsetY=40,distTH=7):continue
            if isGetMission:bf.getMission(1)
            bf.press('d',5);bf.slide('w',4)
            bf.press('a',3);bf.press('w',3)
            return
        bf.slide('w')
        check=bf.checkColorByXY(492,78,color=(246, 233, 58))
        if check:
            print('3.先滑一步後黃色問號和港口在左前前.')
            bf.press('a',8);bf.slide('w',3);bf.press('a',5);bf.press('w',4)
            if not bf.close2Color(offsetX=5,offsetY=40,distTH=7):continue
            if isGetMission:bf.getMission(1)
            bf.slide('d',3);bf.press('s',6)
#             bf.slide('d',4);bf.press('w',6);
#             bf.slide('w',1);bf.press('w',2);
            return
        check=bf.checkColorByXY(426,111,color=(239, 220, 41))
        if check:
            print('4.先滑一步後黃色問號和港口在左前前.')
            bf.slide('w');bf.slide('a');
            bf.press('a',2);bf.slide('w',2)
            if not bf.close2Color(offsetX=5,offsetY=40,distTH=7):continue
            if isGetMission:bf.getMission(1)
            bf.slide('d',2);bf.press('d',10)
            bf.press('w',2)
            return
        check=bf.checkColorByXY(223,287,color=(241, 234, 55))
        if check:
            print('5.先滑一步後黃色問號和港口在左左左前.')
            bf.slide('a',1);bf.slide('w',2)
            bf.slide('a',2);
            if not bf.close2Color(offsetX=5,offsetY=40,distTH=7):continue
            if isGetMission:bf.getMission(1)
#             bf.press('d',3);bf.slide('w',3);bf.press('w',3)
#             bf.press('a',2)
            bf.press('d',8);bf.slide('w',3);
            bf.press('w',14);bf.press('d',3)
            return
        check=bf.checkColorByXY(223,296,color=(241, 234, 55))
        if check:
            print('6.先滑一步後黃色問號和港口在左左左前.')
            bf.slide('a',1);bf.slide('w',1)
            bf.slide('a',1);
            if not bf.close2Color(offsetX=5,offsetY=40,distTH=7):continue
            if isGetMission:bf.getMission(1)
            bf.press('d',8);bf.slide('w',4);
            bf.press('w',5)
            return

while True:
    for i in range(50):
        resetUntilOK()
        fight()
    bf.switchSever(join='navy')
'''
code['叢林']='''
import autobf as bf
import time
print(\'\'\'
===============
森林島 前置作業：
1.開啟「快速模式」
2.櫃檯(ON)
3.輸入法切換至 ENG(純英文)
4.視窗位置：左大(遊戲視窗)，右小(PYTHON IDE)
5.開啟羅盤顯示目標NPC純綠方塊
6.螢幕解析度調整為：1920x1080
================
\'\'\')
def fight():
    notHit = 0
    for i in range(720):
        if bf.isComplete():return
        bf.click()
#         for j in range(80):bf.click()
        if not bf.isHit():notHit+=1
        else:notHit=0
        if notHit>80:break
        print('notHit=',notHit)
    bf.closePopUp()
    
def resetUntilOK():
    bf.quitJob()
    while True:
        bf.click(center=True)
        bf.switchOn('1')
        check=bf.checkColorByXY(396,421,color=(0, 255, 0))
        if check:
            print('寶箱旁')
            bf.jumpSlide('w',2,3)
            time.sleep(1)
            bf.press('s',1)
            bf.jumpSlide('w',2,2)
            bf.zoom2max()
            bf.press('a',8);bf.press('w',2)
            bf.press('a',8);bf.press('w',1)
            bf.press('a',8);bf.press('w',1);
            bf.press('a',7);bf.press('w',2);
            bf.press('a',2)
            if not bf.close2Color(offsetX=5,offsetY=40,
                                  distTH=7,repeat=40):continue
            bf.getMission()
            bf.press('w',1)
            bf.jumpSlide('w',2,3)
            time.sleep(1)
            bf.slide('w')
            return
        bf.reset()

while True:
    for i in range(50):
        resetUntilOK()
        fight()
    bf.switchSever(join='navy')

'''
code['沙漠']='''
import autobf as bf
bf.setCenterXY(x=639,y=530);bf.click(center=True)
def resetUntilOK():
    while True:
        bf.reset();bf.isComplete();bf.closePopUp()
        isGetMission=True
        check=bf.checkColorByXY(239,525,color=(255, 255, 255))
        if check:isGetMission=False;print('不接任務')
        bf.openPopUp();bf.click(66,563)
        check=bf.checkColorByXY(40,549,color=(0, 254, 0))
        bf.closePopUp()
        if check:
            print('島上較靠近任務點')
            bf.zoom2max()
            bf.slide('w',3);bf.slide('d',3);bf.press('w',4)
            if not bf.close2Color():continue
            if isGetMission:bf.getMission(1)
            bf.jumpSlide('w',4,2)
            bf.press('s',3);bf.press('d',2)
            return
        check=bf.checkColorByXY(528,496,color=(0, 223, 71))
        if check:
            print('船商站靠近左邊')
            bf.zoom2max()
            bf.jumpSlide('d',4,4);bf.slide('s',3);bf.jumpSlide('d',4,2)
            bf.press('s',4);bf.press('d',5)
            if not bf.close2Color():continue
            if isGetMission:bf.getMission(1)
            bf.slide('d');bf.press('d',4);bf.press('w',3)
            return
def fight():
    bf.switchOn('1')
    for i in range(6):
        print('round',i)
        bf.click(center=True)
        bf.click(repeat=150)
        if bf.isComplete():return
        bf.closePopUp()     
while True:
    bf.zoom2max()
    for i in range(50):
        resetUntilOK()
        fight()
    bf.switchSever(join='navy')
'''
code['海盜村']='''
import autobf as bf
bf.setCenterXY(x=639,y=530)
bf.click(center=True)
def resetUntilOK():
    while True:
        check=bf.checkColorByXY(866,467,color=(255, 255, 255))
        if check:bf.click(866,467)     
        isGetMission=True
        check=bf.checkColorByXY(217,523,color=(255, 255, 255))
        if check:isGetMission=False
        bf.reset()
        # 外面
        check=bf.checkColorByXY(979,518,color=(149, 80, 4))
        if check:
            print('外面')
            bf.zoom2max()
            bf.jumpSlide('s',2,1)
            bf.slide('d',3)
            bf.keyDown('left',1.45)
            bf.press('d',3)
            bf.press('s',9)
            if not bf.close2Color(tolorance=15,offsetY=30):continue
            if isGetMission:bf.getMission(1)
            bf.press('d',5)
            bf.slide('s',3)
            bf.press('a',4)
            bf.slide('s',1)
            bf.press('w',4)
        else:
            print('中間門')
            bf.zoom2max()
            bf.press('w',6)
            bf.press('d',6)
            if not bf.close2Color(tolorance=15,offsetY=30):continue
            if isGetMission:bf.getMission(1)
            bf.press('d',5)
            bf.slide('s',3)
            bf.press('a',4)
            bf.slide('s',1)
            bf.press('w',4)
        break
def fight():
    bf.press('1')
    for i in range(6):
        print('round',i)
        bf.click(center=True)
        bf.click(repeat=150)
        if bf.isComplete():return
        check=bf.checkColorByXY(866,467,color=(255, 255, 255))
        if check:bf.click(866,467)
while True:
    bf.zoom2max()
    for i in range(50):
        resetUntilOK()
        fight()
    bf.switchSever(join='navy')
'''

def getCode(location=0):
    global code
    if isinstance(location, int):
        print('#===',list(code.keys())[location],'===')
        pyperclip.copy(list(code.values())[location])
        print('程式碼已複製到剪貼簿')
    else:
        try:
            pyperclip.copy(code[location])
            print(f'{location} 程式碼已複製到剪貼簿')
        except: print(location,'目前無程式碼')
        
# checkAndClick(1819,921,color=(222, 66, 45))
#=============================================        
# def goEnemy():
#     global isGetMission
#     zoom2max()
#     if checkColorByXY(x=553,y=656):
#         #背對問號
#         keyDown('left',0.5)
#         slide('w',2);slide('a',2)
#         close2Color(color=(241, 234, 41))
#         if isGetMission:getMission(p1=(1400,510))
#         isGetMission = False
#         slide('d',5)
#         slide('s',12)
#     else:
#         #面向問號
#         slide('w',4);slide('d',1)
#         if checkColorByXY(x=1124,y=93):
#             slide('w',3);slide('d',1)
#             close2Color(color=(241, 234, 41))
#             getMission(p1=(1400,510))
#             print('1')
#             slide('a',5);slide('s',3);slide('a',9)
#         elif checkColorByXY(x=1132,y=96):
#             slide('w',3);slide('d',1)
#             close2Color(color=(241, 234, 41))
#             getMission(p1=(1400,510))
#             print('2')
#             slide('a',5);slide('s',2);slide('a',8)
#         else:
#             close2Color(color=(241, 234, 41))
#             getMission(p1=(1400,510))
#             slide('a',12)
#             slide('w',2)
#             print('3')
# 
# 
# def fight():
#     for i in range(33):
#         print('fight:',i)
#         instinctOn()
#         time.sleep(0.6)
#         shotEnemy(a='', b='v', c='')
#         if aimEnemy():
#             if getXYDist(1590,918,(180,180,180))>50:
#                 press('v')
#             else:press('4');click();press('2')
#         press('e')
#         for j in range(150):click()
#         if isComplete(targetImgPath='goal.png', p1=(740,596)):
#             return True
#     return False
#     
# isGetMission = False
# def work():
#     global isGetMission
#     while True:
#         reset()
#         if getXYDist(925,962,(131, 226, 247))>30:press('2')
#         goEnemy()
#         isGetMission = fight()
        
        
# if __name__ == '__main__':
#     
#     click(Xc,Yc)
#     work()






