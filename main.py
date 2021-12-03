import functions
import os

# First line of CSV is the final file name
# Anything after that is an image URL

functions.merge_to_pdf('urls.csv')
os.remove('./output/current_page.pdf')
print('Completed! Check output folder.')

