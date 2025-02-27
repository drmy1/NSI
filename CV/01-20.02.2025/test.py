class Ucebna:
    def __init__(self,seatcount):
        self.seatcount = seatcount
        self.studentcount = 0
        self.students = []
        
    def prichod(self, name):
        if self.studentcount == self.seatcount:
            raise Exception("Ucebna je plna")
        self.students.append(name)
        self.studentcount += 1
    
    def print_class_attendance(self):
        for i in self.students:
            print(i)
        
test = Ucebna(2)
test.prichod("Jana")
test.prichod("Pavel")
test.print_class_attendance()