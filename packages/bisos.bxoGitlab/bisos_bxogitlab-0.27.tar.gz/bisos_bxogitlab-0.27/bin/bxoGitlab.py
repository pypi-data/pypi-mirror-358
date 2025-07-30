#!/bin/env python
# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CmndSvc= for
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-u
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/bxRepos/bisos-pip/bxoGitlab/py3/bin/bxoGitlab.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['bxoGitlab'], }
csInfo['version'] = '202408032024'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'bxoGitlab-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]

#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

import enum
import os

import gitlab


""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~csuList emacs-list Specifications~  [[elisp:(blee:org:code-block/above-run)][ /Eval Below/ ]] [[elisp:(org-cycle)][| ]]
#+BEGIN_SRC emacs-lisp
(setq  b:py:cs:csuList
  (list
   "bisos.b.cs.ro"
   "bisos.csPlayer.bleep"
   "bisos.common.serviceObject"
 ))
#+END_SRC
#+RESULTS:
| bisos.b.cs.ro | bisos.csPlayer.bleep | bisos.common.serviceObject |
#+end_org """

####+BEGIN: b:py3:cs:framework/csuListProc :pyImports t :csuImports t :csuParams t
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =Process CSU List= with /3/ in csuList pyImports=t csuImports=t csuParams=t
#+end_org """

from bisos.b.cs import ro
from bisos.csPlayer import bleep
from bisos.common import serviceObject


csuList = [ 'bisos.b.cs.ro', 'bisos.csPlayer.bleep', 'bisos.common.serviceObject', ]

g_importedCmndsModules = cs.csuList_importedModules(csuList)

def g_extraParams():
    csParams = cs.param.CmndParamDict()
    cs.csuList_commonParamsSpecify(csuList, csParams)
    cs.argsparseBasedOnCsParams(csParams)

####+END:

####+BEGIN: b:py3:cs:main/exposedSymbols :classes ()
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] ~Exposed Symbols List Specification~ with /0/ in Classes List
#+end_org """
####+END:

####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples" :extent "verify" :ro "noCli" :comment "FrameWrk: CS-Main-Examples" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples>>  *FrameWrk: CS-Main-Examples*  =verify= argsMin=0 argsMax=0 ro=noCli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    rtInvConstraints = cs.rtInvoker.RtInvoker.new_noRo() # NO RO From CLI

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:
        """FrameWrk: CS-Main-Examples"""
        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org ***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Conventional top level example.
        #+end_org """)

        od = collections.OrderedDict
        cmnd = cs.examples.cmndEnter
        literal = cs.examples.execInsert

        def cpsInit(): return collections.OrderedDict()
        def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity,
                                 comment='none', icmWrapper=None, icmName=None) # verbosity: 'little' 'basic' 'none'
        def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)


        cs.examples.myName(cs.G.icmMyName(), cs.G.icmMyFullName())

        cs.examples.commonBrief()

        bleep.examples_csBasic()

        # cs.examples.menuChapter('=Misc=  *Facilities*')

        # cmnd('someCmnd', pars=od([('someParam', 'True'),]), args="""'firstArg' 'SecondArg'""")

        # cs.examples.menuChapter('=ExecLine Example=  *Example Of Echo GPG Install Commands*')

        # literal(f"""echo sudo apt -y install gnupg""")

####+BEGIN: bx:cs:python:cmnd:subSection :title "Imported: bxPlatformBaseDirs"

####+END:

        oneBxoId='prs_bisos'
        oneBxoRoot = bxoRootDir_obtain(bpoId=oneBxoId)
        oneKeyPath = os.path.join(oneBxoRoot, 'credentials/priv/ssh/id_rsa.pub')
        oneKeyTypeName = '_priv-pubkey'
        oneKeyName = oneKeyTypeName
        oneSnapshotOutFile = '/tmp/git-' + oneBxoId + '-iso.tar'

        #serviceObject.examples_bxoSrBaseDir()

        cs.examples.menuChapter('*Gitlab BxE Realization -- Create Account*')

        cmndName = "acctCreate" ; cmndArgs = ""
        cps=cpsInit() ; cps['bpoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "acctVerify" ; cmndArgs = ""
        cps=cpsInit() ; cps['bpoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "acctList" ; cmndArgs = ""
        cps=cpsInit(); menuItem(verbosity='little')

        cmndName = "acctDelete" ; cmndArgs = ""
        cps=cpsInit() ; cps['bpoId'] = oneBxoId
        menuItem(verbosity='little')

        cs.examples.menuChapter('*Gitlab BxE Realization -- Key Upload*')

        cmndName = "pubkeysList" ; cmndArgs = ""
        cps=cpsInit() ; cps['bpoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "pubkeyObtain" ; cmndArgs = ""
        cps=cpsInit() ; cps['bpoId'] = oneBxoId ; cps['keyName'] = oneKeyName
        menuItem(verbosity='little')

        cmndName = "pubkeyUpload" ; cmndArgs = oneKeyPath
        cps=cpsInit() ; cps['bpoId'] = oneBxoId ; cps['keyName'] = oneKeyName
        menuItem(verbosity='little')

        cmndName = "pubkeyDelete" ; cmndArgs = ""
        cps=cpsInit() ; cps['bpoId'] = oneBxoId ; cps['keyName'] = oneKeyName
        menuItem(verbosity='little')

        cs.examples.menuChapter('*Gitlab Repos -- List, Create and Delete Repos*')

        cmndName = "reposList" ; cmndArgs = ""
        cps=cpsInit() ; cps['bpoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "reposCreate" ; cmndArgs = "iso"
        cps=cpsInit() ; cps['bpoId'] = oneBxoId
        menuItem(verbosity='little')

        cmndName = "reposDelete" ; cmndArgs = "iso"
        cps=cpsInit() ; cps['bpoId'] = oneBxoId
        menuItem(verbosity='little')

        cs.examples.menuChapter('*Gitlab BxE Construction -- Take A Snapshot Of Repo*')

        cmndName = "repoSnapshot" ; cmndArgs = "iso"
        cps=cpsInit() ; cps['bpoId'] = oneBxoId ; cps['outFile'] = oneSnapshotOutFile
        menuItem(verbosity='little')
        
        b.ignore(ro.__doc__,  cmndArgsSpecDict)  # We are not using these modules, but they are auto imported.

        return(cmndOutcome)

####+BEGIN: b:py3:cs:func/typing :funcName "commonParamsSpecify" :comment "~CSU Specification~" :funcType "ParSpc" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ParSpc [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/  ~CSU Specification~  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
####+END:
        csParams: cs.param.CmndParamDict,
) -> None:
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
        parName='outFile',
        parDescription="Output File Name",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--outFile',
    )

    csParams.parDictAdd(
        parName='keyName',
        parDescription="Name Of The SSH Key",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        parScope=cs.CmndParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--keyName',
    )

####+BEGIN: bx:icm:py3:section :title "CS-Commands"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CS-Commands*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "someCmnd" :comment "" :extent "verify" :ro "cli" :parsMand "someParam" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<someCmnd>>  =verify= parsMand=someParam argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class someCmnd(cs.Cmnd):
    cmndParamsMandatory = [ 'someParam', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             someParam: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'someParam': someParam, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        someParam = csParam.mappedValue('someParam', someParam)
####+END:
        if self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  A starting point command.
        #+end_org """): return(cmndOutcome)

        runArgs  = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)
        joinedRunArgs = " ".join(runArgs)

        processedParamsAndArgs = f"""params={someParam} args={joinedRunArgs}"""

        if b.subProc.WOpW(invedBy=self, log=1).bash(
                f"""echo Provided Params and Args were: {processedParamsAndArgs} """,
        ).isProblematic():  return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "cmndArgsSpec" :methodType "ArgsSpec" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-ArgsSpec [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(
####+END:
            self,
) -> cs.arg.CmndArgsSpecDict:
        """ #+begin_org
*** [[elisp:(org-cycle)][| *cmndArgsSpec:* |]] Command Argument Specifications
        #+end_org """
        cmndArgsSpecDict = cs.arg.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="listToApply",
            argChoices=[],
            argDescription="List Of Arguments To Be Applied"
        )
        return cmndArgsSpecDict

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "acctCreate" :comment "" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<acctCreate>>  =verify= parsMand=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class acctCreate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        bxoRoot = bxoRootDir_obtain(bpoId=bpoId)

        bxeDescRoot = bxo_bxeDescRootDir_obtain(bxoRoot)

        selectedSiteRoot = usgSitesSelectedDir_obtain(usgAcct=None)
        gitServerInfo = os.path.join(selectedSiteRoot, "gitServerInfo")

        gitServerUrl = b.fp.FileParamValueReadFrom(parRoot=gitServerInfo, parName="gitServerUrl")
        gitServerPrivToken = b.fp.FileParamValueReadFrom(parRoot=gitServerInfo, parName="gitServerPrivToken")

        # gl = gitlab.Gitlab.from_config('bisosAdmin', ['/bxo/usg/bystar/.python-gitlab.cfg'])
        # private token or personal token authentication
        # gl = gitlab.Gitlab('http://192.168.0.56', private_token='qji9-_YqoqzZ4Rymk_qG')

        gl = gitlab.Gitlab(gitServerUrl, private_token=gitServerPrivToken)

        user = getUserForBxo(gl, bpoId)
        if user:
            b_io.ann.write("Acct Already Exists -- user={}".format(user.username))
            return cmndOutcome.set(
                opError=b.OpError.Success,
                opResults=None,
            )

        bxeOid = b.fp.FileParamValueReadFrom(parRoot=bxeDescRoot, parName="bxeOid")
        if not bxeOid:
            b_io.eh.problem_usageError("Missing Path {}".format(bxeDescRoot))
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        # AdminContactEmail = b.fp.FileParamValueReadFrom(bxeDescRoot, parName='AdminContactEmail')
        AdminContactEmail = "git-" + bpoId + "@mohsen.1.banan.byname.net"
        passwd = 'somePassword'
        # acctName = "oid-" + bxeOid
        acctName = bpoId  + "-bxe-" + bxeOid

        user = gl.users.create({
            'username': bpoId,
            'name': acctName,
            'email': AdminContactEmail,
            'password': passwd,
            'skip_confirmation': True
        })

        # BASH equivalent:
        # gitlab user create  --email test2@example.com --username test2 --name "Test User2" --password "secret01" --skip-confirmation true

        print("Activating User")
        user.activate()

        if rtInv.outs:
            #b_io.ann.write("{}".format(bxoRoot))
            print((user.username))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=user.username,
        )

####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  NOTYET AdminContactEmail should be fixed.
***** TODO Passwd should be auto generated -- not something specific as it is never used.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "acctVerify" :comment "" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<acctVerify>>  =verify= parsMand=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class acctVerify(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bpoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=user.username,
        )


####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "acctDelete" :comment "" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<acctDelete>>  =verify= parsMand=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class acctDelete(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bpoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        userName=user.username

        user.delete()

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=user.name,
        )


####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "acctList" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<acctList>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class acctList(cs.Cmnd):
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

        gl = bxoGitlab_connect()

        users = gl.users.list(all=True)

        for eachUser in users:
            print((eachUser.username))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "pubkeysList" :comment "" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<pubkeysList>>  =verify= parsMand=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class pubkeysList(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bpoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        keys = user.keys.list(all=True)

        for eachKey in keys:
            print((eachKey.title))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  List repos for bpoId.
"""



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "pubkeyObtain" :comment "" :parsMand "bpoId keyName" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<pubkeyObtain>>  =verify= parsMand=bpoId keyName ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class pubkeyObtain(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'keyName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             keyName: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'keyName': keyName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        keyName = csParam.mappedValue('keyName', keyName)
####+END:

        gitlab = bxoGitlab_connect()

        key = bxoKeyGet(gitlab, bpoId, keyName)
        if not key:
            return cmndOutcome.set(opError=b.OpError.Success, opResults=None,)

        if rtInv.outs:
            print((key.key))

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=key.key,
        )


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "pubkeyUpload" :comment "" :parsMand "bpoId keyName" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<pubkeyUpload>>  =verify= parsMand=bpoId keyName argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class pubkeyUpload(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'keyName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             keyName: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'keyName': keyName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
        keyName = csParam.mappedValue('keyName', keyName)
####+END:

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        keyPath=cmndArgs[0]

        gitlab = bxoGitlab_connect()

        key = keyUploadForBxo(gitlab, bpoId, keyName, keyPath)
        if not key:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        if rtInv.outs:
            #b_io.ann.write("{}".format(bxoRoot))
            print(key)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=key.title,
        )

####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "pubkeyDelete" :comment "" :parsMand "bpoId keyName" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<pubkeyDelete>>  =verify= parsMand=bpoId keyName ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class pubkeyDelete(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'keyName', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             keyName: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'keyName': keyName, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        bpoId = csParam.mappedValue('bpoId', bpoId)
        keyName = csParam.mappedValue('keyName', keyName)
####+END:

        gitlab = bxoGitlab_connect()

        key = bxoKeyGet(gitlab, bpoId, keyName)
        if not key:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        keyTitle = key.title

        if rtInv.outs:
            #b_io.ann.write("Deleting keyTitle={}".format(keyTitle))
            print(key)

        key.delete()

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=keyTitle,
        )

####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reposList" :comment "" :noMapping "t" :parsMand "bpoId" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reposList>>  =verify= parsMand=bpoId ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reposList(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bpoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        # list all the projects
        projects = gl.projects.list(sudo=bpoId, all=True)
        for project in projects:
            if project.name != "Monitoring":
                print((project.name))
                #print(project.attributes)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  List repos for bpoId.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reposCreate" :comment "" :parsMand "bpoId" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reposCreate>>  =verify= parsMand=bpoId argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reposCreate(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bpoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        # example code fragment:

        # bxeType = b.fp.FileParamValueReadFrom(
        #     parRoot=os.path.abspath(bxeDescRoot),
        #     parName="bxeType"
        # )

        def processEachArg(eachArg,):

            project = getRepoOfBxo(gl, bpoId, eachArg)
            if project:
                b_io.ann.write("Repo Already Exists -- repoName={}".format(project.name))
                return None

            # If you have the administrator status, you can use sudo to act as another user.
            project = gl.projects.create(
                {
                'name': eachArg,
                },
                sudo=bpoId,
            )
            b_io.ann.write("Created Repo -- repoName={}".format(project.name))
            print((project.name))
            return project

        for eachArg in cmndArgs:
            project = processEachArg(eachArg)

        if project:
            return cmndOutcome.set(
                opError=b.OpError.Success,
                opResults=project.name,
            )
        else:
            return cmndOutcome.set(
                opError=icm.OpError.Failure,
                opResults="AlreadyExists",
            )


####+BEGIN: b:py3:cs:method/typing :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(
####+END:
            self,
) -> cs.arg.CmndArgsSpecDict:
        """
***** Cmnd Args Specification  -- Each As Any.
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "reposDelete" :comment "" :parsMand "bpoId" :parsOpt "" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<reposDelete>>  =verify= parsMand=bpoId argsMin=1 argsMax=9999 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class reposDelete(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        bpoId = csParam.mappedValue('bpoId', bpoId)
####+END:

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        gl = bxoGitlab_connect()

        user = getUserForBxo(gl, bpoId)
        if not user:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        # example code fragment:

        # bxeType = b.fp.FileParamValueReadFrom(
        #     parRoot=os.path.abspath(bxeDescRoot),
        #     parName="bxeType"
        # )

        def processEachArg(eachArg,):

            project = getRepoOfBxo(gl, bpoId, eachArg)
            if not project:
                b_io.ann.write("Missing Repo -- repoName={}".format(eachArg))
                return project

            project.delete()

        for eachArg in cmndArgs:
            project = processEachArg(eachArg)

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:method/typing :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(
####+END:
            self,
) -> cs.arg.CmndArgsSpecDict:
        """
***** Cmnd Args Specification  -- Each As Any.
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "repoSnapshot" :comment "" :noMapping "t" :parsMand "bpoId outFile" :parsOpt "" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<repoSnapshot>>  =verify= parsMand=bpoId outFile argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class repoSnapshot(cs.Cmnd):
    cmndParamsMandatory = [ 'bpoId', 'outFile', ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             bpoId: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Mandatory Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'bpoId': bpoId, 'outFile': outFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        repoName = cmndArgs[0]

        gitlab = bxoGitlab_connect()

        thisRepo = getRepoOfBxo(gitlab, bpoId, repoName)
        if not thisRepo:
            return cmndOutcome.set(opError=icm.OpError.Failure, opResults=None,)

        tarFile = thisRepo.snapshot()

        f = open(outFile, "wb+")
        f.write(tarFile)
        f.close()

        return cmndOutcome.set(
            opError=b.OpError.Success,
            opResults=None,
        )

####+BEGIN: b:py3:cs:method/typing :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(
####+END:
            self,
) -> cs.arg.CmndArgsSpecDict:
        """
***** Cmnd Args Specification  -- Each As Any.
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:method/typing :methodName "cmndDocStr" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList ""
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndDocStr/  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndDocStr(
####+END:
            self,
) -> str:
        return """
***** TODO [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Place holder for this commands doc string.
"""

####+BEGIN: bx:cs:python:section :title "Supporting Classes And Functions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Supporting Classes And Functions*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:


####+BEGIN: bx:dblock:python:func :funcName "bxoKeyGet" :funcType "Obtain" :retType "str" :deco "" :argsList "gitlab bpoId keyName"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bxoKeyGet/ retType=str argsList=(gitlab bpoId keyName)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bxoKeyGet(
    gitlab,
    bpoId,
    keyName,
):
####+END:
    """
** Get the specified key for bxo.
"""

    user = getUserForBxo(gitlab, bpoId)
    if not user:
        b_io.eh.problem_usageError("Missing user={} for bpoId={}".format(user, bpoId))
        return None

    key = None
    keys = user.keys.list(all=True)

    for eachKey in keys:
        if eachKey.title == keyName:
            b_io.tm.here("Key Already Exists -- keys={}".format(keys))
            key = eachKey
            break

    if not key:
        b_io.tm.here("No Keys Found -- keyName={} for bpoId={}".format(keyName, bpoId))

    return key


####+BEGIN: bx:dblock:python:func :funcName "keyUploadForBxo" :funcType "Obtain" :retType "str" :deco "" :argsList "gitlab bpoId keyName keyPath"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /keyUploadForBxo/ retType=str argsList=(gitlab bpoId keyName keyPath)  [[elisp:(org-cycle)][| ]]
#+end_org """
def keyUploadForBxo(
    gitlab,
    bpoId,
    keyName,
    keyPath,
):
####+END:
    """
** Upload the specified key for bxo.
"""

    bxoRoot = bxoRootDir_obtain(bpoId=bpoId,)

    user = getUserForBxo(gitlab, bpoId)
    if not user:
        b_io.eh.problem_usageError("Missing user={} for bpoId={}".format(user, bpoId))
        return None

    key = None
    keys = user.keys.list(all=True)

    for eachKey in keys:
        if eachKey.title == keyName:
            b_io.tm.here("Key Already Exists -- keys={}".format(keys))
            key = eachKey
            break

    if not key:
        key = user.keys.create({
            'title': keyName,
            'key': open(keyPath).read()
        })

    return key




####+BEGIN: bx:dblock:python:func :funcName "getRepoOfBxo" :funcType "Obtain" :retType "str" :deco "" :argsList "gitlab bpoId repoName"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /getRepoOfBxo/ retType=str argsList=(gitlab bpoId repoName)  [[elisp:(org-cycle)][| ]]
#+end_org """
def getRepoOfBxo(
    gitlab,
    bpoId,
    repoName,
):
####+END:
    """
** Get the gitlab repo (project) based on specified repoName of bpoId.
"""
    project = None
    projects = gitlab.projects.list(search=repoName, sudo=bpoId, all=True)
    for eachProject in projects:
        if eachProject.name == repoName:
            project = eachProject
            break

    if not project:
        b_io.tm.here("Missing repoName={} for bpoId={}".format(repoName, bpoId))

    return project


####+BEGIN: bx:dblock:python:func :funcName "getUserForBxo" :funcType "Obtain" :retType "str" :deco "" :argsList "gitlab bpoId"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /getUserForBxo/ retType=str argsList=(gitlab bpoId)  [[elisp:(org-cycle)][| ]]
#+end_org """
def getUserForBxo(
    gitlab,
    bpoId,
):
####+END:
    """
** Get the gitlab user associated with the specified bpoId.
"""

    user = None
    users = gitlab.users.list(search=bpoId, all=True)

    for eachUser in users:
        if eachUser.username == bpoId:
            user = eachUser
            break

    if not user:
        b_io.tm.here("Missing user bpoId={}".format(bpoId))

    return user


####+BEGIN: bx:dblock:python:func :funcName "bxoGitlab_connect" :funcType "Obtain" :retType "str" :deco "" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bxoGitlab_connect/ retType=str argsList=nil  [[elisp:(org-cycle)][| ]]
#+end_org """
def bxoGitlab_connect():
####+END:
    """
** Obtain a handle for the gitlab class.
"""

    selectedSiteRoot = usgSitesSelectedDir_obtain(usgAcct=None)
    gitServerInfo = os.path.join(selectedSiteRoot, "gitServerInfo")

    gitServerUrl = b.fp.FileParamValueReadFrom(
        parRoot=gitServerInfo,
        parName="gitServerUrl"
    )
    gitServerPrivToken = b.fp.FileParamValueReadFrom(
        parRoot=gitServerInfo,
        parName="gitServerPrivToken"
    )
    gl = gitlab.Gitlab(gitServerUrl, private_token=gitServerPrivToken)

    return gl


####+BEGIN: bx:dblock:python:section :title "Directory Base Locations"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ############## [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Directory Base Locations*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]]
"""
####+END:

####+BEGIN: bx:dblock:python:subSection :title "Bxo Roots And InfoBases"

####+END:

####+BEGINNOT: bx:dblock:python:enum :enumName "bxo_IdType" :comment ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum           :: /bxo_IdType/  [[elisp:(org-cycle)][| ]]
"""
#@enum.unique
class bxo_IdType(enum.Enum):
####+END:
    foreignBxO = 'foreignBxO'
    nativeBxO = 'nativeBxO'
    bystarId = 'bystarId'


####+BEGIN: bx:dblock:python:func :funcName "bpoIdType_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bpoIdType_obtain/ retType=str argsList=(bpoId)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bpoIdType_obtain(
    bpoId,
):
####+END:
    """
** ea-NUM means old ByStarUid, A pure number means nativeSO. nonNumber means foreignBxO
"""
    # return bxo_IdType.foreignBxO
    return bxo_IdType.nativeBxO


####+BEGIN: bx:dblock:python:func :funcName "bxoRootDir_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "bpoId"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bxoRootDir_obtain/ retType=str argsList=(bpoId)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bxoRootDir_obtain(
    bpoId,
):
####+END:
    """
**
"""
    bxoBaseDir = None
    idType = bpoIdType_obtain(bpoId)

    if idType == bxo_IdType.foreignBxO:
        bxoBaseDir = os.path.join(
            bxPlatformConfig.rootDir_foreignBxo_fpObtain(configBaseDir=None,),
            bpoId,
        )
    elif idType == bxo_IdType.nativeBxO:
        bxoBaseDir = os.path.expanduser("~" +  bpoId)

    elif idType == bxo_IdType.bystarId:
        pass
    else:
        b_io.eh.problem_usageError("")

    return bxoBaseDir


####+BEGIN: bx:dblock:python:subSection :title "Bxo+Sr Roots and InfoBases (Control/Input)"

####+END:


####+BEGIN: bx:dblock:python:func :funcName "bxo_bxeDescRootDir_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "bxoBaseDir"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /bxo_bxeDescRootDir_obtain/ retType=str argsList=(bxoBaseDir)  [[elisp:(org-cycle)][| ]]
#+end_org """
def bxo_bxeDescRootDir_obtain(
    bxoBaseDir,
):
####+END:
    """
**
"""
    return (
        os.path.join(
            bxoBaseDir,
            "rbxe/bxeDesc",
        )
    )


####+BEGIN: bx:dblock:python:func :funcName "usgSitesSelectedDir_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList "usgAcct=None"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-Obtain   [[elisp:(outline-show-subtree+toggle)][||]] /usgSitesSelectedDir_obtain/ retType=str argsList=(usgAcct=None)  [[elisp:(org-cycle)][| ]]
#+end_org """
def usgSitesSelectedDir_obtain(
    usgAcct=None,
):
####+END:
    """
**
"""
    if usgAcct:
        usgAcctBase=os.path.expanduser("~" + usgAcct)
    else:
        usgAcctBase=os.path.expanduser("~")

    usgSitesSelectedDir = os.path.join(
        usgAcctBase,
        "bisos/sites/selected"
    )

    if not os.path.exists(usgSitesSelectedDir):
        usgSitesSelectedDir = "/bisos/var/sites/selected"

    return usgSitesSelectedDir




####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Main" :anchor ""  :extraInfo "Framework Dblock"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Main_: |]]  Framework Dblock  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/main :csInfo "csInfo" :noCmndEntry "examples" :extraParamsHook "g_extraParams" :importedCmndsModules "g_importedCmndsModules"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CsFrmWrk   [[elisp:(outline-show-subtree+toggle)][||]] =g_csMain= (csInfo, _examples_, g_extraParams, g_importedCmndsModules)
#+end_org """

if __name__ == '__main__':
    cs.main.g_csMain(
        csInfo=csInfo,
        noCmndEntry=examples,  # specify a Cmnd name
        extraParamsHook=g_extraParams,
        importedCmndsModules=g_importedCmndsModules,
    )

####+END:

####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
