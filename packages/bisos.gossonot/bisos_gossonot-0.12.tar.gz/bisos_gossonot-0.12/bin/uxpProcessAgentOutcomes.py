#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
print("NOTYET, to be revisited.")
sys.exit()


"""\
*    *[Summary]* :: An =ICM=: Bxp (ByStar Platform) Tpa (Target Parameters and Actions) Monitor. 
*  Loads Target-Lists and Params and invokes these ICM Actions and Agent-Actions.
"""

####+BEGIN: bx:cs:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
""" #+begin_org
*  This file:/bisos/git/bxRepos/bisos-pip/gossonot/py3/bin/uxpProcessAgentOutcomes.py :: [[elisp:(org-cycle)][| ]]
 is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
 *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
 A Python Interactively Command Module (PyICM).
 Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
 *WARNING*: All edits wityhin Dynamic Blocks may be lost.
#+end_org """
####+END:

"""
*  [[elisp:(org-cycle)][| *ICM-INFO:* |]] :: Author, Copyleft and Version Information
"""
####+BEGIN: bx:cs:python:name :style "fileName"

####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "202502124844"
####+END:

####+BEGIN: bx:global:icm:status-py :status "Production"
__status__ = "Production"
####+END:

__credits__ = [""]

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/csInfo-mbNedaGpl.py"

####+END:

####+BEGIN: bx:cs:python:topControls :partof "bystar" :copyleft "halaal+minimal"
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

####+BEGIN: bx:cs:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
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

import sys
import os

import shlex
import subprocess


from bisos.csPlayer import bleep

from bisos.gossonot import gossonotPkgThis

from bisos.things import toIcm

g_importedCmnds = {        # Enumerate modules from which CMNDs become invokable
    'bleep': bleep.__file__,    
}


####+BEGIN: bx:cs:python:section :title "= =Framework::= ICM  Description (Overview) ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM  Description (Overview) =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:cs:python:section :title "= =Framework::= ICM Hooks ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= ICM Hooks =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:cs:python:func :funcName "g_icmChars" :comment "ICM Characteristics Spec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-FrameWrk [[elisp:(outline-show-subtree+toggle)][||]] /g_icmChars/ =ICM Characteristics Spec= retType=Void argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def g_icmChars():
####+END:
    csInfo['panel'] = "{}-Panel.org".format(__icmName__)
    csInfo['groupingType'] = "IcmGroupingType-pkged"
    csInfo['cmndParts'] = "IcmCmndParts[common] IcmCmndParts[param]"
    
g_icmChars()


####+BEGIN: bx:cs:python:func :funcName "g_icmPreCmnds" :funcType "FrameWrk" :retType "Void" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-FrameWrk [[elisp:(outline-show-subtree+toggle)][||]] /g_icmPreCmnds/ retType=Void argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def g_icmPreCmnds():
####+END:
    """ PreHook """
    pass


####+BEGIN: bx:cs:python:func :funcName "g_icmPostCmnds" :funcType "FrameWrk" :retType "Void" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-FrameWrk [[elisp:(outline-show-subtree+toggle)][||]] /g_icmPostCmnds/ retType=Void argsList=nil deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def g_icmPostCmnds():
####+END:
    """ PostHook """
    pass


####+BEGIN: bx:cs:python:section :title "= =Framework::= Options, Arguments and Examples Specifications ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::= Options, Arguments and Examples Specifications =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:cs:python:func :funcName "g_argsExtraSpecify" :comment "FrameWrk: ArgsSpec" :funcType "FrameWrk" :retType "Void" :deco "" :argsList "parser"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-FrameWrk [[elisp:(outline-show-subtree+toggle)][||]] /g_argsExtraSpecify/ =FrameWrk: ArgsSpec= retType=Void argsList=(parser)  [[elisp:(org-cycle)][| ]]
#+end_org """
def g_argsExtraSpecify(
    parser,
):
####+END:
    """Module Specific Command Line Parameters.
    g_argsExtraSpecify is passed to G_main and is executed before argsSetup (can not be decorated)
    """
    G = cs.globalContext.get()
    csParams = cs.CmndParamDict()

    csParams.parDictAdd(
        parName='moduleVersion',
        parDescription="Module Version",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--version',
    )

    csParams.parDictAdd(
        parName='pkgSrc',
        parDescription="Package Source",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--pkgSrc',
    )
    
    bleep.commonParamsSpecify(csParams)    
    
    toIcm.targetParamListCommonArgs(parser)    
       
    cs.argsparseBasedOnCsParams(parser, csParams)

    # So that it can be processed later as well.
    G.icmParamDictSet(csParams)
    
    return


####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "examples" :cmndType "ICM-Cmnd-FWrk"  :comment "FrameWrk: ICM Examples" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-ICM-Cmnd-FWrk [[elisp:(outline-show-subtree+toggle)][||]] <<examples>>  *FrameWrk: ICM Examples*  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:
        """FrameWrk: ICM Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        def cpsInit(): return collections.OrderedDict()
        def menuItem(): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
        def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

        icmsPkgInfoBaseDir = gossonotPkgThis.pkgBase_baseDir()

        #print icmsPkgInfoBaseDir

        logControler = b_io.log.Control()
        logControler.loggerSetLevel(20)

        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())
        
        cs.examples.commonBrief()    

        bleep.examples_csBasic()

        
####+BEGIN: bx:cs:python:cmnd:subSection :title "Dev And Testing"

####+END:

        cs.examples.menuChapter('*General Dev and Testing CMNDs*')

        cmndName = "unitTest" ; cmndArgs = "" ;
        cps = collections.OrderedDict() ; # cps['icmsPkgName'] = icmsPkgName 
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='little')
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='full')

        
####+BEGIN: bx:cs:python:cmnd:subSection :title "Simplified Targets Selection"

####+END:
        
        cs.examples.menuChapter('*Simplified Targets Selection*')

        # execLineEx("""ln -s /de/bx/current/district/librecenter/tiimi/targets/bxp/tList/ts-librecenter-localhostIcm.py liTargets.py""")
        # execLineEx("""ln -s /de/bx/current/district/librecenter/tiimi/targets/bxp/paramList/bxpUsageParamsIcm.py liParams.py""")

        execLineEx("""ln -s {pkgBaseDir}/ts-librecenter-localhostIcm.py liTargets.py""".format(pkgBaseDir=icmsPkgInfoBaseDir))
        execLineEx("""ln -s {pkgBaseDir}/bxpUsageParamsIcm.py liParams.py""".format(pkgBaseDir=icmsPkgInfoBaseDir))
        
        execLineEx("""stress --cpu 2 --io 1 --vm 1 --vm-bytes 128M --timeout 10s --verbose""")

        loadTargetArgs=""" --load ./liTargets.py"""
        loadParamsArgs=""" --load ./liParams.py """    
        #ticmoFullInfo=format(commonArgs + loadTargetArgs)

        toIcm.targetParamSelectCommonExamples()

        toIcm.targetParamListCommonExamples(loadTargetArgs=loadTargetArgs,
                                       loadParamsArgs=loadParamsArgs)
    
        #fileParamPath1 = "/de/bx/coll/libreCenter/platforms/bue/0015/params/access/cur/"
        #fileParamPath2 = "/de/bx/coll/libreCenter/platforms/bue/0015/params/access/cur/"

####+BEGIN: bx:cs:python:cmnd:subSection :title "Run With Targets"

####+END:
        
        cs.examples.menuChapter('/TOICM: Monitor/ *targetsParamsToIcmMonitor*')   

        thisCmndAction= " -i linuxUsageKpisRetrieve"
    
        # accessParams = " --targetFqdn " + thisTargetFqdn + " --userName " + thisUser + " --password " + thisPassword
        # icm.cmndExampleMenuItem(format(toIcmMonitorArgs + accessParams  +  thisCmndAction),
        #                         verbosity='none')                            

        icm.cmndExampleMenuItem(format(loadTargetArgs + loadParamsArgs +  thisCmndAction),
                               verbosity='none')                            
        icm.cmndExampleMenuItem(format(loadTargetArgs + loadParamsArgs + thisCmndAction),
                               verbosity='full')                            

        #
        # ICMs PKG Information
        #


        # icmsPkgLib.examples_pkgInfoParsFull(
        #     icmsPkgNameSpecification(),
        #     icmsPkgInfoBaseDir=icmsPkgInfoBaseDir,
        #     icmsPkgControlBaseDir=icmsPkgControlBaseDirDefault(),
        #     icmsPkgRunBaseDir=icmsPkgRunBaseDirDefault(),
        # )
        


####+BEGIN: bx:cs:python:section :title "ICM Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Commands*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "unitTest" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<unitTest>>  =verify= argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class unitTest(cs.Cmnd):
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

        myName=self.myName()
        thisOutcome = b.op.Outcome(invokerName=myName)

        print(G.csInfo)

        for eachArg in effectiveArgsList:
            b_io.ann.here("{}".format(eachArg))

        print((icm.__file__))
        print(sys.path)

        import imp
        print((imp.find_module('unisos/icm')))

        @ucf.runOnceOnly
        def echo(str):
            print(str)
            
        echo("first")
        echo("second")  # Should not run
    
        return thisOutcome
    
    def cmndDocStr(self): return """
** Place holder for ICM's experimental or test code.  [[elisp:(org-cycle)][| ]]
*** You can use this Cmnd for rapid prototyping and testing of newly developed functions.
"""


    

####+BEGIN: bx:cs:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *General Interactively Invokable Functions (CMND)*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Common-CMND   ::  commonParamsDefaultsSet    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def commonParamsDefaultsSet(interactive=icm.Interactivity.Both,):
    """ Set Monitor FILE_Params to their defaults."""
####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/icmFuncHead.py"

####+END:

    if icm.Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        if icm.cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=icm.int__gt):
            return(icm.ReturnCode.UsageError)

    icm.b.fp.FileParamWriteToPath(
        parNameFullPath="./icmsIn/control/targetsChunkSize",
        parValue=200
    )
    icm.b.fp.FileParamWriteToPath(
        parNameFullPath="./icmsIn/control/paramWriterBufferSize",
        parValue=500
    )
    icm.b.fp.FileParamWriteToPath(
        parNameFullPath="./icmsIn/control/paramReaderBufferSize",
        parValue=100
    )
    icm.b.fp.FileParamWriteToPath(
        parNameFullPath="./icmsIn/control/exclusionListsControl",
        parValue="fullyIgnore"
    )
    icm.b.fp.FileParamWriteToPath(
        parNameFullPath="./icmsIn/control/execResultsControl",
        parValue="complete"
    )
    icm.b.fp.FileParamWriteToPath(
        parNameFullPath="./icmsIn/control/cmParamsVerificationControl",
        parValue="none"
    )

    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Common-CMND   ::  commonParamsGet    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def commonParamsGet(interactive=icm.Interactivity.Both,):
    """ Lists The ParameterNames that were loaded. """
####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/icmFuncHead.py"

####+END:

    if icm.Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        if icm.cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=icm.int__gt):
            return(icm.ReturnCode.UsageError)

    icm.FILE_paramDictReadDeep(interactive=False, 
                      inPathList=["./icmsIn"])
    return


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Common-CMND   ::  usageParams    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def usageParams(interactive=icm.Interactivity.Both,):
    """ Lists The ParameterNames that were loaded. """
####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/icmFuncHead.py"

####+END:

    if icm.Interactivity().interactiveInvokation(interactive):
        icmRunArgs = G.icmRunArgsGet()
        if icm.cmndArgsLengthValidate(cmndArgs=icmRunArgs.cmndArgs, expected=0, comparison=icm.int__gt):
            return(icm.ReturnCode.UsageError)

    inPrep_usageParams(interactive=True,
                       cmndName="usageParams",
    ) 
    
    return


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *ICM Specific Interactively Invokable Functions (ICM-CMND)*
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-CMND      ::  inPrep_usageParams    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=False, fnExit=False)
def inPrep_usageParams(interactive, cmndName):
    """ Get relevant input parameters
    """
####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/icmFuncHead.py"

####+END:

    G.usageParams.enforceScope=None

            
    return



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-CMND      ::  enetLibsUpdate    [[elisp:(org-cycle)][| ]]
"""
@io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def enetLibsUpdate(
        interactive=False,
        targetFqdn=None,     # Optional
        accessMethod=None,   # Optional
        userName=None,       # Optional
        password=None,       # Optional
):
    """ Given An ToIcmTag, dateVer in TICMO
    """
    try: icm.callableEntryEnhancer(type='cmnd')
    except StopIteration:  return

    cmndThis = icm.FUNC_currentGet().__name__

    if interactive == True:
        G = cs.globalContext.get()
        icmRunArgs = G.icmRunArgsGet()

        if not len(icmRunArgs.cmndArgs) == 0:
            try:  b_io.eh.runTime(format(cmndThis + 'Bad Number Of cmndArgs'))
            except RuntimeError:  return


    targetsAccessList=toIcm.targetsAccessListGet(interactive=interactive,
                                                 targetFqdn=targetFqdn,
                                                 accessMethod=accessMethod,
                                                 userName=userName,
                                                 password=password)

    targetParamsList = toIcm.targetParamsListGet(interactive=interactive)

    @io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def targetsListProc(pathTargetsList):
        """Process List of Ephemera and Persistent Targets"""
        @io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
        def targetProc(thisPathTarget):
            """Process One Target"""
            @io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)            
            def paramsListProc(paramsList):
                """Process List of Parameters"""
                @io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)            
                def paramProc(thisParam):
                    """At this point, we have the target and the parameter, ready for processing.
                    - From thisParam's fileParams, get the agent and parName, 
                    - Then remoteExec the agent on target and get the results.
                    - Record the obtained results with local invokation of the agent.
                    """
                    
                    b_io.tm.here('targetPath=' + thisPathTarget)  # Target Access Information
                    b_io.tm.here(format('ticmoBase=' + thisTicmoBase))  # TICMO Base

                    paramBase = thisParam.base()
                    b_io.tm.here('paramBase=' + paramBase)

                    agent = b.fp.FileParamValueReadFrom(parRoot=paramBase, parName='agent')
                    if not agent: return(io.eh.problem_unassignedError())
                        
                    parName = b.fp.FileParamValueReadFrom(parRoot=paramBase, parName='parName')
                    if not parName: return(io.eh.problem_unassignedError())

                    commandLine=format(agent + ' -p mode=agent -i ' + parName)
                    b_io.tm.here('RemoteExec: ' + commandLine)                    
                                                
                    resultLines = linuxTarget.runCommand(connection, commandLine)

                    pipeableResultLines = ""
                    for thisResultLine in resultLines:
                        pipeableResultLines =  pipeableResultLines + thisResultLine + '\n'
                    
                    b_io.tm.here('ResultLines: ' + str(resultLines)) 

                    # We can now dateVer and empnaPkg write the resultLines for parName in TICMO
                    #fileParWriteBase = os.path.join(thisTicmoBase, empnaPkg, dateVer)

                    # updated =  icm.b.fp.FileParamWriteTo(parRoot=fileParWriteBase,
                    #                               parName=parName,
                    #                               parValue=resultLines[0])

                    #
                    # We ask the agent to capture the resultLines in ticmo
                    #
                    commandLine=format(agent  + ' ' + '-n showRun -p mode=capture -p ticmoBase=' +  ' -i ' + parName)
                    commandArgs=shlex.split(commandLine)

                    b_io.tm.here('SubProc: ' + commandLine)                                        
                    p = subprocess.Popen(commandArgs,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)

                    out, err = p.communicate(input=format(pipeableResultLines.encode()))

                    if out: icm.ANN_note("Stdout: " +  out)
                    if err: icm.ANN_note("Stderr: " +  err)

                    return
                                    
                for thisParam in paramsList:
                    paramProc(thisParam)
                return    

            linuxTarget = toIcm.TARGET_Proxy_Linux(basePath=thisPathTarget)

            accessParams = linuxTarget.accessParamsGet()
            targetId = accessParams.targetFqdnValue

            thisTicmoBase = toIcm.targetBaseGet(targetId=targetId)

            connection = linuxTarget.connect()

            paramsListProc(targetParamsList)
            
            return            

        for thisPathTarget in pathTargetsList:
            targetProc(thisPathTarget)

        return

    targetsListProc(targetsAccessList)

    #empna.dateVerRecordForNext(dateVer=dateVer)

    return

####+BEGIN: b:py3:cs:cmnd/classHead :modPrefix "new" :cmndName "linuxUsageKpisRetrieve" :comment "" :parsMand "" :parsOpt "targetFqdn accessMethod userName password" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<linuxUsageKpisRetrieve>>  =verify= parsOpt=targetFqdn accessMethod userName password ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class linuxUsageKpisRetrieve(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'targetFqdn', 'accessMethod', 'userName', 'password', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             targetFqdn: typing.Optional[str]=None,  # Cs Optional Param
             accessMethod: typing.Optional[str]=None,  # Cs Optional Param
             userName: typing.Optional[str]=None,  # Cs Optional Param
             password: typing.Optional[str]=None,  # Cs Optional Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'targetFqdn': targetFqdn, 'accessMethod': accessMethod, 'userName': userName, 'password': password, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        targetFqdn = csParam.mappedValue('targetFqdn', targetFqdn)
        accessMethod = csParam.mappedValue('accessMethod', accessMethod)
        userName = csParam.mappedValue('userName', userName)
        password = csParam.mappedValue('password', password)
####+END:

        targetsAccessList=toIcm.targetsAccessListGet(interactive=interactive,
                                                     targetFqdn=targetFqdn,
                                                     accessMethod=accessMethod,
                                                     userName=userName,
                                                     password=password)

        targetParamsList = toIcm.targetParamsListGet(interactive=interactive)

        @io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
        def targetsListProc(pathTargetsList):
            """Process List of Ephemera and Persistent Targets"""
            @io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
            def targetProc(thisPathTarget):
                """Process One Target"""
                @io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)            
                def paramsListProc(paramsList):
                    """Process List of Parameters"""
                    @io.track.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)            
                    def paramProc(thisParam):
                        """At this point, we have the target and the parameter, ready for processing.
                        - From thisParam's fileParams, get the agent and parName, 
                        - Then remoteExec the agent on target and get the results.
                        - Record the obtained results with local invokation of the agent.
                        """

                        b_io.tm.here('targetPath=' + thisPathTarget)  # Target Access Information
                        b_io.tm.here(format('ticmoBase=' + thisTicmoBase))  # TICMO Base

                        paramBase = thisParam.base()
                        b_io.tm.here('paramBase=' + paramBase)

                        agent = b.fp.FileParamValueReadFrom(parRoot=paramBase, parName='agent')
                        if not agent: return(io.eh.problem_unassignedError())

                        parName = b.fp.FileParamValueReadFrom(parRoot=paramBase, parName='parName')
                        if not parName: return(io.eh.problem_unassignedError())

                        commandLine=format(agent + ' -p mode=agent -i ' + parName)
                        b_io.tm.here('RemoteExec: ' + commandLine)                    

                        resultLines = linuxTarget.runCommand(connection, commandLine)

                        pipeableResultLines = ""
                        for thisResultLine in resultLines:
                            pipeableResultLines =  pipeableResultLines + thisResultLine + '\n'

                        b_io.tm.here('ResultLines: ' + str(resultLines)) 

                        # We can now dateVer and empnaPkg write the resultLines for parName in TICMO
                        #fileParWriteBase = os.path.join(thisTicmoBase, empnaPkg, dateVer)

                        # updated =  icm.b.fp.FileParamWriteTo(parRoot=fileParWriteBase,
                        #                               parName=parName,
                        #                               parValue=resultLines[0])

                        #
                        # We ask the agent to capture the resultLines in ticmo
                        #
                        commandLine=format(agent  + ' ' + '-n showRun -p mode=capture -p ticmoBase=' +  ' -i ' + parName)
                        commandArgs=shlex.split(commandLine)

                        b_io.tm.here('SubProc: ' + commandLine)                                        
                        p = subprocess.Popen(commandArgs,
                                             stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)

                        out, err = p.communicate(input=format(pipeableResultLines.encode()))

                        if out: icm.ANN_note("Stdout: " +  out)
                        if err: icm.ANN_note("Stderr: " +  err)

                        return

                    for thisParam in paramsList:
                        paramProc(thisParam)
                    return    

                linuxTarget = toIcm.TARGET_Proxy_Linux(basePath=thisPathTarget)

                accessParams = linuxTarget.accessParamsGet()
                targetId = accessParams.targetFqdnValue

                thisTicmoBase = toIcm.targetBaseGet(targetId=targetId)

                connection = linuxTarget.connect()

                paramsListProc(targetParamsList)

                return            

            for thisPathTarget in pathTargetsList:
                targetProc(thisPathTarget)

            return

        targetsListProc(targetsAccessList)

        #empna.dateVerRecordForNext(dateVer=dateVer)

        return


####+BEGIN: bx:cs:python:section :title "Common/Generic Facilities -- Library Candidates"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common/Generic Facilities -- Library Candidates*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

    
####+BEGIN: bx:cs:python:section :title "= =Framework::=   G_main -- Instead Of ICM Dispatcher ="
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *= =Framework::=   G_main -- Instead Of ICM Dispatcher =*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:cs:python:func :funcName "G_main" :funcType "FrameWrk" :retType "Void" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-FrameWrk [[elisp:(outline-show-subtree+toggle)][||]] /G_main/ retType=Void argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def G_main():
####+END:
    """ 
** Replaces ICM dispatcher for other command line args parsings.
"""
    pass

####+BEGIN: bx:cs:python:icmItem :itemType "Configuration" :itemTitle "= =Framework::= g_ Settings -- ICMs Imports ="
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Configuration [[elisp:(outline-show-subtree+toggle)][||]] = =Framework::= g_ Settings -- ICMs Imports =  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

g_examples = examples  # or None 
g_mainEntry = None  # or G_main

####+BEGIN: bx:dblock:global:file-insert :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/icm2.G_main.py"

####+END:

####+BEGIN: bx:cs:python:section :title "Unused Facilities -- Temporary Junk Yard"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Unused Facilities -- Temporary Junk Yard*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:
"""
*       /Empty/  [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :title " ~End Of Editable Text~ "
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _ ~End Of Editable Text~ _: |]]    [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"

####+END:
