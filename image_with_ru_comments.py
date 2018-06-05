import os # модуль python, позволяющий нам дотянуться до файлов
import argparse # модуль python, позволяющий нам передавать в скрипт аргументы

from PIL import Image # модуль библиотеки Python Image Library, позволяющий нам работать с картинками
import svgwrite # модуль python, позволяющий нам работать с SVG

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="Path to source image", type=str) # в этот аргумент мы передаем текст (путь к файлу)
parser.add_argument("-s", help="Image output resolution", type=int) # в этот аргумент мы передаем целочисленное значение (размер картинки)
parser.add_argument("-c", help="Number of colors", type=int) # в этот аргумент мы передаем целочисленное значение (количество цветов)
args = parser.parse_args() # помещаем все вышеперечисленные аргументы в переменную

PATH = args.i # достаем путь к исходной картинке, если его нет, то ничего работать не будет

if args.s: # достаем размер картинки
    IMAGE_SIZE = args.s
else: # если мы его не передали в аргумент, то берем значение по-умолчанию
    IMAGE_SIZE = 128

if args.c: # достаем количество цветов в картинке
    COLORS = args.c
else: # если мы их не передали в аргумент, то берем значение по-умолчанию
    COLORS = 8

# формируем путь для сохранения SVG, он будет например такой "/path/to/image.jpg.s<размер картинки>.c<количество цветов в картинке>.svg"
SVG_PATH = '.'.join([PATH, 's{}'.format(IMAGE_SIZE), 'c{}'.format(COLORS), 'svg'])

d = 10 # диаметр SVG круга или высота SVG прямоугольника
r = d/2 # радиус SVG круга или радиус закругления углов SVG прямоугольника

def get_image_data(file_path):
    # Функция, которая отдает нам информацию о пикселях в картинке построчно.
    # Она принимает на вход путь к картинке.
    # Отдает список состоящий из строк, где каждая строка -- это список из RGB цветов, например (255, 255, 255),
    # и размеры картинки.
    im = Image.open(file_path) # Берем картинку
    im.thumbnail((IMAGE_SIZE,IMAGE_SIZE), resample=3) # уменьшаем ее до нужного нам размера
    im = im.convert('P', palette=Image.ADAPTIVE, colors=COLORS) # уменьшаем количество цветов в ней до необходимого количества
    im = im.convert('RGB', palette=Image.ADAPTIVE, colors=COLORS) # удоставеряемся, что цвета -- RGB
    list_of_pxs = list(im.getdata()) # достаем список цветов пикселей, из которых состоит преобразованная картинка
    image_width = im.width # берем ширину картинки
    image_height = im.height # берем ее высоту картинки (количество строк в картинке)

    print('Get data from image to lines') # вывод отладочной информации,
                                          # чтобы мы знали на каком моменте сейчас находится выполнение нашего скрипта

    lines = [] # заготавливаем список под строки
    for line_number in range(image_height): # для каждой строки из всех строк картинки
        start_of_slice = image_width*line_number # находим номер первого пиксел в строке
        end_of_slice = image_width*line_number+image_width # находим номер последнего пикселя в строке
        lines.append(list_of_pxs[start_of_slice:end_of_slice]) # добавляем в наш список строк строку с пикселями,
                                                               # начиная с первого и заканчивая последним
    return lines, image_width, image_height # Отдаем наружу список строк и размеры картинки

def current_stack_defaults(): # Функция, которая создает "набор" пикселей, подробности ниже
    return {'count':0, 'color':(-1,-1,-1)}

def stack_colors(lines, image_width):
    # Фунция, которая объединяет пиксели одного цвета в 'наборы', стоящие рядом
    # например [(255, 0, 0),(255, 0, 0),(255, 0, 0)] превратится в [{'count':3, 'color':(255, 0, 0)}]
    # "набор" -- это словарь, в котором count -- это количество рядом стоящих пикселей,
    # а color -- цвет этих пикселей
    # Набор в дальнейшем будет преобразован в SVG прямоугольник, где count -- длина прямоугольника, а color -- его цвет
    print('Stack colors')
    stack_lines = [] # заготавливаем список для строк с "наборами"
    for line_number, line in enumerate(lines): # достаем номер строки и строку из списка строк преобразованной картинки
        stack_line = [] # заготавливам список для наборов, в данной строке
        current_stack = current_stack_defaults() # создаем набор пикселей
        for index, pixel in enumerate(line): # достаем номер пикселя и пиксель, точнее цвет пикселя, из строки
            if index == 0: # если это первый пиксель в строке
                current_stack['count'] = 1 # тогда пишем, что в наборе есть как минимум один пиксель
                current_stack['color'] = pixel # c данным цветом

            elif index == image_width - 1: # если это последний пиксель в строке
                if line[index-1] == pixel: # и если послений пиксель такой же как предыдущий по цвету, тогда
                    current_stack['count'] += 1 # в наборе на один пиксель больше
                else: # если последний пиксель другой по цвету
                    stack_line.append(current_stack.copy()) # делаем копию набора и добавляем её к строке
                    current_stack['count'] = 1 # говорим, что в наборе снова один пиксель
                    current_stack['color'] = pixel # конкретного цвета
                stack_line.append(current_stack.copy()) # делаем копию набора и добавляем её к строке,
                                                        # ибо, по-любому, на последнем в строке пикселе набор должен завершиться

            elif line[index-1] == pixel: # если это не первый и не последний пиксель равный по цвету предыдущему, тогда
                current_stack['count'] += 1 # в наборе на один пиксель больше

            else: # если это не первый и не последний пиксель не равный по цвету предыдущему, тогда
                stack_line.append(current_stack.copy()) # делаем копию набора и добавляем её к строке,
                current_stack['count'] = 1 # говорим, что в наборе снова один пиксель
                current_stack['color'] = pixel # конкретного цвета

        # Проверяем, что сумма count в строке ровна количеству пикселей в строке
        pixels_sum = 0
        for stack in stack_line:
            pixels_sum += stack['count']
        # выводим отладочную информацию с результатами проверки
        print('Line {}: {}/{} pixels ({}) '.format(line_number+1, pixels_sum, image_width, pixels_sum == image_width))

        stack_lines.append(stack_line) # добавляем  строку с наборами в список строк с наборами
    return stack_lines # отдаем наружу список строк с наборами


#image_data = numpy.stack(lines)
def create_svg_circles(lines, image_width, image_height):
    # Функция, которая создает SVG с кругами вместо пикселей
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
    # Функция, которая создает SVG с прямоугольниками со скругленными углами вместо наборов пикселей
    print('Draw SVG') # отладочная информация для самоосознания
    # Создаем SVG файл, с нужным путем, с нужным размером холста
    dwg = svgwrite.Drawing(SVG_PATH, size=('{}mm'.format(image_width), '{}mm'.format(image_height)), viewBox=('0 0 {} {}'.format(image_width*d,image_height*d)))
    for line_number, stack_line in enumerate(lines): # берем номер строки и строку с наборами из списка строк
        print('Proceed line: {}/{}'.format(line_number, image_height), end='\r') # Отладочная информация: процесс заполнения холста строками
        # Один набор в строке это прямоугольник в SVG, count это его длина, color -- цвет
        rect_y = d*line_number # Начальная координата прямоугольнмка по оси Y, определяет строку
        rect_x = 0 # Начальная координата прямоугольника по оси X, смещение прямоугольника вправо

        for stack_index, stack in enumerate(stack_line): # берем номер набора и набор из строки с наборами
            if stack_index != 0: # если набор не первый, то
                rect_x += d*stack_line[stack_index-1]['count'] # увеличиваем координату X прямоугольника, тем самым смещаем прямоугольник вправо,
                                                               # на длину предыдущего
            else: # если набор первый, то
                rect_x = 0 # навсякий случай, обнуляем ему координату X

            rect_height = d # задаем высоту прямоугольника (см строку 28)
            rect_width = d*stack['count'] # задаем длину прямоугольника
            rect_color = stack['color'] # задаем цвет прямоугольника
            print('{}.{}: x={} {} {}'.format(line_number,stack_index, rect_x, rect_width, rect_color)) # отладочная
            # добавляем на холст прямоугольник, дополнительно переводя цвет в HEX: (255, 255, 255) => FFFFFF
            dwg.add(dwg.rect(insert=(rect_x,rect_y), size=(rect_width,rect_height), ry=r, style="fill:#{:02x}{:02x}{:02x}".format(rect_color[0],rect_color[1],rect_color[2])))
    dwg.save() # Сохраняем SVG файл

if __name__ == "__main__": # Начало выполнения скрипта
    lines, image_width, image_height = get_image_data(args.i) # Создаем список строк с цветами пикселей преобразованной картинки,
                                                              # размеры преобразованной на основе аргументов, переданных в скрипт
    stack_lines = stack_colors(lines, image_width) # Создаем список строк с наборами пикселей
    create_svg_rectangles(stack_lines, image_width, image_height) # Создаем SVG изображение (файл) на основе списка с наборами пикселей
    #create_svg_circles(lines, image_width, image_height)
