# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Lib= for creating and managing symetric gpg  encryption/decryption.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, b-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-mu
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
** This File: /bisos/git/auth/bxRepos/bisos-pip/crypt/py3/bisos/crypt/gpgSym.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:python:file/particulars-csInfo :status "inUse"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['gpgSym'], }
csInfo['version'] = '202209261325'
csInfo['status']  = 'inUse'
csInfo['panel'] = 'gpgSym-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: [[file:/bisos/git/auth/bxRepos/blee-binders/bisos-core/PyFwrk/bisos.crypt/_nodeBase_/fullUsagePanel-en.org][PyFwrk bisos.crypt Panel]]
Module description comes here.
** Relevant Panels:
** Status: In use with BISOS
** /[[elisp:(org-cycle)][| Planned Improvements |]]/ :
*** TODO complete fileName in particulars.
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
#+end_org """
####+END:

####+BEGIN: b:python:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:orgItem/basic :type "=PyImports= " :title "*Py Library IMPORTS*" :comment "-- with classification based framework/imports"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  =PyImports=  [[elisp:(outline-show-subtree+toggle)][||]] *Py Library IMPORTS* -- with classification based framework/imports  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
** Imports Based On Classification=cs-lib
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io

####+END:

import sys
import collections
import gnupg


####+BEGIN: b:py3:cs:orgItem/section :title "CSU-Lib Examples" :comment "-- Providing examples_csu"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *CSU-Lib Examples* -- Providing examples_csu  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:func/typing :funcName "examples_csu" :comment "~CSU Specification~" :funcType "eType" :retType "" :deco "default" :argsList ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  F-T-eType  [[elisp:(outline-show-subtree+toggle)][||]] /examples_csu/  ~CSU Specification~ deco=default  [[elisp:(org-cycle)][| ]]
#+end_org """
@cs.track(fnLoc=True, fnEntry=True, fnExit=True)
def examples_csu(
####+END:
        passwd: str,
        sectionTitle: typing.AnyStr = '',
) -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Examples of Cmnds provided by this CSU-Lib
    #+end_org """

    def cpsInit(): return collections.OrderedDict()
    def menuItem(verbosity): cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity=verbosity) # 'little' or 'none'
    def execLineEx(cmndStr): cs.examples.execInsert(execLine=cmndStr)

    if sectionTitle == 'default':
        cs.examples.menuChapter('*Manage Symmetric Gpg -- Encypt and Decrypt*')

    def cmndCommonParsWithArgs(cmndName, cmndArgs=""): # type: ignore
        cps = cpsInit() ; cps['passwd'] = passwd ;
        cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none')

    cs.examples.menuSection('*GPG Symmetric Encryption*')

    clearFile = "/tmp/gpgSymEx1"
    cipherFile = "/tmp/gpgSymEx1.gpg"

    execLineEx(f"""cp /etc/motd {clearFile}""")

    cmndCommonParsWithArgs(cmndName="gpg_symEncrypt", cmndArgs=f"{clearFile}")

    def cmndStdinEncrypt(cmndName): # type: ignore
        icmWrapper = "echo HereComes Some ClearText | "
        cps = cpsInit() ; cps['passwd'] = passwd ; cmndArgs = ""
        #return cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)
        return cs.examples.csCmndLine(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)
    encryptCmndStr = cmndStdinEncrypt("gpg_symEncrypt")
    #print(f"{encryptCmndStr}")


####+BEGIN: bx:cs:python:cmnd:subSection :context "func-1" :title "Decrypt"

####+END:

    cs.examples.menuSection('*GPG Symmetric Decryption*')

    cmndCommonParsWithArgs(cmndName="gpg_symDecrypt", cmndArgs=f"{cipherFile}")

    def cmndStdinDecrypt(cmndName, icmWrapper): # type: ignore
        cps = cpsInit() ; cps['passwd'] = passwd ; cmndArgs = ""
        return cs.examples.cmndInsert(cmndName, cps, cmndArgs, verbosity='none', icmWrapper=icmWrapper)

    cmndStdinDecrypt("gpg_symDecrypt", icmWrapper=f"cat {cipherFile} | ")

    cmndStdinDecrypt("gpg_symDecrypt", icmWrapper=f"{encryptCmndStr} | ")



####+BEGIN: b:py3:class/decl :className "GpgSym" :superClass "object" :comment "" :classType "basic"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Cls-basic  [[elisp:(outline-show-subtree+toggle)][||]] /GpgSym/  superClass=object  [[elisp:(org-cycle)][| ]]
#+end_org """
class GpgSym(object):
####+END:
    """ #+begin_org
** This is really a namespace not a class. All methods are static.
    #+end_org """

####+BEGIN: b:py3:cs:method/typing :methodName "__init__" :deco "default"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /__init__/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def __init__(
####+END:
            self,
            alg=""
    ):
        self.alg = alg  # Unused, placeholder

####+BEGIN: b:py3:cs:method/typing :methodName "encryptBytes" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /encryptBytes/ deco=staticmethod  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def encryptBytes(
####+END:
            clearText: str,
            symKey: str,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]] Returns gpgOutcome. Usage: cipheredText = gpgOutcome.data
        #+end_org """

        gpg = gnupg.GPG()

        #
        # This is the interface to python-gnupg-0.5.4 package
        # Which is very different from gnupg package.
        # Make sure that you are using pip install python-gnupg
        #
        gpgOutcome = gpg.encrypt(
            clearText,
            recipients=None,
            symmetric='AES256',
            passphrase=symKey,
            #armor=False,
        )
        #cipheredText = gpgOutcome.data
        return gpgOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "decryptBytes" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /decryptBytes/ deco=staticmethod  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def decryptBytes(
####+END:
            cipherText: str,
            symKey: str,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]] Returns gpgOutcome. Usage: clearText = gpgOutcome.data
        #+end_org """

        gpg = gnupg.GPG()

        gpgOutcome = gpg.decrypt(
            cipherText,
            passphrase=symKey,
            #armor=False,
        )
        #clearText = gpgOutcome.data
        return gpgOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "encryptFile" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /encryptFile/ deco=staticmethod  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def encryptFile(
####+END:
            clearFilePath: str,
            symKey: str,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]] Returns gpgOutcome. Usage: cipheredText = gpgOutcome.data
        #+end_org """

        gpg = gnupg.GPG()

        with open(clearFilePath, "rb") as fileObj:
            gpgOutcome = gpg.encrypt_file(
                fileObj,
                recipients=None,
                symmetric='AES256',
                passphrase=symKey,
                #armor=False,
                output=f"{clearFilePath}.gpg"
            )
            b_io.tm.here(f"""Processed File={clearFilePath}""")

            return gpgOutcome

####+BEGIN: b:py3:cs:method/typing :methodName "decryptFile" :deco "staticmethod"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-     [[elisp:(outline-show-subtree+toggle)][||]] /decryptFile/ deco=staticmethod  deco=staticmethod  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @staticmethod
    def decryptFile(
####+END:
            cipherFilePath: str,
            symKey: str,
    ):
        """ #+begin_org
*** [[elisp:(org-cycle)][| *MethodDesc:* | ]] Returns gpgOutcome. Usage: clearText = gpgOutcome.data
        #+end_org """

        gpg = gnupg.GPG()

        with open(cipherFilePath, "rb") as fileObj:
            gpgOutcome = gpg.decrypt_file(
                fileObj,
                passphrase=symKey,
                #armor=False,
            )
        # NOTYET, write the clean text
        return gpgOutcome

    
####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "CmndSvcs" :anchor ""  :extraInfo "Command Services Section"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*     [[elisp:(outline-show-subtree+toggle)][| _CmndSvcs_: |]]  Command Services Section  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: bx:cs:py3:section :title "Primary Command Services"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Primary Command Services*  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpgSymEncryptDecyptExample" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpgSymEncryptDecyptExample>> ro=cli   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpgSymEncryptDecyptExample(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
    ) -> b.op.Outcome:

####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        gpg = gnupg.GPG()
        data = 'the quick brown fow jumps over the laxy dog.'
        passphrase='12345'
        crypt = gpg.encrypt(
            data,
            recipients=None,
            symmetric='AES256',
            passphrase=passphrase,
            armor=False,
        )
        print(crypt.data)

        clear = gpg.decrypt(
            crypt.data,
            passphrase=passphrase,
        )

        print(clear)

        return cmndOutcome


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_symEncrypt" :comment "stdin as clearText" :parsMand "passwd" :parsOpt "outFile" :argsMin 0 :argsMax 9999 :pyInv "clearText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_symEncrypt>>  *stdin as clearText* parsMand=passwd parsOpt=outFile argsMax=9999 ro=cli pyInv=clearText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_symEncrypt(cs.Cmnd):
    cmndParamsMandatory = [ 'passwd', ]
    cmndParamsOptional = [ 'outFile', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             clearText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as clearText"""
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        gpg = gnupg.GPG()

        cmndArgs = self.cmndArgsGet("0&9999", self.cmndArgsSpec(), argsList)

        filesProcessed = False
        for each in typing.cast(list, cmndArgs):
            filesProcessed = True
            with open(each, "rb") as fileObj:
                gpgStatus = gpg.encrypt_file(
                    fileObj,
                    recipients=None,
                    symmetric='AES256',
                    passphrase=passwd,
                    #armor=False,
                    output=f"{each}.gpg"
                )
                b_io.tm.here(f"""Processed File={each}""")

        if not clearText:
            clearText = b_io.stdin.read()

        if not clearText and not filesProcessed:
            b_io.eh.problem_usageError(f"noFiles and no clearText")
            return cmndOutcome

        if clearText:
            gpgStatus = gpg.encrypt(
                clearText,
                recipients=None,
                symmetric='AES256',
                passphrase=passwd,
                #armor=False,
            )

            cipheredText = gpgStatus.data

            b_io.tm.here(f"""clearText={clearText}""")
            b_io.tm.here(f"""cipheredText={cipheredText}""")

            sys.stdout.buffer.write(cipheredText)  # print does not work.

        return cmndOutcome

####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
        )

        return cmndArgsSpecDict


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "gpg_symDecrypt" :extent "verify" :comment "stdin as cipherText" :parsMand "passwd" :parsOpt "outFile" :argsMin 0 :argsMax 9999 :pyInv "cipherText"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<gpg_symDecrypt>>  *stdin as cipherText*  =verify= parsMand=passwd parsOpt=outFile argsMax=9999 ro=cli pyInv=cipherText   [[elisp:(org-cycle)][| ]]
#+end_org """
class gpg_symDecrypt(cs.Cmnd):
    cmndParamsMandatory = [ 'passwd', ]
    cmndParamsOptional = [ 'outFile', ]
    cmndArgsLen = {'Min': 0, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             passwd: typing.Optional[str]=None,  # Cs Mandatory Param
             outFile: typing.Optional[str]=None,  # Cs Optional Param
             argsList: typing.Optional[list[str]]=None,  # CsArgs
             cipherText: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:
        """stdin as cipherText"""
        callParamsDict = {'passwd': passwd, 'outFile': outFile, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        cmndArgsSpecDict = self.cmndArgsSpec()
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]
        #+end_org """)

        gpg = gnupg.GPG()

        cmndArgs = self.cmndArgsGet("0&9999", cmndArgsSpecDict, argsList)

        filesProcessed = False
        for each in typing.cast(list, cmndArgs):
            filesProcessed = True
            with open(each, "rb") as fileObj:
                gpgStatus = gpg.decrypt_file(
                    fileObj,
                    passphrase=passwd,
                    #armor=False,
                )


        if not cipherText:
            cipherText = b_io.stdin.read()

        if not cipherText and not filesProcessed:
            b_io.eh.problem_usageError(f"noFiles and no cipheredText")
            return cmndOutcome

        if cipherText:
            gpgStatus = gpg.decrypt(
                cipherText,
                passphrase=passwd,
                #armor=False,
            )

            clearText = gpgStatus.data

            b_io.tm.here(f"""clearText={clearText}""")
            b_io.tm.here(f"""cipheredText={cipherText}""")

            sys.stdout.buffer.write(clearText)  # print does not work.

        return cmndOutcome


####+BEGIN: b:py3:cs:method/args :methodName "cmndArgsSpec" :methodType "anyOrNone" :retType "bool" :deco "default" :argsList "self"
    """ #+begin_org
**  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_ [[elisp:(outline-show-branches+toggle)][|=]] [[elisp:(bx:orgm:indirectBufOther)][|>]] *[[elisp:(blee:ppmm:org-mode-toggle)][|N]]*  Mtd-T-anyOrNone [[elisp:(outline-show-subtree+toggle)][||]] /cmndArgsSpec/ deco=default  deco=default  [[elisp:(org-cycle)][| ]]
    #+end_org """
    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmndArgsSpec(self, ):
####+END:
        """  #+begin_org
** [[elisp:(org-cycle)][| *cmndArgsSpec:* | ]]
        #+end_org """
        cmndArgsSpecDict = cs.CmndArgsSpecDict()
        cmndArgsSpecDict.argsDictAdd(
            argPosition="0&9999",
            argName="cmndArgs",
            argChoices=[],
            argDescription="List Of CmndArgs To Be Processed. Each As Any."
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
