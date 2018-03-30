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


class Remote():

    def __init__(self,session):

        # SUBSCRIBING SERVICES
        self.motion_service           = session.service("ALMotion")
        self.posture_service          = session.service("ALRobotPosture")
        self.tts                      = session.service("ALTextToSpeech")
        self.animation_player_service = session.service("ALAnimationPlayer")
        self.video                    = session.service("ALVideoDevice")

        # INITIALISING CAMERA POINTERS
        self.imageNo2d                = 1
        self.imageNo3d                = 1


    def _userArmArticular(self):
        # If needed to make hands move while moving.
        # Arms motion from user have always the priority than walk arms motion

        JointNames = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
        Arm1 = [-40,  25, 0, -40]
        Arm1 = [ x * motion.TO_RAD for x in Arm1]

        Arm2 = [-40,  50, 0, -80]
        Arm2 = [ x * motion.TO_RAD for x in Arm2]

        pFractionMaxSpeed = 0.6

        self.motion_service.angleInterpolationWithSpeed(JointNames, Arm1, pFractionMaxSpeed)
        self.motion_service.angleInterpolationWithSpeed(JointNames, Arm2, pFractionMaxSpeed)
        self.motion_service.angleInterpolationWithSpeed(JointNames, Arm1, pFractionMaxSpeed)

        return

    def _rotateHead(self):

        JointNamesH = ["HeadPitch", "HeadYaw"] # range ([-1,1],[-0.5,0.5]) // HeadPitch :{(-)up,(+)down} , HeadYaw :{(-)left,(+)right}

        amntY =  raw_input("Enter amount to Move Up(-) And Down(+) [-1,1] : ")
        amntX =  raw_input("Enter amount to Move Left(-) And Right(+) [-0.5,0.5] : ")

        pFractionMaxSpeed = 0.2

        HeadA = [float(amntY),float(amntX)]

        self.motion_service.angleInterpolationWithSpeed(JointNamesH, HeadA, pFractionMaxSpeed)
        time.sleep(1)

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
            self.motion_service.moveToward(X, Y, Theta)
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion_service.stopMove()
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

    # @WARNING : Dont Use this as Pepper doesn't have a sensor at its back
    def _moveBackward(self, amnt):
        #TARGET VELOCITY
        X = -0.5  # backward
        Y = 0.0
        Theta = 0.0

        try:
            self.motion_service.moveToward(X, Y, Theta)
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion_service.stopMove()
            exit()
        except Exception, errorMsg:
            print str(errorMsg)
            print "This example is not allowed on this robot."
            exit()
        amnt = 1.0 # default overiding the original value , JUST FOR CAUTION
        print "====================================================================="
        print "Backward Movement Started"
        time.sleep(float(amnt))
        print "Backward Movement Complete"
        print "====================================================================="

        return

    def _rotateRight(self, amnt):
        #TARGET VELOCITY
        X = 0.0
        Y = 0.0
        Theta = -0.5

        try:
            self.motion_service.moveToward(X, Y, Theta)
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion_service.stopMove()
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
            self.motion_service.moveToward(X, Y, Theta)
        except KeyboardInterrupt:
            print "KeyBoard Interrupt initiated"
            self.motion_service.stopMove()
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

        return

    def run(self):

        print " === START === "
        # Wake up robot
        self.motion_service.wakeUp()

        # Send robot to Stand
        self.posture_service.goToPosture("StandInit", 0.5)

        #####################
        ## Enable arms control by Motion algorithm
        #####################
        self.motion_service.setMoveArmsEnabled(True, True)

        #####################
        ## FOOT CONTACT PROTECTION
        #####################
        self.motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

        while(1):

            try:
                in_command = raw_input("Enter Command : ")

                if in_command == "w" : # moveForward
                    try:
                        amnt = raw_input("Enter Value : ")
                        self._moveForward(amnt)
                        self.motion_service.stopMove()
                    except KeyboardInterrupt:
                        print "KeyBoard Interrupt initiated"
                        self.motion_service.stopMove()
                        exit()
                    except Exception, errorMsg:
                        print str(errorMsg)
                        print "This example is not allowed on this robot."
                        exit()

                if in_command == "back" : # moveBackward
                    try:
                        amnt = raw_input("Enter Value : ")
                        self._moveBackward(amnt)
                        self.motion_service.stopMove()
                    except KeyboardInterrupt:
                        print "KeyBoard Interrupt initiated"
                        self.motion_service.stopMove()
                        exit()
                    except Exception, errorMsg:
                        print str(errorMsg)
                        print "This example is not allowed on this robot."
                        exit()

                if in_command == "a" : # rotateLeft
                    try:
                        amnt = raw_input("Enter Value : ")
                        self._rotateLeft(amnt)
                        self.motion_service.stopMove()
                    except KeyboardInterrupt:
                        print "KeyBoard Interrupt initiated"
                        self.motion_service.stopMove()
                        exit()
                    except Exception, errorMsg:
                        print str(errorMsg)
                        print "This example is not allowed on this robot."
                        exit()

                if in_command == "d" : # rotateRight
                    try:
                        amnt = raw_input("Enter Value : ")
                        self._rotateRight(amnt)
                        self.motion_service.stopMove()
                    except KeyboardInterrupt:
                        print "KeyBoard Interrupt initiated"
                        self.motion_service.stopMove()
                        exit()
                    except Exception, errorMsg:
                        print str(errorMsg)
                        print "This example is not allowed on this robot."
                        exit()

                if in_command == "s" : # speak
                    try:
                        user_msg = raw_input("Enter Sentence To Speak : ")
                        future = self.animation_player_service.run("animations/Stand/Gestures/Give_3", _async=True)
                        sentence = "\RSPD="+ str( 100 ) + "\ "
                        sentence += "\VCT="+ str( 100 ) + "\ "
                        sentence += user_msg
                        sentence +=  "\RST\ "
                        self.tts.say(str(sentence))
                        future.value()
                        self.posture_service.goToPosture("StandInit", 0.5)

                    except KeyboardInterrupt:
                        print "KeyBoard Interrupt initiated"
                        self.motion_service.stopMove()
                        self.posture_service.goToPosture("StandInit", 0.5)
                        future.cancel()
                        exit()
                    except Exception, errorMsg:
                        print str(errorMsg)
                        print "This example is not allowed on this robot."
                        exit()

                if in_command == "c2d" : # capture2dImage
                    try:
                        cameraId = raw_input("Enter CameraId [TopCamera : 0, BottomCamera : 1] : ")
                        self._capture2dImage(int(cameraId))
                    except KeyboardInterrupt:
                        print "KeyBoard Interrupt initiated"
                        exit()
                    except Exception, errorMsg:
                        print str(errorMsg)
                        print "This example is not allowed on this robot."
                        exit()

                if in_command == "c3d" : # capture3dImage
                    try:
                        self._capture3dImage()
                    except KeyboardInterrupt:
                        print "KeyBoard Interrupt initiated"
                        exit()
                    except Exception, errorMsg:
                        print str(errorMsg)
                        print "This example is not allowed on this robot."
                        exit()

                if in_command == "h" : # rotateHead
                    try:
                        self._rotateHead()
                        self.motion_service.stopMove()
                    except KeyboardInterrupt:
                        print "KeyBoard Interrupt initiated"
                        self.motion_service.stopMove()
                        exit()
                    except Exception, errorMsg:
                        print str(errorMsg)
                        print "This example is not allowed on this robot."
                        exit()

                if in_command == "x" : # exiting
                    print "Exiting gracefully"
                    break;

            except Exception, errorMsg:
                print str(errorMsg)
                print "This example is not allowed on this robot."
                exit()

        print "====================================================================="
        print "End Movement"
        print "====================================================================="

        # Go to rest position
        self.motion_service.rest()

        return


def main(session):

    remote = Remote(session)
    remote.run()
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="10.9.45.11",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)
