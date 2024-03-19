import qrcode
url = "https://calendar.google.com/calendar/u/0/r/week"

# https://medium.com/@rahulmallah785671/create-qr-code-by-using-python-2370d7bd9b8d#:~:text=To%20create%20a%20QR%20code,a%20text%20or%20a%20URL
# https://github.com/lincolnloop/python-qrcode

def makeQRCode(url):
    qr = qrcode.QRCode(version=3, box_size=20, border=1, error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr_code.png")

makeQRCode(url)