import numpy as np
from mindaffectBCI.decoder.utils import RingBuffer

class lower_bound_tracker():
    """ sliding window linear trend tracker
    """   

    def __init__(self, window_size=100, outlier_thresh=2, step_size=.1, step_threshold=2, a0=1, b0=0, warmup_size=.1):
        self.window_size = window_size
        self.step_size = int(step_size*window_size) if step_size<1 else step_size
        self.a0 = a0
        self.b0 = b0
        self.warmup_size = int(warmup_size*window_size) if step_size<1 else warmup_size
        self.step_threshold = step_threshold
        self.outlier_thresh = outlier_thresh

    def reset(self, keep_model=False):
        self.buffer.clear()
        if not keep_model:
            self.a = self.a0
            self.b = self.b0

    def fit(self,X,Y):
        self.buffer = RingBuffer(self.window_size, (2,))
        self.append(X,Y)
        self.a = self.a0
        self.b = self.buffer[-1,1] - self.a * self.buffer[-1,0]

    def append(self,X,Y):
        if isinstance(X, np.ndarray) and X.ndim > 1:
            self.buffer.extend(np.hstack((X,Y)))
        else:
            self.buffer.append(np.array((X,Y)))

    def transform(self,X,Y):
        if not hasattr(self,'buffer'):
            self.fit(X,Y)
            return Y
        
        # add into ring-buffer
        self.append(X,Y)

        # update the fit
        self.update()

        # return Yest
        return self.getY(X)

    def update(self):
        if self.buffer.shape[0]>0 and self.buffer.shape[0] < self.warmup_size :
            self.b = self.buffer[-1,1] - self.a * self.buffer[-1,0]
            return

        # get the data
        x = self.buffer[:,0]
        y = self.buffer[:,1]
        # ls fit.
        # add constant feature  for the intercept
        x = np.append(x[:,np.newaxis],np.ones((x.shape[0],1)),1)
        # LS  solve
        y_fit = y.copy()
        for i in range(3):
            ab,res,_,_ = np.linalg.lstsq(x,y_fit,rcond=-1)
            y_est = x[:,0]*ab[0] + ab[1]
            err = y - y_est # server > true, clip positive errors
            scale = np.mean(np.abs(err))
            clipIdx = err > self.outlier_thresh*scale
            #print("{} overestimates".format(np.sum(clipIdx)))
            y_fit[clipIdx] = y_est[clipIdx] + self.outlier_thresh*scale
            clipIdx = err < -self.outlier_thresh*scale
            #print("{} underestimates".format(np.sum(clipIdx)))
            y_fit[clipIdx] = y_est[clipIdx] - self.outlier_thresh*scale
        
        self.a = ab[0]
        self.b = ab[1]        

        # check for steps in the last part of the data - if enough data
        if err.shape[0]> 2*self.step_size:
            mu_err = np.median(err[:-self.step_size])
            std_err = np.std(err[:-self.step_size])
            mu = np.median(err[-self.step_size:])
            if mu > mu_err + self.step_threshold * std_err or mu < mu_err - self.step_threshold * std_err:
                #print('step detected!')
                self.reset(keep_model=True)

    def getX(self,y):
        return ( y  - self.b ) / self.a 

    def getY(self,x):
        return self.a * x + self.b

    @staticmethod
    def testcase():
        X = np.arange(1000) + np.random.randn(1)*1e6
        a = 1000/50 
        b = 1000*np.random.randn(1)
        Ytrue= a*X+b
        Y    = Ytrue+ np.random.standard_normal(Ytrue.shape)*10

        import glob
        import os
        files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../logs/mindaffectBCI*.txt')) # * means all if need specific format then *.csv
        savefile = max(files, key=os.path.getctime)
        #savefile = "C:\\Users\\Developer\\Downloads\\mark\\mindaffectBCI_brainflow_200911_1339.txt" 
        #savefile = "C:/Users/Developer/Downloads/khash/mindaffectBCI_brainflow_ipad_200908_1938.txt"
        from mindaffectBCI.decoder.offline.read_mindaffectBCI import read_mindaffectBCI_messages
        from mindaffectBCI.utopiaclient import DataPacket
        print("Loading: {}".format(savefile))
        msgs = read_mindaffectBCI_messages(savefile,regress=None) # load without time-stamp fixing.
        dp = [ m for m in msgs if isinstance(m,DataPacket)]
        nsc = np.array([ (m.samples.shape[0],m.sts,m.timestamp) for m in dp])
        X = np.cumsum(nsc[:,0])
        Y = nsc[:,1]
        Ytrue = nsc[:,2]

        ltt = lower_bound_tracker(window_size=200, outlier_thresh=2, step_size=10, step_threshold=3)
        ltt.fit(X[0],Y[0]) # check scalar inputs
        step = 1
        idxs = list(range(1,X.shape[0],step))
        ab = np.zeros((len(idxs),2))
        print("{}) a={} b={}".format('true',a,b))
        dts = np.zeros((Y.shape[0],))
        dts[0] = ltt.getY(X[0])
        for i,j in enumerate(idxs):
            dts[j:j+step] = ltt.transform(X[j:j+step],Y[j:j+step])
            ab[i,:] = (ltt.a,ltt.b)
            yest = ltt.getY(X[j])
            err =  yest - Y[j]
            if abs(err)> 1000:
                print("{}) argh! yest={} ytrue={} err={}".format(i,yest,Ytrue[j],err))
            if i < 100:
                print("{:4d}) a={:5f} b={:5f}\ty_est-y={:2.5f}".format(j,ab[i,0],ab[i,1],
                        Y[j]-yest))

        import matplotlib.pyplot as plt
        ab,res,_,_ = np.linalg.lstsq(np.append(X[:,np.newaxis],np.ones((X.shape[0],1)),1),Y,rcond=-1)
        ots = X*ab[0]+ab[1]        
        idx=range(X.shape[0])
        plt.plot(X[idx],Y[idx]- X[idx]*ab[0]-Y[0],label='server ts')
        plt.plot(X[idx],dts[idx] - X[idx]*ab[0]-Y[0],label='regressed ts (samp vs server)')
        plt.plot(X[idx],ots[idx] - X[idx]*ab[0]-Y[0],label='regressed ts (samp vs server) offline')

        err = Y - X*ab[0] - Y[0]
        cent = np.median(err); scale=np.median(np.abs(err-cent))
        plt.ylim((cent-scale*5,cent+scale*5))

        plt.legend()
        plt.show()

if __name__ == "__main__":
    lower_bound_tracker.testcase()