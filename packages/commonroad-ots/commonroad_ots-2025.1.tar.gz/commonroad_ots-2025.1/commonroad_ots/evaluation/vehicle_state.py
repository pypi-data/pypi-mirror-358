class VehicleState:
    timestep = 0
    pos = [0, 0]
    vel = 0.0
    ori = 0.0
    length = 0.0
    width = 0.0

    def __init__(self, t: float, p: list, v: float, o: float, l: float, w: float):
        """
        Constructor of the VehicleState class.

        Parameters
        ----------
        t: float
            timestep
        p: list
            position [x,y]
        v: float
            velocity
        o: float
            orientation
        l: float
            length
        w: float
            width
        """
        self.timestep = t
        self.pos = p
        self.vel = v
        self.ori = o
        self.length = l
        self.width = w
