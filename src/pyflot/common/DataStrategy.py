class DataStrategy:

    #stratRepartingCoupleList =  [[0,1],[0,0.5],[0.5,1],[0,0]]
    ## Every single of 5 call sites by 10% slices
    #stratRepartingCoupleList =  [[0,0.2],[0.2,0.4],[0.4,0.6],[0.6,0.8],[0.8,1]]
    #stratCoupleList = [
    #        ([[0,0.1]],  [[1,0]]),
    #        ([[0.1,0.2]],[[1,0]]),
    #        ([[0.2,0.3]],[[1,0]]),
    #        ([[0.3,0.4]],[[1,0]]),
    #        ([[0.4,0.5]],[[1,0]]),
    #        ([[0.5,0.6]],[[1,0]]),
    #        ([[0.6,0.7]],[[1,0]]),
    #        ([[0.7,0.8]],[[1,0]]),
    #        ([[0.8,0.9]],[[1,0]]),
    #        ([[0.9,1]],  [[1,0]])
    #        ]

    #stratCoupleList = [
    #        ([[0,0.003]],[[0.997,1]]),
    #        ([[0,0.002]],[[0.998,1]]),
    #        ([[0,0.0015]],[[0.9985,1]]),
    #        ([[0,0.001]],[[0.999,1]]),
    #        ([[0,0.05]],[[0.9995,1]]),
    #        ([[0,0.01]],[[0.9998,1]]),
    #        ([[0,0.005]],[[0.9999,1]])
    #        ]
    ## Studying comp_Kc by 1./(30.*10) slices
    stratRepartingCoupleList = []
    stratCoupleList = []
    def __init__(self):
        ## Only CompKc
        self.stratRepartingCoupleList =  [[0,0.2]]
        ## Small slices
        slicesize = 1./3000.
        self.stratCoupleList = [ ([[i*slicesize, (i+1)*slicesize]],[[1,0]]) for i in range(100,2900) ]
