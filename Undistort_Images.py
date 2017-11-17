import bpy

# switch on nodes and get reference
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree

# clear default nodes
for node in tree.nodes:
    tree.nodes.remove(node)

# create input image node
image_node = tree.nodes.new(type='CompositorNodeImage')
image_node.image = bpy.data.images['G0014937.JPG']
image_node.location = 0,0

# create output node
comp_node = tree.nodes.new('CompositorNodeComposite')   
comp_node.location = 400,0

# create output node
viewer_node = tree.nodes.new('CompositorNodeViewer')   
viewer_node.location = 400,-200

# link nodes
links = tree.links
link_image2comp = links.new(image_node.outputs[0], comp_node.inputs[0])
link_image2viewer = links.new(image_node.outputs[0], viewer_node.inputs[0])