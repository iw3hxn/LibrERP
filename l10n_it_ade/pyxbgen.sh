#! /bin/bash
# -*- coding: utf-8 -*-
#
# pyxbgen
# Agenzia delle Entrate pyxb generator
#
# This free software is released under GNU Affero GPL3
# author: Antonio M. Vigliotti - antoniomaria.vigliotti@gmail.com
# (C) 2017-2017 by SHS-AV s.r.l. - http://www.shs-av.com - info@shs-av.com
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

__version__=0.1.5.5


OPTOPTS=(h        k        l        n           O       p          q            u       V           v           x)
OPTDEST=(opt_help opt_keep opt_list opt_dry_run opt_OCA opt_nopep8 opt_verbose  opt_uri opt_version opt_verbose opt_exclude)
OPTACTI=(1        1        "1>"     1           1       1          0            "1>"    "*"         1           "=>")
OPTDEFL=(1        0        0        0           0       0          -1            0       ""         -1           "DatiFatturaMessaggi,FatturaPA_versione_1.1,MessaggiTypes")
OPTMETA=("help"   ""       ""       ""          ""      ""         "silent"     ""      "version"   "verbose"   "module")
OPTHELP=("this help"\
 "keep temporary files"\
 "list xml schemas and module names"\
 "do nothing (dry-run)"\
 "OCA compatible (convert numeric type to string)"\
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
  print_help "Agenzia delle Entrate pyxb generator\nEsegui questa app nella directory binding"\
  "(C) 2017 by zeroincombenze(R)\nhttp://wiki.zeroincombenze.org/en/Linux/dev\nAuthor: antoniomaria.vigliotti@gmail.com"
  exit 0
fi
XSD_FILES=("fornituraIvp_2017_v1.xsd" "FatturaPA_versione_1.2.xsd" "FatturaPA_versione_1.1.xsd" "DatiFatturav2.1.xsd" "DatiFatturaMessaggiv2.0.xsd" "MessaggiTypes_v1.1.xsd")
MOD_NAMES=("vat_settlement_v_1_0"     "fatturapa_v_1_2"            "fatturapa_v_1_1"            "dati_fattura_v_2_1"  "messaggi_fattura_v_2_0"      "MessaggiTypes_v_1_1")
bin_path=${PATH//:/ }
for x in $TDIR $TDIR/.. $bin_path; do
  if [ -e $x/pyxbgen ]; then
    # [ $opt_verbose -ne 0 ] && echo "PYXBGEN=$x/pyxbgen"
    PYXBGEN=$x/pyxbgen
    break
  fi
done
cmd=
mdl=
grpl=
OCA_binding=
if [ $opt_OCA -ne 0 ]; then OCA_binding="OCA"; fi
BINDINGS=$TDIR/bindings
SCHEMAS=../data
if [ $opt_list -eq 0 ]; then
  rm -fR $BINDINGS
fi
mkdir -p $BINDINGS
pushd $BINDINGS ?>/dev/null
[ $opt_verbose -ne 0 ] && echo "\$ cd $PWD"
exclude="(${opt_exclude//,/|})"
for d in $SCHEMAS/*; do
  if [ -d $d ]; then
    x=$(basename $d)
    if [ "$x" != "common" ]; then
      if [ ! -L $d/xmldsig-core-schema.xsd ]; then
        ln -s $SCHEMAS/common/xmldsig-core-schema.xsd $SCHEMAS/$x/
      fi
    fi
    p=$d
    for x in main liquidazione; do
      if [ -d $d/$x ]; then
        p=$d/$x
        break
      fi
    done
    [ $opt_verbose -ne 0 ] && echo ".. reading directory $p"
    for f in $p/*.xsd; do
      fn=$(basename $f)
      if [[ $fn =~ $exclude ]]; then
        :
      else
        # [ $opt_verbose -ne 0 ] && echo ".... parsing file $fn"
        jy=0
        while ((jy<${#XSD_FILES[*]})); do
          xsd="${XSD_FILES[jy]}"
          mdn="${MOD_NAMES[jy]}"
          if [ "$fn" == "$xsd" ]; then
            grp=${mdn:0: -6}
            if [ $opt_list -ne 0 ]; then
              echo "Found schema $xsd, module $mdn ($grp)"
            elif [[ $grpl =~ $grp ]]; then
              echo "Schema $xsd conflict with prior schema $grp"
            else
              grpl="$grpl $grp"
              mdl="$mdl $mdn"
              cmd="-u $f -m $mdn $cmd"
            fi
            break
          fi
          ((jy++))
        done
      fi
    done
  fi
done
cmd="$PYXBGEN $cmd --archive-to-file=./ade.wxs"
if [ $opt_list -eq 0 ]; then
  [ $opt_verbose -ne 0 ] && echo "\$ $cmd"
  [ $opt_dry_run -ne 0 ] || eval "$cmd"
  i=./__init__.py
  if [ $opt_dry_run -eq 0 ]; then
    echo "# -*- coding: utf-8 -*-" >$i
    echo "# Copyright 2017 - SHS-AV s.r.l. <http://wiki.zeroincombenze.org/it/Odoo>">>$i
    echo "#                  Associazione Odoo Italia <http://www.odoo-italia.org>">>$i
    echo "# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).">>$i
    echo "#">>$i
    echo "# Generated $(date '+%a %Y-%m-%d %H:%M:%S') by pyxbgen.sh $__version__">>$i
    echo "# by Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>">>$i
    echo "#">>$i
    for m in $mdl; do
      echo "from . import $m">>$i
    done
  fi
  for f in _cm _ds $mdl; do
    fn=$f.py
    [ $opt_verbose -ne 0 ] && echo "\$ $TDIR/pyxbgen.py $fn $SCHEMAS $OCA_binding"
    [ $opt_dry_run -ne 0 -a $opt_keep -ne 0 ] || cp $fn $fn.bak
    [ $opt_dry_run -ne 0 ] || eval $TDIR/pyxbgen.py $fn $SCHEMAS "$OCA_binding"
    if [ $opt_nopep8 -eq 0 ]; then
      [ $opt_verbose -ne 0 ] && echo "\$ autopep8 $fn -i"
      [ $opt_dry_run -ne 0 ] || autopep8 $fn -i
    fi
  done
fi
popd ?>/dev/null
if [ $opt_list -eq 0 -a $opt_keep -eq 0 ]; then
  find . -name "*.bak" -delete
  find . -name "*.pyc" -delete
fi
