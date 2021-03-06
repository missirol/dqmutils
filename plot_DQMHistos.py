#!/usr/bin/env python
import argparse, os, ROOT

from common import *

from plot_style import load_plot_style

def TH1_keys(tdirectory, prefix='', contains_all=[], contains_one=[]):

    th1_keys = []

    for k_key in tdirectory.GetListOfKeys():
        k_key_name = k_key.GetName()

        k_obj = tdirectory.Get(k_key_name)
        if not k_obj: continue

        if k_obj.InheritsFrom('TDirectory'):

           th1_keys += TH1_keys(k_obj, prefix=prefix+k_obj.GetName()+'/', contains_all=contains_all, contains_one=contains_one)

        elif k_obj.InheritsFrom('TH1'):

           h_name = prefix+k_obj.GetName()

           if len(contains_all) > 0:
              skip = False
              for _tmp in contains_all:
                  if _tmp not in h_name: skip = True; break;
              if skip: continue

           if len(contains_one) > 0:
              skip = True
              for _tmp in contains_one:
                  if _tmp in h_name: skip = False; break;
              if skip: continue

           th1_keys += [prefix+k_obj.GetName()]

    return th1_keys

def get_text(x1ndc_, y1ndc_, talign_, tsize_, text_):

    txt = ROOT.TLatex(x1ndc_, y1ndc_, text_)
    txt.SetTextAlign(talign_)
    txt.SetTextSize(tsize_)
    txt.SetTextFont(42)
    txt.SetNDC()

    return txt
#### ----

#### main
if __name__ == '__main__':
    ### args --------------
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', dest='input', required=True, action='store', default=None,
                        help='path to input DQM .root file')

    parser.add_argument('-o', '--output', dest='output', required=True, action='store', default=None,
                        help='path to output directory')

    parser.add_argument('--only-keys', dest='only_keys', nargs='+', default=['/HLT/Run summary/Filters/', '/HLT/Run summary/JME/', '/HLT/Run summary/TOP/'],
                        help='list of strings required to be in histogram key')

    parser.add_argument('-e', '--exts', dest='exts', nargs='+', default=['pdf', 'png'],
                        help='list of extension(s) for output file(s)')

    parser.add_argument('-n', '--name-only', dest='name_only', action='store_true', default=False,
                        help='only print name of input histograms')

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
                        help='enable verbose mode')

    opts, opts_unknown = parser.parse_known_args()
    ### -------------------

    ROOT.gROOT.SetBatch()
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    log_prx = os.path.basename(__file__)+' -- '

    ### args validation ---
    if not os.path.isfile(opts.input):
       KILL(log_prx+'invalid path to input .root file [-i]: '+opts.input)

    if os.path.exists(opts.output):
       KILL(log_prx+'target path to output .root file already exists [-o]: '+opts.output)

    EXTS = list(set(opts.exts))

    ONLY_KEYS = list(set(opts.only_keys))

    if len(ONLY_KEYS):
       print '\n >>> will plot only TH1 objects containing all of the following strings in their internal path:', ONLY_KEYS, '\n'

    if len(opts_unknown) > 0:
       KILL(log_prx+'unrecognized command-line arguments: '+str(opts_unknown))
    ### -------------------

    ### input histograms --
    histo_dict = {}

    i_inptfile = ROOT.TFile.Open(opts.input)
    if (not i_inptfile) or i_inptfile.IsZombie() or i_inptfile.TestBit(ROOT.TFile.kRecovered): raise SystemExit(1)

    for h_key in TH1_keys(i_inptfile, contains_one=ONLY_KEYS):

        if h_key in histo_dict:
           KILL(log_prx+'input error -> key "'+h_key+'" already exists in histogram-dictionary')

        h0 = i_inptfile.Get(h_key)
        if not (h0 and h0.InheritsFrom('TH1')):
           KILL(log_prc+'input error -- key "'+h_key+'" not associated to a TH1 object: '+opts.input)

        h0.SetDirectory(0)
        histo_dict[h_key] = h0

        if opts.verbose: print '\033[1m'+'\033[92m'+'[input]'+'\033[0m', h_key

    i_inptfile.Close()
    ### -------------------

    ### output files (plots)
    load_plot_style()

    ROOT.TGaxis.SetMaxDigits(4)

    for histo_key in sorted(histo_dict.keys()):

        if not histo_dict[histo_key].InheritsFrom('TH1'):
           WARNING(log_prx+'input histogram does not inherit from TH1 (not supported), will be skipped')
           continue

        if histo_dict[histo_key].InheritsFrom('TH3'):
           WARNING(log_prx+'input histogram inherits from TH3 (not supported), will be skipped')
           continue

        if opts.name_only:
           print '\033[1m'+'\033[92m'+'['+str(histo_dict[histo_key].ClassName())+']'+'\033[0m', histo_key
           continue

        isTH2 = histo_dict[histo_key].InheritsFrom('TH2')

        if isTH2: opt_draw = 'colz,text'
        else:
           if histo_dict[histo_key].GetName().startswith('effic_') and ('/Filters/' not in histo_key):
              opt_draw = 'pex0'
           else:
              opt_draw = 'hist,e'

        canvas = ROOT.TCanvas(histo_key, histo_key)
        canvas.SetTickx()
        canvas.SetTicky()

        if isTH2: canvas.SetGrid(0,0)
        else: canvas.SetGrid(1,1)

        T = canvas.GetTopMargin()
        R = canvas.GetRightMargin()
        B = canvas.GetBottomMargin()
        L = canvas.GetLeftMargin()

        ROOT.TGaxis.SetExponentOffset(-L+.50*L, 0.03, 'y')

        txt1 = None
        if 'denominator' in histo_dict[histo_key].GetTitle(): txt1 = get_text(L+(1-R-L)*1.00, (1-T)+T*0.15, 31, .025, '[Denominator]')
        elif 'numerator' in histo_dict[histo_key].GetTitle(): txt1 = get_text(L+(1-R-L)*1.00, (1-T)+T*0.15, 31, .025, '[Numerator]')

        txt2 = None # get_text(L+(1-R-L)*0.05, B+(1-B-T)*.77, 13, .040, '')

        histo_dict[histo_key].SetBit(ROOT.TH1.kNoTitle)

        histo_dict[histo_key].UseCurrentStyle()

        if isTH2:
           histo_dict[histo_key].SetMarkerColor(1)
           histo_dict[histo_key].SetMarkerSize(1)
           histo_dict[histo_key].SetMarkerStyle(20)
           histo_dict[histo_key].SetLineColor(1)
           histo_dict[histo_key].SetLineWidth(2)

        else:
           histo_dict[histo_key].SetMarkerColor(2)
           histo_dict[histo_key].SetMarkerSize(1)
           histo_dict[histo_key].SetMarkerStyle(20)
           histo_dict[histo_key].SetLineColor(2)
           histo_dict[histo_key].SetLineWidth(2)

        canvas.cd()

        hmax = 0.0
        for i_bin in range(1, histo_dict[histo_key].GetNbinsX()+1):
            hmax = max(hmax, (histo_dict[histo_key].GetBinContent(i_bin) + histo_dict[histo_key].GetBinError(i_bin)))

        canvas.cd()

        histo_dict[histo_key].Draw(opt_draw)

        if txt1: txt1.Draw('same')
        if txt2: txt2.Draw('same')

        output_basename_woExt = os.path.abspath(opts.output)+'/'+histo_key.replace(' ', '_')

        output_dirname = os.path.dirname(output_basename_woExt)
        if not os.path.isdir(output_dirname): EXE('mkdir -p '+output_dirname)

        for i_ext in EXTS:

            out_file = output_basename_woExt+'.'+i_ext

            canvas.SaveAs(out_file)

            print '\033[1m'+'\033[92m'+'[output]'+'\033[0m', os.path.relpath(out_file)

        canvas.Close()
    ### -------------------
