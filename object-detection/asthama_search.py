import qi
import argparse
import sys
import time
import requests
import json
import base64
import random
import numpy
import math
import motion
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('TkAgg')     # For running program in mac
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ==============================================================================

# =============== ORIENTATION BASED ON INITIAL BOT POSITION ====================

PHI = 0 # AMOUNT TO MOVE TO FACE TOWARDS EAST (0`)
#               0
#   math.pi/2       -math.pi/2
#            math.pi
PENDING_PHI = 0

# ==============================================================================
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# =============================== CONFIG =======================================

MOVEMENT_WAIT = 1  # In seconds
TIME_CALIBERATED = 4660 # For calculating use program robot_velocity_caliberatoion.py
ONEUNITDIST = 0.5
MAX_NODES = 90
DL_SERVER_URL = "http://10.9.45.103:5000/getPredictions"
NODE_IP = "10.9.15.11" # IP Address of the node in which you are running this program
BX = 222 # boundary x
BY = 222 # boundary y

# ==============================================================================
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ==============================================================================
#                      --- INITIALISATIONS ---

vis = {}
adj = [[] for v in range(100005)]
pointsX = [0]
pointsY = [0]
NODES_COVERED = 0

distBtwXaxisGridLines = {} # west,east
distBtwYaxisGridLines = {} # north,south

# ==============================================================================





class Bcolors():
    # COLOUR SCHEME FOR PRINTING
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AsthamaDetector(object):

    def __init__(self, app):
        super(AsthamaDetector, self).__init__()

        try:
            app.start()
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " +
                   str(args.port) + ".\n")

            sys.exit(1)

        session = app.session
        self.subscribers_list = []

        # SUBSCRIBING SERVICES
        self.tts                      = session.service("ALTextToSpeech")
        self.video_service            = session.service("ALVideoDevice")
        self.dialog_service           = session.service("ALDialog")
        self.memory_service           = session.service("ALMemory")
        self.motion_service           = session.service("ALMotion")
        self.posture_service          = session.service("ALRobotPosture")
        self.speaking_movement        = session.service("ALSpeakingMovement")
        self.tablet_service           = session.service("ALTabletService")
        self.animation_player_service = session.service("ALAnimationPlayer")

        # INITIALISING CAMERA POINTERS
        self.imageNo2d = 1
        self.imageNo3d = 1

        # PUMP SPECS
        self.grsOn             = False
        self.pumpFound         = False
        self.pumpImgNo         = 0
        self.pumpAngleRotation = 0

        # GRAPHPLOT
        self.PLOTXMIN = -3
        self.PLOTXMAX =  3
        self.PLOTYMIN = -3
        self.PLOTYMAX =  3
        self.fig  = plt.figure()


    def _printLogs(self, log, pType):
        # PRINTING LOGS
        printObjects = ["NORMAL", "WARNING", "OKBLUE", "FAIL", "LINE"]

        if pType == "NORMAL":
            print str(log) + "\n"

        if pType == "WARNING":
            print Bcolors.WARNING + str(log) + Bcolors.ENDC + "\n"

        if pType == "OKBLUE":
            print Bcolors.OKBLUE + str(log) + Bcolors.ENDC + "\n"

        if pType == "FAIL":
            print Bcolors.BOLD + Bcolors.FAIL + str(log) + Bcolors.ENDC + "\n"

        if pType == "LINE":
            if log == "":
                print
            if log == "+":
                print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
            if log == "-":
                print "-------------------------------------------------------\n"
            if log == "=":
                print "=======================================================\n"

        if pType not in printObjects:
            # pType unknown, hence do normal print
            print str(log) + "\n"

        return


    def create_callbacks(self):
        self.connect_callback("capture_image_event",
                              self.capture_image_event)

        self.connect_callback("search_asthama_pump_event",
                              self.search_asthama_pump_event)
        return

    def connect_callback(self, event_name, callback_func):

        self._printLogs("Callback connection", "NORMAL")

        subscriber = self.memory_service.subscriber(event_name)
        subscriber.signal.connect(callback_func)
        self.subscribers_list.append(subscriber)

        return


    def _isAsthamaPump(self, imageWidth, imageHeight, imageString):
        result = {}
        coordinates = {}
        metadata = {}
        isPresent = False

        try :
            self._printLogs("Sending Image To DL Server...", "NORMAL")

            url = DL_SERVER_URL
            payload = {
                        "imageWidth"   : imageWidth,
                        "imageHeight"  : imageHeight,
                        "image_string" : base64.b64encode(imageString),
                        "imageID"      : self.imageNo2d
                        }
            headers = {'content-type': 'application/json'}

            res = requests.post(url, data=json.dumps(payload), headers=headers)
            result = res.json()
            self._printLogs("[*] Sent to  : " + str(url), "OKBLUE")
            self._printLogs("[*] Response : " + str(result), "OKBLUE")

        except Exception, err:
            self._printLogs("Error Found on connecting to server : " + str(err), "FAIL")
            self._printLogs("+", "LINE")

        if result and result["pumpFound"] :
            # print " *** Pump Found *** \n"
            self.pumpFound = True
            coordinates["x0"] = result["left"]
            coordinates["y0"] = result["top"]
            coordinates["x1"] = result["right"]
            coordinates["y1"] = result["bottom"]

            isPresent = True
        else :
            # print "Pump Not Found\n"
            self.pumpFound = False

        metadata["isPresent"] = isPresent
        metadata["coordinates"] = coordinates

        return metadata

    def _checkIfAsthamaInEnvironment(self, cameraId):
        self._printLogs("Capturing Image For Asthama Pump", "NORMAL")

        # Capture Image in RGB

        # WARNING : The same Name could be used only six time.
        strName = "capture2DImage_{}".format(random.randint(1,10000000000))

        clientRGB = self.video_service.subscribeCamera(strName, cameraId, AL_kVGA, 11, 10)
        imageRGB = self.video_service.getImageRemote(clientRGB)

        imageWidth   = imageRGB[0]
        imageHeight  = imageRGB[1]
        array        = imageRGB[6]
        image_string = str(bytearray(array))

        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)


        # CHECK IF ASTHAMA PUMP IS IN THE IMAGE OR NOT
        metadata = self._isAsthamaPump(imageWidth, imageHeight, image_string)
        res = metadata["isPresent"]
        coordinates = metadata["coordinates"]

        if res:
            # Creating Bounding Box
            x0 = float(coordinates["x0"])
            y0 = float(coordinates["y0"])
            x1 = float(coordinates["x1"])
            y1 = float(coordinates["y1"])

            draw = ImageDraw.Draw(im)
            draw.rectangle([(x0, y0), (x1, y1)], fill=None, outline = "red")
            del draw

            # Save the image.
            base_url = "/var/www/html/pepper_hack/images/" # your localhost server addr
            image_name_2d = base_url + "img2d-" + str(self.imageNo2d) + ".png"
            im.save(image_name_2d, "PNG") # Stored in images folder in the pwd, if not present then create one
            self.pumpImgNo = self.imageNo2d

        self.imageNo2d += 1

        return


    def _moveHand(self):

        JointNamesL = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
        JointNamesR = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]

        # ArmL/R
        # [   hand            { - : up, + : down }
        #     shoulder        { - : right side horizontal movement, + : left side horizontal movement }
        #     Palm rotation   { + : clockwise, - : anti-clockwise }
        #     Elbow movement  { + : right to left, - : left to right }
        # ]
        # these hand movements will only work if rotation are possible in those directions
        # ArmL1 = [-50,  30, 0, 0]
        # ArmL1 = [ x * motion.TO_RAD for x in ArmL1]

        ArmR1 = [0, 0, 50, 0]
        ArmR1 = [ x * motion.TO_RAD for x in ArmR1]

        pFractionMaxSpeed = 0.1
        self.motion_service.angleInterpolationWithSpeed(JointNamesR, ArmR1, pFractionMaxSpeed)

        return

    def _showOnTablet(self):
        # Display Image On Tablet
        base_url = "http://{}/pepper_hack/images/img2d-".format(NODE_IP)
        image_url = base_url + str(self.pumpImgNo) + ".png"
        try:
            self.tablet_service.showImageNoCache(image_url)
            self._printLogs("Displaying image : " + image_url, "OKBLUE")
            # Hide the web view , Clean Up Code
            # self.tablet_service.hideImage()
        except Exception, err:
            self._printLogs("Error Showing On Tablet : " + str(err), "FAIL")
            self._printLogs("+", "LINE")

        return

    def _moveHead(self, amntX, amntY):

        JointNamesH = ["HeadPitch", "HeadYaw"] # range ([-1,1],[-0.5,0.5]) // HeadPitch :{(-)up,(+)down} , HeadYaw :{(-)left,(+)right}
        pFractionMaxSpeed = 0.1
        HeadA = [float(amntY),float(amntX)]

        self.motion_service.angleInterpolationWithSpeed(JointNamesH, HeadA, pFractionMaxSpeed)

        return

    def _makePepperSpeak(self, userMsg):
        # MAKING PEPPER SPEAK
        # future = self.animation_player_service.run("animations/Stand/Gestures/Give_3", _async=True)
        sentence = "\RSPD="+ str( 100 ) + "\ "
        sentence += "\VCT="+ str( 100 ) + "\ "
        sentence += userMsg
        sentence +=  "\RST\ "
        self.tts.say(str(sentence))
        # future.value()

        return

    def _startImageCapturingAtGraphNode(self):
        amntY = 0.3
        xdir = [-0.5, 0, 0.5]
        cameraId = 0

        for idx,amntX in enumerate(xdir):
            self._moveHead(amntX, amntY)
            time.sleep(0.1)
            self._checkIfAsthamaInEnvironment(cameraId)
            if self.pumpFound :
                # Setting rotation angle of body towards head
                theta = 0
                if idx == 0: # LEFT
                    theta = math.radians(-45)
                if idx == 2: # RIGHT
                    theta = math.radians(45)
                self.pumpAngleRotation = theta

                return "KILLING GRAPH SEARCH : PUMP FOUND"

        self._moveHead(0, 0) # Bringing to initial view

        return

    def _transformTheta(self, theta):
        # CONVERTING THETA { THETA' % 360}
        if (float(theta) == math.radians(360)):
            theta = 0.0

        if (float(theta) == -(math.radians(360))):
            theta = 0.0

        if (float(theta) == math.radians(270)):
            theta = -math.pi/2

        if (float(theta) == -(math.radians(270))):
            theta = math.pi/2

        return theta

    def _turnTheta(self, theta, toward, withCapture):
        global PENDING_PHI

        theta = self._transformTheta(theta)

        if PENDING_PHI != 0:
            theta += PENDING_PHI
            PENDING_PHI = 0

        theta = self._transformTheta(theta)

        X = 0.0
        Y = 0.0
        Theta = theta

        y = 0
        x = False
        if float(theta) == 0.0 :
            self._printLogs("No need to turn : " + str(theta), "OKBLUE")
            x = True

        self._printLogs("Trying turning : " + str(toward), "OKBLUE")


        # while not x :
        #     if y > 1:
        #         print "Cant turn closing program"
        #         # need human intervention
        #         raw_input("Please align me in direction : "+ str(toward))
        #         break
        #
        #     print "Trying turning : ", toward
        #     x = motion_service.moveTo(X, Y, Theta)
        #     print "Turning Possible : ",x
        #     if not x:
        #         print "Trying again : ", theta
        #
        #     time.sleep(MOVEMENT_WAIT)
        #     y += 1


        if not x:
            y = self.motion_service.moveTo(X, Y, Theta)
            if not y:
                self._printLogs("Cant turn", "FAIL")
                self._printLogs("", "LINE")

                # need human intervention
                raw_input("Please align me in direction : " + str(toward)) + \
                " and press enter after it"
            else:
                self._printLogs("Turning complete with theta : " + str(theta), "OKBLUE")

        if withCapture and float(theta) != 0.0 :
            self._startImageCapturingAtGraphNode()

        return

    def _moveForward(self, distToMove):

        X = min(distToMove, ONEUNITDIST)  # forward
        Y = 0.0
        Theta = 0.0

        x = 0
        t0= time.time()

        # Blocking call
        a = self.motion_service.moveTo(X, Y, Theta)

        t1 = time.time()
        t = t1 -t0
        t *= 1000


        units = float(t) * (1.0 / TIME_CALIBERATED)
        # TIME_CALIBERATED is an average time per m length. Need to caliberate according to the flooring.

        resDist = 0
        if units >= 0.2:
            resDist = units

        if not a:
            self._printLogs("# OBSTACLE found in btw, bot moved dist : " + str(resDist), "NORMAL")
        else:
            self._printLogs("# Journey Complete : " + str(ONEUNITDIST), "NORMAL")

        if resDist != 0 :
            self._startImageCapturingAtGraphNode()


        # print "dist in m : ",units
        possible = True # movement possible in direction
        if units < 0.2:
            possible =  False
            units = ONEUNITDIST # NOT UPDATING AS OBSTCLE JUST IN FRONT HENCE WE DONT WANT 0 BTW GRID LINES

        return [possible , units]



    def _graphAlgo(self, x, y, pn, distArrived, actX, actY):
        global PHI
        global PENDING_PHI
        global MAX_NODES
        global NODES_COVERED
        global BX
        global BY

        phiArrived = PHI
        totalDeviationOnThisNode = 0
        NODES_COVERED += 1

        self._printLogs("=", "LINE")
        self._printLogs("Arrived at point : " + str(x) + " " + str(y), "WARNING")
        self._printLogs("=", "LINE")


        vis[(x,y)] = True

        dx = [-1, 0, 1, 0]
        dy = [0, 1, 0, -1]

        for i in range(4):
            x1 = x + dx[i]
            y1 = y + dy[i]

            if self.pumpFound :
                return "KILLING GRAPH SEARCH : PUMP FOUND"

            if abs(x1) >= BX or abs(y1) >= BY :
                self._printLogs("+", "LINE")
                self._printLogs("Coordinate restricted by user : " + str(x1) + " , " + str(y1), "WARNING")
                self._printLogs("+", "LINE")
                continue

            if (x1,y1) not in vis:
                self._printLogs("\n-> visiting  : " + str(x1) + " , " + str(y1), "WARNING")
                self._printLogs("", "LINE")
                if i == 0:
                    # TURN WEST
                    theta = math.pi/2
                    theta = PHI + theta
                    PHI = PHI - theta
                    totalDeviationOnThisNode = totalDeviationOnThisNode + theta
                    self._turnTheta(theta, "WEST", withCapture = True)

                    if self.pumpFound :
                        return "KILLING GRAPH SEARCH : PUMP FOUND"

                    # ===== FINDING DIST TO MOVE
                    distToMove = ONEUNITDIST

                    if (x,x1) in distBtwXaxisGridLines :
                        distToMove = distBtwXaxisGridLines[(x,x1)]

                    self._printLogs("\nDist to move forward  : " + str(distToMove), "OKBLUE")


                    metadata = self._moveForward(distToMove)
                    possible = metadata[0]
                    dist = metadata[1]

                    if distToMove == ONEUNITDIST: # updating new dist
                        distBtwXaxisGridLines[(x1,x)] = dist
                        distBtwXaxisGridLines[(x,x1)] = dist

                    # =====

                    if possible:
                        self._printLogs("Moving in left direction : Possible with dist : " + str(dist), "WARNING")

                        time.sleep(MOVEMENT_WAIT)

                        # as robot moved to these points
                        pointsX.append(actX + (dx[i] * dist))
                        pointsY.append(actY + (dy[i] * dist))

                        self._graphAlgo(x1, y1, [x,y], dist, actX + (dx[i] * dist), actY + (dy[i] * dist))

                        if self.pumpFound :
                            return "KILLING GRAPH SEARCH : PUMP FOUND"
                        if NODES_COVERED >= MAX_NODES :
                            return "KILLING GRAPH SEARCH : MAX NODES ACHIEVED"
                    else:
                        self._printLogs("Moving left : not possible : OBSTACLE", "OKBLUE")
                        time.sleep(MOVEMENT_WAIT)
                        vis[(x1,y1)] = True


                if i == 1:
                    # TURN NORTH
                    theta = 0
                    theta = PHI + theta
                    PHI = PHI - theta
                    totalDeviationOnThisNode = totalDeviationOnThisNode + theta
                    self._turnTheta(theta , "NORTH", withCapture = True)

                    if self.pumpFound :
                        return "KILLING GRAPH SEARCH : PUMP FOUND"

                    # ===== FINDING DIST TO MOVE
                    distToMove = ONEUNITDIST

                    if (y,y1) in distBtwYaxisGridLines :
                        distToMove = distBtwYaxisGridLines[(y,y1)]

                    self._printLogs("\nDist to move forward  : " + str(distToMove), "OKBLUE")

                    metadata = self._moveForward(distToMove)
                    possible = metadata[0]
                    dist = metadata[1]

                    if distToMove == ONEUNITDIST: # updating new dist
                        distBtwYaxisGridLines[(y1,y)] = dist
                        distBtwYaxisGridLines[(y,y1)] = dist

                    # =====

                    if possible:
                        self._printLogs("Moving in front direction : Possible with dist : " + str(dist), "WARNING")
                        time.sleep(MOVEMENT_WAIT)

                        # as robot moved to these points
                        pointsX.append(actX + (dx[i] * dist))
                        pointsY.append(actY + (dy[i] * dist))

                        self._graphAlgo(x1, y1, [x,y], dist, actX + (dx[i] * dist), actY + (dy[i] * dist))

                        if self.pumpFound :
                            return "KILLING GRAPH SEARCH : PUMP FOUND"
                        if NODES_COVERED >= MAX_NODES :
                            return "KILLING GRAPH SEARCH : MAX NODES ACHIEVED"
                    else:
                        self._printLogs("Moving front : not possible : OBSTACLE", "OKBLUE")
                        time.sleep(MOVEMENT_WAIT)
                        vis[(x1,y1)] = True

                if i == 2:
                    # TURN EAST
                    theta = -math.pi/2
                    theta = PHI + theta
                    PHI = PHI - theta
                    totalDeviationOnThisNode = totalDeviationOnThisNode + theta
                    self._turnTheta(theta , "EAST", withCapture = True)

                    if self.pumpFound :
                        return "KILLING GRAPH SEARCH : PUMP FOUND"

                    # ===== FINDING DIST TO MOVE
                    distToMove = ONEUNITDIST

                    if (x,x1) in distBtwXaxisGridLines :
                        distToMove = distBtwXaxisGridLines[(x1,x)]

                    self._printLogs("\nDist to move forward  : " + str(distToMove), "OKBLUE")

                    metadata = self._moveForward(distToMove)
                    possible = metadata[0]
                    dist = metadata[1]

                    if distToMove == ONEUNITDIST: # updating new dist
                        distBtwXaxisGridLines[(x1,x)] = dist
                        distBtwXaxisGridLines[(x,x1)] = dist

                    # =====

                    if possible:
                        self._printLogs("Moving in right direction : Possible with dist : " + str(dist), "WARNING")
                        time.sleep(MOVEMENT_WAIT)

                        # as robot moved to these points
                        pointsX.append(actX + (dx[i] * dist))
                        pointsY.append(actY + (dy[i] * dist))

                        self._graphAlgo(x1, y1, [x,y], dist, actX + (dx[i] * dist), actY + (dy[i] * dist))

                        if self.pumpFound :
                            return "KILLING GRAPH SEARCH : PUMP FOUND"
                        if NODES_COVERED >= MAX_NODES :
                            return "KILLING GRAPH SEARCH : MAX NODES ACHIEVED"
                    else:
                        self._printLogs("Moving right : not possible : OBSTACLE", "OKBLUE")
                        time.sleep(MOVEMENT_WAIT)
                        vis[(x1,y1)] = True

                if i == 3:
                    # TURN SOUTH # REMMEBER THESE ORIENTATIONS ARE RELATED TO ORIGINAL ORIENTATION
                    theta = math.pi
                    theta = PHI + theta
                    PHI = PHI - theta
                    totalDeviationOnThisNode = totalDeviationOnThisNode + theta
                    self._turnTheta(theta , "SOUTH", withCapture = True)

                    if self.pumpFound :
                        return "KILLING GRAPH SEARCH : PUMP FOUND"

                    # ===== FINDING DIST TO MOVE
                    distToMove = ONEUNITDIST

                    if (y,y1) in distBtwYaxisGridLines :
                        distToMove = distBtwYaxisGridLines[(y,y1)]

                    self._printLogs("\nDist to move forward  : " + str(distToMove), "OKBLUE")

                    metadata = self._moveForward(distToMove)
                    possible = metadata[0]
                    dist = metadata[1]

                    if distToMove == ONEUNITDIST: # updating new dist
                        distBtwYaxisGridLines[(y1,y)] = dist
                        distBtwYaxisGridLines[(y,y1)] = dist

                    # =====

                    if possible:
                        self._printLogs("Moving in backwards : Possible with dist : " + str(dist), "WARNING")
                        time.sleep(MOVEMENT_WAIT)

                        # as robot moved to these points
                        pointsX.append(actX + (dx[i] * dist))
                        pointsY.append(actY + (dy[i] * dist))

                        self._graphAlgo(x1, y1, [x,y], dist, actX + (dx[i] * dist), actY + (dy[i] * dist))

                        if self.pumpFound :
                            return "KILLING GRAPH SEARCH : PUMP FOUND"
                        if NODES_COVERED >= MAX_NODES :
                            return "KILLING GRAPH SEARCH : MAX NODES ACHIEVED"
                    else:
                        self._printLogs("Moving back : not possible : OBSTACLE", "OKBLUE")
                        time.sleep(MOVEMENT_WAIT)
                        vis[(x1,y1)] = True

            else :
                direct = ""
                if i == 0:
                    direct = "Left"
                if i == 1:
                    direct = "Front"
                if i == 2:
                    direct = "Right"
                if i == 3:
                    direct = "Back"

                self._printLogs("-> already visited : " + str(x1) + " , " + str(y1) + " was trying direction : " + direct, "WARNING")


        self._printLogs("Tried all directions all visited should go back to previous node i.e. : " + str(pn), "WARNING")

        self._printLogs("Node : " + str(x) + " , " + str(y) + " completely explored ---\n", "WARNING")



        PHI = phiArrived
        theta = - totalDeviationOnThisNode


        if x == 0 and y == 0:  # should not go back to any point from coordinate(0,0) as there is nothing.
            self._turnTheta(theta, "TURN-AROUND : ORIGINAL ORIENTATION FOR NODE", withCapture = False)
            return "Succesfully Completed Exploration"

        if self.pumpFound :
            return "KILLING GRAPH SEARCH : PUMP FOUND"

        theta += math.pi # CALCULATING TOTAL DEVIATION TO GO BACK TO PREVIOUS NODE
        self._turnTheta(theta , "TURN-AROUND : TO GO BACK \n", withCapture = True)

        if self.pumpFound :
            return "KILLING GRAPH SEARCH : PUMP FOUND"

        self._printLogs("Moving dist to go back : " + str(distArrived), "WARNING")
        metadata = self._moveForward(distArrived)
        possible = metadata[0]


        if possible:
            self._printLogs("Moving Back : possible", "WARNING")
            time.sleep(MOVEMENT_WAIT)
        else:
            self._printLogs("Cannot move back to previous state", "FAIL")
            sys.exit()

        self._printLogs("", "LINE")
        theta = -math.pi
        PENDING_PHI += theta
        # self._turnTheta(theta , "Turning Around again to orientation where it left the present arrived node", withCapture = False)

        if self.pumpFound :
            return "KILLING GRAPH SEARCH : PUMP FOUND"

        self._printLogs("=", "LINE")
        self._printLogs("Arrived at point : " + str(pn) + ", After further exploration ===", "WARNING")
        self._printLogs("=", "LINE")


        # as robot moved to these points
        pointsX.append(pn[0])
        pointsY.append(pn[1])

        self._printLogs("GRAPH SEARCH FOR NODE : " + str(x) + " , " + str(y) + " COMPLETE ========================\n\n", "WARNING")

        return


    def _startAsthamaPumpFoundProcedures(self):
        # After Finding Asthama Pump; Procedures To Follow
        global PENDING_PHI
        theta = self.pumpAngleRotation

        # TEMPORARY RESETING
        pending_phi = PENDING_PHI
        PENDING_PHI = 0
        self._turnTheta(theta, "TOWARDS ASTHAMA PUMP", withCapture = False)

        self._showOnTablet()
        user_msg = "Yaayy ! I found Asthama Pump"
        self._moveHand()
        self._makePepperSpeak(user_msg)
        self.posture_service.goToPosture("StandInit", 0.3)

        time.sleep(10)
        # Hide the web view
        self.tablet_service.hideImage()

        # TEMPORARY RESETING OVER
        PENDING_PHI = pending_phi
        self._turnTheta(-theta, "TOWARDS ORIGINAL DIRECTION", withCapture = False)
        self.pumpAngleRotation = 0

        return

    def startAsthamaPumpSearch(self):
        if not self.grsOn :
            self.pumpFound = False
            self.grsOn = True

            self._startImageCapturingAtGraphNode()

            if not self.pumpFound : # Only go on search when pump not present in front
                self._printLogs("- - - Starting Exploring - - -", "NORMAL")
                X = 0
                Y = 0
                dist = 0
                parentInit = [-1, -1]

                res = self._graphAlgo(X, Y, parentInit, dist, X, Y)
                self._printLogs("--- GRAPH SEARCH Process Complete --- : " + str(res), "OKBLUE")

            self._moveHead(0, 0) # Bringing to initial view

            if self.pumpFound :
                self._printLogs("\nFound Asthama Pump in GRAPH SEARCH", "FAIL")
                self._printLogs("", "LINE")
                self._startAsthamaPumpFoundProcedures()
            else :
                self._printLogs("Could Not Find Asthama Pump", "NORMAL")
                self._makePepperSpeak("Sorry ! I could not find aasthaama pump")

            self.grsOn = False
        else :
            self._printLogs("Already Searching", "FAIL")

        return

    def search_asthama_pump_event(self, value):
        self._printLogs("Searching Asthama Pump : " + str(value), "NORMAL")
        try:
            self.startAsthamaPumpSearch()
        except KeyboardInterrupt:
            self._printLogs("KeyBoard Interrupt initiated", "FAIL")
            self.motion_service.stopMove()
            return

        time.sleep(1)

        return

    def _capture2dImage(self, cameraId):
        # Capture Image in RGB

        # WARNING : The same Name could be used only six time.
        strName = "capture2DImage_{}".format(random.randint(1,10000000000))

        clientRGB = self.video_service.subscribeCamera(strName, cameraId, AL_kVGA, 11, 10)
        imageRGB = self.video_service.getImageRemote(clientRGB)

        imageWidth   = imageRGB[0]
        imageHeight  = imageRGB[1]
        array        = imageRGB[6]
        image_string = str(bytearray(array))

        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

        # Save the image.
        image_name_2d = "images/img2d-" + str(self.imageNo2d) + ".png"
        im.save(image_name_2d, "PNG") # Stored in images folder in the pwd, if not present then create one
        self.imageNo2d += 1
        im.show()

        return

    def _capture3dImage(self):
        # Depth Image in RGB

        # WARNING : The same Name could be used only six time.
        strName = "capture3dImage_{}".format(random.randint(1,10000000000))


        clientRGB = self.video_service.subscribeCamera(strName, AL_kDepthCamera, AL_kQVGA, 11, 10)
        imageRGB = self.video_service.getImageRemote(clientRGB)

        imageWidth  = imageRGB[0]
        imageHeight = imageRGB[1]
        array       = imageRGB[6]
        image_string = str(bytearray(array))

        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)
        # Save the image.
        image_name_3d = "images/img3d-" + str(self.imageNo3d) + ".png"
        im.save(image_name_3d, "PNG") # Stored in images folder in the pwd, if not present then create one
        self.imageNo3d += 1
        im.show()

        return

    def capture_image_event(self, value):
        self._printLogs("Capturing Image : " + str(value), "NORMAL")

        if str(value) == "2d":
            cameraId = 0 # DEFAULT TOP
            self._capture2dImage(cameraId)

        if str(value) == "3d":
            self._capture3dImage()

        time.sleep(1)
        return


    def _updateAxes(self, x, y):

        if x >= self.PLOTXMAX :
            self.PLOTXMAX += x
        if x <= self.PLOTXMIN :
            self.PLOTXMIN += x
        if y >= self.PLOTYMAX :
            self.PLOTYMAX += y
        if y <= self.PLOTYMIN :
            self.PLOTYMIN += y

        plt.xlim(self.PLOTXMIN, self.PLOTXMAX)
        plt.ylim(self.PLOTYMIN, self.PLOTYMAX)

        return

    def _animate(self, i):
        cord = (pointsX[:i+1], pointsY[:i+1])
        self.graph.set_data(cord)
        self._updateAxes(cord[0][-1], cord[1][-1])

        return self.graph

    def _initialisePlot(self):

        plt.rc('grid', linestyle=":", color='black')
        plt.rcParams['axes.facecolor'] = 'black'
        plt.rcParams['axes.edgecolor'] = 'white'
        plt.rcParams['grid.alpha'] = 1
        plt.rcParams['grid.color'] = "green"
        plt.grid(True)
        plt.xlim(self.PLOTXMIN, self.PLOTXMAX)
        plt.ylim(self.PLOTYMIN, self.PLOTYMAX)
        self.graph, = plt.plot([], [], 'o')

        return


    def _addTopic(self):

        self._printLogs("Starting topic adding process", "NORMAL")

        # disabling hand gestures and movement while speaking
        self.speaking_movement.setEnabled(False)

        self.dialog_service.setLanguage("English")
        # Loading the topic given by the user (absolute path is required)
        topic_path = "/home/nao/chat/asthama_search.top"

        topf_path = topic_path.decode('utf-8')
        self.topic_name = self.dialog_service.loadTopic(topf_path.encode('utf-8'))

        # Activating the loaded topic
        self.dialog_service.activateTopic(self.topic_name)

        # Starting the dialog engine - we need to type an arbitrary string as the identifier
        # We subscribe only ONCE, regardless of the number of topics we have activated
        self.dialog_service.subscribe('asthama_search_example')

        self._printLogs("\nSpeak to the robot using rules. Robot is ready", "NORMAL")

        return

    def _cleanUp(self):

        self._printLogs("Starting Clean Up process", "FAIL")

        # Stopping any movement if there
        self.motion_service.stopMove()
        # stopping the dialog engine
        self.dialog_service.unsubscribe('asthama_search_example')
        # Deactivating the topic
        self.dialog_service.deactivateTopic(self.topic_name)

        # now that the dialog engine is stopped and there are no more activated topics,
        # we can unload our topic and free the associated memory
        self.dialog_service.unloadTopic(self.topic_name)

        # Hide the web view
        self.tablet_service.hideImage()

        self.posture_service.goToPosture("StandInit", 0.1)

        return



    def run(self):
        self._printLogs("Waiting for the robot to be in wake up position", "OKBLUE")

        self.motion_service.wakeUp()
        self.posture_service.goToPosture("StandInit", 0.1)

        self.create_callbacks()
        # self.startDLServer()
        self._addTopic()

        # graphplots
        self._initialisePlot()
        ani = animation.FuncAnimation(self.fig, self._animate, blit=False, interval=500 ,repeat=False)


        # loop on, wait for events until manual interruption
        try:
            # while True:
            #     time.sleep(1)
            # starting graph plot
            plt.show() # blocking call hence no need for while(True)

        except KeyboardInterrupt:
            self._printLogs("Interrupted by user, shutting down", "FAIL")
            self._cleanUp()

            self._printLogs("Waiting for the robot to be in rest position", "FAIL")
            # self.motion_service.rest()
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
    app = qi.Application(["AsthamaDetector",
                          "--qi-url=" + connection_url])

    object_detector = AsthamaDetector(app)
    object_detector.run()
