import qi
import argparse
import sys
import time


class HumanTrackedEventWatcher(object):
    """ A class to react to HumanTracked and PeopleLeft events """

    def __init__(self, app):
        """
        Initialisation of qi framework and event detection.
        """
        super(HumanTrackedEventWatcher, self).__init__()

        try:
            app.start()
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " +
                   str(args.port) + ".\n")

            sys.exit(1)

        session = app.session
        self.subscribers_list = []
        self.is_speech_reco_started = False

        # SUBSCRIBING SERVICES
        self.tts             = session.service("ALTextToSpeech")
        self.memory          = session.service("ALMemory")
        self.motion          = session.service("ALMotion")
        self.speech_reco     = session.service("ALSpeechRecognition")
        self.basic_awareness = session.service("ALBasicAwareness")


    def create_callbacks(self):

        self.connect_callback("ALBasicAwareness/HumanTracked",
                              self.on_human_tracked)
        self.connect_callback("ALBasicAwareness/HumanLost",
                              self.on_people_left)

        return

    def connect_callback(self, event_name, callback_func):
        """ connect a callback for a given event """
        print "Callback connection"

        subscriber = self.memory.subscriber(event_name)
        subscriber.signal.connect(callback_func)
        self.subscribers_list.append(subscriber)

        return

    def on_human_tracked(self, value):
        """ callback for event HumanTracked """
        print "Got HumanTracked: detected person with ID:", str(value)
        if value >= 0:  # found a new person
            self.pepper_speak("Ohh I found a new person, let me tag you with id  {}".format(value))
            position_human = self.get_people_perception_data(value)
            [x, y, z] = position_human
            print "The tracked person with ID", value, "is at the position:", \
                "x=", x, "/ y=",  y, "/ z=", z

        return

    def on_people_left(self, value):
        """ callback for event PeopleLeft """
        print "Got PeopleLeft: lost person", str(value)
        self.pepper_speak("Ohh No ! I lost the person")

    def pepper_speak(self, msg):

        sentence = "\RSPD="+ str( 100 ) + "\ "
        sentence += "\VCT="+ str( 100 ) + "\ "
        sentence += msg
        sentence +=  "\RST\ "
        self.tts.say(str(sentence))

        return

    def get_people_perception_data(self, id_person_tracked):
        """
            return information related to the person who has the id
            "id_person_tracked" from People Perception
        """
        memory_key = "PeoplePerception/Person/" + str(id_person_tracked) + \
                     "/PositionInWorldFrame"
        return self.memory.getData(memory_key)



    def run(self):
        """
            this example uses the setEngagementMode, startAwareness and
            stopAwareness methods
        """
        # start
        print "Waiting for the robot to be in wake up position"
        self.motion.wakeUp()

        self.create_callbacks()

        print "Starting BasicAwareness with the fully engaged mode"
        self.basic_awareness.setEngagementMode("FullyEngaged")
        self.basic_awareness.setEnabled(True)

        # loop on, wait for events until manual interruption
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, shutting down"
            # stop
            print "Stopping BasicAwareness"
            self.basic_awareness.setEnabled(False)

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
    app = qi.Application(["HumanTrackedEventWatcher",
                          "--qi-url=" + connection_url])

    human_tracked_event_watcher = HumanTrackedEventWatcher(app)
    human_tracked_event_watcher.run()
