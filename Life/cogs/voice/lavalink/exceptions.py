

class LavaLinkException(Exception):
    pass


class NodeException(LavaLinkException):
    pass


class NodeCreationError(NodeException):
    pass


class NodeConnectionError(NodeException):
    pass


class NodeNotFound(NodeException):
    pass


class NodesNotFound(NodeException):
    pass

