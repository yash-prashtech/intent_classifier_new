import PyPDF2
import requests
import io
# from pprint import pprint

class AIPDF:
    def __init__(self): pass

    def returnPDFData(self, file):
        response = requests.get(file)
        content = response.content
        fhandle = io.BytesIO(content)

        # fhandle = open(file, 'rb')
        pdfReader = PyPDF2.PdfFileReader(fhandle)
        pagehandle = pdfReader.getPage(0)
        data = (pagehandle.extractText().strip())
        fhandle.close() 
        rawList = [t.strip() for t in data.splitlines()]
        res = self.PDF2JSON(rawList[3:13])
        return res

    #helping function
    def PDF2JSON(self, rawList):
        result = {
            'date_of_notice': '',
            'emp_identification_number': '',
            'number_of_notice': '',
            'company_title': '',
            'company_subtitle':'', 
            'full_address': '',
            'street_address': '', 
            'city': '',
            'state': '', 
            'zip': ''
        }
        
        rawList = [_.strip() for _ in rawList if _.strip()]

        result['date_of_notice'] = rawList[0].replace('Date of this notice:', '').strip()
        result['emp_identification_number'] = rawList[2].strip()
        result['number_of_notice'] = rawList[4].replace('Number of this notice:', '').strip()
        result['company_title'] = rawList[5].strip()
        
        if len(rawList) == 10:
            del rawList[6]
            result['company_subtitle'] = rawList[6].replace('For assistance you may call us at:', '').strip()
            add1 = rawList[7].replace('1-800-829-4933', '').strip().replace('  ',' ')
            add2 = rawList[8].strip().replace('  ',' ')
        else:
            if '1-800-829-4933' == rawList[-1]:
                result['company_subtitle'] = ''
                add1 = rawList[6].strip()
                add2 = rawList[7].replace('For assistance you may call us at:', '').strip()
            else:
                result['company_subtitle'] = rawList[6].strip()
                add1 = rawList[7].replace('For assistance you may call us at:', '').strip()
                add2 = rawList[8].replace('1-800-829-4933', '').strip()
                
        result['full_address'] = f"{add1}, {add2}".replace('  ',' ')
        result['street_address'] = f"{add1}"
        result['city'] = add2.split(',', 1)[0]
        result['state'] = str(add2.split(',')[1]).strip().split()[0]
        result['zip'] = str(add2.split(',')[1]).strip().split()[1]
        # pprint(result)
        return result
