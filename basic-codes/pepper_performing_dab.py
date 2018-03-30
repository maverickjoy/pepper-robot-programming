import qi
import argparse
import motion
import sys

def userArmArticular(motion_service, tts):
    # Arms motion from user have always the priority than walk arms motion

    JointNamesL = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
    JointNamesR = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]

    # [    hand{-:up,+:down} | shoulder{-:right side horizontal movement,+:left side horizontal movement}
    #    | Palm rotation{+:clockwise,-:anti-clockwise} |   Elbow movement{+:right to left,-:left to right}  ]
    # these hand movements will only work if rotation are possible in those directions


    JointNamesH = ["HeadPitch","HeadYaw"] # range ([-1,1],[-0.5,0.5]) // HeadPitch :{(-)up,(+)down} , HeadYaw :{(-)left,(+)right}

    ArmL1 = [-50,  30, 0, 0]
    ArmL1 = [ x * motion.TO_RAD for x in ArmL1]

    ArmR1 = [-50,  30, 0, 40]
    ArmR1 = [ x * motion.TO_RAD for x in ArmR1]

    ArmR2 = [-40,  50, 0, 80]
    ArmR2 = [ x * motion.TO_RAD for x in ArmR2]

    pFractionMaxSpeed = 0.5

    HeadA = [0.1,0.3] # dont make more than 0.1 for these combinations as it can bang its head with the arm

    motion_service.angleInterpolationWithSpeed(JointNamesL, ArmL1, pFractionMaxSpeed)
    motion_service.angleInterpolationWithSpeed(JointNamesR, ArmR1, pFractionMaxSpeed)
    motion_service.angleInterpolationWithSpeed(JointNamesR, ArmR2, pFractionMaxSpeed)
    motion_service.angleInterpolationWithSpeed(JointNamesH, HeadA, pFractionMaxSpeed)
    tts.say("Dabb !")

    return

def main(session):
    """
    Use the goToPosture Method to PoseZero.
    Set all the motors of the body to zero.
    """
    # Get the services ALMotion, ALRobotPosture & ALTextToSpeech.

    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")
    tts = session.service("ALTextToSpeech")

    # Wake up robot
    motion_service.wakeUp()

    posture_service.goToPosture("StandInit", 0.5)
    userArmArticular(motion_service, tts)


    print " --- Over --- "
    time.sleep(3)
    # Go to rest position
    motion_service.rest()

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
