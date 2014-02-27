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

TOOD:
 - Add a "ready for massive UUID assignement" function.

 """

__author__  = 'Dorian Fevrier <fevrier.dorian@yahoo.fr>'
__version__ = '1.0'
__all__     = [ 'set_all_uuids',
                'set_uuid'     ,
                'uuid_map'     ,
                'get_node'     ,
                'get_uuid'     ,
                'check_uuids'  ]

import uuid
import maya.cmds as mc
import config

uuid_attr_name = config.UUID_ATTR_NAME


def _remove_all_uuids() :
    """Should actually never be used because it could compromise every node dependencies!"""
    mc.warning( 'You are using a risky method, if you don\'t know what you are doing, please call RnD!' )
    for node in mc.ls( long = True ) :
        _remove_uuid( node )

def _remove_uuid( node ) :
    """Remove the uuid of the given node."""
    node_attr = '%s.%s' % ( node, uuid_attr_name )
    if mc.attributeQuery( uuid_attr_name, node = node, exists = True ) :
        if mc.referenceQuery( node, isNodeReferenced = True ) :
            msg  = 'This node has a uuid attribute on it but '
            msg += 'is in reference, can\'t remove attribute : %s' % node
            mc.warning( msg )
        if mc.getAttr( node_attr, lock = True ) :
            mc.setAttr( node_attr, lock = False )
        mc.deleteAttr( node, attribute = uuid_attr_name )

def set_all_uuids() :
    """Create a uuid to every node in your current Maya scene."""
    for node in uuid_missing_nodes() :
        set_uuid( node )

def set_uuid( node ) :
    """Set a uuid to the given node."""
    mc.addAttr( node, longName = uuid_attr_name, dataType='string' )
    mc.setAttr( '%s.%s' % ( node, uuid_attr_name ), str(uuid.uuid4().hex), type='string', lock=True )

def uuid_missing_nodes() :
    """A generator to nodes that are supposed to have uuid on them but don't."""
    for node in uuid_nodes() :
        if mc.referenceQuery( node, isNodeReferenced = True ) :
            continue
        if not mc.attributeQuery( uuid_attr_name, node = node, exists = True ) :
            yield node

def uuid_nodes() :
    """A generator to every nodes supposed to have a uuid on them."""
    for node in mc.ls( long = True, persistentNodes = False, type = config.TRACKABLE_NODE_TYPES ) :
        yield node

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

def get_uuid( node ) :
    """Return the uuid value of the given node."""
    return mc.getAttr( '%s.%s' % ( node, uuid_attr_name ) )

def check_uuids() :
    """Return if the current scene is "uuid consistant".

    If this fail, the scene has inconsistant uuid nodes, you should fix the problems before going further.
    """
    for node in uuid_nodes() :
        node_attr = '%s.%s' % ( node, uuid_attr_name )
        if not mc.attributeQuery( uuid_attr_name, node = node, exists=True ) :
            mc.warning( "This node is supposed to have a uuid : %s" % node )
            if mc.referenceQuery( node, isNodeReferenced = True ) :
                mc.warning( "As this node seems to be in reference, you should solve the problem in the reference itself." )
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

