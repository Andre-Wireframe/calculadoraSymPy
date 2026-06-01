import sympy as sym

x,y,z = sym.symbols("x,y,z")

ecuation = (x-2)/(x-4) + (y - 2)/(y-4)
resultado = sym.latex(ecuation).replace("frac", "f").replace("}{", "/")
print(resultado)

