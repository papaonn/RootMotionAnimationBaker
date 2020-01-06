#
#
#    Copyright (c) <2020> <Daniel H.D.Ong, Papaonn>
#    
#    Contact    : Papaonn Daniel ( Facebook, Twitter )
#    Presskit   : https://papaonn.blogspot.com
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
#
#    <Rev, 1.1>
#
#
import bpy
import mathutils

#
# index of list
#
def indexOfList( data, lpList):
    try:
        return lpList.index( data )
    except ValueError:
        return -1 

#
# variables 
#

# initialization
bpy.context.scene.frame_set( 0 )

# extract root motion position in 1st frame 
rootBone = "LowerBody";
root = bpy.context.object.pose.bones[ rootBone ]
#rootPosition = root.location.copy()
rootPosition = mathutils.Vector((0.0, 0.0, 0.0))

# calibrate IK Bones positions to associated target bones
targetBones = [ "IK-Neck", "IK-LowerBody", "IK-HandLeft", "IK-HandRight", "IKFoot-Left", "IKFoot-Right" ]

#
# IMPORTANT : sometimes animation might require pole targets to be calibrated as well,
#             other times if pole target did not cause problem just ignore it.
#
_UPDATE_POLE_TARGETS_ = 0

if _UPDATE_POLE_TARGETS_ == 1 :
    targetBones.extend( [ "Pole-Neck", "Pole-LowerBody", "Pole-RightLeg", "Pole-LeftLeg", "Pole-RightHand", "Pole-LeftHand" ] )

#
keyframePathInfos = {}
keyframes = []
keyframeContents = {}

# extract all bones path info 
for i in range( len( targetBones ) ) :
    bone = bpy.context.object.pose.bones[ targetBones[i] ]
    keyframePathInfos[ bone ] = bone.path_from_id()    
    # allocate buffer for index list
    keyframeContents[ bone ] = []
    
#
# extract keyframe unique index
#
obj = bpy.context.object
action = obj.animation_data.action

for fcurve in action.fcurves : 
    for p in fcurve.keyframe_points :
        index = int( p.co[0] )
        bonePath = fcurve.data_path;
        #
        for path in keyframePathInfos.items() :
            if path[1] in bonePath : 
                # add unique index
                if indexOfList( index, keyframeContents[ path[0] ] ) == -1 :
                    keyframeContents[ path[0] ].append( index )
                

# render all frames 
frameLength = int( action.frame_range[1] ) + 1

for key in keyframeContents.items() : 
    for i in range( frameLength ) :
        bpy.context.scene.frame_set( i )
        # update to animation current keyframe
        key[0].bone.select = True
        bpy.ops.anim.keyframe_insert_menu ( type='Location' )
        key[0].bone.select = False

    
# calibrate joints positions
keyframeGeometries = {}
worldMatrix = bpy.context.object.matrix_world

for key in keyframeContents.items() : 
    for i in range( frameLength ) :
        bpy.context.scene.frame_set( i )
        # calculate geometry offset to root bone
        rootCurrentPosition = root.bone.matrix_local * root.location
        offset = key[0].bone.matrix_local * key[0].location - rootCurrentPosition
        key[0].location = rootPosition + key[0].bone.matrix_local.inverted() * offset
        # update to animation current keyframe
        key[0].bone.select = True
        bpy.ops.anim.keyframe_insert_menu ( type='Location' )
        key[0].bone.select = False
    

# finally, calibrate root bone position
for i in range( frameLength ) : 
    bpy.context.scene.frame_set( i ) 
    root.location = rootPosition
    # update to animation current keyframe
    root.bone.select = True
    bpy.ops.anim.keyframe_insert_menu ( type='Location' )
    root.bone.select = False


