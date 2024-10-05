# Termux Set-up Storage 
**step by step** so please read it carefully and use common sense and some common knowledge higher your reading comprehension to avoid confusion or leading code not to work.

# Installing Dependencies 
**installing the pkg `python`, `git` and `apt`**
```json
pkg install python git apt
```
![Screenshot_2024-10-05-21-15-28-44_84d3000e3f4017145260f7618db1d683](https://github.com/user-attachments/assets/332499d9-3a3e-43db-9315-d952a66dfe0a)

* **after putting the command a lot of text should appear it indicating it started to download the dependencies, you will likely encountered message asking ``Do you want to continue? [Y/n]`` always ``Y`` as yes it asking an permission to use some of your space MB to be used to download dependencies**

![Screenshot_2024-10-05-21-22-03-91_84d3000e3f4017145260f7618db1d683](https://github.com/user-attachments/assets/2058c2d2-0ea0-4b53-8d19-aaad8a210ec4)

* **after all done and the text stop appearing it indicate you downloaded all things good let's move now to another step upgrading all things to latest version to avoid any complict on upcoming installing modules.**

# Upgrading to latest version 
* **Run this command `apt upgrade && update`**
```json
apt upgrade && update
```

* **if run the command and encountered this short messages text**
![Screenshot_2024-10-05-21-31-24-42_84d3000e3f4017145260f7618db1d683](https://github.com/user-attachments/assets/5309c5e5-238d-4d60-8cad-9184a3f679a5)

* **Install the Apt again by running the following command:**
```json
pkg install apt
```
* **and let all text to stop appearing and after it stop run another command**
```json
apt upgrade && update
```
* **after running it should gonna ask you ``Y/N`` always ``Y`` at everything and the appearing text should be long if you did all step properly and got same results as what i am saying then your good move to Cloning the git else please go in server and Open ticket.**

# Cloning repository 
* **Run the following command**
```json
git clone https://github.com/JustAScripts/Nerium.git
```
* **After running the command we gonna open the repository we just clone by running the following command**
```json
cd Nerium
```
* ***after getting in Type in command ``ls`` to confirm it and results should be similar to mine**

![Screenshot_2024-10-05-21-44-32-65_84d3000e3f4017145260f7618db1d683](https://github.com/user-attachments/assets/f354a20d-6f4d-4a47-b4f1-415a6fcde028)
> **let's now move to installing Modules.**

# Installing Modules
* **run the following command**
```json
pip install aiohttp colorama
```
![Screenshot_2024-10-05-21-49-22-66_84d3000e3f4017145260f7618db1d683](https://github.com/user-attachments/assets/bef36b78-8692-4741-84af-841b8d6e0e2b)
* **after running command there should be long ass text keep appearing and keep asking `Y/N` always do `Y` after it prompt successful install Let's move on Editing your config!**

# Config Json Editing 
* **Open your config.json files by running following command**
```json
nano config.json
```
* **Now Move how you can configure your setting**

* **Very self explanatory or just higher your reading comprehension and you gonna get it immediately**
![Screenshot_2024-10-05-21-54-24-53](https://github.com/user-attachments/assets/2bb48d33-2178-48bf-979d-b03409e42297)

# Saving Nano Files
![IMG_20241005_220044](https://github.com/user-attachments/assets/5d4b3685-1f7d-4b2c-bee8-ff3aa844863f)

* and for finishing Touch

# Finishing Touch
```json
python main.py
```
* run this to run the code
