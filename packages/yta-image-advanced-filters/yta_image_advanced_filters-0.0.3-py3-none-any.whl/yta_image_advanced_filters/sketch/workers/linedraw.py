from yta_image_advanced_filters.sketch.workers.filters import *
from yta_image_advanced_filters.sketch.workers.strokesort import *
from yta_image_advanced_filters.sketch.workers.util import *
from yta_image_advanced_filters.sketch.workers import perlin
from yta_image_base.converter import ImageConverter
from random import *
from PIL import Image, ImageDraw, ImageOps


no_cv = False
draw_contours = True
draw_hatch = True
show_bitmap = False
resolution = 1920    # Our default scene size
hatch_size = 16
contour_simplify = 2

try:
    import numpy as np
    import cv2
except:
    no_cv = True

def find_edges(IM):
    if no_cv:
        #appmask(IM,[F_Blur])
        appmask(IM,[F_SobelX,F_SobelY])
    else:
        im = np.array(IM) 
        im = cv2.GaussianBlur(im,(3,3),0)
        im = cv2.Canny(im,100,200)
        IM = Image.fromarray(im)
    return IM.point(lambda p: p > 128 and 255)  


def getdots(IM):
    PX = IM.load()
    dots = []
    w,h = IM.size
    for y in range(h-1):
        row = []
        for x in range(1,w):
            if PX[x,y] == 255:
                if len(row) > 0:
                    if x-row[-1][0] == row[-1][-1]+1:
                        row[-1] = (row[-1][0],row[-1][-1]+1)
                    else:
                        row.append((x,0))
                else:
                    row.append((x,0))
        dots.append(row)
    return dots
    
def connectdots(dots):
    contours = []
    for y in range(len(dots)):
        for x,v in dots[y]:
            if v > -1:
                if y == 0:
                    contours.append([(x,y)])
                else:
                    closest = -1
                    cdist = 100
                    for x0,v0 in dots[y-1]:
                        if abs(x0-x) < cdist:
                            cdist = abs(x0-x)
                            closest = x0

                    if cdist > 3:
                        contours.append([(x,y)])
                    else:
                        found = 0
                        for i in range(len(contours)):
                            if contours[i][-1] == (closest,y-1):
                                contours[i].append((x,y,))
                                found = 1
                                break
                        if found == 0:
                            contours.append([(x,y)])
        for c in contours:
            if c[-1][1] < y-1 and len(c)<4:
                contours.remove(c)
    return contours


def getcontours(IM,sc=2):
    IM = find_edges(IM)
    IM1 = IM.copy()
    IM2 = IM.rotate(-90,expand=True).transpose(Image.FLIP_LEFT_RIGHT)
    dots1 = getdots(IM1)
    contours1 = connectdots(dots1)
    dots2 = getdots(IM2)
    contours2 = connectdots(dots2)

    for i in range(len(contours2)):
        contours2[i] = [(c[1],c[0]) for c in contours2[i]]    
    contours = contours1+contours2

    for i in range(len(contours)):
        for j in range(len(contours)):
            if len(contours[i]) > 0 and len(contours[j])>0:
                if distsum(contours[j][0],contours[i][-1]) < 8:
                    contours[i] = contours[i]+contours[j]
                    contours[j] = []

    for i in range(len(contours)):
        contours[i] = [contours[i][j] for j in range(0,len(contours[i]),8)]


    contours = [c for c in contours if len(c) > 1]

    for i in range(0,len(contours)):
        contours[i] = [(v[0]*sc,v[1]*sc) for v in contours[i]]

    for i in range(0,len(contours)):
        for j in range(0,len(contours[i])):
            contours[i][j] = int(contours[i][j][0]+10*perlin.noise(i*0.5,j*0.1,1)),int(contours[i][j][1]+10*perlin.noise(i*0.5,j*0.1,2))

    return contours


def hatch(IM,sc=16):
    PX = IM.load()
    w,h = IM.size
    lg1 = []
    lg2 = []
    for x0 in range(w):
        for y0 in range(h):
            x = x0*sc
            y = y0*sc
            if PX[x0,y0] > 144:
                pass
                
            elif PX[x0,y0] > 64:
                lg1.append([(x,y+sc/4),(x+sc,y+sc/4)])
            elif PX[x0,y0] > 16:
                lg1.append([(x,y+sc/4),(x+sc,y+sc/4)])
                lg2.append([(x+sc,y),(x,y+sc)])

            else:
                lg1.append([(x,y+sc/4),(x+sc,y+sc/4)])
                lg1.append([(x,y+sc/2+sc/4),(x+sc,y+sc/2+sc/4)])
                lg2.append([(x+sc,y),(x,y+sc)])

    lines = [lg1,lg2]
    for k in range(0,len(lines)):
        for i in range(0,len(lines[k])):
            for j in range(0,len(lines[k])):
                if lines[k][i] != [] and lines[k][j] != []:
                    if lines[k][i][-1] == lines[k][j][0]:
                        lines[k][i] = lines[k][i]+lines[k][j][1:]
                        lines[k][j] = []
        lines[k] = [l for l in lines[k] if len(l) > 0]
    lines = lines[0]+lines[1]

    for i in range(0, len(lines)):
        for j in range(0, len(lines[i])):
            lines[i][j] = int(lines[i][j][0]+sc*perlin.noise(i*0.5,j*0.1,1)),int(lines[i][j][1]+sc*perlin.noise(i*0.5,j*0.1,2))-j
    return lines


def apply_line_sketch_to_image(image: str, output_filename: str):
    # TODO: If this is for internal use we don't need 'output_filename'
    if not isinstance(image, np.ndarray) and not image:
        raise Exception('No "image" provided.')
    
    # TODO: Check 'output_filename'
    if isinstance(image, np.ndarray):
        IM = ImageConverter.numpy_image_to_pil(image)
    else:
        IM = Image.open(image)
    
    w, h = IM.size

    IM = IM.convert("L")
    IM = ImageOps.autocontrast(IM, 10)

    lines = []
    if draw_contours:
        lines += getcontours(IM.resize((resolution // contour_simplify, resolution // contour_simplify * h // w)), contour_simplify)
    if draw_hatch:
        lines += hatch(IM.resize((resolution // hatch_size, resolution // hatch_size * h // w)), hatch_size)

    lines = sortlines(lines)
    
    disp = Image.new("RGB", (resolution, resolution * h // w), (255, 255, 255))
    draw = ImageDraw.Draw(disp)
    for l in lines:
        draw.line(l, (0, 0, 0), 5)

    return disp

    disp.save(output_filename)

    # # We force it to be a svg file
    # output_filename = get_file_filename_without_extension(output_filename + '.svg')
    
    # f = open(output_filename, 'w')
    # f.write(makesvg(lines))
    # f.close()

    # TODO: Check svg to png conversion
    # https://stackoverflow.com/questions/6589358/convert-svg-to-png-in-python

    return output_filename


def makesvg(lines):
    out = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">'

    for l in lines:
        l = ",".join([str(p[0]*0.5)+","+str(p[1]*0.5) for p in l])
        out += '<polyline points="'+l+'" stroke="black" stroke-width="2" fill="none" />\n'
    out += '</svg>'

    return out



# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Convert image to vectorized line drawing for plotters.')
#     parser.add_argument('-i','--input',dest='input_path',
#         default='lenna',action='store',nargs='?',type=str,
#         help='Input path')

#     parser.add_argument('-b','--show_bitmap',dest='show_bitmap',
#         const = not show_bitmap,default= show_bitmap,action='store_const',
#         help="Display bitmap preview.")

#     parser.add_argument('-nc','--no_contour',dest='no_contour',
#         const = draw_contours,default= not draw_contours,action='store_const',
#         help="Don't draw contours.")
       
#     parser.add_argument('-nh','--no_hatch',dest='no_hatch',
#         const = draw_hatch,default= not draw_hatch,action='store_const',
#         help='Disable hatching.')

#     parser.add_argument('--no_cv',dest='no_cv',
#         const = not no_cv,default= no_cv,action='store_const',
#         help="Don't use openCV.")


#     parser.add_argument('--hatch_size',dest='hatch_size',
#         default=hatch_size,action='store',nargs='?',type=int,
#         help='Patch size of hatches. eg. 8, 16, 32')
#     parser.add_argument('--contour_simplify',dest='contour_simplify',
#         default=contour_simplify,action='store',nargs='?',type=int,
#         help='Level of contour simplification. eg. 1, 2, 3')

#     args = parser.parse_args()
    
#     draw_hatch = not args.no_hatch
#     draw_contours = not args.no_contour
#     hatch_size = args.hatch_size
#     contour_simplify = args.contour_simplify
#     show_bitmap = args.show_bitmap
#     no_cv = args.no_cv
#     sketch(args.input_path)