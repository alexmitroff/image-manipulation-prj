import os
import argparse

from PIL import Image
import svgwrite

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="Path to source image", type=str)
parser.add_argument("-s", help="Image size", type=int)
parser.add_argument("-c", help="Number of colors", type=int)
args = parser.parse_args()

if args.s:
    IMAGE_SIZE = args.s
else:
    IMAGE_SIZE = 128

if args.c:
    COLORS = args.c
else:
    COLORS = 8

d = 10
r = d/2

def get_image_data(file_path):
    im = Image.open(file_path) # Can be many different formats.
    im.thumbnail((IMAGE_SIZE,IMAGE_SIZE), resample=3)
    im = im.convert('P', palette=Image.ADAPTIVE, colors=COLORS)
    im = im.convert('RGB', palette=Image.ADAPTIVE, colors=COLORS)
    list_of_pxs = list(im.getdata())
    image_width = im.width
    image_height = im.height

    print('Get data from image to lines')
    lines = []
    for line_number in range(image_height):
        start_of_slice = image_width*line_number
        end_of_slice = image_width*line_number+image_width
        lines.append(list_of_pxs[start_of_slice:end_of_slice])

    return lines, image_width, image_height

def current_stack_defaults():
    return {'count':0, 'color':(-1,-1,-1)}

def stack_colors(lines, image_width):
    print('Stack colors')
    stack_lines = []
    for line_number, line in enumerate(lines):
        stack_line = []
        current_stack = current_stack_defaults()
        for index, pixel in enumerate(line):
            if index == 0:
                current_stack['count'] = 1
                current_stack['color'] = pixel
            elif index == image_width - 1:
                if line[index-1] == pixel:
                    current_stack['count'] += 1
                else:
                    stack_line.append(current_stack.copy())
                    current_stack['count'] = 1
                    current_stack['color'] = pixel
                stack_line.append(current_stack.copy())
            elif line[index-1] == pixel:
                current_stack['count'] += 1
            else:
                stack_line.append(current_stack.copy())
                current_stack['count'] = 1
                current_stack['color'] = pixel

        pixels_sum = 0
        for stack in stack_line:
            pixels_sum += stack['count']
        print('Line {}: {}/{} pixels ({}) '.format(line_number+1, pixels_sum, image_width, pixels_sum == image_width))

        stack_lines.append(stack_line)
    return stack_lines


#image_data = numpy.stack(lines)
def create_svg_circles(lines, image_width, image_height):
    #print(lines)
    print('Draw SVG')
    dwg = svgwrite.Drawing('test2.svg', size=('{}mm'.format(image_width), '{}mm'.format(image_height)), viewBox=('0 0 {} {}'.format(image_width*d,image_height*d)))
    for line_number, line in enumerate(lines):
        print('Proceed line: {}/{}'.format(line_number, image_height), end='\r')
        line_center = d*line_number + r
        for circle_number, circle_color in enumerate(line):
            column_center = d*circle_number + r
            dwg.add(dwg.circle(center=(column_center,line_center),r=r, style="fill:#{:02x}{:02x}{:02x}".format(circle_color[0],circle_color[1],circle_color[2])))
    dwg.save()

def create_svg_rectangles(lines, image_width, image_height):
    #print(lines)
    print('Draw SVG')
    dwg = svgwrite.Drawing('test2.svg', size=('{}mm'.format(image_width), '{}mm'.format(image_height)), viewBox=('0 0 {} {}'.format(image_width*d,image_height*d)))
    for line_number, stack_line in enumerate(lines):
        print('Proceed line: {}/{}'.format(line_number, image_height), end='\r')
        rect_y = d*line_number
        rect_x = 0
        for stack_index, stack in enumerate(stack_line):
            if stack_index != 0:
                rect_x += d*stack_line[stack_index-1]['count']
            else:
                rect_x = 0
            rect_height = d
            rect_width = d*stack['count']
            rect_color = stack['color']
            print('{}.{}: x={} {} {}'.format(line_number,stack_index, rect_x, rect_width, rect_color))
            dwg.add(dwg.rect(insert=(rect_x,rect_y), size=(rect_width,rect_height), ry=r, style="fill:#{:02x}{:02x}{:02x}".format(rect_color[0],rect_color[1],rect_color[2])))
    dwg.save()

if __name__ == "__main__":
    lines, image_width, image_height = get_image_data(args.i)
    stack_lines = stack_colors(lines, image_width)
    create_svg_rectangles(stack_lines, image_width, image_height)
    #create_svg_circles(lines, image_width, image_height)
