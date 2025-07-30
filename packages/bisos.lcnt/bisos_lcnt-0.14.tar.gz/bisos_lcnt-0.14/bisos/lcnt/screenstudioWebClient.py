# -*- coding: utf-8 -*-
"""\
* TODO *[Summary]* ::  A /library/ Beginning point for development of new ICM oriented libraries.
"""

####+BEGIN: bx:cs:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
""" #+begin_org
*  This file:/bisos/git/bxRepos/bisos-pip/lcnt/py3/bisos/lcnt/screenstudioWebClient.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM).
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 *WARNING*: All edits wityhin Dynamic Blocks may be lost.
#+end_org """
####+END:


"""
*  [[elisp:(org-cycle)][| *Lib-Module-INFO:* |]] :: Author, Copyleft and Version Information
"""

####+BEGIN: bx:global:lib:name-py :style "fileName"
__libName__ = "screenstudioWebClient"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "202502110108"
####+END:

####+BEGIN: bx:global:icm:status-py :status "Production"
__status__ = "Production"
####+END:

__credits__ = [""]

####+BEGIN: bx:cs:python:topControls 
""" #+begin_org
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
#+end_org """
####+END:



####+BEGIN: bx:cs:python:section :title "ContentsList"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ContentsList*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:dblock:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Imports=  [[elisp:(outline-show-subtree+toggle)][||]] *IMPORTS*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGINNOT: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

import os
import collections
import enum

import requests

####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:cs:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:cs:python:func :funcName "serviceUrlDefault" :funcType "defaultVerify" :retType "echo" :deco "" :argsList "serviceUrl"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-defaultVerify [[elisp:(outline-show-subtree+toggle)][||]] /serviceUrlDefault/ retType=echo argsList=(serviceUrl)  [[elisp:(org-cycle)][| ]]
#+end_org """
def serviceUrlDefault(
    serviceUrl,
):
####+END:
    if not serviceUrl:
        return "http://localhost:8080"
    else:
        return serviceUrl



####+BEGIN: b:py3:class/decl :className "ScreenstudioWebClient" :superClass "" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /ScreenstudioWebClient/  superClass=object  [[elisp:(org-cycle)][| ]]
#+end_org """
class ScreenstudioWebClient(object):
####+END:
    """
** This is just a placeholder for now. It needs to use the filesystem for persistence.
"""
        
    def __init__(self,
                 serviceUrl=None,
    ):
        self.serviceUrl = serviceUrl

    def recordingStart(self,):
        try:
            response = requests.get(self.serviceUrl)
        except Exception as e:
            print(e)
            return False

        b_io.ann.here(response)
        b_io.ann.here(response.status_code)

        startRecordingUrl = "{serviceUrl}/?action=record".format(serviceUrl=self.serviceUrl)
        print(startRecordingUrl)
        try:
            resp = requests.get(startRecordingUrl)

        except Exception as e:
            print(e)
            return False

        print(resp)

    def recordingStop(self,):
        self.recordingStart()
      
    def recordingStatus(self,):
        b_io.ann.here("NOTYET")

####+BEGIN: bx:dblock:python:section :title "ICM Examples"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Examples*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:cs:python:func :funcName "commonParamsSpecify" :funcType "void" :retType "bool" :deco "" :argsList "csParams"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-void     [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/ retType=bool argsList=(csParams)  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
    csParams,
):
####+END:

    csParams.parDictAdd(
        parName='sessionType',
        parDescription="One of: liveSession or narratedSession",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--sessionType',
    )

    csParams.parDictAdd(
        parName='nuOfDisplays',
        parDescription="One of: 1 or 3",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--nuOfDisplays',
    )
    


####+BEGIN: bx:cs:python:func :funcName "recordingIcmExamples" :funcType "void" :retType "bool" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-void     [[elisp:(outline-show-subtree+toggle)][||]] /recordingIcmExamples/ retType=bool argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def recordingIcmExamples():
####+END:
        def cpsInit(): return collections.OrderedDict()
        def menuItem(): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
        def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        nuOfDisplays = nuOfDisplaysGet().cmnd().results

        cs.examples.menuChapter('*Recorder Preparations*')

        cmndName = "screenstudioRcUpdate"
        cmndArgs = ""; cps = cpsInit(); cps['sessionType'] = "liveSession"
        menuItem()

        cmndArgs = ""; cps = cpsInit(); cps['sessionType'] = "narratedSession"
        menuItem()

        cmndName = "screenstudioRcStdout"
        cmndArgs = ""; cps = cpsInit(); cps['sessionType'] = "liveSession" ; cps['nuOfDisplays'] = nuOfDisplays
        menuItem()

        cmndArgs = ""; cps = cpsInit(); cps['sessionType'] = "narratedSession" ; cps['nuOfDisplays'] = nuOfDisplays
        menuItem()

        cmndName = "screenstudioRun"
        cmndArgs = ""; cps = cpsInit(); # cps['sessionType'] = "liveSession" ; cps['nuOfDisplays'] = nuOfDisplays
        menuItem()

        cmndName = "recorderIsUp"
        cmndArgs = serviceUrlDefault(None); cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        menuItem()
        #cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')

        cs.examples.menuChapter('*Recordings Start/Stop*')
        
        cmndName = "recordingStart"
        cmndArgs = serviceUrlDefault(None); cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        menuItem()
        
        cmndName = "recordingStop"
        cmndArgs = serviceUrlDefault(None); cps = cpsInit(); # cps['icmsPkgName'] = icmsPkgName 
        menuItem()


        
 
####+BEGIN: bx:dblock:python:section :title "Recording ICMs -- Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Recording ICMs -- Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "recordingStart" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<recordingStart>>  =verify= argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class recordingStart(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        serviceUrl = serviceUrlDefault(effectiveArgsList[0])

        myName=self.myName()
        thisOutcome = b.op.Outcome(invokerName=myName)

        screenstudioClient = ScreenstudioWebClient(serviceUrl=serviceUrl)

        screenstudioClient.recordingStart()
        
        return thisOutcome
    
    def cmndDocStr(self): return """
** Place holder for ICM's experimental or test code.  [[elisp:(org-cycle)][| ]]
 You can use this Cmnd for rapid prototyping and testing of newly developed functions.
"""
    

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "recordingStop" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<recordingStop>>  =verify= argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class recordingStop(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        serviceUrl = serviceUrlDefault(effectiveArgsList[0])

        myName=self.myName()
        thisOutcome = b.op.Outcome(invokerName=myName)

        screenstudioClient = ScreenstudioWebClient(serviceUrl=serviceUrl)

        screenstudioClient.recordingStop()
        
        return thisOutcome
    
    def cmndDocStr(self): return """
** Place holder for ICM's experimental or test code.  [[elisp:(org-cycle)][| ]]
 You can use this Cmnd for rapid prototyping and testing of newly developed functions.
"""

        
 
####+BEGIN: bx:dblock:python:section :title "Recorder Configuration And Run ICMs -- Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Recorder Configuration And Run ICMs -- Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "nuOfDisplaysGet" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<nuOfDisplaysGet>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class nuOfDisplaysGet(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:

        outcome = icm.subProc_bash(
            """\
xrandr -q | grep ' connected' | wc -l\
"""
        ).log()
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))

        nuOfScreens = outcome.stdout.strip('\n')

        if rtInv.outs:
            b_io.ann.write("{}".format(nuOfScreens))
        
        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=nuOfScreens,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "screenstudioRun" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<screenstudioRun>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class screenstudioRun(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        """
** TODO UnUsed.
        """
        
        #offlineimaprcPath = withInMailDomGetOfflineimaprcPath(controlProfile, inMailAcct)            

        outcome = icm.subProc_bash(
            """screenstudio"""
        ).log()
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))
        
        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "screenstudioRcUpdate" :comment "" :parsMand "sessionType" :parsOpt "nuOfDisplays" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<screenstudioRcUpdate>>  =verify= parsMand=sessionType parsOpt=nuOfDisplays ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class screenstudioRcUpdate(cs.Cmnd):
    cmndParamsMandatory = [ 'sessionType', ]
    cmndParamsOptional = [ 'nuOfDisplays', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             sessionType: typing.Optional[str]=None,  # Cs Mandatory Param
             nuOfDisplays: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'sessionType': sessionType, 'nuOfDisplays': nuOfDisplays, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        sessionType = csParam.mappedValue('sessionType', sessionType)
        nuOfDisplays = csParam.mappedValue('nuOfDisplays', nuOfDisplays)
####+END:

        if not nuOfDisplays:
            outcome = nuOfDisplaysGet().cmnd()
            if outcome.isProblematic(): return(io.eh.badOutcome(outcome))
            
            nuOfDisplays = outcome.results

        outcome = screenstudioRcStdout().cmnd(
            interactive=False,
            sessionType=sessionType,
            nuOfDisplays=nuOfDisplays,
        )
        if outcome.isProblematic(): return(io.eh.badOutcome(outcome))

        screenstudioRcStr = outcome.results

        screenstudioRcPath = screenstudioRcFileNameGet(sessionType, nuOfDisplays)

        with open(screenstudioRcPath, "w") as thisFile:
            thisFile.write(screenstudioRcStr + '\n')

        if rtInv.outs:
            b_io.ann.here("screenstudioRcPath={val}".format(val=screenstudioRcPath))
        
        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=screenstudioRcPath,
        )

####+BEGIN: bx:cs:python:func :funcName "screenstudioRcFileNameGet" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "sessionType nuOfDisplays"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /screenstudioRcFileNameGet/ retType=bool argsList=(sessionType nuOfDisplays)  [[elisp:(org-cycle)][| ]]
#+end_org """
def screenstudioRcFileNameGet(
    sessionType,
    nuOfDisplays,
):
####+END:
    fileName = "./screenstudio-{sessionType}-{nuOfDisplays}disps.xml".format(
        sessionType=sessionType,
        nuOfDisplays=nuOfDisplays,
    )
    return os.path.abspath(fileName)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "screenstudioRcStdout" :comment "" :parsMand "sessionType" :parsOpt "nuOfDisplays" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<screenstudioRcStdout>>  =verify= parsMand=sessionType parsOpt=nuOfDisplays ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class screenstudioRcStdout(cs.Cmnd):
    cmndParamsMandatory = [ 'sessionType', ]
    cmndParamsOptional = [ 'nuOfDisplays', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             sessionType: typing.Optional[str]=None,  # Cs Mandatory Param
             nuOfDisplays: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'sessionType': sessionType, 'nuOfDisplays': nuOfDisplays, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        sessionType = csParam.mappedValue('sessionType', sessionType)
        nuOfDisplays = csParam.mappedValue('nuOfDisplays', nuOfDisplays)
####+END:

        if not nuOfDisplays:
            outcome = nuOfDisplaysGet().cmnd()
            if outcome.isProblematic(): return(io.eh.badOutcome(outcome))
            
            nuOfDisplays = outcome.result

        cwd = os.getcwd()

        if sessionType == "narratedSession":
            audiosystemStr="""Monitor of Built-in Audio Analog Stereo"""
            microphoneStr="""None"""

        elif sessionType == "liveSession":
            audiosystemStr="""None"""
            microphoneStr="""Yeti Stereo Microphone Analog Stereo"""
            
        else:
            b_io.eh.usageError("Bad sessionType -- {}".format(sessionType))

        displaysStr = screenstudioRcTemplate(
            nuOfDisplays,
        )

        if displaysStr:
            resStr = displayStr.format(
                audiosystemStr=audiosystemStr,
                microphoneStr=microphoneStr,
                outputvideofolderStr=cwd,
            )
        else:
            resStr = ""   # NOTYET, Is This An Error?

        if rtInv.outs:
            print(resStr)
        
        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=resStr
        )

####+BEGIN: bx:cs:python:func :funcName "screenstudioRcTemplate" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "nuOfDisplays"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /screenstudioRcTemplate/ retType=bool argsList=(nuOfDisplays)  [[elisp:(org-cycle)][| ]]
#+end_org """
def screenstudioRcTemplate(
    nuOfDisplays,
):
####+END:

    screens_1_templateStr = """ 
<?xml version="1.0" encoding="UTF-8" standalone="no"?><screenstudio><audios audiobitrate="Audio44K" audiosystem="{audiosystemStr}" microphone="{microphoneStr}"/><output outputframerate="10" outputheight="1080" outputpreset="ultrafast" outputtarget="MP4" outputvideofolder="{outputvideofolderStr}" outputwidth="1920" rtmpkey="" rtmpserver="" videobitrate="1000"/><settings backgroundmusic=""/><desktop bg="0" bgAreaColor="0" capturex="0" capturey="0" effect="None" end="0" fg="0" font="" fontsize="0" id="Screen 1" start="0" transstart="None" transstop="None" type=""><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/></desktop></screenstudio>
"""

    screens_3_templateStr = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?><screenstudio><audios audiobitrate="Audio44K" audiosystem="{audiosystemStr}" microphone="{microphoneStr}"/><output outputframerate="10" outputheight="1080" outputpreset="ultrafast" outputtarget="MP4" outputvideofolder="{outputvideofolderStr}" outputwidth="1920" rtmpkey="" rtmpserver="" videobitrate="1000"/><settings backgroundmusic=""/><desktop bg="0" bgAreaColor="0" capturex="0" capturey="0" effect="None" end="0" fg="0" font="" fontsize="0" id="Screen 3" start="0" transstart="None" transstop="None" type=""><view alpha="1.0" display="true" h="1080" name="View" order="0" w="1920" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="5760" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="5760" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="5760" x="0" y="0"/><view alpha="1.0" display="true" h="1080" name="View" order="0" w="5760" x="0" y="0"/></desktop></screenstudio>
"""

    templateStr = None          

    icm.unusedSuppressForEval(
        screens_1_templateStr,
        screens_3_templateStr,
    )

    exec(
        "templateStr = screens_{}_templateStr".format(str(nuOfDisplays))
    )

    return templateStr

    
    

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _ ~End Of Editable Text~ _: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:
