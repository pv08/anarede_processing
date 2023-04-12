# node-impedance-matriz-pwf
Intend to execute the code, just use
```cmd
python main.py
```

This code utilizes the `.pwf` file that must be inside the `data` folder. After you put it inside the folder, use the parameter `--file`. But don't worry, there's a file already based on the IEEE-24 bars sample.

```cmd
python main.py --file data/file.pwf
```

Ather the code is finished, the `etc` and `results` folders will be created. The first one shows all `.pwf` data in a `.json` file. Thus, will be created `DCTE.json`, `DBAR.json` and `DLIN.json`.

The second folder shows all the results. For this project, the admittance matrix using the data exported in JSON will be created.
