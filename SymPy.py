import sympy as sym
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application, convert_xor
from sympy.plotting import plot
from flask import jsonify, Flask, request
import numpy as np

x,y,z = sym.symbols("x,y,z")

def transform_string(ecuation): 
    transforms = (standard_transformations + (implicit_multiplication_application, convert_xor))
    ecuation = sym.parse_expr(ecuation, transformations=transforms)
    return ecuation

def calc(ecuation): #Nota esta función también sirve para ecuaciones no simbólicas, como eval()
    p1 = transform_string(ecuation)
    result = sym.expand(p1)
    return result

#print(polinom_calc("x**2*(2*x + 2)/x**2"))

def derivate(fx):
    strfx = transform_string(fx)
    result = sym.diff(strfx, x)
    return result

#print(derivate("2x+x"))

def integrate_indef(fx):
    strfx = transform_string(fx)
    result = sym.integrate(strfx, x)
    return result

#print(integrate_indef("2x"))

def integrate_def(fx, range):
    strfx = transform_string(fx)
    result = sym.integrate(strfx, (x, range[0], range[1]))
    return result

#print(integrate_def("2x", (0, 5)))

def integrate_doble(fx, rangex, rangey):
    strfx = transform_string(fx)
    result = sym.integrate(strfx, (x, rangex[0], rangex[1]), (y, rangey[0], rangey[1]))
    return result

#print(integrate_doble("2x + 2y", (0, 6), (0, 5)))

def graficate(fx, range, multiplier, cualiti = 240):
    fx_sympy = transform_string(fx)
    fx_numpy = sym.lambdify(x, fx_sympy, "numpy")
    x_points = np.linspace(float(range[0]), float(range[1]), cualiti)
    y_points = fx_numpy(x_points)

    NaN_filter = np.isfinite(y_points)
    x_final = x_points[NaN_filter]
    y_final = y_points[NaN_filter]

    x_int = [int(round(p*multiplier)) for p in x_final]
    y_int = [int(round(p*multiplier)) for p in y_final]

    return x_int, y_int

def solver(ecuation):
    strecuation = transform_string(ecuation)
    result = sym.solve(strecuation)
    return result

def fact(ecuation):
    strecuation = transform_string(ecuation)
    result = sym.factor(strecuation)
    return result

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message":"Hola mundo"})

@app.route("/solve", methods=["POST"])
def get_result():
    data = request.get_json()
    mode = data.get("mode")
    ecuation = data.get("ecuation")

    result = None
    if mode == "sym":
        result = sym.latex(calc(ecuation))

    elif mode == "derivate":
        result = sym.latex(derivate(ecuation))

    elif mode == "integrate_indef":
        result = sym.latex(integrate_indef(ecuation))

    elif mode == "integrate_def":
        range = data.get("range")
        result = sym.latex(integrate_def(ecuation, range))

    elif mode == "integrate_doble":
        rangex = data.get("rangex")
        rangey = data.get("rangey")
        result = sym.latex(integrate_doble(ecuation, rangex, rangey))

    elif mode == "grafic":
        range = data.get("range")
        multiplier = data.get("multiplier")
        cualiti = data.get("cualiti")
        x, y = graficate(ecuation, range, multiplier, cualiti)
        result = {
            "x_points":x,
            "y_points":y
        }

    elif mode == "solve":
        result = sym.latex(solver(ecuation))

    elif mode == "fact":
        result = sym.pretty(fact(ecuation), use_unicode = True)
    
    return jsonify({
        "result":result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3030, debug=True)