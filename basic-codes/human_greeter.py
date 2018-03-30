import qi
import time
import sys
import argparse


class HumanGreeter(object):
    """
    A simple class to react to face detection events.
    """

    def __init__(self, app):
        """
        Initialisation of qi framework and event detection.
        """
        super(HumanGreeter, self).__init__()
        app.start()
        session = app.session

        # Get the services ALMemory, ALTextToSpeech and ALFaceDetection..
        self.memory         = session.service("ALMemory")
        self.tts            = session.service("ALTextToSpeech")
        self.face_detection = session.service("ALFaceDetection")
        self.motion         = session.service("ALMotion")

        # Connect the event callback.
        self.subscriber = self.memory.subscriber("FaceDetected")
        self.subscriber.signal.connect(self.on_human_tracked)
        self.face_detection.subscribe("HumanGreeter")
        self.got_face = False


    def on_human_tracked(self, value):
        """
        Callback for event FaceDetected.
        """
        if value == []:  # empty value when the face disappears
            self.got_face = False
        elif not self.got_face:  # only speak the first time a face appears
            self.got_face = True
            print "I saw a face!"
            self.tts.say("Hello Human !")
            # First Field = TimeStamp.
            timeStamp = value[0]
            print "TimeStamp is: " + str(timeStamp)

            # Second Field = array of face_Info's.
            faceInfoArray = value[1]
            for j in range( len(faceInfoArray)-1 ):
                faceInfo = faceInfoArray[j]

                # First Field = Shape info.
                faceShapeInfo = faceInfo[0]

                # Second Field = Extra info (empty for now).
                faceExtraInfo = faceInfo[1]

                print "Face Infos :  alpha %.3f - beta %.3f" % (faceShapeInfo[1], faceShapeInfo[2])
                print "Face Infos :  width %.3f - height %.3f" % (faceShapeInfo[3], faceShapeInfo[4])
                print "Face Extra Infos :" + str(faceExtraInfo)

            # Waiting for a buffer time so that it is not very quick and confusing.
            time.sleep(3)

        return

    def run(self):
        """
        Loop on, wait for events until manual interruption.
        """
        # start
        print "Waiting for the robot to be in wake up position"
        self.motion.wakeUp()

        print "Starting HumanGreeter"
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, stopping HumanGreeter"
            self.face_detection.unsubscribe("HumanGreeter")
            #stop
            sys.exit(0)

        return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="10.9.45.11",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["HumanGreeter", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    human_greeter = HumanGreeter(app)
    human_greeter.run()
