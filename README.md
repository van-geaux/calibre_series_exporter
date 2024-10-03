# What is this

Copy books from calibre library to a new directory

Instead of using calibre directory structure, books of the same series will be put together inside their respective series directory

Will only copy book file, not metadata and image

Source: '/path/to/calibre/library/{author name}/{book name}/{book files}'

Destination: '/path/to/new/library/{series name}/{book files}'

Final book file name will be: '{book name on calibre} [{publisher name}].{format}'

i.e. 'Overlord, Vol. 6 (light novel) [Yen Press LLC].epub'

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

Because some of my family members and friends prefers Komga and it create series based on series folder instead of books' metadata
