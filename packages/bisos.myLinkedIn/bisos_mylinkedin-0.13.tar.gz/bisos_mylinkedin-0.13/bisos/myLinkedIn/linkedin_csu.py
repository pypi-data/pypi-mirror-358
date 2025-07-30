# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Unit= as equivalent of facter in py and remotely with rpyc.
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
** This File: /bisos/git/bxRepos/bisos-pip/myLinkedIn/py3/bisos/myLinkedIn/linkedin_csu.py
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/myLinkedIn/py3/bisos/myLinkedIn/linkedin_csu.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['linkedin_csu'], }
csInfo['version'] = '202505100819'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'linkedin_csu-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/COMEEGA/_nodeBase_/fullUsagePanel-en.org][BISOS COMEEGA Panel]]
This a =Cs-Unit= for running the equivalent of facter in py and remotely with rpyc.
With BISOS, it is used in CMDB remotely.

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

####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= "  :title "*Py Library IMPORTS*" :comment "-- Framework and External Packages Imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- Framework and External Packages Imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

# import os
import collections
# import pathlib
# import invoke

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

# from bisos.facter import facter
# from bisos.banna import bannaPortNu

import pathlib
import re

# from telemetry import Telemetry

from bisos.myLinkedIn import linkedinUtils
from bisos.myLinkedIn import connections
from bisos.myLinkedIn import invitations
from bisos.myLinkedIn import messages

from bisos.myLinkedIn import messagesMaildir

import logging
logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)



####+BEGIN: b:py3:cs:orgItem/basic :type "=Executes=  "  :title "CSU-Lib Executions" :comment "-- cs.invOutcomeReportControl"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =Executes=   [[elisp:(outline-show-subtree+toggle)][||]] CSU-Lib Executions -- cs.invOutcomeReportControl  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

cs.invOutcomeReportControl(cmnd=True, ro=True)

####+BEGIN: b:py3:cs:orgItem/section :title "Common Parameters Specification" :comment "based on cs.param.CmndParamDict -- As expected from CSU-s"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification* based on cs.param.CmndParamDict -- As expected from CSU-s  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "commonParamsSpecify" :comment "~CSU Specification~" :funcType "ParSpc" :deco ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-ParSpc [[elisp:(outline-show-subtree+toggle)][||]] /commonParamsSpecify/  ~CSU Specification~  [[elisp:(org-cycle)][| ]]
#+end_org """
def commonParamsSpecify(
####+END:
        csParams: cs.param.CmndParamDict,
) -> None:
    csParams.parDictAdd(
        parName='myLinkedInBase',
        parDescription="Path to the directory where myLinkedIn files and directories are stored or will be written.",
        parDataType=None,
        parDefault="~/bpos/usageEnvs/selected/myLinkedIn/selected",
        parChoices=[],
        argparseShortOpt=None,
        argparseLongOpt='--myLinkedInBase',
    )
    csParams.parDictAdd(
        parName='dataExportDir',
        parDescription="Path to the directory where Basic_LinkedInDataExport.zip is unzipped in.",
        parDataType=None,
        parDefault="~/bpos/usageEnvs/selected/myLinkedIn/selected/LinkedInDataExport",
        parChoices=[],
        argparseShortOpt=None,
        argparseLongOpt='--dataExportDir',
    )
    csParams.parDictAdd(
        parName='vcardsDir',
        parDescription="Path to the directory where .vcf files are stored or will be written.",
        parDataType=None,
        parDefault="~/bpos/usageEnvs/selected/myLinkedIn/selected/VCards",
        parChoices=[],
        argparseShortOpt=None,
        argparseLongOpt='--vcardsDir',
    )
    csParams.parDictAdd(
        parName='maildir',
        parDescription="Path to the directory where maildir files are stored or will be written.",
        parDataType=None,
        parDefault="~/bpos/usageEnvs/selected/myLinkedIn/selected/maildir",
        parChoices=[],
        argparseShortOpt=None,
        argparseLongOpt='--maildir',
    )
    csParams.parDictAdd(
        parName='extent',
        parDescription="The extent to which a command should invoke others.",
        parDataType=None,
        parDefault="default",
        parChoices=["default", "full", "minimal"],
        argparseShortOpt=None,
        argparseLongOpt='--extent',
    )


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Direct Command Services" :anchor ""  :extraInfo "Examples and CSs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _Direct Command Services_: |]]  Examples and CSs  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples_csu" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples_csu>>  =verify= ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class examples_csu(cs.Cmnd):
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
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Basic example command.
        #+end_org """)

        od = collections.OrderedDict
        cmnd = cs.examples.cmndEnter
        literal = cs.examples.execInsert

        cs.examples.menuChapter('=Direct Interface Commands=')

        # fromFilePars = od([('fromFile', fileName), ('cache', 'True')])

        oneExportZipFile="~/bpos/usageEnvs/selected/myLinkedIn/selected/Basic_LinkedInDataExport.zip"
        oneLinkedInBase="~/bpos/usageEnvs/selected/myLinkedIn/selected"
        oneDataExportDir="~/bpos/usageEnvs/selected/myLinkedIn/selected/LinkedInDataExport"
        oneVCardsDir="~/bpos/usageEnvs/selected/myLinkedIn/selected/VCards"
        oneMaildir="~/bpos/usageEnvs/selected/myLinkedIn/selected/maildir"

        downloadedExportZipFile="~/Downloads/Basic_LinkedInDataExport.zip"
        downloadedLinkedinBase="~/Downloads"

        cs.examples.menuSection('/Show Selected as target of symlink/')
        literal(f"readlink -f {oneVCardsDir}")
        literal(f"ls -l {oneVCardsDir}")
        literal(f"ls -l {oneExportZipFile}")

        cs.examples.menuSection('/fullUpdate:: Using Exported Basic_LinkedInDataExport.zip File (Creates VCards and maildir)/')

        cmnd('fullUpdate',
             args=oneExportZipFile)

        cmnd('fullUpdate',
             pars=od([('myLinkedInBase', downloadedLinkedinBase),]),
             args=downloadedExportZipFile)
        
        cs.examples.menuSection('/exportedPrep:: Prepare the LinkedInDataExport Base -- Unzips arg0 in dataExportDir/')

        cmnd('exportedPrep',
             pars=od([('dataExportDir', oneDataExportDir),]),
             args=oneExportZipFile)

        cs.examples.menuSection('/vcardsGenerate:: -- Generate Initial VCards/')

        cmnd('vcardsGenerate',
             pars=od([('vcardsDir', oneVCardsDir),]),
             args=f"{oneLinkedInBase}/Connections.csv")

        cs.examples.menuSection('/vcardsInvitations:: -- Augment VCards/')

        cmnd('vcardsInvitations',
             pars=od([('vcardsDir', oneVCardsDir),]),
             args=f"{oneLinkedInBase}/Invitations.csv")

        cs.examples.menuSection('/maildirMessage:: vcardsMessages:: -- Create maildir from messages.csv/')

        cmnd('vcardsMessages',
             pars=od([('vcardsDir', oneVCardsDir),]),
             args=f"{oneLinkedInBase}/messages.csv")

        cmnd('maildirMessages',
             pars=od([('maildir', oneMaildir),]),
             args=f"{oneLinkedInBase}/messages.csv")

        return(cmndOutcome)


def extract_date_from_filename(zip_path: pathlib.Path) -> str:
    """Extracts the date portion (MM-DD-YYYY) from a LinkedIn ZIP filename."""
    match = re.search(r'LinkedInDataExport_(\d{2}-\d{2}-\d{4})', zip_path.name)
    if match:
        return match.group(1)
    raise ValueError(f"Date not found in filename: {zip_path.name}")

def refresh_symlink_dir(symlink_path: pathlib.Path, target_dir: pathlib.Path) -> None:
    """
    Replace or create a symbolic link pointing to target_dir.

    Args:
        symlink_path (Path): The path where the symlink will be created.
        target_dir (Path): The directory the symlink should point to.
    """
    symlink_path = symlink_path.expanduser()
    target_dir = target_dir.expanduser().resolve(strict=True)

    if symlink_path.exists() or symlink_path.is_symlink():
        symlink_path.unlink()

    symlink_path.symlink_to(target_dir, target_is_directory=True)
    logger.info(f"Symlink refreshed: {symlink_path} → {target_dir}")

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fullUpdate" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "extent myLinkedInBase" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fullUpdate>>  =verify= parsOpt=extent myLinkedInBase argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class fullUpdate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'extent', 'myLinkedInBase', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             extent: typing.Optional[str]=None,  # Cs Optional Param
             myLinkedInBase: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'extent': extent, 'myLinkedInBase': myLinkedInBase, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        extent = csParam.mappedValue('extent', extent)
        myLinkedInBase = csParam.mappedValue('myLinkedInBase', myLinkedInBase)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        fileToExportedZip = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        path_exportedZip = pathlib.Path(fileToExportedZip).expanduser().resolve(strict=True)

        assert  path_exportedZip.exists(), f"Missing {path_exportedZip}"

        path_myLinkedInBase = pathlib.Path(myLinkedInBase).expanduser().resolve(strict=True)

        g_parDict = cs.globalContext.get().icmParamDictGet().parDictGet()

        # if myLinkedInBase was not specified on the command line
        # and the default does not exist, use the parent of ExportedZip file.
        try:
            g_parDict['myLinkedInBase']
        except  KeyError:
            # An optional param was not specified.
            if not path_myLinkedInBase.exists():
                path_myLinkedInBase = path_exportedZip.parent

        # assert  path_myLinkedInBase.exists(), f"Missing {path_myLinkedInBase}"
        if not path_myLinkedInBase.exists(): return failed(cmndOutcome, f"Missing {path_myLinkedInBase}")

        myLinkedInBase = str(path_myLinkedInBase)

        logger.info(f"cmnd={fullUpdate} -- optPar:: myLinkedInBase={myLinkedInBase}  arg0:: exportedZip={path_exportedZip}")

        if exportedPrep().pyCmnd(
            dataExportDir=f"{myLinkedInBase}/LinkedInDataExport",
            argsList=argsList,
        ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

        if vcardsGenerate().pyCmnd(
            myLinkedInBase=myLinkedInBase,
            vcardsDir=f"{myLinkedInBase}/VCards",
            argsList=[f"{myLinkedInBase}/LinkedInDataExport/Connections.csv"],
        ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

        if vcardsInvitations().pyCmnd(
            myLinkedInBase=myLinkedInBase,
            vcardsDir=f"{myLinkedInBase}/VCards",
            argsList=[f"{myLinkedInBase}/LinkedInDataExport/Invitations.csv"],
        ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

        if extent == "full":
            if vcardsMessages().pyCmnd(
                myLinkedInBase=myLinkedInBase,
                vcardsDir=f"{myLinkedInBase}/VCards",
                argsList=[f"{myLinkedInBase}/LinkedInDataExport/messages.csv"],
            ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

        if maildirMessages().pyCmnd(
            myLinkedInBase=myLinkedInBase,
            maildir=f"{myLinkedInBase}/maildir",
            argsList=[f"{myLinkedInBase}/LinkedInDataExport/messages.csv"],
        ).isProblematic(): return(b_io.eh.badOutcome(cmndOutcome))

        return cmndOutcome.set(opResults=None,)

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="pathToExportedZip",
            argDefault='',
            argChoices=[],
            argDescription="Path to the LinkedIn Basic_LinkedInDataExport_DATE.zip file."
        )

        return cmndArgsSpecDict

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "exportedPrep" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "dataExportDir" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<exportedPrep>>  =verify= parsOpt=dataExportDir argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class exportedPrep(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'dataExportDir', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             dataExportDir: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'dataExportDir': dataExportDir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        dataExportDir = csParam.mappedValue('dataExportDir', dataExportDir)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Unzips arg0 in dataExportDir, if myLinkedInBase does not exist.
        #+end_org """)

        fileToExportedZip = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        path_exportedZip = pathlib.Path(fileToExportedZip).expanduser().resolve()
        if not path_exportedZip.exists(): return failed(cmndOutcome, f"Missing {path_exportedZip}")

        path_dataExportDir = pathlib.Path(dataExportDir).expanduser().resolve()

        logger.info(f"cmnd={exportedPrep} -- optPar:: dataExportDir={path_dataExportDir}  arg0:: exportedZip={path_exportedZip}")

        if path_dataExportDir.is_dir():
            logger.info(f"dataExportDir={path_dataExportDir} exists, creation skipped")
        else:
            linkedinUtils.Common.unzip_file(path_exportedZip, path_dataExportDir)

        return cmndOutcome.set(opResults=f"dataExportDir={path_dataExportDir}",)


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="pathToExportedZip",
            argDefault='',
            argChoices=[],
            argDescription="Path to the LinkedIn Basic_LinkedInDataExport_DATE.zip file."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vcardsGenerate" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "myLinkedInBase vcardsDir" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vcardsGenerate>>  =verify= parsOpt=myLinkedInBase vcardsDir argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vcardsGenerate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'myLinkedInBase', 'vcardsDir', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             myLinkedInBase: typing.Optional[str]=None,  # Cs Optional Param
             vcardsDir: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'myLinkedInBase': myLinkedInBase, 'vcardsDir': vcardsDir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        myLinkedInBase = csParam.mappedValue('myLinkedInBase', myLinkedInBase)
        vcardsDir = csParam.mappedValue('vcardsDir', vcardsDir)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Takes in Connections.csv, creates vcards, returns count
        #+end_org """)


        inFile = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        path_inFile = pathlib.Path(inFile).expanduser().resolve()
        if not path_inFile.exists(): return failed(cmndOutcome, f"Missing {path_inFile}")

        if vcardsDir is not None:
            path_vcardsDir = pathlib.Path(vcardsDir).expanduser().resolve(strict=False)
            path_vcardsDir.mkdir(exist_ok=True)

        logger.info(f"cmnd={vcardsGenerate} -- optPar:: vcardsDir={vcardsDir}  arg0:: Connections.csv={path_inFile}")

        generation = connections.LinkedInConnections(path_inFile)
        generation.load()
        count = generation.create_vcards(path_vcardsDir)

        return cmndOutcome.set(opResults=f"vcardsDir={path_vcardsDir} count={count}",)


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="inFile",
            argDefault='',
            argChoices=[],
            argDescription="Path to the Exported LinkedIn connections file."
        )

        return cmndArgsSpecDict



####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vcardsInvitations" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "myLinkedInBase vcardsDir" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vcardsInvitations>>  =verify= parsOpt=myLinkedInBase vcardsDir argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vcardsInvitations(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'myLinkedInBase', 'vcardsDir', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             myLinkedInBase: typing.Optional[str]=None,  # Cs Optional Param
             vcardsDir: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'myLinkedInBase': myLinkedInBase, 'vcardsDir': vcardsDir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        myLinkedInBase = csParam.mappedValue('myLinkedInBase', myLinkedInBase)
        vcardsDir = csParam.mappedValue('vcardsDir', vcardsDir)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Takes in Invitations.csv, augments vcards, returns count
        #+end_org """)

        inFile = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        path_inFile = pathlib.Path(inFile).expanduser().resolve()
        if not path_inFile.exists(): return failed(cmndOutcome, f"Missing {path_inFile}")

        if vcardsDir is not None:
            path_vcardsDir = pathlib.Path(vcardsDir).expanduser().resolve(strict=True)

        logger.info(f"cmnd={vcardsInvitations} -- optPar:: vcardsDir={vcardsDir}  arg0:: Invitations.csv={path_inFile}")

        augmentation = invitations.LinkedInInvitations(path_inFile)
        augmentation.load()
        count = augmentation.augment_vcards(path_vcardsDir)

        return cmndOutcome.set(opResults=f"vcardsDir={path_vcardsDir} count={count}",)


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="inFile",
            argDefault='',
            argChoices=[],
            argDescription="Path to the Exported LinkedIn invitations file."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "vcardsMessages" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "myLinkedInBase vcardsDir" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<vcardsMessages>>  =verify= parsOpt=myLinkedInBase vcardsDir argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class vcardsMessages(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'myLinkedInBase', 'vcardsDir', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             myLinkedInBase: typing.Optional[str]=None,  # Cs Optional Param
             vcardsDir: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'myLinkedInBase': myLinkedInBase, 'vcardsDir': vcardsDir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        myLinkedInBase = csParam.mappedValue('myLinkedInBase', myLinkedInBase)
        vcardsDir = csParam.mappedValue('vcardsDir', vcardsDir)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Takes in messages.csv, augments vcards, returns count
        #+end_org """)

        inFile = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        path_inFile = pathlib.Path(inFile).expanduser().resolve()
        if not path_inFile.exists(): return failed(cmndOutcome, f"Missing {path_inFile}")

        if vcardsDir is not None:
            path_vcardsDir = pathlib.Path(vcardsDir).expanduser().resolve(strict=True)

        logger.info(f"cmnd={vcardsMessages} -- optPar:: vcardsDir={vcardsDir}  arg0:: Connections.csv={path_inFile}")

        augmentation = messages.LinkedInMessages(path_inFile)
        augmentation.load()
        augmentation.augment_vcards(path_vcardsDir)

        return cmndOutcome.set(opResults=path_vcardsDir,)



####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="inFile",
            argDefault='',
            argChoices=[],
            argDescription="Path to the Exported LinkedIn messages.csv file."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "maildirMessages" :comment "" :extent "verify" :ro "cli" :parsMand "" :parsOpt "myLinkedInBase maildir" :argsMin 1 :argsMax 1 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<maildirMessages>>  =verify= parsOpt=myLinkedInBase maildir argsMin=1 argsMax=1 ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class maildirMessages(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'myLinkedInBase', 'maildir', ]
    cmndArgsLen = {'Min': 1, 'Max': 1,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             myLinkedInBase: typing.Optional[str]=None,  # Cs Optional Param
             maildir: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'myLinkedInBase': myLinkedInBase, 'maildir': maildir, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
        myLinkedInBase = csParam.mappedValue('myLinkedInBase', myLinkedInBase)
        maildir = csParam.mappedValue('maildir', maildir)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Returns runFacterAndGetJsonOutputBytes.
        #+end_org """)


        inFile = self.cmndArgsGet("0", cmndArgsSpecDict, argsList)
        csv_path = pathlib.Path(inFile)
        if not csv_path.exists(): return failed(cmndOutcome, f"Missing {csv_path}")

        assert  csv_path.exists(), f"Missing {csv_path}"

        maildir_path = pathlib.Path(maildir)

        # telemetry = Telemetry("LinkedInMessages822")
        # converter = messages822.LinkedInMessagesToMaildir(csv_path, maildir_path, telemetry)
        converter = messagesMaildir.LinkedInMessagesToMaildir(csv_path, maildir_path)
        converter.run()

        return cmndOutcome.set(opResults=maildir_path,)


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """
***** Cmnd Args Specification
"""
        cmndArgsSpecDict = cs.CmndArgsSpecDict()

        cmndArgsSpecDict.argsDictAdd(
            argPosition="0",
            argName="inFile",
            argDefault='',
            argChoices=[],
            argDescription="Path to the Exported LinkedIn connections file."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
