#-*- coding: utf-8 -*-

import qncfg
import xlrd
import xlwt
from datetime import datetime

def read_from_excel ():
    book = xlrd.open_workbook(qncfg.input_data_path)
    for i in range(book.nsheets):
        sh = book.sheet_by_index(i)
        #print sh.name, sh.nrows, sh.ncols
        for j in range(sh.nrows):
            row_entry = sh.row(j)
        
style0 = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
	num_format_str='#,##0.00')
style1 = xlwt.easyxf(num_format_str='D-MMM-YY')

wb = xlwt.Workbook()
ws = wb.add_sheet('Sheet0')

ws.write(0, 0, u"出发机场")
ws.write(0, 1, u"到达机场")
ws.write(0, 2, u"航班日期")
wb.save('example.xls')
