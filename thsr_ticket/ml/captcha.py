import cv2
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

_reader = None  # module-level cache

dic = [[0] * 2 for i in range(100)]
for i in range(100):
    dic[i][0] = 25
    dic[i][1] = 25

dic[50][0]=26
dic[50][1]=24
dic[48][0]=23
dic[48][1]=30
dic[46][0]=27
dic[46][1]=25
dic[45][0]=21
dic[45][1]=30

def preprocess(image):

    # Denoising
    img = cv2.cvtColor(np.array(image.convert('RGB')), cv2.COLOR_RGB2BGR)
    dst = cv2.fastNlMeansDenoisingColored(img, None, 31, 31 ,7 ,21)
    height1, width1 = img.shape[:2]
        
    fig = plt.figure(figsize=(width1, height1), dpi=100)
    plt.axis('off')
    plt.imshow(dst)
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)

    # Save to a buffer
    buf = BytesIO()
    plt.savefig(buf,dpi=10)
    plt.close(fig)
    buf.seek(0)

    img2 = Image.open(buf)
    img2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGBA2BGR)
        
    ret,thresh = cv2.threshold(img2,127,255,cv2.THRESH_BINARY_INV)
    height, width = thresh.shape[:2]
        
    # Find white pixels coordinates
    imgarr = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    imgarr[:,100:width-40] = 0
    white_pixels = np.where(imgarr == 255) 
        
    X = np.array([white_pixels[1]])
    Y = height - white_pixels[0]

    # Polynomial fit
    poly_reg= PolynomialFeatures(degree = 2)
    X_ = poly_reg.fit_transform(X.T)
    regr = LinearRegression()
    regr.fit(X_, Y)

    X2 = np.array([[i for i in range(0,width)]])
    X2_ = poly_reg.fit_transform(X2.T)

    # Remove the polynomial line
    for ele in np.column_stack([regr.predict(X2_).round(0),X2[0],] ):
        pos = height - int(ele[0])
        thresh[pos-int(dic[height1][0]):pos+int(dic[height1][1]), int(ele[1])] = 255 - thresh[pos-int(dic[height1][0]):pos+int(dic[height1][1]),int(ele[1])]

    img3 = cv2.resize(thresh, (140, 48))
    buf = BytesIO()
    fig = plt.figure(figsize=(140, 48), dpi=100)
    plt.axis('off')
    plt.imshow(img3)
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
    plt.savefig(buf, dpi=1)
    plt.close(fig)
    buf.seek(0)

    return Image.open(buf)


def get_ocr_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['en'])
    return _reader


def predict(image):
    reader = get_ocr_reader()
    result = reader.readtext(np.array(image.convert('RGB')), detail = 0, paragraph = True)
    return result[0] if result else None
