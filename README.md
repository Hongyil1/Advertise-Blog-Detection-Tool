# Advertise-Blog-Detection-Tool
This Python tool is used to detect the Wordpress blogs that allow clients to advertise. It reads the file from au_1 to au_20 and write the result in three folders: problem, target and time.
* targer folder contains 20 .csv files which record the detection result of file au_1 to au_20
* problem folder contains 20 .csv files which record the problme urls. The problem urls incur the exception when detecting its CMS. Sometimes there are some target urls in this file.
* time folder contains 20 .txt files which record the running time.

## Prerequisites
* python3+
* Chrome browser
* chromedriver (http://chromedriver.chromium.org/)
* MPI

## How to use
```
mpiexec -n number_of_process python3 crawler.py
```

## Authors

* **[Hongyi Lin](https://github.com/Hongyil1)** 

## License

This project is licensed under the MIT License

## Demo

<img src="https://user-images.githubusercontent.com/22671087/40592113-af3e2cd6-625e-11e8-959c-3466a9bf9276.png" width="400">
