import numpy as np

RGB_TO_XYZ = np.array([[0.412453, 0.357580, 0.180423],
                       [0.212671, 0.715160, 0.072169],
                       [0.019334, 0.119193, 0.950227]])
                       
XYZ_TO_RGB = np.array([[ 3.240479, -1.537150, -0.498535],
                       [-0.969256,  1.875991,  0.041556],
                       [ 0.055648, -0.204043,  1.057311]])

def rgb_to_xyz(rgb):
    return RGB_TO_XYZ.dot(rgb) 

def xyz_to_rgb(xyz):
    return XYZ_TO_RGB.dot(xyz) 
    
def y(rgb):
    return RGB_TO_XYZ[1].dot(rgb)