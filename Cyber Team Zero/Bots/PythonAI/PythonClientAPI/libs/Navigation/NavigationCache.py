from zipfile import ZipFile

from PythonClientAPI.libs.Game.Enums import Direction


class NavigationCache:
    def __init__(self):
        self.navigation_data = []
        self.loaded = False

    def deserialize_nav_data(self, array):
        d1 = array[0]
        d2 = array[1]
        d3 = array[2]
        d4 = array[3]

        data = []
        dir_list = [Direction.NOWHERE] + list(Direction._rotation_list.keys())
        for i1 in range(d1):
            data.append([])
            for i2 in range(d2):
                data[i1].append([])
                for i3 in range(d3):
                    data[i1][i2].append([])
                    for i4 in range(d4):
                        index = 4 + i1 * d2 * d3 * d4 + i2 * d3 * d4 + i3 * d4 + i4
                        c_byte = array[index]
                        c_dir = dir_list[c_byte]
                        data[i1][i2][i3].append(c_dir)

        print("Loaded navigation cache")
        return data

    def load_compiled_data(self, file):
        with ZipFile(file) as zip_file:
            info = zip_file.getinfo("data")

            expected_size = info.file_size

            data = zip_file.read('data')

            if len(data) != expected_size:
                raise EOFError("Expected " + str(expected_size) + " bytes, got " + str(len(data)))

            self.navigation_data = self.deserialize_nav_data(data)
            self.loaded = True

    def get_next_direction_in_path(self, position, target):
        return self.navigation_data[position[0]][position[1]][target[0]][target[1]]

navigation_cache = NavigationCache()
