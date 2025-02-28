# 📚 Calibre Library Series Exporter

## What is this?  

This script organizes books from your Calibre library into a more structured directory based on their series. Instead of using Calibre's default structure, books from the same series are placed in a single folder.  

### 📂 Source Structure:  
```
/path/to/calibre/library/{author}/{book}/{book files}
```

### 📂 Destination Structure:  
```
/path/to/new/library/{series}/{book files}
```

The final book filename format:  
```
{book name on calibre}.{format}
```

**Example:**  
A book in Calibre named `Overlord, Vol. 6 (light novel).epub` will be hardlinked as:  
```
/path/to/new/library/Overlord/Overlord, Vol. 6 (light novel).epub
```

## ✨ Features  
✅ Organizes books into series-based folders  
✅ Keeps books without a series name in a configurable folder  
✅ Uses hardlinks to avoid duplicating files  

## 🚀 How to Use  

1. **Clone the repository**  
   ```sh
   git clone https://github.com/your-repo-name.git
   cd your-repo-name
   ```  

2. **Edit the configuration**  
   Modify `config.yml` to set your library paths and preferences.  

3. **(Optional) Create a virtual environment**  
   ```sh
   python -m venv env
   ```  

4. **Activate the virtual environment**  
   - On macOS/Linux:  
     ```sh
     source env/bin/activate
     ```  
   - On Windows:  
     ```sh
     env\Scripts\activate
     ```  

5. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```  
   _or just:_  
   ```sh
   pip install pyyaml
   ```  

6. **Run the script**  
   ```sh
   python main.py
   ```  

## 🤔 Why?  

Some of my family members and friends use **Komga**, which organizes books based on folder structure rather than metadata. I also find this structure more convenient since I often search for books by series rather than by author.  
