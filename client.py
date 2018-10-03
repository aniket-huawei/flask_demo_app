#!/usr/bin/env python2
# -*- coding: utf-8 -*-

################################################################
#
# This flask application would take image url as an input and  
# invoke scene graph generation in the background. Once 
# scene graph is generated it will be display on the web page. 
#
# Author: Aniket Adnaik (aniket.adnaik@huawei.com)
################################################################
import os
import requests
import uuid
import pdb
from flask import Flask, render_template, request, url_for
from scripts import url_tools
from os.path import basename, splitext
import urllib3
import pickle
import json
import cv2

#define some globals
APP_ROOT= os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, root_path=APP_ROOT, static_url_path='/static')

FLASK_DOWNLOAD_DIR = './static/'
FLASK_SG_OUTPUT_DIR = './sg_output/'
IMAGE_EXT = 'jpg'

#DETECTRON_URL = 'http://0.0.0.0:8085/detectron'
#SCENEGRAPH_URL = 'http://0.0.0.0:8080/sg_srvc'


def cleanup_files():
    [os.remove(os.path.join(os.path.abspath(FLASK_DOWNLOAD_DIR),file)) for file in os.listdir(FLASK_DOWNLOAD_DIR) if file.endswith('.jpg')]

def adjust_bbox_scale(image_size, sub_bbox_list, obj_bbox_list):
    # Get image height, width
    new_w = image_size['W']
    new_h = image_size['H']
    x_scale = float(new_w)/float(img_w)
    y_scale = float(new_h)/float(img_h)

    #print x_scale, y_scale
    xmin_adj = np.round(int(xmin.text)*x_scale)
    ymin_adj = np.round(int(ymin.text)*y_scale)
    xmax_adj = np.round(int(xmax.text)*x_scale)
    ymax_adj = np.round(int(ymax.text)*y_scale)
    p_xmin_adj = np.round(int(person[1][0])*x_scale)
    p_ymin_adj = np.round(int(person[1][1])*y_scale)
    p_xmax_adj = np.round(int(person[1][2])*x_scale)
    p_ymax_adj = np.round(int(person[1][3])*y_scale)


def draw_boundingbox(image_path, image_size, coordinates_list):
    #image_rgb = cv2.imread(image_name)
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    PURPLE = (255, 0, 255)
    YELLOW = (0, 255, 255)

    img = cv2.imread(image_path)
    image_rgb = cv2.resize(img, (image_size['W'], image_size['H']))
    image_id = splitext(basename(image_path))[0]+'.jpg'
    cv2.putText(image_rgb, str(image_id), (40,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 255, 155), 2)

    for idx in range(len(coordinates_list)):
        if coordinates_list[idx][-1] == True:
            cv2.rectangle(image_rgb, (int(coordinates_list[idx][0]), int(coordinates_list[idx][1])),
               (int(coordinates_list[idx][2]), int(coordinates_list[idx][3])), PURPLE, 2)
        else:
            cv2.rectangle(image_rgb, (int(coordinates_list[idx][0]), int(coordinates_list[idx][1])),
                          (int(coordinates_list[idx][2]), int(coordinates_list[idx][3])), YELLOW, 2)
#    cv2.imshow(image_id + '_bndbox', image_rgb)
    image_write_path, image_ext = splitext(image_path)
    image_write_path = image_write_path + '_bbox'+ image_ext 
    cv2.resize(image_rgb, (512, 512))
    cv2.imwrite(image_write_path, image_rgb)
    return image_write_path
#    cv2.waitKey(1500)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()

#setup index page
@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
   
    if request.method == "POST":
        # Cleanup previous residual files
        cleanup_files()

        # get url that the user has entered
        try:
            url_path = request.form['url']
            if not url_tools.validate_url(url_path):
                return render_template('index.html')
            http = urllib3.PoolManager()

            pdb.set_trace()
            res = http.request('POST', DETECTRON_URL, fields={'url':url_path})
            cls_boxes = res.data 

            # Get scene graph data from Scen graph serice for a given image url 
            if cls_boxes:
                sg_res = http.request('POST', SCENEGRAPH_URL, fields={'url':url_path, 'data':cls_boxes})
                if (sg_res.status == 200):
                    sg_data = json.loads(sg_res.data)
                    if sg_data:
                        #Draw bounding boxes
                        coordinates_list = sg_data['sub_bbox_list'] + sg_data['obj_bbox_list']
                        image_size_list = sg_data['image_info'][2]
                        image_2_path = draw_boundingbox(download_path, image_size_list, coordinates_list)
                        # Generate unique file name to store the image
                        unique_file_name = uuid.uuid4().hex
                        download_path = os.path.join(FLASK_DOWNLOAD_DIR, unique_file_name + "." + IMAGE_EXT)
                        print (download_path)
                        url_tools.download_image(url_path, download_path) 
                        _, d_file_name = os.path.split(download_path)
                        abs_path_image = os.path.abspath(download_path)
                elif (sg_res.status == 204):
                    errors.append('No scene graph generated for this image. Please enter another url')
                    return render_template('index.html', errors=errors, results=results)
                else:
                    errors.append('Scene graph generation failed. Please enter another url')
                    return render_template('index.html', errors=errors, results=results)
            else:
                return render_template('index.html', msg='Could not generate region proposals info.')


            return render_template('plot_image.html', user_image1=download_path, user_image2=image_2_path) #, user_image3=None)
        except:
            errors.append(
                 "Unable to get URL. please make sure it's valid and try again"
                )
    return render_template('index.html', errors=errors, results=results)

#Run the app server
if __name__ == '__main__':
    try:
        DETECTRON_URL = os.environ['DETECTRON_URL']
        SCENEGRAPH_URL = os.environ['SCENEGRAPH_URL']
    except:
        print ('Please set environment variable: DETECTRON_URL=http://<ip addr>:8085/detectron')
        print ('Please set enviroment variable: SCENEGRAPH_URL=http://<ip addr>:8080/sg_srvc')
        exit(-1)
    app.run( port=int('8181'), host='0.0.0.0')
#    app.run( port=int('8181'), host='0.0.0.0', debug=True)
