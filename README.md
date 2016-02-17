# hwHound
Download homeworks from NPU portal

Usage: 

1. Log in portal in explorer, navigate to target week homework grading page

2. Get Cookie, Referer and Link (URL) from explorer, add them into hwHound.

```ApacheConf
Referer = https://stuosc.npu.edu/TALA/Assignment?enc=A1B2C3
Cookie = __utma=123.123.123; __utmz=123.123.123....

Link = https://stuosc.npu.edu/TALA/Assignment/Grade/12345?enc=A1B2C3/a1b2c3

Path = C:\Users\foo\Documents\Class\CS350\Week3\
```

3. Specify target directory in hwHound.ini

4. Run script in commandline

e.g.
```
python .\hwHound.py
```
