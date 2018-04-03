import qi
import argparse
import sys
import numpy
import time
import math

def moveForward(motion_service):
    X = 1  # forward
    Y = 0.0
    Theta = 0.0

    print "Movement Starting"
    t0= time.time()

    # Blocking call
    possible = motion_service.moveTo(X, Y, Theta)

    t1 = time.time()

    timeDiff = t1 -t0
    timeDiff *= 1000

    if not possible:
        return -1

    # if not possible:
    #     print "Interruption case Time : ",timeDiff
    # else:
    #     print "Journey over Time : ",timeDiff

    return timeDiff


def turnTheta(motion_service,theta):
    X = 0.0 # forward
    Y = 0.0
    Theta = theta
    res = motion_service.moveTo(X, Y, Theta)
    return res

def main(session):
    navigation_service = session.service("ALNavigation")
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    # Wake up robot
    motion_service.wakeUp()
    posture_service.goToPosture("StandInit", 0.1)
    motion_service.moveInit()

    listOfTime = []
    print "Starting Calculation : "
    noOfIterations = 3


    for i in xrange(noOfIterations * 2):
        units = 0
        units = moveForward(motion_service)

        if units == -1:
            print "OBSTACLE In between Caliberation INCOMPLETE EXITING"
            exit()

        listOfTime.append(units)
        time.sleep(2)
        res = _turnTheta(motion_service,math.pi)

        if not res :
            print "OBSTACLE In between Caliberation INCOMPLETE EXITING"
            exit()

        time.sleep(2)

    avgUnits = 0

    for unitTime in listOfTime :
        print "Unit Time : ",unitTime
        avgUnits += unitTime

    avgUnits /= (noOfIterations * 2)

    print "Caliberation Succesfull Time Units : ",avgUnits

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
