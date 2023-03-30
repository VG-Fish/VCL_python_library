import errno

class InvalidFormat(Exception):
    def __init__(sel, msg):
        super().__init__(msg)

class VCLParser:
    def __init__(self, file):
        self.file = file

        if not self.file.endswith(".vcl"):
            raise InvalidFormat("File must be of type vcl.")
        
        self.identifier = ["info!"]
        self.file_variables = {}
        self.string = "\"'"
        self._read()

    def _read(self):
        try:
            fp = open(self.file)
        except IOError as e:
            if e.errno == errno.EACCES:
                raise ImportError("Permission denied.")
            elif e.errno == errno.ENOENT:
                raise ImportError("No such file or directory")
        with fp:
            fp = (row for row in fp.read().splitlines())
            fp = (row.partition("#")[0].strip() for row in fp)
            fp = (row for row in fp if row)
            fp = " ".join(fp)

            curr, prev, is_valid = "", None, False
            i = 0
            while i < len(fp):
                if fp[i] == "=":
                    while fp[i].isspace() or fp[i] == "=":
                        i += 1

                    if fp[i] == "[":
                        i += 1
                        value = ""
                        self.file_variables[prev] = []
                        while fp[i] != "]":
                            if fp[i] == "," or fp[i].isspace():
                                if value:
                                    self.file_variables[prev].append(value)
                                value = ""
                            elif fp[i] not in self.string:
                                value += fp[i]
                            i += 1
                        if value:
                            self.file_variables[prev].append(value)
                        continue

                    value = ""
                    while i < len(fp):
                        if not fp[i].isspace() and fp[i] not in self.string:
                            value += fp[i] 
                        elif fp[i].isspace() and value:
                            break
                        i += 1
                    
                    value = self._check_type(value)
                    self.file_variables[prev] = value 
                elif not fp[i].isspace():
                    curr += fp[i]
                else:
                    if curr not in self.identifier and not is_valid:
                        raise InvalidFormat("Variables must be declared after info!")
                    elif curr in self.identifier:
                        is_valid = True
                        curr = ""
                    elif is_valid:
                        prev = curr 
                        curr = ""
                i += 1

    def add_new_variable(self, var, value):
        if var in self.file_variables:
            return
        with open(self.file, "a") as fp:
            fp.write(f"{var} = \"{value}\" \n")
        self._read()

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
    test = VCLParser("FBLA GAME/VCL/format.vcl")
    my_vcl_vars = test.get_variables()

    for i, j in my_vcl_vars.items():
        print(f"1, {i} = {j}")

    print()

    test.add_new_variable("Vishy", "creator")

    my_vcl_vars = test.get_variables()

    for i, j in my_vcl_vars.items():
        print(f"2, {i} = {j}")

    print()
    
    test.overwrite_variable("rank", 2)

    test.append_to_list("themes_colors_single", "magenta")

    my_vcl_vars = test.get_variables()

    for i, j in my_vcl_vars.items():
        print(f"3, {i} = {j}")
