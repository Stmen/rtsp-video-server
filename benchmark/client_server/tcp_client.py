#!/usr/bin/env python

import socket
from time import sleep

import subprocess32 as subprocess

HOST_PORT = ('10.42.0.1', 15555)

# socket buffer size
BUFFER_SIZE = 1024


# wait for data from the socket
def wait_for_data(sock, sleep_sec=1):
    data = ''
    while data == '':
        data = sock.recv(BUFFER_SIZE)
        sleep(sleep_sec)
    return data


if __name__ == '__main__':

    sleep(60 * 140)

    with open('left_camera_output.log', 'w') as left_cam_logfile:

        with open('right_camera_output.log', 'w') as right_cam_logfile:

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect(HOST_PORT)

            while True:

                print "Waiting for command form server..."

                server_data = wait_for_data(s)

                print "Command: {}".format(server_data)

                server_data = server_data.replace('<replace>', '{}')

                if server_data == 'KILL':
                    break
                else:

                    while True:

                        try:

                            print "Launch openRTSP for the left camera ..."

                            open_rtsp_left_process = subprocess.Popen(server_data.format('left', 'left_cam').split(),
                                                                      stdout=left_cam_logfile,
                                                                      stderr=left_cam_logfile)

                            print "Launch openRTSP for the right camera ..."

                            open_rtsp_right_process = subprocess.Popen(server_data.format('right', 'right_cam').split(),
                                                                       stdout=right_cam_logfile,
                                                                       stderr=right_cam_logfile)

                            print "Waiting for processes to finish..."

                            exit_codes = [p.wait() for p in open_rtsp_left_process, open_rtsp_right_process]

                            print 'Exit codes:', exit_codes

                            success_codes = [e for e in exit_codes if e == 0]

                            if len(success_codes) != 2:
                                raise Exception('Exit codes are not all zeros - openRTSP')

                            print "Send FINISHED signal ..."
                            break
                        except Exception as e:
                            print str(e)
                            print "Retrying..."
                            sleep(5)

                    s.sendall("FINISHED")
    s.close()
