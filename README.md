# gelding

An app to be used for personal financial tracking.
None of the existing apps made any sense to me.
Made as part of the Personal Project course on [boot.dev](https://www.boot.dev/courses/build-personal-project-1).

<img width="1914" height="1074" alt="Gelding Screenshot" src="https://github.com/user-attachments/assets/1127859e-57ef-4295-8917-365c2737a6b2" />

## What is gelding?
gelding is a financial planner app I made for personal use.
As of today, 27.02.2026, it is consistent of a very very minimal overview, but it's everything I need at the moment and it works.
I prefer not to expose my finances online, but I have included a dummy database if you'd like to try it out.

## Features
Currren user abilities:
- Add months
- Add transactions
- Delete transactions
- Change balance

## Requirements
  - Python 3.x
  - PySide6

Install PySide6 ependency through
```python
python3 -m pip install --user PySide6
```
or with your package manger e.g.
```sh
sudo pacman -S PySide6
```

## Install

Clone the repository
```sh
git clone https://github.com/rnirthe/gelding
cd gelding
```

then start the program either through
```
python3 main.py
```
or 
```sh
chmod +x main.sh
./main.sh
```
