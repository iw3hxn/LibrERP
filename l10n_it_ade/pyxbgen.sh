#! /bin/bash
# -*- coding: utf-8 -*-
#
# pyxbgen
# Agenzia delle Entrate pyxb generator
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2017-2019 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
#
THIS=$(basename "$0")
TDIR=$(readlink -f $(dirname $0))
PYTHONPATH=$(echo -e "import sys\nprint str(sys.path).replace(' ','').replace('\"','').replace(\"'\",\"\").replace(',',':')[1:-1]"|python)
for d in $TDIR $TDIR/.. ${PYTHONPATH//:/ } /etc; do
  if [ -e $d/z0librc ]; then
    . $d/z0librc
    Z0LIBDIR=$d
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  elif [ -d $d/z0lib ]; then
    . $d/z0lib/z0librc
    Z0LIBDIR=$d/z0lib
    Z0LIBDIR=$(readlink -e $Z0LIBDIR)
    break
  fi
done
if [ -z "$Z0LIBDIR" ]; then
  echo "Library file z0librc not found!"
  exit 2
fi

__version__=0.1.5.9

gen_init() {
    local mdl="${1//,/ }"
    local i=./__init__.py
    if [ $opt_dry_run -eq 0 ]; then
      echo "# flake8: noqa">$i
      echo "# -*- coding: utf-8 -*-" >>$i
      echo "# Copyright 2017-2019 - SHS-AV s.r.l. <http://wiki.zeroincombenze.org/it/Odoo>">>$i
      echo "# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).">>$i
      echo "#">>$i
      echo "# Generated $(date '+%a %Y-%m-%d %H:%M:%S') by pyxbgen.sh $__version__">>$i
      echo "# by Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>">>$i
      echo "#">>$i
      for m in $mdl; do
        if [ "$opt_mod" == "." ]; then
          echo "from . import $m">>$i
        else
          echo "import odoo.addons.${opt_mod}.bindings.$m">>$i
        fi
      done
    fi
}

create_hook() {
    local fn=$1
    if [ $opt_dry_run -eq 0 ]; then
      echo "# flake8: noqa">$fn
      echo "# -*- coding: utf-8 -*-">>$fn
      echo "# Copyright 2017-2019 - SHS-AV s.r.l. <http://wiki.zeroincombenze.org/it/Odoo>">>$fn
      echo "# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).">>$fn
      echo "#">>$fn
      echo "import pyxb">>$fn
      stmt="if"
      for v in 1.2.4 1.2.5 1.2.6; do
        echo "$stmt pyxb.__version__ == '$v':">>$fn
        if [ "$opt_mod" == "." ]; then
          echo "    from ${fn:0: -3}__${v//./_} import *">>$fn
        else
          echo "    from odoo.addons.${opt_mod}.${fn:0: -3}__${v//./_} import *">>$fn
        fi
        stmt="elif"
      done
      echo "else:">>$fn
      echo "    raise pyxb.PyXBVersionError('1.2.4 to 1.2.6')">>$fn
      # echo "">>$fn
    fi
}

excl="DatiFatturaMessaggi,Fattura_VFSM10.xsd,FatturaPA_versione_1.1,FatturaPA_versione_1.2,MessaggiTypes"


OPTOPTS=(h        b          K        k        l        I         M        m       n           o        p          q            u       V           v           x)
OPTDEST=(opt_help opt_branch opt_cont opt_keep opt_list opt_ginit opt_mult opt_mod opt_dry_run opt_odoo opt_nopep8 opt_verbose  opt_uri opt_version opt_verbose opt_exclude)
OPTACTI=(1        "="        1        1        "1>"     "=>"      1        "="     1           "=>"     1          0            "1>"    "*"         1           "=>")
OPTDEFL=(1        ""         0        0        0        ""        0        "."     0           ""       0          -1            0       ""         -1          "$excl")
OPTMETA=("help"   "vers"     ""       ""       ""       "files"   ""       "name"  ""          "path"   ""         "silent"     ""      "version"   "verbose"   "file")
OPTHELP=("this help"\
 "odoo branch for topep8; may be 6.1 7.0 8.0 9.0 10.0 11.0 or 12.0"\
 "keep binding directory, if found"\
 "keep temporary files"\
 "list xml schemas and module names"\
 "generate __init__.py with modules list"\
 "multi version (append pyxb version to file names)"\
 "copy file to module path (i.e. ~/10.0/l10n-italy/l10n_it_ade/"\
 "odoo module name (def='.')"\
 "do nothing (dry-run)"\
 "do not apply pep8"\
 "silent mode"\
 "execute uri Agenzia delle Entrate"\
 "show version"\
 "verbose mode"\
 "commma separated module exclusion list; i.e. fornituraIvp,FatturaPA,DatiFattura,DatiFatturaMessaggi")
OPTARGS=()

DISTO=$(xuname "-d")
if [ "$DISTO" == "CentOS" ]; then
  parseoptargs "$@"
else
  echo "Warning! This tool run just under CentOS, version 6 o 7"
  opt_version=0
  opt_help=1
fi
if [ "$opt_version" ]; then
  echo "$__version__"
  exit 0
fi
if [ $opt_help -gt 0 ]; then
  print_help "Agenzia delle Entrate pyxb generator\nPer generare file .py usare switch -u"\
  "(C) 2017-2019 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi
XSD_FILES=("fornituraIvp_2017_v1.xsd" "FatturaPA_versione_1.2.xsd" "FatturaPA_versione_1.1.xsd" "DatiFatturav2.1.xsd" "DatiFatturaMessaggiv2.0.xsd" "MessaggiTypes_v1.1.xsd" "Fattura_VFPR12.xsd" "Fattura_VFSM10.xsd")
MOD_NAMES=("vat_settlement_v_1_0"     "fatturapa_v_1_2"            "fatturapa_v_1_1"            "dati_fattura_v_2_1"  "messaggi_fattura_v_2_0"      "MessaggiTypes_v_1_1"    "fatturapa_v_1_2"    "fatturapa_v_1_0")
bin_path=${PATH//:/ }
PYXBGEN_BIN=
for x in $TDIR $TDIR/.. $bin_path; do
  if [ -e $x/pyxbgen ]; then
    PYXBGEN_BIN=$x/pyxbgen
    break
  fi
done
[ -z "PYXBGEN_BIN" ] && echo "File pyxbgen not found!"
PYXBGEN_PY=
for x in $TDIR $TDIR/.. $bin_path; do
  if [ -e $x/pyxbgen.py ]; then
    PYXBGEN_PY=$x/pyxbgen.py
    break
  fi
done
[ -z "PYXBGEN_PY" ] && echo "File pyxbgen.py not found!"
TOPEP8=$(which topep8 2>/dev/null)
if [ -z "$TOPEP8" ]; then
  TOPEP8=$(which autopep8 2>/dev/null)
  [ -n "$TOPEP8" ] && TOPEP8="$TOPEP8 -eL"
else
  TOPEP8="$TOPEP8 -eL"
  [ -n "$opt_branch" ] && TOPEP8="$TOPEP8 -b$opt_branch"
fi
if [ -z "$TOPEP8" -a $opt_nopep8 -eq 0 ]; then
  echo "topep8/autopep8 not found!"
  echo "Operations will be executed with switch -p"
fi
if [ -n "$opt_ginit" ]; then
  echo "$0 -I $opt_ginit"
  gen_init "$opt_ginit"
  exit 0
fi
pyxbgen_ver=$($PYXBGEN_BIN --version|grep -Eo "[0-9.]+")
pyxb_ver=$(pip show pyxb 2>/dev/null|grep "^Version"|grep -Eo "[0-9.]+")
if [ "$pyxbgen_ver" != "$pyxb_ver" ]; then
  echo "Version mismatch"
  echo "pyxb version is $pyxb_ver  "
  echo "$PYXBGEN_PY version is $pyxbgen_ver"
  exit 1
fi
echo "PYXB generator $__version__ by pyxb $pyxb_ver"
FMLIST=
MDL=
grpl=
BINDINGS=$TDIR/bindings
SCHEMAS=../data
VALID_COLOR="\e[0;92;40m"
INVALID_COLOR="\e[0;31;40m"
NOP_COLOR="\e[0m"
if [ "$PWD" != "$TDIR" ]; then
  [ $opt_verbose -ne 0 ] && echo "\$ cd $TDIR"
  cd $TDIR
fi
if [ -n "$opt_odoo" ]; then
  if [ ! -d $opt_odoo ]; then
    echo "Invalid path $opt_odoo!"
    exit 1
  fi
  for f in pyxbgen.sh pyxbgen.py z0librc; do
    echo "\$ cp $f $opt_odoo"
    cp $f $opt_odoo
  done
  for f in pyxbgen pyxbdump pyxbwsdl; do
    if [ -f $opt_odoo/$f ]; then
      echo "\$ rm -f $opt_odoo/$f"
      rm -f $opt_odoo/$f
    fi
  done
  echo "\$ cp bindings/* $opt_odoo/bindings/"
  cp bindings/* $opt_odoo/bindings/
  exit 0
fi
if [ $opt_list -eq 0 ]; then
   if [ -d $BINDINGS.bak -a ! -f $BINDINGS.bak/_ds.py  -a ! -f $BINDINGS.bak/_cm.py ]; then
     [ $opt_verbose -ne 0 ] && echo "\$ rm -fR $BINDINGS.bak"
     rm -fR $BINDINGS.bak
   fi
   if [ -d $BINDINGS -a ! -f $BINDINGS/_ds.py  -a ! -f $BINDINGS/_cm.py ]; then
     [ $opt_verbose -ne 0 ] && echo "\$ rm -fR $BINDINGS"
     rm -fR $BINDINGS
   fi
   if [ $opt_cont -eq 0 -a -d $BINDINGS ]; then
     if [ -d $BINDINGS.bak ]; then
       [ $opt_verbose -ne 0 ] && echo "\$ rm -fR $BINDINGS.bak"
       rm -fR $BINDINGS.bak
     fi
     [ $opt_verbose -ne 0 ] && echo "\$ mv $BINDINGS $BINDINGS.bak"
     mv $BINDINGS $BINDINGS.bak
   fi
fi
[ $opt_verbose -ne 0 ] && echo "\$ mkdir -p $BINDINGS"
mkdir -p $BINDINGS
[ $opt_verbose -ne 0 ] && echo "\$ cd $BINDINGS"
pushd $BINDINGS ?>/dev/null
if [ ! -d "$SCHEMAS" ]; then
  echo "Directory $SCHEMAS not found!"
fi
exclude="(${opt_exclude//,/|})"
for d in $SCHEMAS/*; do
  if [ -d $d ]; then
    x=$(basename $d)
    if [ "$x" != "common" ]; then
      [ $opt_verbose -ne 0 ] && echo "# analyzing directory $d ..."
      if [ -L $d/xmldsig-core-schema.xsd ]; then
        [ $opt_verbose -ne 0 ] && echo "\$ rm -f $d/xmldsig-core-schema.xsd"
        rm -f $d/xmldsig-core-schema.xsd
      fi
      if [ ! -f $d/xmldsig-core-schema.xsd ]; then
        [ $opt_verbose -ne 0 ] && echo "\$ cp $SCHEMAS/common/xmldsig-core-schema.xsd $SCHEMAS/$x/"
        cp $SCHEMAS/common/xmldsig-core-schema.xsd $SCHEMAS/$x/
      fi
    fi
    p=$d
    for x in main liquidazione; do
      if [ -d $d/$x ]; then
        p=$d/$x
        break
      fi
    done
    [ $opt_verbose -ne 0 ] && echo "# searching for schemas into directory $p ..."
    for f in $p/*.xsd; do
      fn=$(basename $f)
      ff=$(readlink -f $f)
      if [[ ! $fn =~ $exclude || $opt_list -ne 0 ]]; then
        jy=0
        while ((jy<${#XSD_FILES[*]})); do
          xsd="${XSD_FILES[jy]}"
          mdn="${MOD_NAMES[jy]}"
          if [ "$fn" == "$xsd" ]; then
            grp=${mdn:0: -6}
            if [[ $fn =~ $exclude ]]; then
              info="deprecated"
              TEXT_COLOR="$INVALID_COLOR"
            else
              info=""
              TEXT_COLOR="$VALID_COLOR"
            fi
            _xsd=$(printf "%-30.30s" "$xsd")
            _mdn=$(printf "%-20.20s" "$mdn")
            if [ $opt_list -ne 0 ]; then
              echo -e "Found schema $TEXT_COLOR$_xsd$NOP_COLOR module $_mdn (by $grp) $info"
            else
              [[ $grpl =~ $grp ]] && echo "Schema $_xsd may conflict with prior schema by $grp"
              grpl="$grpl $grp"
              MDL="$MDL $mdn"
              FMLIST="-u $f -m $mdn $FMLIST"
            fi
            break
          fi
          ((jy++))
        done
      fi
    done
  fi
done
cmd="$PYXBGEN_BIN $FMLIST --archive-to-file=./ade.wxs"
if [ $opt_list -eq 0 ]; then
  [ $opt_verbose -ne 0 ] && echo "\$ $cmd"
  [ $opt_dry_run -ne 0 ] || eval $cmd
  echo "$(readlink -f $0) -I ${MDL// /,}"
  gen_init "$MDL"
  for f in _cm _ds $MDL; do
    fn=$f.py
    if [ ! -f $fn ]; then
      echo "File $fn not found!"
      echo "Cannot execute $PYXBGEN_PY $fn $SCHEMAS $FMLIST"
    else
      [ $opt_verbose -ne 0 ] && echo "\$ $PYXBGEN_PY $fn $SCHEMAS \"$FMLIST\""
      [ $opt_dry_run -ne 0 -a $opt_keep -ne 0 ] || cp $fn $fn.bak
      [ $opt_dry_run -ne 0 ] || eval $PYXBGEN_PY $fn $SCHEMAS "$FMLIST"
      if [ $opt_nopep8 -eq 0 ]; then
        [ $opt_verbose -ne 0 ] && echo "\$ $TOPEP8 $fn"
        [ $opt_dry_run -ne 0 ] || eval $TOPEP8 $fn
        [ $opt_verbose -ne 0 ] && echo "\$ oca-autopep8 -i $fn"
        [ $opt_dry_run -ne 0 ] || oca-autopep8 -i $fn
      fi
      # [ $opt_verbose -ne 0 ] && echo "\$ sed -e \"s|/opt/odoo/tmp/|../|\" -i $fn"
      # [ $opt_dry_run -ne 0 ] || sed -e "s|/opt/odoo/tmp/|../|" -i $fn
      # read -p "Press RET to continue"       #debug
      [ $opt_verbose -ne 0 ] && echo "\$ $PYXBGEN_PY $fn -3"
      [ $opt_dry_run -ne 0 ] || eval $PYXBGEN_PY $fn -3
      if [ $opt_mult -gt 0 ]; then
        if [ ${fn: -3} == ".py" ]; then
          tgt="${fn:0: -3}__${pyxb_ver//./_}${fn: -3}"
          echo "\$ mv $fn $tgt"
          mv $fn $tgt
          create_hook $fn
        fi
      fi
    fi
  done
fi
popd ?>/dev/null
if [ $opt_list -eq 0 -a $opt_keep -eq 0 ]; then
  find . -name "*.bak" -delete
  find . -name "*.pyc" -delete
fi
