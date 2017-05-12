#!/usr/bin/python

# -*- coding: utf-8 -*-
# @Author: Kevin Sun
# @Date:   2016-11-03 20:24:43
# @Last Modified by:   Kevin Sun
# @Last Modified time: 2016-11-06 23:49:03


import caffe
from caffe import layers as L, params as P


def conv_relu(name, bottom, nout, ks=3, stride=1, pad=1, group=1, lr1=1, lr2=2):
    conv = L.Convolution(bottom, kernel_size=ks, stride=stride,
        num_output=nout, pad=pad, group=group, weight_filler=dict(type='xavier'),
        param=[dict(name=name+"_w", lr_mult=lr1, decay_mult=1), dict(name=name+"_b", lr_mult=lr2, decay_mult=0)])
    return conv, L.ReLU(conv, in_place=True)

def fc(bottom, nout, lr1=1, lr2=2, filler_type='xavier'):
    ip = L.InnerProduct(bottom, num_output=nout, weight_filler=dict(type=filler_type),
      param=[dict(lr_mult=lr1, decay_mult=1), dict(lr_mult=lr2, decay_mult=0)])
    return ip

def fc_relu(bottom, nout, lr1=1, lr2=2, filler_type='xavier'):
    ip = L.InnerProduct(bottom, num_output=nout, weight_filler=dict(type=filler_type),
      param=[dict(lr_mult=lr1, decay_mult=1), dict(lr_mult=lr2, decay_mult=0)])
    return ip, L.ReLU(ip, in_place=True)

def max_pool(bottom, ks=2, stride=2):
    return L.Pooling(bottom, pool=P.Pooling.MAX, kernel_size=ks, stride=stride)

def ave_pool(bottom, ks=2, stride=2):
    return L.Pooling(bottom, pool=P.Pooling.AVE, kernel_size=ks, stride=stride)

def cnn(split):
    n = caffe.NetSpec()
    pydata_params = dict(dataset_dir='/home/kevin/dataset/rgbd', split=split, mean=(104.00698793, 116.66876762, 122.67891434),
            seed=1337, img_size=(224,224), crop_size=(224,224,224,224))
    
    if split == 'train':
        pylayer = 'RGBDDataLayer'
	pydata_params['randomize'] = True
	pydata_params['batch_size'] = 64
    elif split == 'test':
	pylayer = 'RGBDDataLayer'
	pydata_params['randomize'] = False
	pydata_params['batch_size'] = 1
    else:
        n.img = L.Input(name='input', ntop=2, shape=[dict(dim=1),dict(dim=1),dict(dim=224),dict(dim=224)])


    #---------------------------------Data Layer---------------------------------------#
    n.rgb, n.depth, n.label = L.Python(name="data", module='data_layers.rgbd_data_layer', layer=pylayer,
            ntop=3, param_str=str(pydata_params))


    #---------------------------------RGB-Net---------------------------------------#
    # the caffe-net (alex-net)
    n.rgb_conv1, n.rgb_relu1 = conv_relu("rgb_conv1", n.rgb, 96, ks=11, stride=4, pad=0)
    n.rgb_pool1 = max_pool(n.rgb_relu1, ks=3)
    n.rgb_norm1 = L.LRN(n.rgb_pool1, lrn_param=dict(local_size=5, alpha=0.0005, beta=0.75, k=2))

    n.rgb_conv2, n.rgb_relu2 = conv_relu("rgb_conv2", n.rgb_norm1, 256, ks=5, pad=2, group=2)
    n.rgb_pool2 = max_pool(n.rgb_relu2, ks=3)
    n.rgb_norm2 = L.LRN(n.rgb_pool2, lrn_param=dict(local_size=5, alpha=0.0005, beta=0.75, k=2))

    n.rgb_conv3, n.rgb_relu3 = conv_relu("rgb_conv3", n.rgb_norm2, 384, ks=3, pad=1, lr1=1, lr2=2)
    n.rgb_conv4, n.rgb_relu4 = conv_relu("rgb_conv4", n.rgb_relu3, 384, ks=3, pad=1, group=2, lr1=1, lr2=2)

    n.rgb_conv5, n.rgb_relu5 = conv_relu("rgb_conv5", n.rgb_relu4, 256, ks=3, pad=1, group=2, lr1=1, lr2=2)
    n.rgb_pool5 = max_pool(n.rgb_relu5, ks=3)

    # fully conv
    n.rgb_fc6, n.rgb_relu6 = fc_relu(n.rgb_pool5, 4096, lr1=1, lr2=2)
    n.rgb_drop6 = L.Dropout(n.rgb_relu6, dropout_ratio=0.5, in_place=True)
    n.rgb_fc7, n.rgb_relu7 = fc_relu(n.rgb_drop6, 4096, lr1=1, lr2=2)
    n.rgb_drop7 = L.Dropout(n.rgb_relu7, dropout_ratio=0.5, in_place=True)

    n.rgb_fc8 = fc(n.rgb_drop7, 11, lr1=0, lr2=0)

    #---------------------------------Depth-Net---------------------------------------#

    # the base net
    n.depth_conv1, n.depth_relu1 = conv_relu("depth_conv1", n.depth, 128, ks=5, stride=2, pad=2, lr1=1, lr2=2)
    n.depth_pool1 = max_pool(n.depth_relu1, ks=3)
    n.depth_norm1 = L.LRN(n.depth_pool1, lrn_param=dict(local_size=5, alpha=0.0005, beta=0.75, k=2))

    n.depth_conv2, n.depth_relu2 = conv_relu("depth_conv2", n.depth_norm1, 256, ks=5, stride=1, pad=2, lr1=1, lr2=2)
    n.depth_pool2 = max_pool(n.depth_relu2, ks=3)
    n.depth_norm2 = L.LRN(n.depth_pool2, lrn_param=dict(local_size=5, alpha=0.0005, beta=0.75, k=2))

    n.depth_conv3, n.depth_relu3 = conv_relu("depth_conv3", n.depth_norm2, 384, ks=3, pad=1, group=2, lr1=1, lr2=2)
    n.depth_pool3 = max_pool(n.depth_relu3, ks=3)

    n.depth_conv4, n.depth_relu4 = conv_relu("depth_conv4", n.depth_pool3, 512, ks=3, pad=1, group=1, lr1=1, lr2=2)

    n.depth_conv5, n.depth_relu5 = conv_relu("depth_conv5", n.depth_relu4, 512, ks=3, pad=1, group=1, lr1=1, lr2=2)
    
    n.depth_pool5 = max_pool(n.depth_relu5, ks=3)

    n.depth_fc6, n.depth_relu6 = fc_relu(n.depth_pool5, 4096, lr1=1, lr2=2)   
    n.depth_drop6 = L.Dropout(n.depth_relu6, dropout_ratio=0.5, in_place=True)
    n.depth_fc7, n.depth_relu7 = fc_relu(n.depth_drop6 , 4096, lr1=1, lr2=2)
    n.depth_drop7 = L.Dropout(n.depth_relu7, dropout_ratio=0.5, in_place=True)

    n.depth_fc8 = fc(n.depth_drop7, 11, lr1=1, lr2=2)

    #-----------------------------------final output---------------------------------#
    # Concatenation
    #n.concat = L.Concat(n.rgb_drop7, n.depth_drop7, axis=1)
    #n.rgbd_fc8 = fc(n.concat, 6, lr1=1, lr2=2)

    if split != 'deploy':
	n.rgb_accuracy = L.Accuracy(n.rgb_fc8, n.label)
        n.rgb_loss = L.SoftmaxWithLoss(n.rgb_fc8, n.label)
	n.depth_accuracy = L.Accuracy(n.depth_fc8, n.label)
        n.depth_loss = L.SoftmaxWithLoss(n.depth_fc8, n.label)
        #n.accuracy = L.Accuracy(n.rgbd_fc8, n.label)
        #n.loss = L.SoftmaxWithLoss(n.rgbd_fc8, n.label)

    return n.to_proto()

def make_net():
    with open('train.prototxt', 'w') as f:
        f.write(str(cnn('train')))

    with open('test.prototxt', 'w') as f:
        f.write(str(cnn('test')))

    #with open('deploy.prototxt', 'w') as f:
    #    f.write(str(cnn('deploy')))

if __name__ == '__main__':
    make_net()