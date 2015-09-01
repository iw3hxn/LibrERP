__author__ = 'carlo'

import xlrd
import csv

FILENAME = 'DataExport_23_8_2015__21_35_56.xls'
OPEN_SHEET = 'Applied_MFN'
HEADER_LINE = 4

FILE_COLUMNS = {
    'code': 4,
    'name': 17,
    'duty_free_tl': 11,
    'custom_rate': 14
}

REFERENCED_FIELDS = ['parent_id', 'category_id']

category = {
    'id': [],
    'code': [],
    'name': [],
    'parent_id': [],
    'type': []
}

hs_code = {
    'id': [],
    'code': [],
    'name': [],
    'category_id': [],
    'duty_free_tl': [],
    'custom_rate': [],
}


class main():

    @staticmethod
    def add_category(code, name, parent_id, category_type):
        category['id'].append('categ_' + code)
        category['code'].append(code)
        category['name'].append(name)
        category['parent_id'].append((parent_id and 'categ_' + parent_id) or '')
        category['type'].append(category_type)
        return

    @staticmethod
    def add_code(code, name, category_id, duty_free_tl, custom_rate):
        hs_code['id'].append('hs_code_' + code)
        hs_code['code'].append(code)
        hs_code['name'].append(name)
        hs_code['category_id'].append('categ_' + category_id)
        hs_code['duty_free_tl'].append(duty_free_tl)
        hs_code['custom_rate'].append(custom_rate)
        return

    @staticmethod
    def write_file(dic, write_file):
        writer = open(write_file, 'w')
        row = ''

        for col in range(len(dic.keys())):
            if dic.keys()[col] in REFERENCED_FIELDS:
                row += '"' + dic.keys()[col] + ':id"'
            else:
                row += '"' + dic.keys()[col] + '"'
            if col != len(dic.keys()) - 1:
                row += ','

        row += '\n'
        writer.write(row)
        row = ''
        for lin in range(len(dic['id'])):
            for col in range(len(dic.keys())):
                row += '"' + str(dic[dic.keys()[col]][lin]).replace('"', '\'') + '"'
                if col != len(dic.keys()) - 1:
                    row += ','
            row += '\n'
            writer.write(row)
            row = ''

        writer.close()

    @staticmethod
    def import_customers():

        excel = xlrd.open_workbook(FILENAME)
        sheet = excel.sheet_by_name(OPEN_SHEET)

        for row in range(sheet.nrows):
            if row <= HEADER_LINE:
                continue

            code = sheet.cell(row, FILE_COLUMNS['code']).value.encode('utf-8', 'ignore')
            name = sheet.cell(row, FILE_COLUMNS['name']).value.encode('utf-8', 'ignore')

            if len(code) == 2:
                main.add_category(code, name, False, 'view')
                continue

            if len(code) == 4:
                main.add_category(code, name, code[0:2], 'normal')
                continue

            if len(code) == 6:
                duty_free_tl = sheet.cell(row, FILE_COLUMNS['duty_free_tl']).value
                custom_rate = sheet.cell(row, FILE_COLUMNS['custom_rate']).value
                main.add_code(code, name, code[0:4], duty_free_tl, custom_rate)

        main.write_file(category, 'hs.category.csv')
        main.write_file(hs_code, 'hs.code.csv')


if __name__ == "__main__":
    main.import_customers()
    print 'END IMPORT'