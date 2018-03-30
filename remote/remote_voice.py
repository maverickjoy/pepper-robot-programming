import qi
import sys
import time
import almath
import motion
import random
import argparse
from PIL import Image




# ==============================================================================
#                      --- CAMERA INFORMATION ---

# AL_resolution
AL_kQQQQVGA = 8 	#Image of 40*30px
AL_kQQQVGA  = 7 	#Image of 80*60px
AL_kQQVGA   = 0 	#Image of 160*120px
AL_kQVGA    = 1 	#Image of 320*240px
AL_kVGA     = 2 	#Image of 640*480px
AL_k4VGA    = 3 	#Image of 1280*960px
AL_k16VGA   = 4 	#Image of 2560*1920px

# Camera IDs
AL_kTopCamera    = 0
AL_kBottomCamera = 1
AL_kDepthCamera  = 2

# Need to add All color space variables
AL_kBGRColorSpace = 13

# ==============================================================================



class RemoteVoice(object):

    def __init__(self, app):

        super(RemoteVoice, self).__init__()

        try:
            app.start()
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " +
                   str(args.port) + ".\n")

            sys.exit(1)

        session = app.session
        self.subscribers_list = []

        # SUBSCRIBING SERVICES
        self.video             = session.service("ALVideoDevice")
        self.memory            = session.service("ALMemory")
        self.motion            = session.service("ALMotion")
        self.alDialog          = session.service("ALDialog")
        self.posture_service   = session.service("ALRobotPosture")
        self.speaking_movement = session.service("ALSpeakingMovement")

        # INITIALISING CAMERA POINTERS
        self.imageNo2d                = 1
        self.imageNo3d                = 1

    def create_callbacks(self):

        self.connect_callback("capture_image_event",
                              self.capture_image_event)

        self.connect_callback("move_forward_event",
                              self.move_forward_event)

        self.connect_callback("turn_right_event",
                              self.turn_right_event)

        self.connect_callback("turn_left_event",
                              self.turn_left_event)

        self.connect_callback("turn_around_event",
                              self.turn_around_event)

        self.connect_callback("stop_movment_event",
                              self.stop_movment_event)

        return

    def connect_callback(self, event_name, callback_func):

        print "Callback Connection"

        subscriber = self.memory.subscriber(event_name)
        subscriber.signal.connect(callback_func)
        self.subscribers_list.append(subscriber)

        return


    def _capture2dImage(self,cameraId):
        # Capture Image in RGB

        # WARNING : The same Name could be used only six time.
        strName = "capture2DImage_{}".format(random.randint(1,10000000000))


        clientRGB = self.video.subscribeCamera(strName, cameraId, AL_kVGA, 11, 10)
        imageRGB = self.video.getImageRemote(clientRGB)

        imageWidth = imageRGB[0]
        imageHeight = imageRGB[1]
        array = imageRGB[6]
        image_string = str(bytearray(array))

        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

        # Save the image inside the images foler in pwd.
        image_name_2d = "images/img2d-" + str(self.imageNo2d) + ".png"
        im.save(image_name_2d, "PNG") # Stored in images folder in the pwd, if not present then create one
        self.imageNo2d += 1
        im.show()

        return

    def _capture3dImage(self):
        # Depth Image in RGB

        # WARNING : The same Name could be used only six time.
        strName = "capture3dImage_{}".format(random.randint(1,10000000000))

        clientRGB = self.video.subscribeCamera(strName, AL_kDepthCamera, AL_kQVGA, 11, 15)
        imageRGB = self.video.getImageRemote(clientRGB)

        imageWidth = imageRGB[0]
        imageHeight = imageRGB[1]
        array = imageRGB[6]
        image_string = str(bytearray(array))

        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

        # Save the image inside the images foler in pwd.
        image_name_3d = "images/img3d-" + str(self.imageNo3d) + ".png"
        im.save(image_name_3d, "PNG") # Stored in images folder in the pwd, if not present then create one
        self.imageNo3d += 1
        im.show()

        return

    def capture_image_event(self, value):

        print "Capturing Image : " + str(value)

        if str(value) == "2d":
            cameraId = 0 # DEFAULT TOP
            self._capture2dImage(cameraId)

        if str(value) == "3d":
            self._capture3dImage()

        time.sleep(1)
        return


    '''
    MOVERMENTS ARE RELATIVE HERE NOT ABSOLUTE, FOR ABSOLUTE MOVEMENT ONE CAN
    USE ANGLES AND USE 'moveTo()' METHOD FOR IT.
    '''
    def _moveForward(self, amnt):
        #TARGET VELOCITY
        X = 0.5  # forward
        Y = 0.0
        Theta = 0.0

        try:
            self.motion.moveToward(X, Y, Theta)
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion.stopMove()
            exit()
        except Exception, errorMsg:
            print str(errorMsg)
            print "This example is not allowed on this robot."
            exit()

        print "====================================================================="
        print "Forward Movement Started"
        time.sleep(float(amnt))
        print "Forward Movement Complete"
        print "====================================================================="

        return

    def _rotateRight(self, amnt):
        #TARGET VELOCITY
        X = 0.0
        Y = 0.0
        Theta = -0.5

        try:
            self.motion.moveToward(X, Y, Theta)
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion.stopMove()
            exit()
        except Exception, errorMsg:
            print str(errorMsg)
            print "This example is not allowed on this robot."
            exit()

        print "====================================================================="
        print "Rotate Right Movement Started"
        time.sleep(float(amnt))
        print "Rotate Right Movement Complete"
        print "====================================================================="

        return

    def _rotateLeft(self, amnt):
        #TARGET VELOCITY
        X = 0.0
        Y = 0.0
        Theta = 0.5

        try:
            self.motion.moveToward(X, Y, Theta)
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion.stopMove()
            exit()
        except Exception, errorMsg:
            print str(errorMsg)
            print "This example is not allowed on this robot."
            exit()

        print "====================================================================="
        print "Rotate Left Movement Started"
        time.sleep(float(amnt))
        print "Rotate Left Movement Complete"
        print "====================================================================="


    def move_forward_event(self,value):
        print "Got event Move Forward : ",str(value)

        try:
            self._moveForward(value)
            self.motion.stopMove()
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion.stopMove()
            exit()
        except Exception, errorMsg:
            print str(errorMsg)
            print "This example is not allowed on this robot."
            exit()

        return

    def turn_around_event(self,value):
        print "Got event Turn Around : ",str(value)

        try:
            self._rotateRight(value)
            self.motion.stopMove()
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion.stopMove()
            exit()
        except Exception, errorMsg:
            print str(errorMsg)
            print "This example is not allowed on this robot."
            exit()

        return

    def turn_left_event(self,value):
        print "Got event turn left : ",str(value)

        try:
            self._rotateLeft(value)
            self.motion.stopMove()
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion.stopMove()
            exit()
        except Exception, errorMsg:
            print str(errorMsg)
            print "This example is not allowed on this robot."
            exit()

        return

    def turn_right_event(self,value):
        print "Got event turn right : ",str(value)

        try:
            self._rotateRight(value)
            self.motion.stopMove()
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion.stopMove()
            exit()
        except Exception, errorMsg:
            print str(errorMsg)
            print "This example is not allowed on this robot."
            exit()

        return

    def stop_movment_event(self, value):
        print "Stopping movement : " , str(value)
        self.motion.stopMove()
        time.sleep(2)

        return



    def addTopic(self):
        print " Starting topic adding process "

        # disabling hand gestures and movement while speaking
        self.speaking_movement.setEnabled(False)

        self.alDialog.setLanguage("English")

        # Loading the topic given by the user (absolute path is required)
        # Topic file to be present inside nao or pepper filesystem.
        topic_path = "/home/nao/chat/remote_commands.top"

        topf_path = topic_path.decode('utf-8')
        self.topic_name = self.alDialog.loadTopic(topf_path.encode('utf-8'))

        # Activating the loaded topic
        self.alDialog.activateTopic(self.topic_name)

        # Starting the dialog engine - we need to type an arbitrary string as the identifier
        # We subscribe only ONCE, regardless of the number of topics we have activated
        self.alDialog.subscribe('remote_commands')

        print "\nSpeak to the robot using rules from the just loaded topic file."

        return

    def cleanUp(self):
        # stopping the dialog engine
        self.alDialog.unsubscribe('remote_commands')
        # Deactivating the topic
        self.alDialog.deactivateTopic(self.topic_name)

        # now that the dialog engine is stopped and there are no more activated topics,
        # we can unload our topic and free the associated memory
        self.alDialog.unloadTopic(self.topic_name)
        self.motion.stopMove()

        return

    def run(self):
        # start
        print "Waiting for the robot to be in wake up position"
        self.motion.wakeUp()
        self.posture_service.goToPosture("StandInit", 0.5)

        self.create_callbacks()
        self.addTopic()


        # loop on, wait for events until manual interruption
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, shutting down"

            print "Starting Clean Up process"
            self.cleanUp()

            print "Waiting for the robot to be in rest position"
            self.motion.rest()

            sys.exit(0)

        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="10.9.45.11",
                        help="Robot IP address. On robot or Local Naoqi: use \
                        '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()

    # Initialize qi framework.
    connection_url = "tcp://" + args.ip + ":" + str(args.port)
    app = qi.Application(["RemoteVoice",
                          "--qi-url=" + connection_url])

    remote_voice = RemoteVoice(app)
    remote_voice.run()
