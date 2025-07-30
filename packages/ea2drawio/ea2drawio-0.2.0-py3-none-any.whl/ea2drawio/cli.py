#============================================================ (c) Kolesov A. ==
# Выгрузка диаграммы из Enterprise Architect в XML-файл формата Drawio
# Работа с Enterprise Architect через COM-объекты.
# Работа начинается с диаграммы, выделенной в дереве модели.
# Перебираем все элементы диаграммы и выводим их в XML-файл.
# Алгоритм:
# 1. Выбираем все элементы диаграммы и сохраняем их в словарь.
#     Каждый элемент словаря - это экземпляр класса DioElement
# 2. Перебираем словарь с элементами диаграммы и выводим их в XML-файл.
#------------------------------------------------------------------------------
# 09-02-2023 :Выгрузка диаграммы в XML-файл формата Drawio (BestDoctor)
# 07-08-2024 :Устранены ошибки, дополнен вывод (Лоция)
# 14-05-2025 :Формирование XML-файла в формате Drawio с использованием XML DOM
#            :Узнал, где EA хранит параметры шрифта и некоторые др.свойства
# 25-06-2025 :Environment и Node выводятся визуально как блоки. Правильно обрабатываются
#            :Event и Decision. Activity выводятся со скругленными углами.
# 26-06-2025 :Установка цвета компонентов
#            :Добавлен режим explore, когда просто выводятся свойства элементов 
# 27-06-2025 :Параметры элементов по умолчанию берутся из конфига.
#------------------------------------------------------------------------------
# TODO:
#+0. Добавить режим вызова - анализ. И просто выводить все элементы и их параметры на экран.
#+1. Цвета на даграммах в EA и Drawio отличаются.
# 2. На коннекторах имя и стереотип имеют разные координаты. 
# 3. Для маленьких текстовых меток делать отступ текста от верха метки -7.
#+4. Установка цвета линий коннекторов
#+5. Note - выводить текст. Сейчас теряется. 
# 6. Поиграть с вариантами прокладки линии.
# 7. Вывод значений тэгов.
#------------------------------------------------------------------------------
#region  import
from importlib.metadata import version
import argparse
import win32com
import win32com.client.dynamic
from xml.dom import minidom
import xml.etree.ElementTree as ET
import re
import os
import json
from pathlib import Path
from importlib import resources

#region  Вспомогательные функции

class Config:
    """
        Класс для работы с конфигурационным файлом, содержащим дефолтовые настройки элементов EA.
    """
    __slots__ = ('config')
    def __init__(self, file_name):
        self.config = self.load_config(file_name)

    def load_config(self,file_name):
        """
            Загружаем конфигурационный файл
        """
        config_path = os.path.join(os.getcwd(), file_name)
        print(f"Путь к конфигурационному файлу: {config_path}")

        if os.path.exists(config_path):
            print(f"Используется существующий {file_name}")
        else:
            print(f"Файл {file_name} не найден. Копирую из ресурсов...")
            try:
                # Используем importlib.resources для доступа к файлам внутри пакета
                with resources.as_file(resources.files("ea2drawio").joinpath(file_name)) as source_path:
                    with open(source_path, 'r', encoding='utf-8') as src_file:
                        default_config = src_file.read()
                # Сохраняем в текущую директорию
                with open(config_path, 'w', encoding='utf-8') as dst_file:
                    dst_file.write(default_config)
                print("Конфиг создан.")
            except Exception as e:
                raise RuntimeError(f"Не удалось скопировать файл конфигурации: {e}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def find(self, type, stereotype, attr, default=None):
        """
        Ищет запись в таблице по комбинации type и stereotype.
        Логика использования метода: всегда передаем type и stereotype, если они известны в месте вызова.
        А уже внутри метода разбираемся, как их использовать. 
        Т.е. инкапсулируем нюансы EA здесь.
        :param table: Словарь с данными (ключ: "type|stereotype", значение: словарь атрибутов)
        :param type: Значение type для поиска (опционально)
        :param stereotype: Значение stereotype для поиска (опционально)
        :param attr: Имя атрибута, значение которого нужно вернуть
        :param default: Значение по умолчанию, если запись или атрибут не найдены
        :return: Значение атрибута или значение по умолчанию, если ничего не найдено
        """
        # Обработка None как "None"
        type = "None" if type is None else str(type)
        stereotype = "None" if stereotype is None else str(stereotype)
        
        # Создание ключа. Тут немного учтем специфику EA
        if stereotype in ("ArchiMate_Application", "ArchiMate_Business"):   
            # Для этих стереотипов параметры едины для всех типов и они в конфиге описаны без указания типа
            type = "None"
        
        if not stereotype.startswith("ArchiMate_"): 
            # Если не Archimate, то стереотип не учитываем.
            stereotype = "None"    

        key = f"{type}|{stereotype}"
        
        # Поиск по ключу
        res = self.config.get(key)          # Ищеем список атрибутов по ключу
        if res is not None:                 # Если нашли
            return res.get(attr, default)   # Возвращаем значение атрибута
        else:
            return default

CONF = Config("eadefault.json")     # Глобальная конфигурация дефолтовых параметров в Enterprise Architect

def get_bld_value(data: str) -> str:
    """
    Извлекает значение параметра BLD из строки формата LMT=...
    Нужна для определения признака bold у надписи на коннекторе
    :param data: Входная строка с описанием параметров
    :return: Значение параметра BLD или пустая строка, если не найдено
    """
    # Ищем подстроку, начинающуюся с LMT=
    lmt_match = re.search(r'LMT=[^;]*', data)
    if not lmt_match:
        return ""

    lmt_part = lmt_match.group(0)  # Например: 'LMT=CX=50:CY=14:OX=-12:OY=-1:HDN=0:BLD=1:...'

    # Ищем BLD=цифра внутри этой подстроки
    bld_match = re.search(r'BLD=(\d+)', lmt_part)
    if bld_match:
        return bld_match.group(1)

    return ""

def get_param_value(data: str, param_name: str) -> str:
    """
    Возвращает значение параметра из строки вида 'name=value;name=value;'
    Нужна для определения признака bold у надписи на элементе
    :param data: Строка с парами name=value, разделёнными точкой с запятой
    :param param_name: Имя параметра, значение которого нужно найти
    :return: Значение параметра или пустая строка, если параметр не найден
    """
    # Убираем лишние пробелы и точку с запятой в конце
    data = data.strip().rstrip(';')
    
    # Разбиваем строку на пары "ключ=значение"
    for pair in data.split(';'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            if key.strip() == param_name:
                return value.strip()
    
    return ""  # Параметр не найден

def prettify(elem):
    """Возвращает красиво отформатированную XML-строку для элемента."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def escape_xml_chars(s):
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&quot;")
    )

# Дополняет строку слева до заданной длины заданным символом
def padl(string, length, char):
    if len(string) < length:
        return char * (length - len(string)) + string
    else:
        return string
    
# Получает цвет в Long и возвращает строку RGB
def eaColorToRgb(eaClr):
    clr = padl(str.replace(hex(eaClr),"0x",""),6,"0")   # Цвет из EA в формате long преобразуем к виду FFFFFF
    bgr = list(clr)   
    rgb = f'{bgr[4]}{bgr[5]}{bgr[2]}{bgr[3]}{bgr[0]}{bgr[1]}'  # Перевернем BGR в RGB
    return rgb

#endregion

#region Определение классов
#==============================================================================
class DioElement:
    """
        Класс для хранения параметров одного элемента диаграммы
        :param dObj:  Объект диаграммы
        :param dElem: Объект в модели
    """
    __slots__ = ('guid', 'name', 'x', 'y', 'width', 'height', 'fillcolor', 'strokeColor', 'zord', 'square',
                  'shape', 'fontsize', 'fontbold', 'formattedname')

    def __init__(self, dObj, dElem, cornerX, cornerY):
        self.guid = dObj.InstanceGUID

        # Первым делом определим type и stereotype
        type = dElem.Type
        stereotype = dElem.Stereotype

        self.fontsize = dObj.FontSize
        if self.fontsize == 0:  # Если размер шрифта не задан, то ищем его в конфиге.
            self.fontsize = CONF.find(type, stereotype, "fontsize", 8)

        # В EA элементы всегда имеют шрифт bold, даже если признак не стоит.
        # self.fontbold = True if get_param_value(dObj.Style, "bold") == "1" else False
        self.fontbold = CONF.find(type, stereotype, "fontbold", True)      

        self.name = escape_xml_chars(dElem.Notes if type == "Note" else dElem.name)

        self.x = dObj.Left + cornerX
        self.y = -dObj.Top + cornerY
        self.width = dObj.Right - dObj.Left
        self.height = -(dObj.Bottom-dObj.Top)

        if dObj.BackgroundColor != -1:   # Цвет не по умолчанию, используем его
            self.fillcolor = eaColorToRgb(dObj.BackgroundColor)
        else:               # Цвет по умолчанию. Пытаемся его определить по типу и стереотипу элемента
            self.fillcolor = CONF.find(type, stereotype, "backgroundcolor", 'F4EFDA')

        if dObj.BorderColor != -1:
            self.strokeColor = eaColorToRgb(dObj.BorderColor)
        else:
            self.strokeColor = CONF.find(type, stereotype, "bordercolor", 'EDD5CB')

        self.zord = dObj.Sequence
        self.square = self.width * self.height  # Будем использовать в качестве ZOrder

        self.shape = CONF.find(type, stereotype, "shape", "")


#==============================================================================
class Pos:
    """
        Класс для хранения координат
        :param x: координата X
        :param y: координата Y
    """
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

class DioConnector:
    """
        Класс для хранения параметров одного коннектора диаграммы
        :param dLnk:  Объект диаграммы
        :param dConn: Объект в модели
    """
    __slots__ = ('guid', 'name', 'stereotype','startX', 'startY', 'endX', 'endY', 'sourceID', 'targetID', 'positions',
                 'startArrow', 'endArrow', 'dashed', 'strokeColor', 'lineWidth','edgeStyle', 
                 'fontsize', 'fontbold', 'formattedname', 'formattedstereotype')

    def __init__(self, dLnk, dConn, cornerX, cornerY):
        self.guid = dLnk.ConnectorID

        tmpName = escape_xml_chars(dConn.name)

        self.name = ""
        if tmpName != "" and dLnk.HiddenLabels== False:
            self.name = tmpName
        
        self.fontsize = 8
        self.fontbold = True if get_bld_value(dLnk.Geometry) == "1" else False
        # print(f"Conn: {self.name} Geometry: {dLnk.Geometry}  Bold: {self.fontbold}")

        self.stereotype = ""
        if dConn.Stereotype != "" and dConn.Type == "InformationFlow"  and dLnk.HiddenLabels== False:
            self.stereotype = dConn.Stereotype

        # print(f"Connector: {tmpName} Style: {dLnk.Style} Geometry: {dLnk.Geometry}")

        self.startX = dConn.StartPointX + cornerX
        self.startY = -dConn.StartPointY + cornerY
        self.endX = dConn.EndPointX + cornerX
        self.endY = -dConn.EndPointY + cornerY

        self.sourceID = dLnk.SourceInstanceUID
        self.targetID = dLnk.TargetInstanceUID

        connType = dConn.Type   # 'InformationFlow', 'Dependency', 'Association', 'Realization'
        # geometry = dLnk.Geometry

#region Определяем вид коннектора (линия и стрелки)
        arrow = CONF.find(connType, None, "arrow", 'classic')
        fill = CONF.find(connType, None, "fill", 0)
        self.dashed = f'dashed={CONF.find(connType, None, "dashed", 1)};'

        if dConn.Direction == 'Source -> Destination':
            self.startArrow = f'startArrow=none;startFill=1;'
            self.endArrow = f'endArrow={arrow};endFill={fill};'
        elif dConn.Direction == 'Bi-Directional':
            self.startArrow = f'startArrow={arrow};startFill={fill};'
            self.endArrow = f'endArrow={arrow};endFill={fill};'
        elif dConn.Direction == 'Unspecified':
            self.startArrow = f'startArrow=none;startFill=1;'
            self.endArrow = f'endArrow=none;endFill=1;'
        elif dConn.Direction == 'Destination -> Source':
            self.startArrow = f'startArrow={arrow};startFill={fill};'
            self.endArrow = f'endArrow=none;endFill=1;'
        else:
            self.startArrow = f'startArrow=none;startFill=1;'
            self.endArrow = f'endArrow={arrow};endFill={fill};'
#endregion

        self.positions = []     # Словарь для хранения координат сегментов коннекторов
        if len(dLnk.Path) > 0:
            posArr = dLnk.Path.split(';')   # Разбивка по сегментам
            for pos in posArr:
                if(len(pos) > 0):
                    posArr2 = pos.split(':')    # Разбивка по координатам
                    self.positions.append(Pos(int(posArr2[0]) + cornerX, -int(posArr2[1]) + cornerY))

        # Цвет приходит числом, в котором порядок цветов BGR. Нужно число преобразовать в шестнадцатиричное
        # и повернуть цвета в RGB
        if dLnk.LineColor != -1:
            self.strokeColor = f'strokeColor=#{eaColorToRgb(dLnk.LineColor)};'
        else:
            self.strokeColor = f'strokeColor=#{CONF.find(connType, None, "linecolor", "000000")};'

        # Ширина линии
        self.lineWidth = f'strokeWidth={max(1,dLnk.LineWidth)};'    

        # Варант прокладки линии
        # Значения LineStyle
        # 1 = Direct
        # 2 = Auto Routing
        # 3 = Custom Line
        # 4 = Tree Vertical
        # 5 = Tree Horizontal
        # 6 = Lateral Vertical
        # 7 = Lateral Horizontal
        # 8 = Orthogonal Square
        # 9 = Orthogonal Rounded
        # Будем различать только Direct, а все остальные считаем Ortogonal Rounded
        # Также будем считать Direct, если нет сегментов линии, т.е. например, она Ortogonal Rounded, но идет по прямой.
        if dLnk.LineStyle == 1  or len(self.positions) == 0:
            self.edgeStyle = 'edgeStyle=elbowEdgeStyle;'
        else:
            self.edgeStyle = 'edgeStyle=orthogonalEdgeStyle;'

#endregion

def selectDiagramConnectors(diagram, connectors, cornerX, cornerY):
    """ 
        Выбор коннекторов текущей диаграммы и занесение в словарь
        :param diagram: текущая диаграмма в дереве модели
        :param connectors: словарь, в котором складываем коннекторы
        :param cornerX: координата X диаграммы на основной диаграмме (левый верхний угол)
        :param cornerY: координата Y диаграммы на основной диаграмме (левый верхний угол)
        :return: ничего 
    """        
    # for dLnk in item.DiagramLinks:          # Выборка всех коннекторов на диаграмме EA
    for dLnk in diagram.DiagramLinks:         # Выборка всех коннекторов на диаграмме EA
        if dLnk.IsHidden == False: 
            dConn = currentRep.GetConnectorByID(dLnk.ConnectorID)
            conn = DioConnector(dLnk, dConn, cornerX, cornerY)
            connectors[conn.guid] = conn

#==============================================================================
# Выбор элементов текущей диаграммы и занесение в словарь.
# Поддерживает вложенные диаграммы
def selectDiagramElement(diagram, elements, connectors, cornerX, cornerY):
    """
        Выбор элементов текущей диаграммы и занесение в словарь
        :param diagram: текущая диаграмма в дереве модели
        :param elements: словарь, в который складываем найденные элементы
        :param connectors: словарь, в котором складываем коннекторы
        :param cornerX: координата X диаграммы на основной диаграмме (левый верхний угол)
        :param cornerY: координата Y диаграммы на основной диаграмме (левый верхний угол)
        :return: ничего
    """
    for dObj in diagram.DiagramObjects:                     # Выборка всех элементов диаграммы
        dElem = currentRep.GetElementByID(dObj.ElementID)   # Читаем параметры элемента модели
        elem = DioElement(dObj,dElem, cornerX, cornerY)     # Создаем класс с параметрами этого элемента
        elements[elem.guid] = elem                          # И кладем его в список
        print(f'{dElem.name} - {dElem.Type}')  # Чтобы видеть что происходит
        # if dElem.Type == "ProxyConnector":  # Пропускаем, это отвод от средины стрелки 
        #     continue                        # Не, пропускать нельзя, линия к нему идет.
        if dElem.Type == "UMLDiagram":
            # Если текущий элемент - это фрейм с диаграммой, нужно найти саму диаграмму
            # и выбрать с нее все элементы
            diagID = dElem.MiscData(0)          # Тут лежит ID диаграммы, связанной с фреймом
            diag = currentRep.GetDiagramByID(diagID)
            selectDiagramElement(diag, elements, connectors, dObj.Left, -dObj.Top)

    selectDiagramConnectors(diagram, connectors, cornerX, cornerY ) # Выбор коннекторов

#==============================================================================
# Формирование описания текущей диаграммы в формате drawio
#------------------------------------------------------------------------------
def drawioGenerate(diagram):
    fname = f'{diagram.Name}.drawio'
    mxfile = ET.Element('mxfile', host='Electron', modified='2023-02-09T11:49:41.294Z',
                        agent='draw.io', etag='AvFAkIZB1bcPTriSJ9FB', version='20.8.16', type='device')

    diagram_element = ET.SubElement(mxfile, 'diagram', name='Page-1', id=diagram.DiagramGUID)

    graph_model = ET.SubElement(diagram_element, 'mxGraphModel',
                                dx="1290", dy="638", grid="1", gridSize="10",
                                guides="1", tooltips="1", connect="1", arrows="1",
                                fold="1", page="1", pageScale="1",
                                pageWidth=str(diagram.cx), pageHeight=str(diagram.cy),
                                math="0", shadow="0")

    root = ET.SubElement(graph_model, 'root')
    ET.SubElement(root, 'mxCell', id="0")
    ET.SubElement(root, 'mxCell', {'id':'1', 'parent':'0'}) 

    elements = {}
    connectors = {}
    selectDiagramElement(diagram, elements, connectors, 0, 0)

    sorted_elements = dict(sorted(elements.items(), key=lambda item: -item[1].width * item[1].height))

    # Вывод всех элементов
    for key in sorted_elements:
        el = sorted_elements[key]
        bldBgn = "<b>" if el.fontbold else ""
        bldEnd = "</b>" if el.fontbold else "" 
        cell = ET.SubElement(
            root, 'mxCell',
            id=el.guid,
            value= f'<font style="font-size: {el.fontsize}px;">{bldBgn}{el.name}{bldEnd} </font>',
            style=f"{el.shape}whiteSpace=wrap;html=1;verticalAlign=top;" +
                  f"fillColor=#{el.fillcolor};strokeColor=#{el.strokeColor};",
            parent="1",  # type: ignore
            vertex="1"
        ) 
        geom = ET.SubElement(cell, 'mxGeometry', x=str(el.x), y=str(el.y),
                             width=str(el.width), height=str(el.height),
                             attrib={'as': 'geometry'})
    
    # Вывод всех коннекторов
    for key in connectors:
        conn = connectors[key]
        bldBgn = "<b>" if conn.fontbold else ""
        bldEnd = "</b>" if conn.fontbold else "" 

        edge = ET.SubElement(
            root, 'mxCell',
            id=str(conn.guid),
            # value=conn.name + conn.stereotype,
            value= f'<font style="font-size: {conn.fontsize}px;">{bldBgn}{conn.name + conn.stereotype}{bldEnd} </font>',
            style=f"{conn.endArrow}html=1;rounded=1;{conn.dashed}{conn.edgeStyle}" +
                  f"{conn.startArrow}{conn.strokeColor}{conn.lineWidth}",
            edge="1",
            parent="1", # type: ignore
            source=conn.sourceID,
            target=conn.targetID
        )

        geom = ET.SubElement(edge, 'mxGeometry', width="0", relative="1",
                             attrib={'as': 'geometry'})
        ET.SubElement(geom, 'mxPoint', x=str(conn.startX), y=str(conn.startY),
                      attrib={'as': 'sourcePoint'})
        ET.SubElement(geom, 'mxPoint', x=str(conn.endX), y=str(conn.endY),
                      attrib={'as': 'targetPoint'})

        if len(conn.positions) > 0:
            points_array = ET.SubElement(geom, 'Array', attrib={'as': 'points'})
            for pos in conn.positions:
                ET.SubElement(points_array, 'mxPoint', x=str(pos.x), y=str(pos.y))

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(prettify(mxfile))
    print(f"Диаграмма успешно экспортирована в {fname}")

#endregion

def explore(item):
    # Тут просто для изучения выводим все элементы диаграммы и коннекторы с их свойствами списком
    print(f'Diagram: {item.name} Тип: {item.Type} Ширина: {item.cx} Высота: {item.cy}')
    for dObj in item.DiagramObjects:        # Выборка всех элементов диаграммы
        dElem = currentRep.GetElementByID(dObj.ElementID)
        print(f'Элемент:{dElem.Name} Тип:{dElem.Type} Стереотип:{dElem.Stereotype} Notes:{dElem.Notes}')
        print(f'        GUID:{dObj.InstanceGUID} Left:{dObj.Left} Right:{dObj.Right} Top:{dObj.Top} Bottom:{dObj.Bottom} BackgroundColor:{dObj.BackgroundColor} Z:{dObj.Sequence} FontSize:{dObj.FontSize} TextAlign:{dObj.TextAlign} BorderColor:{dObj.BorderColor}')

    print('=' * 20)
    for dLnk in item.DiagramLinks:          # Выборка всех коннекторов на диаграмме
        dConn = currentRep.GetConnectorByID(dLnk.ConnectorID)
        print(f'Коннектор: ID:{dLnk.ConnectorID}  Название:{dConn.name} Тип:{dConn.Type} Стереотип:{dConn.Stereotype} Source:{dConn.ClientID} Target:{dConn.SupplierID}')
        print(f'           Path:{dLnk.Path} SourceID:{dLnk.SourceInstanceUID} TargetID:{dLnk.TargetInstanceUID} StartPointX:{dConn.StartPointX} StartPointY:{dConn.StartPointY} EndPointX:{dConn.EndPointX} EndPointY:{dConn.EndPointY}')
        print(f'           Direction:{dConn.Direction} LineColor:{dLnk.LineColor} lineWidth:{dLnk.LineWidth}')


#region Main ####################
def main():
    # print(version('ea2drawio'))  # выведем версию модуля

    parser = argparse.ArgumentParser(description="Convert EA diagrams to draw.io format")
    parser.add_argument("-e", "--explore", required=False, action="store_true", default=False, help="Launch in research mode")
    args = parser.parse_args()

    try:
        print('Connect to the EA')
        eapp = win32com.client.dynamic.Dispatch("EA.App")
        print(f'EA: {eapp}')
    except:
        print('Please Open Enterprise Architect')

    try:
        print('Connect to the Repository')
        global currentRep
        currentRep = eapp.Repository
        print(f'Repository: {currentRep}')
    except:
        print('Please Open a Model in Enterprise Architect')

    dicItemName = {
        2: 'Repository',
        4: 'Element',
        5: 'Package',
        7: 'Connector',
        8: 'Diagram',
        23: 'Attribute'
    }

    try:
        itemType = currentRep.GetContextItemType()
        print(f'Selected Item Type: {dicItemName.get(itemType)}')
    except:
        print('Nothing selected')

    print('=' * 40)
    itemType, item = currentRep.GetTreeSelectedItem()
    if itemType == 8:               # Diagram
        if args.explore:
            explore(item)           # Просто выводим список элементов диаграммы и их свойства
        else:   
            drawioGenerate(item)    # Генерируем диаграмму

#endregion


if __name__ == "__main__":
   print(version('ea2drawio'))  # выведем версию модуля
   main()
 
