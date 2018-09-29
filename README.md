Requirements:
1. A machine with nividia GPU with >4GB memory to run two docker containers.
2. install nvidia-docker
3. pip install -r flask_demo_app/requirements.txt

Set following environment variables; 
export DETECTRON_URL='http://<ip addr>:8085/detetron'

export SCENEGRAPH_URL='http://<ip addr>:8080/sg_srvc'

sudo nvidia-docker run -d --name detectron_srvc -p 8085:8085 aniketadnaik/detectron_srvc:version1

sudo nvidia-docker run -d --name sg_srvc -p 8080:8080 aniketadnaik/sg_srvc:version1

cd flask_demo_app/images
python -m SimpleHTTPServer 7400 &

cd flask_demo_app
python client.py
( This will start a flask app listening on "0.0.0.0:8181" )
Open http://0.0.0.0:8181 on the host machine running client.py.
Enter URL with a complete IP address.
Example:  http://<xx.xxx.xx.xx>:7400/1.jpg or 2.jpg
Currently only 2 images are served as an example.
Note : Do not use localhost:7400 or 127.0.0.1:7400
