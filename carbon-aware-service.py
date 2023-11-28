from datetime import datetime
from enum import Enum
from flask import Flask,jsonify
from numpy import random

# Carbon intensity reader (mock)
from carbon.reader_mock import CarbonIntensityReader

# ------ STRATEGIES ------
# Import and enum carbon-aware strategies (aka. flavours)
from flavours.interface import CarbonAwareStrategy
from flavours.low_power import LowPowerStrategy
from flavours.full_power import FullPowerStrategy

class CarbonAwareStrategies(Enum):
    LowPower = LowPowerStrategy
    FullPower = FullPowerStrategy

# ------ CONTEXT ------
# Carbon-aware context
class Context:
    # constructor
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    # initializer
    def __init__(self):
        self.co2 = None
        self.carbonIntensityReader = CarbonIntensityReader(100,500,1500)
     
    def getCarbonAwareStrategy(self) -> CarbonAwareStrategy:
        self.co2 = self.carbonIntensityReader.read()
        if (self.co2 >= 1000):
            return CarbonAwareStrategies.LowPower.value
        else:
            return CarbonAwareStrategies.FullPower.value

# ------ SERVICE ------
app = Flask(__name__)

# generate random data
generator = random.Generator(random.PCG64())
rand = lambda : round(generator.random()*10000)
app.data = [rand() for i in range(5000000)]

# set service's context
app.context = Context()

@app.route("/")
def nop():
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy()
    # Invoke strategy with dynamic typing
    answer = strategy.nop()
    return answer

@app.route("/avg")
def avg():
    # Get carbon-aware strategy
    strategy = app.context.getCarbonAwareStrategy()
    # Invoke strategy with dynamic typing (and measure running time)
    start = datetime.now()
    average = strategy.avg(app.data)
    elapsed = round((datetime.now() - start).microseconds/1000)
    # Return result and elapsed time
    result = {}
    result["average"] = average
    result["elapsed"] = elapsed
    result["co2"] = app.context.co2
    return jsonify(result)

app.run(host='0.0.0.0',port=50000)