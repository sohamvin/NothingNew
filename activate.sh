cwd=$(pwd)
python3 "$cwd/VTwo/WorkerTwo.py" &
# python3 "$cwd/VTwo/PostProcessorTwo.py" &
python3 "$cwd/main.py" &
wait
