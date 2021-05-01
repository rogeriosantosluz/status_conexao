* python3 -m pip install --upgrade pip
* python3 -m venv env (PS> virtualenv env)
* source env/bin/activate (PS> .\env\Scripts\activate.bat)
* pip3 install -r requirements.txt

pyinstaller --onedir --noconsole status_conexao.pyw

MAC
pyinstaller --onefile --noconsole status_conexao.pyw