from IPython.display import Math, display,Latex


def scicount(x,pci=2):
    '''
    Function to convert a number to scientific notation
    '''
    mantissa = 0
    exponent = 0
    unit = True
    try:
        x.unit
    except AttributeError:
        unit = False
    v = x.value if unit else x
    if abs(v)<10 and abs(v)>1 :
        return f"{v:.{pci}f}"
    else:
        file = f"{v:.{pci}e}".split('e')
        mantissa = file[0]
        exponent = int(file[1])
    if unit:
        return f"{mantissa} \\times 10^{{{exponent}}} \\, {x.unit}"
    else:
        return f"{mantissa} \\times 10^{{{exponent}}}"