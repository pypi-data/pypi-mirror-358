import quantities
def isdimensionless(value):
    is_dimensionless = value.units == 1 * quantities.dimensionless
    is_degree = (value.units == quantities.deg or
                    value.units == quantities.degree or
                    value.units == quantities.degrees or
                    value.units == quantities.rad or 
                    value.units == quantities.radian or
                    value.units == quantities.radians)
    return is_dimensionless and not is_degree

def writeVal(f, space_name, elemName, key, value):
    typeID = getTypeID(value)

    last_part = "/" + key if key else ""

    if isinstance(value, quantities.Quantity):

        magnitude = value.magnitude
        unit = value.units
        if "**" in str(unit):
            # Handle cases like "m**2" or "m**3"
            unit = str(unit).replace("**", "") # unit is of the form 1.0 m2
            parts = unit.split(" ")
            
            if len(parts) == 2:
                # If the unit has a magnitude and a unit part
                magnitude = float(parts[0]) * magnitude
                unit = parts[1]
            else:
                raise ValueError(f"Unexpected unit format: {unit}")
            
            value = f"{magnitude} {unit}"
            
        if isdimensionless(value):
            value = float(value.magnitude)  # If the unit is dimensionless, just use the magnitude

            typeID = getTypeID(value)  # Update typeID to unitless
    


    match typeID:
        case "d" | "u" | "i":  # dimensioned
            f.write(f'{typeID}:{space_name}/{elemName}{last_part} = {value}\n')
        case "s" | "b":  # string
            f.write(f'{typeID}:{space_name}/{elemName}{last_part} = \"{value}\"\n')
        case "dv" | "uv" | "iv":  # vector
            f.write(f'{typeID}:{space_name}/{elemName}{last_part} = {len(value)}')
            if not isinstance(value[0], quantities.Quantity):
                for val in value:
                    f.write(f" {val:.9f}")
            else:
                for val in value:
                    f.write(f" {float(val.magnitude)}")
                f.write(f" {str(value[-1].units).split(' ')[-1]}")
            f.write("\n")
        case "sv" | "bv":
            f.write(f'{typeID}:{space_name}/{elemName}{last_part} = {len(value)}')
            for val in value:
                f.write(f' \"{val}\"')
            f.write("\n")

        case _:  # unsupported type
            print(typeID)
            raise TypeError(f"Unsupported type for key '{key}': {type(value)}")
        

def getTypeID(value):

    if isinstance(value, list):
        return getTypeID(value[0]) + "v" # vector
    
    if isinstance(value, quantities.Quantity) and not isdimensionless(value):
        return "d" # dimensioned
    
    elif isinstance(value, float):
        return "u" # unitless
    
    elif isinstance(value, quantities.Quantity) and not isdimensionless(value):
        return "u" # unitless
    
    elif isinstance(value, bool):
        return "b" # boolean
    
    elif isinstance(value, int):
        return "i" # integer
    
    elif isinstance(value, str):
        return "s" # string
    
    else:
        raise TypeError(f"Unsupported type: {type(value)}")