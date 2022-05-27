#  Copyright (c) 2019 MindAffect B.V. 
#  Author: Jason Farquhar <jadref@gmail.com>
# This file is part of pymindaffectBCI <https://github.com/mindaffect/pymindaffectBCI>.
#
# pymindaffectBCI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pymindaffectBCI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pymindaffectBCI.  If not, see <http://www.gnu.org/licenses/>

import numpy as np
from mindaffectBCI.decoder.normalizeOutputScores import normalizeOutputScores
from mindaffectBCI.decoder.zscore2Ptgt_softmax import zscore2Ptgt_softmax
from mindaffectBCI.decoder.utils import block_permute

#@function
def decodingSupervised(Fy, softmaxscale=3.5, marginalizemodels=True, 
                       marginalizedecis=False,
                       prior=None,
                       nocontrolamplitude=None,
<<<<<<< HEAD
                       tiebreaking_noise=1e-3, nvirt_out=None, **kwargs):
=======
                       tiebreaking_noise=1e-3, **kwargs):
>>>>>>> 53e3633bc55dd13512738c132868bdd9a2fa713a
  """    true-target estimator and error-probility estimator for each trial

   Args:
      Fy (nModel,nTrl,nEp,nY): The output scores.
      softmaxscale (float, optional): the scale length to pass to zscore2Ptgt_softmax.py, this is the inverse *noise* sigma. Defaults to 3.5.
      badFyThresh (int, optional): threshold for detction of bad Fy entry, in std-dev. Defaults to 4.
      centFy (bool, optional): bool, do we center Fy before computing  *important*  (true). Defaults to True.
      detrendFy (bool, optional): [description]. Defaults to True.
      nEpochCorrection (int, optional): int, number of epochs to use a base for correction of number epochs in the sum.
               such that: zscore = Fy / ( sigma * ( 1+1/(nEpoch/nEpochErrorCorrection)) ),
               basically, nEpoch < nEpochCorrection have highly increased Perr, so unlikely to be selected. Defaults to 100.
      minDecisLen (int, optional): int, number of epochs to use as base for distribution of time-based decision points.
                         i.e. decisions at, [1,2,4,...2^n]*exptDistDecis
                    OR: minDecisLen<0 => decision point every abs(minDeicsLen) epochs. Defaults to 0.
      maxDecisLen (int, optional): maximum number of epochs for a decision. Defaults to 0.
      bwdAccumulate (bool, optional): accumulate data backwards from last epoch gathered. Defaults to False.
      marginalizemodels (bool, optional): [description]. Defaults to True.
      marginalizedecis (bool, optional): [description]. Defaults to False.
      prior ([type], optional): [description]. Defaults to None.
      nocontrolamplitude ([type], optional): [description]. Defaults to None.
      priorsigma (tuple, optional): (sigma,N) prior estimate of sigma2 and number pseudo-points. Defaults to (-1,120).
      tiebreaking_noise ([type], optional): [description]. Defaults to 1e-3.

   Raises:
      NotImplementedError: [description]

   Returns:
      Yest (nTrl,nDecis): the most likely / minimum error output for each decision point
      Perr (nTrl,nDecis): the probability that this selection is an ERROR for each decision point
      Ptgt (nTrl,nDecis,nY): the probability each target is the true target for each decision point
      decisMdl, 
      decisEp

    Copyright (c) MindAffect B.V. 2018
  """   
  if Fy is None:
      return -1, 1, None, None, None
  
<<<<<<< HEAD
  if nvirt_out is not None and not nvirt_out == 0:
    # generate virtual outputs for testing -- not from the 'true' target though
    virt_Fy = block_permute(Fy[...,1:], nvirt_out, axis=-1, perm_axis=-2)
    nvirt_out = virt_Fy.shape[-1]
    Fy = np.append(Fy,virt_Fy,axis=-1)

  #print("decodingSup args={}".format(kwargs))

  # get the info on which outputs are zero in each trial
  validTgt = np.any(Fy != 0, axis=-2) # valid if non-zero for any epoch..# (nModel,nTrl,nY)  
  # normalize the raw scores for each model to have nice distribution
  ssFy,varsFy,decisIdx,nEp,nY=normalizeOutputScores(Fy, validTgt=validTgt, **kwargs)

  if nocontrolamplitude is not None:
    raise NotImplementedError('no-control signal not yet implemented correctly')
    # # add a no-control pseudo-output to simulate not looking
    # #Median rather than mean?
    # mussFy=np.sum(ssFy,0)/np.maximum(2,np.sum(validTgt,0,keepdims=True)) # mean score for each trial/decisPt [ 1 x nDecis x nTrl x nMdl ]
    # # add to the scores & validTgt info
    # ssFy=np.concatenate((ssFy,nocontrolamplitude+mussFy),0)
    # validtgtTrl=np.concatenate((validtgtTrl,np.ones([1,size(validtgtTrl,2),size(validtgtTrl,3),size(validtgtTrl,4)])))

  # compute the target probabilities over output for each model+trial
  # use the softmax approach to get Ptgt for all outputs
  Ptgt = zscore2Ptgt_softmax(ssFy,
                              softmaxscale,
                              validTgt=validTgt,
                              marginalizemodels=marginalizemodels,
                              marginalizedecis=marginalizedecis,
                              prior=prior) # (nM,nTrl,nDecis,nY)
  # extract the predicted output and it's probability of being the target
  Ptgt2d = Ptgt.reshape((np.prod(Ptgt.shape[:-1]), Ptgt.shape[-1])) # make 2d-copy
  # add tie-breaking noise
  if tiebreaking_noise > 0:
      Ptgt2d = Ptgt2d + (np.random.standard_normal(Ptgt2d.shape)*tiebreaking_noise).astype(Ptgt.dtype)
      Ptgt2d = np.maximum(0,np.minimum(1,Ptgt2d,dtype=Ptgt.dtype),dtype=Ptgt.dtype)

=======
  #print("decodingSup args={}".format(kwargs))

  # get the info on which outputs are zero in each trial
  validTgt = np.any(Fy != 0, axis=-2) # valid if non-zero for any epoch..# (nModel,nTrl,nY)  
  # normalize the raw scores for each model to have nice distribution
  ssFy,varsFy,decisIdx,nEp,nY=normalizeOutputScores(Fy, validTgt=validTgt, **kwargs)

  if nocontrolamplitude is not None:
    raise NotImplementedError('no-control signal not yet implemented correctly')
    # # add a no-control pseudo-output to simulate not looking
    # #Median rather than mean?
    # mussFy=np.sum(ssFy,0)/np.maximum(2,np.sum(validTgt,0,keepdims=True)) # mean score for each trial/decisPt [ 1 x nDecis x nTrl x nMdl ]
    # # add to the scores & validTgt info
    # ssFy=np.concatenate((ssFy,nocontrolamplitude+mussFy),0)
    # validtgtTrl=np.concatenate((validtgtTrl,np.ones([1,size(validtgtTrl,2),size(validtgtTrl,3),size(validtgtTrl,4)])))

  # compute the target probabilities over output for each model+trial
  # use the softmax approach to get Ptgt for all outputs
  Ptgt = zscore2Ptgt_softmax(ssFy,
                              softmaxscale,
                              validTgt=validTgt,
                              marginalizemodels=marginalizemodels,
                              marginalizedecis=marginalizedecis,
                              prior=prior) # (nM,nTrl,nDecis,nY)
  # extract the predicted output and it's probability of being the target
  Ptgt2d = Ptgt.reshape((np.prod(Ptgt.shape[:-1]), Ptgt.shape[-1])) # make 2d-copy
  # add tie-breaking noise
  if tiebreaking_noise > 0:
      Ptgt2d = Ptgt2d + np.random.standard_normal(Ptgt2d.shape)*tiebreaking_noise

>>>>>>> 53e3633bc55dd13512738c132868bdd9a2fa713a
  Yestidx = np.argmax(Ptgt2d, -1) # max over outputs, i.e. models, decisPts, etc..
  Ptgt_max = Ptgt2d[np.arange(Ptgt2d.shape[0]), Yestidx] # value at max, indexing trick to find..
  Yestidx = Yestidx.reshape(Ptgt.shape[:-1]) # -> (nM,nTrl,nY)
  Ptgt_max = Ptgt_max.reshape(Ptgt.shape[:-1])# -> (nM,nTrl,nY)

  # pick a model for this maxY
  decisMdl = Yestidx if ssFy.ndim>3 else 1
  decisEp = 1   
  Yest = Yestidx
<<<<<<< HEAD

  # remove the virtual outputs and replace the idx with -1
  if nvirt_out is not None and not nvirt_out == 0:
    nreal_out = Ptgt.shape[-1]-nvirt_out
    Ptgt = Ptgt[...,:-nvirt_out]
    Yest[Yest>=nreal_out] = -1

=======
>>>>>>> 53e3633bc55dd13512738c132868bdd9a2fa713a
  # p(maxz != tgt ) = 1 - p(maxz==tgt)
  Perr = 1 - Ptgt_max
  return Yest, Perr, Ptgt, decisMdl, decisEp


def decodingSupervised_streamed(Fy,softmaxscale=3,nocontrolamplitude=None,
                                marginalizemodels=False):
    '''
    true-target estimator and error-probility estimator for each trial
    Inputs:
      Fy   - (nModel,nTrl,nEp,nY) [#Y x #Epoch x #Trials x nModels]
      softmaxscale - the scale length to pass to zscore2Ptgt_softmax.py
      badFyThresh - threshold for detction of bad Fy entry, in std-dev
      centFy   - bool, do we center Fy before computing  *important*  (true)
      nEpochCorrection - int, number of epochs to use a base for correction of number epochs in the sum.
               such that: zscore = Fy / ( sigma * ( 1+1/(nEpoch/nEpochErrorCorrection)) ),
               basically, nEpoch < nEpochCorrection have highly increased Perr, so unlikely to be selected
      minDecisLen - int, number of epochs to use as base for distribution of time-based decision points.
                         i.e. decisions at, [1,2,4,...2^n]*exptDistDecis
                    OR: minDecisLen<0 => decision point every abs(minDeicsLen) epochs
      bwdAccumulate - [bool], accumulate data backwards from last epoch gathered
      maxDecisLen   - maximum number of epochs for a decision
    Outputs:
      Yest - (nTrl,nDecis) [ nDecis x nTrl ] the most likely / minimum error output for each decision point
      Perr - (nTrl,nDecis) [ nDecix x nTrl ] the probability that this selection is an ERROR for each decision point
      Ptgt - (nTrl,nDecis,nY) [ nY x nDecis x nTrl ] the probability each target is the true target for each decision point

    Copyright (c) MindAffect B.V. 2018
    '''
    if Fy is None:
        return -1, 1, None, None, None
    
    # get the info on which outputs are zero in each trial
    validTgt = np.any(Fy != 0, axis=-2) # valid if non-zero for any epoch..# (nModel,nTrl,nY) [ nY x nTrl x nModel ]   
    # normalize the raw scores for each model to have nice distribution
    stdFy,varsFy,N,nEp,nY=normalizeOutputScores_streamed(Fy, validTgt=validTgt,
                                                         badFyThresh=badFyThresh, centFy=centFy,
                                                         minDecisLen=minDecisLen, filtLen=filtLen)



    # compute the target probabilities over output for each block+model+trial
    # use the softmax approach to get Ptgt for all outputs
    Ptgt = zscore2Ptgt_softmax(ssFy,
                               softmaxscale,
                               validTgt=validTgt,
                               marginalizemodels=False) # (nM,nTrl,nDecis,nY) [ nY x nDecis x nTrl]
    # extract the predicted output and it's probability of being the target
    Ptgt2d = Ptgt.reshape((np.prod(Ptgt.shape[:-1]), Ptgt.shape[-1])) # make 2d-copy
    Yestidx = np.argmax(Ptgt2d, -1) # max over outputs
    Ptgt_max = Ptgt2d[np.arange(Ptgt2d.shape[0]), Yestidx] # value at max, indexing trick to find..
    Yestidx = Yestidx.reshape(Ptgt.shape[:-1]) # -> (nM,nTrl,nY)
    Ptgt_max = Ptgt_max.reshape(Ptgt.shape[:-1])# -> (nM,nTrl,nY)

    # pick a model for this maxY
    decisMdl = Yestidx if ssFy.ndim>3 else 1
    decisEp = 1   
    Yest = Yestidx
    # p(maxz != tgt ) = 1 - p(maxz==tgt)
    Perr = 1 - Ptgt_max
    return Yest, Perr, Ptgt, decisMdl, decisEp



#@function
def testcase():
    from normalizeOutputScores import mktestFy
    Fy,nEp=mktestFy(startupNoisefrac=0,trlenfrac=0,sigstr=.4)
    from decodingSupervised import decodingSupervised
    print("Fy={}".format(Fy.shape))
    Yest,Perr,Ptgt,decismdl,decisEp=decodingSupervised(Fy)
    print("Fy={}".format(Fy[:,[0],:,:].shape))
    Yest,maxp,ssFy,decismdl,decisEp=decodingSupervised(Fy[:,[0],:,:])
    np.mean(Yest == 0,1) 
    from decodingCurveSupervised import decodingCurveSupervised
    decodingCurveSupervised(Fy);

if __name__=="__main__":
    testcase()

