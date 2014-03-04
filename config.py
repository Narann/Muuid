
# Disclaimer: This file is not supposed to be modified often. You actually
# should setup this informations once and never change them to avoid
# inconsistancies.

# The uuid attribute name for the Maya nodes.
UUID_ATTR_NAME = 'fd_node_uuid'

# Define a list of node type that will have uuid on them.
TRACKABLE_NODE_TYPES = [ 'transform'        ,
                         'mesh'             ,
                         'nurbsSurface'     ]

# Define a list of custom full path nodes you don't want uuids on.
UNWANTED_NODES = []

# List of Maya internal nodes that can be considered as "defaults".
DEFAULT_NODES = [ '|persp'                        ,
                  '|persp|perspShape'             ,
                  '|top'                          ,
                  '|top|topShape'                 ,
                  '|front'                        ,
                  '|front|frontShape'             ,
                  '|side'                         ,
                  '|side|sideShape'               ,
                  '|defaultLightSet'              ,
                  '|defaultObjectSet'             ,
                  '|defaultLayer'                 ,
                  '|layerManager'                 ,
                  '|dof1'                         ,
                  '|dynController1'               ,
                  '|globalCacheControl'           ,
                  '|hardwareRenderGlobals'        ,
                  '|hardwareRenderingGlobals'     ,
                  '|defaultHardwareRenderGlobals' ,
                  '|ikSystem'                     ,
                  '|lambert1'                     ,
                  '|lightLinker1'                 ,
                  '|particleCloud1'               ,
                  '|characterPartition'           ,
                  '|renderPartition'              ,
                  '|defaultRenderLayer'           ,
                  '|sequenceManager1'             ,
                  '|shaderGlow1'                  ,
                  '|strokeGlobals'                ,
                  '|time1'                        ,
                  '|defaultViewColorManager'      ]

