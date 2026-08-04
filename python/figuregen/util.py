class Fort14():
    def __init__(self, fname):
        self.weirs = False
        self.xs = []
        self.ys = []
        self.bath = []
        
        with open(fname) as f:
            line = f.readline()
            self.title = "_".join(line.split())
            line = f.readline().split()
            self.ne = int(line[0])
            self.np = int(line[1])
            # loop through nodes
            for _ in range(self.np):
                line = f.readline().split()
                self.xs.append(float(line[1]))
                self.ys.append(float(line[2]))
                self.bath.append(float(line[3]))

            # loop through triangulation
            for _ in range(self.ne):
                f.readline()

            self.nope = int(f.readline().split()[0])
            self.neta = int(f.readline().split()[0])

            for _ in range(self.nope):
                nvdll = int(f.readline().split()[0])
                for _ in range(nvdll):
                    f.readline()

            self.nbou = int(f.readline().split()[0])
            self.nvel = int(f.readline().split()[0])

            for _ in range(self.nbou):
                line = f.readline().split()
                nvell = int(line[0])
                ibtype = int(line[1])
                if ibtype == 4 or ibtype == 24:
                    self.weirs = True
                for _ in range(nvell):
                    f.readline()

    def box(self):
        return [min(self.xs), max(self.xs), min(self.ys), max(self.ys)]
