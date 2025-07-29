# [中文](README_CN.md) | English

# Installation

Install etool using pip:

```bash
pip install -U etool
```

# Features and Usage Examples

## Network

### Test Network Speed

```python
from etool import ManagerSpeed
ManagerSpeed.network() # Network test
ManagerSpeed.disk() # Disk test
ManagerSpeed.memory() # Memory test
ManagerSpeed.gpu_memory() # GPU test
```

## Screen and File Sharing

### Share Screen

```python
from etool import ManagerShare
ManagerShare.screen_share() # Share screen
```

### Share File

```python
from etool import ManagerShare
ManagerShare.share_file() # Share file
```

## Office

### PDF Processing

```python
from etool import ManagerPdf

# Convert doc, xlsx, etc. to pdf (convert one file)
ManagerPdf.pdfconverter(os.path.join(os.path.dirname(__file__),'pdf','ex1.docx'),os.path.join(os.path.dirname(__file__),'pdf_out'))
# Convert doc, xlsx, etc. to pdf (convert all files in a directory)
ManagerPdf.pdfconverter(os.path.join(os.path.dirname(__file__),'pdf'),os.path.join(os.path.dirname(__file__),'pdf_out'))

# Add watermark to pdf files (one file)
ManagerPdf.create_watermarks(os.path.join(os.path.dirname(__file__),'pdf_out','ex1.pdf'),os.path.join(os.path.dirname(__file__),'pdf_out','watermarks.pdf'),os.path.join(os.path.dirname(__file__),'pdf_out_watermark'))
# Add watermark to pdf files (all files in a directory)
ManagerPdf.create_watermarks(os.path.join(os.path.dirname(__file__),'pdf_out'),os.path.join(os.path.dirname(__file__),'pdf_out','watermarks.pdf'),os.path.join(os.path.dirname(__file__),'pdf_out_watermark'))

# Encrypt pdf files
ManagerPdf.encrypt_pdf(os.path.join(os.path.dirname(__file__),'pdf_out','ex1.pdf'),r"1234567890")
# Decrypt pdf files
ManagerPdf.decrypt_pdf(os.path.join(os.path.dirname(__file__),'pdf_out','ex1_encrypted.pdf'),r"1234567890")

# Split pdf files (by pages) every 3 pages
ManagerPdf.split_by_pages(os.path.join(os.path.dirname(__file__),'pdf_out','merged.pdf'),3)
# Split pdf files (by number) into 2 parts
ManagerPdf.split_by_num(os.path.join(os.path.dirname(__file__),'pdf_out','merged.pdf'),2)

# Insert pdf ex2 into a specific page of pdf ex1
ManagerPdf.insert_pdf(os.path.join(os.path.dirname(__file__),'pdf_out','ex1.pdf'),os.path.join(os.path.dirname(__file__),'pdf_out','ex2.pdf'),0,os.path.join(os.path.dirname(__file__),'pdf_out','pdf_insert.pdf'))
```

### docx Processing

```python
from etool import ManagerDocx
word_path = 'ex1.docx' # docx file path
result_path = 'result' # save path
ManagerDocx.replace_words(word_path, '1', '2') # Replace text in document
ManagerDocx.change_forward(word_path, 'result.docx') # Change document format
ManagerDocx.get_pictures(word_path, result_path) # Extract images from docx to result folder
```

### Email Sending

```python
from etool import ManagerEmail
ManagerEmail.send_email(
    sender='1234567890@qq.com',
    password='1234567890',
    recipient='1234567890@qq.com',
    subject='Test Email',
    message='Test email content',
    file_path='test.txt',
    image_path='test.webp'
) # Send email
```

### Image Processing

```python
from etool import ManagerImage
pics = ['pic1.webp', 'pic2.webp'] # List of image paths
ManagerImage.merge_LR(pics) # Merge left and right
ManagerImage.merge_UD(pics) # Merge up and down
ManagerImage.fill_image('pic1_UD.webp') # Fill image
ManagerImage.cut_image('pic1_UD_fill.webp') # Cut image
ManagerImage.rename_images('tests', remove=True) # Rename images
```

### Excel Processing

```python
from etool import ManagerExcel
excel_path = 'ex1.xlsx' # Excel file path
save_path = 'result.xlsx' # Save path
ManagerExcel.excel_format(excel_path, save_path) # Copy style from ex1.xlsx to result.xlsx
```

### QR Code Generation

```python
from etool import ManagerQrcode
qr_path = 'qr.png' # Save path
ManagerQrcode.generate_english_qrcode(words='https://www.baidu.com', qr_path) # Generate QR code without Chinese
ManagerQrcode.generate_qrcode(words='百度', qr_path) # Generate QR code with Chinese
ManagerQrcode.decode_qrcode(qr_path) # Decode QR code
```

### ipynb Conversion

```python
from etool import ManagerIpynb
ipynb_dir = 'ipynb_dir' # ipynb directory path
md_dir = 'md' # md directory path

ManagerIpynb.merge_notebooks(ipynb_dir) # Merge ipynb files
ManagerIpynb.convert_notebook_to_markdown(ipynb_dir+'.ipynb', md_dir) # Convert ipynb files to md files
```

## Markdown Processing

```python
from etool import ManagerMd

# Convert Markdown to Word document
ManagerMd.convert_md_to_docx("document.md", "document.docx")

# Convert Markdown to HTML webpage
ManagerMd.convert_md_to_html("document.md", "document.html")

# Extract tables from Markdown to Excel
ManagerMd.extract_tables_to_excel("document.md", "tables.xlsx")
```

## Others

### Task Scheduling

```python
from etool import ManagerScheduler

def job():
    print("job")
    raise Exception("error")

def func_success():
    print("success")

def func_failure():
    print("failure")

ManagerScheduler.pocwatch(job, 2, func_success, func_failure)
"""
- `job`: Task function
- `schedule_time`: Execution time
- `func_success`: Callback function on task success
- `func_failure`: Callback function on task failure

`schedule_time` format:

If it's a number, the default unit is seconds, executed every `schedule_time` seconds, e.g., `120` means every 2 minutes.

If it's a string, the default is a time point, follow the `HH:MM` format, e.g., `08:00`, executed once daily at this time.

If it's a list, the default is multiple time points, e.g., `["08:00", "12:00", "16:00"]`, executed daily at these times.

If a dictionary is passed, parse the dictionary keys:

If the key is a number, the default is a date, the corresponding value follows the above number, string, list judgment.

If the key is a string, the default is a weekday (e.g., Monday, supported formats include: `1`, `monday`, `Monday`, `MONDAY`, `mon`, `mon.`, `m`), the corresponding value follows the above number, string, list judgment.

For example, the 1st at 8:00, the 2nd at 8:00, 12:00, 16:00, the 3rd every hour, every Monday at 8:00.

schedule_time = {
1: "08:00",
2: ["08:00", "12:00", "16:00"],
3: 216000,
"1": "08:00",
}

"""
# If you're unsure about the schedule time, use the parse_schedule_time function to confirm
ManagerScheduler.parse_schedule_time(120)
ManagerScheduler.parse_schedule_time("08:00")
ManagerScheduler.parse_schedule_time(["08:00", "12:00", "16:00"])
ManagerScheduler.parse_schedule_time({1: "08:00", 2: ["08:00", "12:00", "16:00"], 3: 216000, "1": "08:00"})

```

### Password Generation and Base Conversion

```python
from etool import ManagerPassword
print(ManagerPassword.generate_pwd_list(ManagerPassword.results['all_letters'] + ManagerPassword.results['digits'], 2))
# Generate all possible 2-digit passwords (for password cracking)
print(ManagerPassword.random_pwd(8))
# Randomly generate an 8-digit password (random encryption)

print(ManagerPassword.convert_base("A1F", 16, 2))
# Convert 16-digit to 2-digit
print(ManagerPassword.convert_base("-1101", 2, 16))
# Convert 2-digit to 16-digit
print(ManagerPassword.convert_base("Z", 36, 10))
# Convert 36-digit to 10-digit
```

### Install Dependencies

```python
from etool import ManagerInstall
ManagerInstall.install(requirements_file="requirements.txt", failed_file="failed_requirements.txt", retry=2)
# Automatically install dependencies, retry 2 times if installation fails, skip installation if successful. The above are default parameters.
# You can also use the default parameters without specifying parameters.  
ManagerInstall.install()
```

### Manage Windows Right-Click Menu

```python
from etool import ManagerMenu
ManagerMenu.switch_to_classic_menu() # Switch to Windows 11 classic right-click menu
ManagerMenu.switch_to_new_menu() # Switch to Windows 11 new right-click menu
ManagerMenu.add_cursor_context_menu() # Add Cursor to Windows right-click menu
ManagerMenu.remove_cursor_context_menu() # Remove Cursor from Windows right-click menu
```
