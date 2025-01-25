import nfdrs4py
dfm = nfdrs4py.DeadFuelMoisture.createDeadFuelMoisture1()
print(dfm.update(1,1,1,1,1))
dfm.medianRadialMoisture()
dfm.setAdsorptionRate(0.4)
dfm.diffusivitySteps()
dfm.deriveStickNodes(0.3)
