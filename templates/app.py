from flask import Flask, request, render_template
import math

app = Flask(__name__)

def calculate_properties(db_temp_F, rh):
    """Calculate psychrometric properties given dry bulb temp (°F) and RH (%)"""
    # Convert °F to °R
    T_R = db_temp_F + 459.67
    
    # Atmospheric pressure (psia)
    P_atm = 14.696
    
    # Calculate saturation pressure (psia) - using ASHRAE 2017 formula
    T_R_459 = db_temp_F + 459.67
    C1 = -10440.397
    C2 = -11.29465
    C3 = -0.027022355
    C4 = 0.00001289036
    C5 = -0.0000000024780681
    C6 = 6.5459673
    
    # Calculate saturation pressure in psia
    Pws = math.exp(C1/T_R_459 + C2 + C3*T_R_459 + C4*T_R_459**2 + 
                   C5*T_R_459**3 + C6*math.log(T_R_459)) / 144
    
    # Partial vapor pressure
    Pw = (rh/100) * Pws
    
    # Humidity ratio (grains/lb)
    W = 7000 * 0.622 * (Pw/(P_atm-Pw))
    
    # Specific volume (ft³/lb)
    v = 0.370486 * T_R * (1 + 1.607858*W/7000)/P_atm
    
    # Specific enthalpy (BTU/lb)
    h = 0.24 * db_temp_F + (W/7000) * (1061 + 0.444 * db_temp_F)
    
    # Density (lb/ft³)
    density = 1/v

    return {
        "Dry Bulb Temperature": f"{db_temp_F:.2f} °F",
        "Relative Humidity": f"{rh:.2f} %",
        "Humidity Ratio": f"{W:.2f} grains/lb",
        "Specific Volume": f"{v:.4f} ft³/lb",
        "Specific Enthalpy": f"{h:.2f} BTU/lb",
        "Density": f"{density:.3f} lb/ft³"
    }

@app.route('/', methods=['GET', 'POST'])
def calculator():
    results = None
    if request.method == 'POST':
        try:
            db_temp = float(request.form['db_temp'])
            rh = float(request.form['rh'])
            results = calculate_properties(db_temp, rh)
        except ValueError:
            results = "Error: Please enter valid numbers"
        except Exception as e:
            results = f"Error in calculation: {str(e)}"
    
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)