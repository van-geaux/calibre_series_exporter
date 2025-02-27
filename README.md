# What is this

Hardlink books from calibre library to a new directory

Instead of using calibre directory structure, books of the same series will be put together inside their respective series directory

Source: '/path/to/calibre/library/{author name}/{book name}/{book files}'
Destination: '/path/to/new/library/{series name}/{book files}'

Final book file name will be: '{book name on calibre}.{format}'

i.e. 'Overlord, Vol. 6 (light novel).epub'

# Features
1. Extract books from calibre and put them in their respective series folders
2. Books without a series name will all be put in a configurable folder

# How to use
1. Copy the repo
2. Change the config.yml to your need
3. Create a virtual environment (optional)

   `python -m venv env`
   
4. Enter the environment
   
   `source env/bin/activate` or `env\Scripts\activate` if on windows
   
5. Install dependencies (only pyyaml)
   
   `pip install -r requirements.txt` or just simply `pip install pyyaml`
   
6. Run the script `python main.py`

# Why?

Because some of my family members and friends prefers to use Komga and it create series based on series folder instead of using books' metadata.
I also like that directory structure better, make searching for books easier because I often don't care about who wrote them.