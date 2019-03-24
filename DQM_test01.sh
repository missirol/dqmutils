#!/bin/bash

# --- Step_1: DQM
if [ ! -f ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8_DQM.root ]; then

  cmsDriver.py step1 \
   --step DQM:offlineValidationHLTSourceOnAOD \
   --filein /store/mc/RunIIAutumn18DRPremix/ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8/AODSIM/102X_upgrade2018_realistic_v15-v1/270000/87EF3D51-5441-2F49-A2BC-54C446667ACD.root \
   --fileout    file:ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8_DQM.root \
   --python_filename ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8_DQM_cfg.py \
   --mc \
   --eventcontent DQM \
   --datatier DQMIO \
   --conditions 102X_upgrade2018_realistic_v15 \
   --geometry DB:Extended \
   --era Run2_2018 \
   --nThreads 1 \
   --no_exec \
   --runUnscheduled \
   --customise Configuration/DataProcessing/Utils.addMonitoring \
   -n 500 || exit $? ;

  cmsRun ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8_DQM_cfg.py
fi

# --------------

# --- Step_2: Harvesting

if [ -f ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8_DQM.root ]; then

  cmsDriver.py step2 \
   --step HARVESTING:dqmHarvesting --harvesting AtRunEnd \
   --filein     file:ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8_DQM.root \
   --python_filename ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8_Harvesting_cfg.py \
   --filetype DQM \
   --mc \
   --scenario pp \
   --conditions 102X_upgrade2018_realistic_v15 \
   --geometry DB:Extended \
   --era Run2_2018 \
   --no_exec \
   -n -1 || exit $? ;

  cmsRun ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8_Harvesting_cfg.py
fi

# --------------
