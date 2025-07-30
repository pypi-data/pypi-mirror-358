import pyttsx3

# 初始化， 必须要有奥
engine = pyttsx3.init()

# 设置音量
volume = engine.getProperty('volume')
engine.setProperty('volume', volume + 100)

# 设置语速
rate = engine.getProperty('rate')
engine.setProperty('rate', rate + 50)


#
def onStart(name):
    print('starting', name)


def onWord(name, location, length):
    print('word', name, location, length)


def onEnd(name, completed):
    print('finishing', name, completed,"语音播报完毕.....")


engine.connect('started-utterance', onStart)
engine.connect('started-word', onWord)
engine.connect('finished-utterance', onEnd)

#
engine.say('正在读取重量，请保持车辆静止...')
engine.runAndWait()

#
engine.say('我能说第二句话了')
engine.runAndWait()
