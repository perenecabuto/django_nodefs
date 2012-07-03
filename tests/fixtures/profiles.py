from node_fs.lib.model import AbstractNode
from node_fs.lib.model import NodeProfile
from selectors import ModelSelector
from models import Thing


schema = {
    'default': NodeProfile(
        abstract_nodes=[
            AbstractNode(
                selector=ModelSelector(
                    projection='%(label)s',
                    model_class=Thing
                ),
            ),
        ])
}
