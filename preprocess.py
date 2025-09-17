import cv2
import numpy as np




def read_image(path_or_array):
if isinstance(path_or_array, str):
img = cv2.imread(path_or_array)
else:
img = path_or_array
if img is None:
raise FileNotFoundError('Image not found')
return img




def to_grayscale(img):
return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)




def resize_keep_aspect(img, target_w=900):
h, w = img.shape[:2]
if w == 0:
return img
scale = target_w / float(w)
return cv2.resize(img, (target_w, int(h * scale)), interpolation=cv2.INTER_AREA)




def denoise_and_threshold(gray):
blur = cv2.GaussianBlur(gray, (3,3), 0)
th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
cv2.THRESH_BINARY_INV, 15, 8)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
opened = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
return opened




def deskew_image(bin_img):
coords = np.column_stack(np.where(bin_img > 0))
if coords.size == 0:
return bin_img
angle = cv2.minAreaRect(coords)[-1]
if angle < -45:
angle = -(90 + angle)
else:
angle = -angle
(h, w) = bin_img.shape
center = (w // 2, h // 2)
M = cv2.getRotationMatrix2D(center, angle, 1.0)
rotated = cv2.warpAffine(bin_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
return rotated




def preprocess_for_ocr(path_or_array):
img = read_image(path_or_array)
gray = to_grayscale(img)
resized = resize_keep_aspect(gray)
th = denoise_and_threshold(resized)
deskewed = deskew_image(th)
# return deskewed binary image (white text on black background)
return deskewed