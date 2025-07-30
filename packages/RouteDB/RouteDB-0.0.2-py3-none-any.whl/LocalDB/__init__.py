r"""
LocalDB is a module made for managing databases locally!

Go ahead and explore the module! Make something fun! Maybe you could integrate it into a flask app!
"""
import os

class Route:
    """
    Routes are places data go to and from, use these with a Database
    """
    name = ""
    type = ""

    def __init__(self, name:str, type:str):
        self.name = name
        self.type = type

class Database:
    """
    Class for a local Database
    """
    types = dict[str, type]()
    path = ""
    routes = list[Route]()

    def __init__(self, path : str, types : dict[str, type]):
        self.path = path
        self.types = types
        if not os.path.exists(path):
            os.mkdir(path)

    def routeDir(self, route):
        return os.path.join(self.path, self.GetRoute(route).name)

    def getData(self, route, name):
        """
        Gets the data named `name` from `route` and returns it in the appropriate type
        """
        hasRoute = False
        theRoute = None
        for r in self.routes:
            if r.name == route:
                hasRoute = True
                theRoute = r
                break
        if not hasRoute:
            raise NameError(f"Route '{route}' does not exist in this Database")
        datPath = os.path.join(self.path, route, name)
        if not os.path.exists(datPath):
            raise FileNotFoundError(f"Data '{name}' does not exist in route '{route}' of this Database")
        with open(datPath) as f:
            return self.types[theRoute.type](f.read())

    def write(self, data, route : str, name):
        """
        Writes `data` to the route  
        :param data: The data to write  
        :param route: The route to write to  
        :param name: The name of the data to write
        """
        hasRoute = False
        theRoute = None
        for r in self.routes:
            if r.name == route:
                theRoute = r
                hasRoute = True
                break
        if not hasRoute:
            raise NameError(f"Route '{route}' does not exist in this Database")
        if not type(data) == self.types[theRoute.type]:
            raise TypeError(f"The type of the data being passed to route '{route}' is incorrect")
        routPath = os.path.join(self.path, route, name)
        if not os.path.exists(routPath):
            with open(routPath, "x") as f:
                f.write(data)
        else:
            with open(routPath, "w") as f:
                f.write(data)

    def addRoute(self, name : str, type : str):
        """
        Adds a route to the Database  
        Returns: False if `type` has not been added to the Database, otherwise True
        """
        try:
            myType = self.types.get(name)
        except Exception as e:
            print(e)
            return False
        self.routes.append(Route(name, type))
        if not os.path.exists(os.path.join(self.path, name)):
            os.mkdir(os.path.join(self.path, name))
        return True
    
    def GetRoute(self, name : str):
        """
        Gets the route by `name`  
        Returns `None` if the route was not found, otherwise returns the route
        """
        ourRoute = None
        for r in self.routes:
            if r.name == name:
                ourRoute = r
        return ourRoute