#! /bin/bash

mkdir outputs

python main.py --vx 4 --vy 4 --vz 4 -H 300 -W 300 objs/cube.obj -o outputs/cube1.svg
python main.py --vx 0 --vy 0 --vz 10 -H 400 -W 300 objs/cube.obj -o outputs/cube2.svg
python main.py --vx 0 --vy 10 --vz 10 -H 400 -W 400 objs/cube.obj -o outputs/cube3.svg
python main.py --vx 10 --vy 0 --vz 10 -H 400 -W 500 objs/cube.obj -o outputs/cube4.svg
python main.py --vx 0 --vy 10 --vz 10 -H 500 -W 500 -j 45 objs/cube.obj -o outputs/cube5.svg
python main.py --vx 0 --vy 10 --vz 10 -H 500 -W 500 -i 45 -k 45 objs/cube.obj -o outputs/cube6.svg

python main.py --vx 20 --vy 20 --vz 20 -H 500 -W 500 objs/f16.obj -o outputs/f16_1.svg
python main.py --vx 20 --vy 20 --vz 20 -H 600 -W 600 -j 45 objs/f16.obj -o outputs/f16_2.svg
python main.py --vx 0 --vy 20 --vz 20 -H 700 -W 700 objs/f16.obj -o outputs/f16_3.svg
python main.py --vx 20 --vy 10 --vz 20 -H 400 -W 400 objs/f16.obj -o outputs/f16_4.svg
python main.py --vx 0 --vy 20 --vz 20 -H 700 -W 700 -i 45 -j 90 objs/f16.obj -o outputs/f16_5.svg
