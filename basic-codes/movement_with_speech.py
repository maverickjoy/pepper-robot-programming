from naoqi import ALProxy

motion = ALProxy("ALMotion", "10.9.45.11", 9559)
tts    = ALProxy("ALTextToSpeech", "10.9.45.11", 9559)
motion.moveInit()
motion.post.moveTo(1.5, 0, 0)
tts.say("I'm walking")
