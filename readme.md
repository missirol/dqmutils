
* create DQM .root file (DQM+Harvesting)

```
./DQM_test01.sh
```

--------------------------------------------------

* create figures from DQM histograms:

```
./plot_DQMHistos.py -i [DQM_FILE].root -o [OUTPUT_DIR] -e png --only-keys '/DQM/'
```

--------------------------------------------------