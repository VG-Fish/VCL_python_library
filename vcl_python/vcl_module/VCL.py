import errno
from regex import split

class InvalidFormat(Exception):
    def __init__(sel, msg):
        super().__init__(msg)

class VCLParser:
    def __init__(self, file):
        self.file = file

        if not self.file.endswith(".vcl"):
            raise InvalidFormat("File must be of type vcl.")
        
        self.identifiers = ["info!"]
        self.file_variables = {}
        self.string = "\"'"
        self.fp, self.curr_line = None, None
        self.ptr, self.line_len = 0, 0
        self._read()

    def _read(self):
        try:
            self.fp = open(self.file)
        except IOError as e:
            if e.errno == errno.EACCES:
                raise ImportError("Permission denied.")
            elif e.errno == errno.ENOENT:
                raise ImportError("No such file or directory")
        with self.fp:
            self.fp = split(r"\/\*[\s\S]*?\*\/|(['\"])[\s\S]+?\1(*SKIP)(*FAIL)|\#.*\n", "".join(self.fp.readlines()))
            self.fp = (row for row in self.fp if row)
            for i in self.fp:
                self.curr_line = " ".join(i.split())
                self.line_len = len(i)
                print(fp)
                
                while self.ptr < self.line_len:
                    self.ptr += 1

    def _read_variable(self):
        pass

    def _read_non_iterator(self):
        value = ""
        self.ptr += 1
        while self.ptr < self.line_len:
            if self.fp[self.ptr].isspace() and value:
                break
            elif self.fp[self.ptr] not in self.string:
                value += self.fp[self.ptr]
            self.ptr += 1
        value = self._check_type(value)
        return value

    def add_new_variable(self, var, value):
        if var in self.file_variables:
            return
        with open(self.file, "a") as fp:
            fp.write(f"{var} = \"{value}\" \n")
        self.file_variables[var] = value

    def _get_line_idx(self, var):
        if var not in self.file_variables:
            raise InvalidFormat("The variable you inputed is not in the file")

        count = 0
        with open(self.file, "r") as fp:
            lines = fp.readlines()
            for row in lines:
                if var in row:
                    break
                count += 1
        
        return count

    def _overwrite(self, var, value, count):
        with open(self.file, "r") as fp:
            lines = fp.readlines()

        with open(self.file, "w") as fp:
            for line in lines:
                if count != 0:
                    fp.write(line)
                else:
                    tmp = line.partition("#")
                    fp.write(f"{var} = {value} {tmp[1]} {tmp[2]}\n")
                count -= 1

        self.file_variables[var] = value

    def overwrite_variable(self, var, value):
        line_idx = self._get_line_idx(var)
        self._overwrite(var, value, line_idx)

    def append_to_list(self, var, value):
        if var not in self.file_variables:
            raise InvalidFormat("The variable you inputed is not in the file")
        
        line_idx = self._get_line_idx(var)
        new_list = self.file_variables[var] + [value]
        self._overwrite(var, new_list, line_idx)

        self.file_variables[var] = new_list

    def remove_from_list(self, var, value):
        if var not in self.file_variables:
            raise InvalidFormat("The variable you inputed is not in the file")
        
        line_idx = self._get_line_idx(var)
        new_list = [i for i in self.file_variables[var] if i != value]
        print(new_list)
        self._overwrite(var, new_list, line_idx)

        self.file_variables[var] = new_list

    def get_variables(self):
        return self.file_variables

    def _check_type(self, test):
        if test.isnumeric():
            return int(test)
        try:
            float(test)
            return float(test)
        except ValueError:
            if test.capitalize() == "True":
                return True
            elif test.capitalize() == "False":
                return False
            return test
        
if __name__ == "__main__":
    test = VCLParser("vcl_python/vcl_module/test.vcl")
    my_vcl_vars = test.get_variables()

    for i, j in my_vcl_vars.items():
        print(f"1, {i} = {j}")
    print()
    """
    test.add_new_variable("Vishy", "creator")
    my_vcl_vars = test.get_variables()

    for i, j in my_vcl_vars.items():
        print(f"2, {i} = {j}")
    print()
    
    test.overwrite_variable("rank", 2)
    test.append_to_list("themes_colors_single", "magenta")
    test.append_to_list("themes_colors_single", "butterscotch")
    test.remove_from_list("themes_colors_single", "magenta")
    test.add_new_variable("test", "is-it-highlighted?")
    my_vcl_vars = test.get_variables()

    for i, j in my_vcl_vars.items():
        print(f"3, {i} = {j}")"""
