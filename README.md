Media Cloud Visualization Study
==================================

Dev Installation
----------------

 * python 2.7 https://www.python.org/download/releases/2.7/
 * `pip install virtualenv` (if necessary) [also install/link pip if you don't have it (if on Mac OS, use sudo easy_install pip)]
 * [`virtualenv venv`](https://virtualenv.pypa.io/en/stable/)
 * activate your virtualenv (and not run any global python installations)
   * on OSX: `source venv/bin/activate`
   * on Windows: `call venv\Scripts\activate`
 * run `pip install -r requirements.txt` to install dependencies
 * run `python download-google-news-model.py` to download the google news model file

 Running
 -------
 Development: run `python run.py` to test it out
