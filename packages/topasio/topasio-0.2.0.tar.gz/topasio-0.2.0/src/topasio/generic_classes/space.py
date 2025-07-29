from src.generic_classes.element import Element
import logging
import pandas as pd
import re
import quantities as q
from src.printing import writeVal

class Space(Element):
    def __init__(self):
        super().__init__()
        self["_name"] = "GenericSpace"
        self["_modified"] = []  # Track modified attributes

    def __getattr__(self, name):

        if name.startswith("_"):
            raise ValueError(f"Attribute '{name}' is not accessible directly. Use Space[{name}] instead.")

        try:
            res = self[name]
            if name not in self["_modified"]:
                self["_modified"].append(name)

        except KeyError:
            logging.info(f"Automatically creating new Element '{name}' in Space")
            self[name] = Element()
            self["_modified"].append(name)
            return self[name]
        
        return res
    
    def getrepr(self, indent=4):

        res = "Space(\n"
        if len(self["_modified"]) == 0:
            return "Space()"
        for paramname in self["_modified"]:

            if paramname.startswith("_"):
                continue

            res += " " * indent + paramname + ": "
            if isinstance(self[paramname], Element):
                if len(self[paramname]["_modified"]) == 0:
                    res += self[paramname].__class__.__name__ + "()\n"
                else:
                    res += "\n"
                    res += self[paramname].getrepr(2*indent)
            else:
                res += str(self[paramname]) + "\n"

        return res + ")"  # Add closing parenthesis and newline for cleaner output
    
    def from_xlsx(self, file_path="test.xlsx", sheet_name=0):
        for elemname, elemdict in self.get_elems_from_xlsx(file_path, sheet_name):
            if elemname not in self:
                self[elemname] = Element()
            self[elemname].update(elemdict)
            if elemname not in self["_modified"]:
                self["_modified"].append(elemname)


    def dumpToFile(self, basename="autotopas"):
        filepath = f"{basename}/main.in"

        for elemName in self["_modified"]:
            if hasattr(self[elemName], "dumpToFile"):
                self[elemName].dumpToFile(elemName, 
                                        space_name=self["_name"],
                                        filename=filepath)
            else:
                with open(filepath, "a+") as f:
                    writeVal(f, 
                             space_name=self["_name"],
                             elemName=elemName,
                             key=None,
                             value=self[elemName])


    def get_elems_from_xlsx(self, file_path, sheet_name=0):
        """
        Reads elements from an Excel file and updates the Space instance.
        :param file_path: Path to the Excel file.
        :param sheet_name: Name of the sheet to read from. If None, reads the first sheet.

        :return: Yields tuples of (element name, element dictionary).
        """

        def isuseless(col):
            col = col.dropna().astype(str)
            return col.str.startswith('#').all()

        def remove_trailing_nans(ls):
            return [x for x in ls if not pd.isna(x)]

        def convert_unit_to_python(unit:str):
            # find all places where a digit follows a letter
            unit = re.sub(r'([a-zA-Z]+)(\d+)', r"\1**\2", unit)
            return unit
        
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="calamine")

        # Identify indices where rows are all NaN
        nan_rows = df.index[df.isna().all(axis=1)].tolist()

        # Add start and end boundaries
        split_indices = [-1] + nan_rows + [len(df)]

        # Slice into separate DataFrames
        dfs = [df.iloc[split_indices[i]+1 : split_indices[i+1]].reset_index(drop=True)
            for i in range(len(split_indices) - 1)
            if not df.iloc[split_indices[i]+1 : split_indices[i+1]].dropna(how='all').empty]

        dfs = [df.drop(columns=[col for col in df.columns if isuseless(df[col])]) for df in dfs]

        # `dfs` now contains the split DataFrames
        for df in dfs:
            elemName = df.iloc[0, 0]
            df = df.drop(labels=df.columns[0], axis="columns")
            df = df.reset_index(drop=True)

            elemdict = dict()

            for row in df.itertuples(index=False):
                row = list(row)
                row = remove_trailing_nans(row)
                # print(len(row), row)

                if len(row) <= 1:
                    continue

                elif len(row) == 2:
                    val = row[1]

                elif len(row) == 3:
                    unit_candidate = row[2]
                    value_candidate = row[1]
                    try:
                        val = q.Quantity(value_candidate, convert_unit_to_python(unit_candidate))
                    except Exception as e:
                        val = row[1:3]
                
                else:
                    val = row[1:]
                
                
                key = row[0]
                elemdict[key] = val

            yield elemName, elemdict