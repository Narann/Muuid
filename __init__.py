r"""A simple way to add UUIDs to Maya nodes

maya_uuid expose few simple method to add, find, and check
UUID on current scene nodes. UUIDs are stored in the node attribute.

This module is intent to be configured depending on your needs.
Few variables can be redefined in config.py:

 - UUID_ATTR_NAME : The name of the attribute.
 - TRACKABLE_NODE_TYPES : A list on node type you want to put a UUID on.

Set a UUID to every node in your scene::

    >>> import maya_uuid
    >>> maya_uuid.set_all_uuids()

Set a UUID on one specific node::

    >>> import maya_uuid
    >>> set_uuid( node )

Check everything related to UUIDs is valid in the current scene (This is the first thing to do if you want to use maya_uuid on a scene)::

    >>> import maya_uuid
    >>> maya_uuid.check_uuids()
    True

Get a dict with UUIDs as key and full node path as value::

    >>> import maya_uuid
    >>> maya_uuid.uuid_map()
    {u'19e1f2935ac547d08891cbee179c00ef': u'|group1|group2',
     u'3073c0da57d747cbb77b0c290b805c97': u'|bubbleBoy:pSphere3',
     u'6475e1f84465491ab57972e0883df8a3': u'|bubbleBoy:pSphere4',
     u'63547c2a454545958d589e4d7a38d727': u'|bubbleBoy:pSphere5',
     u'6ab75d02bb044c6183b87615a450fd95': u'|group1|group2|testNamespace:group4|pSphere5',
     u'f948a707e0d74bbebe94c942f41b2742': u'|group1'} # 

Get the node with the given UUID::

    >>> import maya_uuid
    >>> maya_uuid.get_node( '19e1f2935ac547d08891cbee179c00ef' )
    
Get the UUID of the given node::

    >>> import maya_uuid
    >>> maya_uuid.get_uuid( '|group1|group2' )
    '19e1f2935ac547d08891cbee179c00ef' 


Limitations::

 - Clashing when import the same ref twice (add a concept of namespace?).
 - Can't deal with by face material assignation.
 - On better infrastructures that use "representation" nodes (low/high rez
   variation) the UUID principe can be irrelevant.
"""

__author__  = 'Dorian Fevrier <fevrier.dorian@yahoo.fr>'
__version__ = '1.0'
__all__     = [ 'set_all_uuids'                     ,
                'set_uuid'                          ,
                'uuid_map'                          ,
                'get_node'                          ,
                'get_uuid'                          ,
                'check_safety'                      ,
                'check_uuids'                       ,
                'register_creation_callback'        ,
                'unregister_all_creation_callbacks' ,
                'unregister_all_callbacks'          ]

import uuid
import maya.cmds     as mc
import maya.OpenMaya as om
import config

_uuid_attr_name = config.UUID_ATTR_NAME
_creation_callback_ids   = list()

def _remove_all_uuids() :
    """Should actually never be used because it could compromise every node dependencies!"""
    mc.warning( 'You are using a risky method, if you don\'t know what you are doing, please call RnD!' )
    for node in mc.ls( long = True ) :
        _remove_uuid( node )

def _remove_uuid( node ) :
    """Remove the uuid of the given node."""
    node_attr = '%s.%s' % ( node, _uuid_attr_name )
    if mc.attributeQuery( uuid_attr_name, node = node, exists = True ) :
        if mc.referenceQuery( node, isNodeReferenced = True ) :
            msg  = 'This node has an uuid on it but is in reference, can\'t '
            msg += 'remove its uuid : %s' % node
            mc.warning( msg )
        if mc.getAttr( node_attr, lock = True ) :
            mc.setAttr( node_attr, lock = False )
        mc.deleteAttr( node, attribute = _uuid_attr_name )

def set_all_uuids() :
    """Create a uuid to every node in your current Maya scene."""
    for node in uuid_missing_nodes() :
        set_uuid( node )

def set_uuid( node ) :
    """Set a uuid to the given node."""
    mc.addAttr( node, longName = _uuid_attr_name, dataType='string' )
    mc.setAttr( '%s.%s' % ( node, _uuid_attr_name ), str(uuid.uuid4().hex), type='string', lock=True )

def uuid_missing_nodes() :
    """A generator to nodes that are supposed to have uuid on them but don't."""
    for node in uuid_nodes() :
        if mc.referenceQuery( node, isNodeReferenced = True ) :
            continue
        if not has_uuid( node ) :
            yield node

def uuid_nodes() :
    """A generator to every nodes supposed to have a uuid on them.
    
    This generator doesn't check if there is uuid on nodes or if you could set
    uuid on them. It just return every node that match with the uuid rules and
    are supposed to have uuid on them in the current scene.
    """
    unwanted_nodes = config.DEFAULT_NODES + config.UNWANTED_NODES
    for node in mc.ls( long = True                        ,
                       type = config.TRACKABLE_NODE_TYPES ) :
        if node in unwanted_nodes :
            continue
        yield node

def could_have_uuid( node ) :
    """Return if the node could recieve a uuid on it."""
    full_path_node = mc.ls( node, long = True )
    return full_path_node in uuid_nodes()

def uuid_map() :
    """Return a dict with UUIDs as key and full nodes path as value."""
    uuid_dict = dict()
    for node in uuid_nodes() :
        uuid_value = get_uuid( node )
        uuid_dict[ uuid_value ] = node
    return uuid_dict

def get_node( uuid_value ) :
    """Return the Maya node having the given uuid value."""
    for node in uuid_nodes() :
        if get_uuid( node ) == uuid_value :
            return node

def has_uuid( node ) :
    """Return if the given node has uuid on it."""
    return mc.attributeQuery( _uuid_attr_name, node = node, exists = True )

def get_uuid( node ) :
    """Return the uuid value of the given node."""
    return mc.getAttr( '%s.%s' % ( node, _uuid_attr_name ) )

def check_safety() :
    """Check if the scene is safe enough to apply a set_uuid everywhere.
    
    This function check every node in the scene to ensure the scene is ready to
    get uuids on every nodes supposed to have one. Fail mean you will not be
    able to apply set_uuid on some/all nodes."""
    safe = True
    for node in uuid_nodes() :
        if mc.lockNode( node, query = True )[ 0 ] :
            msg  = "Node locked, set a uuid on it will be impossible : %s" % node
            mc.warning( msg )
            safe = False
        if mc.referenceQuery( node , isNodeReferenced = True ) :
            msg   = "Node in reference. Set an uuid on it will not make it "
            msg  += "unique. You should disable reference before or set uuids "
            msg  += "at the source of the referenced scene : %s" % node
            mc.warning( msg )
            safe = False
    return safe
    
def check_uuids() :
    """Return if the current scene is "uuid consistant".

    If this fail, the scene has inconsistant uuid nodes, you should fix the
    problems before going further.
    """
    for node in uuid_nodes() :
        node_attr = '%s.%s' % ( node, _uuid_attr_name )
        if not has_uuid( node ) :
            mc.warning( "This node is supposed to have a uuid : %s" % node )
            return False
        # uuid not locked?
        if not mc.getAttr( node_attr, lock = True ) :
            mc.warning( "This node has a unlocked uuid : %s" % node )
            return False
        # No value set in uuid?
        if not get_uuid( node ) :
            mc.warning( "This node seems to have an invalid uuid value : %s" % node )
            return False
        # Check uuid string size is 32
        if len( get_uuid( node ) ) != 32 :
            mc.warning( "This node seems to have an invalid uuid value : %s" % node )
            return False
    return True

def register_uuid_creation_callback() :
    """Register a callback that will create uuids on the fly.
    
    This callback should be registered only once or you could have unexpected
    results.
    """
    global _creation_callback_ids
    
    def set_uuid_on_mobject_callback( mobject, data ):
        """Set a uuid on the given mobject if it's supposed to have one."""
        nodeFullPath = None
        if mobject.hasFn( om.MFn.kDagNode ) :
            nodeFn = om.MFnDagNode( mobject )
            nodeFullPath = nodeFn.fullPathName()
        elif mobject.hasFn( om.MFn.kDependencyNode ) :
            nodeFn = om.MFnDependencyNode( mobject )
            nodeFullPath = '|%s' % nodeFn.name()
        
        if could_have_uuid( nodeFullPath ) :
            set_uuid( nodeFullPath )
        
    callback_id = om.MDGMessage.addNodeAddedCallback( set_uuid_on_mobject_callback )
    
    _creation_callback_ids.append( callback_id )
    
    return callback_id
    
def unregister_all_uuid_creation_callbacks() :
    """Unregister every callbacks created with register_uuid_creation_callback."""
    global _creation_callback_ids
    for callback_id in _creation_callback_ids :
        om.MMessage.removeCallback( callback_id )
    _creation_callback_ids = list()
    
def unregister_all_callbacks() :
    """Unregister every callbacks created using muuid."""
    unregister_all_uuid_creation_callbacks()

