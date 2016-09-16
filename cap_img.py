import logging
import errno,time
import httplib,urllib,base64,re,os
import struct
import cv2
import numpy as np
import sys

key = 'MSAPI-keyxxxxxxxxxxxxxxxxxxxxxxxx'
cam_device = 0

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s (%(threadName)-10s) %(message)s',
                    )

def cap_img():
    while True:
        capture = cv2.VideoCapture(cam_device)

        if capture.isOpened() is False:
            logging.debug("IO Error: camera cannot open")
            logging.debug("Ending")
            exit()

        while True:
            ret, img = capture.read()
            if ret == False:
                continue
            break

        ## save img
        # timestr = time.strftime("%Y%m%d-%H%M%S")
        # f_name = './img/img-%s.jpg'%timestr
        # try:
            # cv2.imwrite(f_name,img)
        # except:
            # pass

        headers = {
            # Request headers
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': key,
        }

        params = urllib.urlencode({
            # Request parameters
            # 'faceRectangles': '',
        })
        img_arr=cv2.cv.fromarray(img)
        encimg=cv2.cv.EncodeImage('.jpg',img_arr).tostring()
        logging.debug('asking MS API')
        conn = httplib.HTTPSConnection('api.projectoxford.ai')
        try:
            conn.connect()
        except Exception as e:
            logging.debug('some error-')
            capture.release()
            time.sleep(1)
            continue
        conn.request("POST", "/emotion/v1.0/recognize?%s" % params, encimg, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        pattern = re.compile(r'"height":(.*?),"left":(.*?),"top":(.*?),"width":(.*?)},"scores":{"anger":(.*?),"contempt":(.*?),"disgust":(.*?),"fear":(.*?),"happiness":(.*?),"neutral":(.*?),"sadness":(.*?),"surprise":(.*?)}}')
        iterator = pattern.finditer(data)
        try:
            match = iterator.next()
        except Exception as e:
            logging.debug('no face found')
            capture.release()
            time.sleep(1)
            continue

        faceRectangle = [
            ['height',to_int(match.group(1))],
            ['left',to_int(match.group(2))],
            ['top',to_int(match.group(3))],
            ['width',to_int(match.group(4))],
        ]
        scores = [
            ['anger',to_int(match.group(5))],
            ['contempt',to_int(match.group(6))],
            ['discust',to_int(match.group(7))],
            ['fear',to_int(match.group(8))],
            ['happiness',to_int(match.group(9))],
            ['neutral',to_int(match.group(10))],
            ['sadness',to_int(match.group(11))],
            ['surprise',to_int(match.group(12))],
        ]

        ## show highest parameter --------------------------
        scores.sort(key=lambda x:x[1],reverse=True)
        logging.debug('conf:%s,emo:%s'%(scores[0][0],scores[0][1]))
        ## show specific parameter --------------------------
        # logging.debug('conf:%s,emo:%s'%(scores[4][0],scores[4][1]))  ## show happy
        
        capture.release()
        time.sleep(1)
        
def to_int(num_org):
    if num_org.rfind('E') > -1:
        n = 0
    else:
        n = num_org
    return n

if __name__ == "__main__":
	cap_img()