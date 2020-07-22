import json
callS = {}
nbIteList = [1,10,20,30,40,80,100,200,300,600,1200]
for ite in nbIteList:
    fi = f"./csvJson-{ite}ite/dumpProfile.json"
    with open(fi,"r") as inf:
        basejs = json.load(inf)
        for js in basejs["IndependantCallStacks"]:
            #print(js["CallStack"][3])
            if not callS.get(js["HashKey"]):
                callS[js["HashKey"]] = []
                callS[js["HashKey"]].append(int(js["CallsCount"]))
            else:
                callS[js["HashKey"]].append(int(js["CallsCount"]))
#print(callS)
#exit(0)
import sys
last = int(sys.argv[1])
mydegree = int(sys.argv[2])

print([(i,x) for i,x in enumerate(nbIteList)])

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
for key,call in callS.items():
    x = np.array(nbIteList[:last]).reshape(-1,1)
    y = np.array(call[:last])##2 dim
    model = LinearRegression().fit(x, y)
    poly = PolynomialFeatures(degree = mydegree)
    X_poly = poly.fit_transform(x)
    poly.fit(X_poly, y)
    lin2 = LinearRegression()
    lin2.fit(X_poly, y)

    #print("Linear")
    y_pred = model.predict(x)
    #print([abs(t-u) for t,u in zip(y,y_pred)])
    #print("Polynome")
    y_pred = lin2.predict(poly.fit_transform(x))
    #print([abs(t-u) for t,u in zip(y,y_pred)])
    #print("6000? ",lin2.predict(6000.0))
    ref = call[-1]
    #prediction = lin2.predict(poly.fit_transform(np.array(1200.0).reshape(-1,1)))[0]
    prediction = lin2.predict(poly.fit_transform(np.array(60000.0).reshape(-1,1)))[0]
    print("ref: {:.2E}".format(ref), " prediction: {:.2E}".format(prediction) )
    print("Rel error predicting ite1200 {:.2f} %".format(abs(ref-prediction)/abs(ref)*100))
    print("Abs error predicting ite1200 {:.2E}".format(abs(ref-prediction)))
    #print("predicting more", lin2.predict(poly.fit_transform(np.array([1200., 1500.,2000.,3000.,4000.,6000.0]).reshape(-1,1))))

    #print('\nLinear\nintercept:', model.intercept_)
    #print('slope:', model.coef_)
    #y_pred = model.predict(x)
    #print('predicted response:', y_pred, sep='\n')
    #print("\nPolyome\n")
    #print('intercept:', lin2.intercept_)
    #print('slope:',lin2.coef_)
    #y_pred = lin2.predict(poly.fit_transform(x))
    ##y_pred = lin2.predict(x)
    #print('predicted response:', y_pred, sep='\n')
