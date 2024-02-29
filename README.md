# asic_validation
Repository that contains the validation scripts of the ASIC that was created by Patrick Jansky and Matthias Meyer

```conda init cmd.exe```

Install single driver\
```conda install conda-forge::nidaqmx-python```

Export Environment\
```conda env export -n asic_validation_2 > environment.yml```

Create environment\
```conda env create -f environment.yml```

Delete environment\
```conda activate asic_validation```


Link to [Conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment)

Shomehow 'pylint' from conda does not work therefore one has to install it manually \
```pip install pylint```\
```pip install nifgen```

## NI-PXI system
Username: &ensp; .\IMES-PXI \
Password: &ensp; IMES\
IP-Address: &ensp; 152.96.172.31

##Others

```
conda install matplotlib -y
conda install -c conda-forge pyvisa -y
pip install niscope
pip install nifgen
pip install pylint
```