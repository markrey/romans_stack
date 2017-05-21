## Prerequsites

If you just want to run the 
#### demo .
Install caffe and pycaffe: http://caffe.berkeleyvision.org/install_apt.html

If you also want to run our 
#### live demo.
In this implementation, MS kinect v2 is used unde Ubuntu through iai kinect2 package, so install iai_kinect2 following their instructions : https://github.com/code-iai/iai_kinect2 .

If you also want to 
#### train the models from the scrach.
Install GPy (http://sheffieldml.github.io/GPy/): 
```
$ sudo pip install --upgrade pip
$ sudo pip install GPy
```

If you also want to do comprision 
#### experiments 
using R-CNN.

Install SVM and Python interface: https://www.csie.ntu.edu.tw/~cjlin/libsvm/ .
```
$ cd ~
$ git clone https://github.com/cjlin1/libsvm.git
$ cd libsvm & make & cd python & make
```
Add libsvm to the python path:
```
$ export PYTHONPATH=/home/kevin/libsvm/python:$PYTHONPATH
```

## Dependencies:
#### ROS
Install [ROS Indigo] http://wiki.ros.org/indigo/Installation/Ubuntu .
#### GNU Scientific Library (GSL).
```
sudo apt-get install libgsl0-dev
```

## Install romans_stack
1. Create a catkin workspace:
```
$ mkdir ~/catkin_ws/src
$ cd ~/catkin_ws/src
```

2. Create .rosinstall file and copy the followings:
```
- git: {local-name: romans_stack, uri: 'git@bitbucket.org:kevinlisun/romans_stack.git', version: master}
- git: {local-name: iai_kinect2, uri: 'https://github.com/code-iai/iai_kinect2', version: master}
```
Clone the repositories:
```
$ wstool update
$ rosdep install --from-paths src --ignore-src -r -y
$ cd ..
```
3. Compile:
```
$ catkin_make -DCMakeType=RELEASE
```
4. Add ROS workspace to the environment
add `source ~/catkin_ws/devel/setup.bash` to ~/.bashrc

## Run the Demo
Download the demo data (demo.rosbag file) and the trained caffe model (deploy.proto, romans_model_fast.caffemodel) from: https://drive.google.com/open?id=0B0jMesRKPfw9MGM4ekxiV2M1RWs
This demo assumes you download the 'romans' folder and put it under home directory (cd ~), change the directory depending your situation.

1. Get RGBD stream from rosbag .
```
$ roslaunch camera kinect2_simulator.launch
$ cd ~/romans/data & rosbag play --clock demo.bag
```

  #### Or
  get RGBD stream from kinect2
```
$ roslaunch camera kinect2.launch
```

2. Run detection node .
```
$ rosrun odr detection_server_kinect2
```

3. Run recognition node .
```
$ rosrun odr inference_end2end.py /home/your_username/romans/models/rgbd_net_fast
```

4. Run visualization node .
```
$ rosrun odr visualization_server
```

5. Run the client .
```
$ rosrun odr odr_test.py kinect2
```

## Programming Style

This implementation is following:
ROS C++ stype: http://wiki.ros.org/CppStyleGuide
Python REP8 style: http://www.ros.org/reps/rep-0008.html
