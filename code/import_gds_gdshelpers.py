import gdspy
from gdshelpers.parts import Port

class new_import:

    def __init__(self, file_path, origin, angle, width):
        self.file_path = file_path
        self.origin = origin
        self.angle = angle
        self.width = width
    
    @classmethod
    def import_gds(cls, file_path, origin, name):
        """
        file_path is the path of the file you want to import

        name is the name of the cell in the file
        """
        # STEP 1: 
        lib = gdspy.GdsLibrary(precision = 1e-10)
        lib.read_gds(file_path)
        cell_all = lib.cells
        return cell_all[name]
        
    @property
    def port(self):
        return Port(self.origin, self.angle, self.width)

def _example():
    file_path = './layout/Combinenation_SiO2.gds'
    origin = (100, 100)
    loadedcell = new_import.import_gds(file_path, origin, 'GC_a230_0_0')
    lib = gdspy.GdsLibrary(name='GC',precision=1e-10)
    device = lib.new_cell('loadedCell')
    device.add(loadedcell)
    gdspy.LayoutViewer(lib)
    # lib.write_gds('./layout/test.gds')

if __name__ == "__main__":
        _example()
