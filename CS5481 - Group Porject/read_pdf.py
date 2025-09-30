import PyPDF2

# 打开PDF文件
pdf_file = open('CS5481_Project.pdf', 'rb')
reader = PyPDF2.PdfReader(pdf_file)

# 提取所有页面的文本
text = ''
for page_num in range(len(reader.pages)):
    page = reader.pages[page_num]
    text += page.extract_text()
    text += '\n--- Page ' + str(page_num + 1) + ' --\n'

# 关闭文件
pdf_file.close()

# 打印提取的文本
print(text)