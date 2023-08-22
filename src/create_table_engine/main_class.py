import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import math
from io import BytesIO
from pathlib import Path

class Create_table ():
    def __init__(self, df : pd.DataFrame, width : int = 500, heigth : int = 500, font_size : int = 16) -> None:
        self.df = df
        self.w = width
        self.h = heigth
        self.font = ImageFont.truetype(font=f"""{Path(Path.cwd(),'src','create_table_engine','Roboto-regular.ttf')}""", size=font_size)
        self.img = Image.new( mode = "RGB", size = (self.w, self.h), color=(255,255,255))
        self.draw = ImageDraw.Draw(self.img)
        self.__count_columns = self.__search_cout_columns()
        self.__count_rows = self.__search_cout_rows()
        self.image = BytesIO()
        pass
    
    def create_table(self):
        width_rectangle = self.w / (self.__count_columns)
        height_rectangle = self.h / (self.__count_rows+1)

        self.draw.rectangle((0,0,self.w,self.h),outline=(0,0,0),width=2)
        x = 0
        y = 0
        for i in range(self.__count_columns):
            x+=width_rectangle
            self.draw.line(xy=((x, 0),(x, self.h)), fill='black', width=2)
        for i in range(self.__count_rows):
            y+=height_rectangle
            self.draw.line(xy=((0, y),(self.w, y)), fill='black', width=2)

        for i,val in enumerate(self.df.columns.values.tolist()):
            y = height_rectangle * float(0) + (height_rectangle/2)
            text = self.get_tex_box(str(val), width_rectangle)
            x = width_rectangle * (i) + (width_rectangle/2)
            self.draw.text(xy=(x,y),text=str(text),fill=(0,0,0), font=self.font,anchor='mm')

        for i,val in self.df.iterrows():
            # print(height_rectangle * float(i), height_rectangle, i)
            y = height_rectangle * float(int(i)+1) + (height_rectangle/2)
            for i2,val2 in enumerate(val):      
                text = self.get_tex_box(str(val2), width_rectangle)
                x = width_rectangle * (i2) + (width_rectangle/2)
                self.draw.text(xy=(x,y),text=str(text),fill=(0,0,0), font=self.font,anchor='mm')


        
        self.img.save(self.image, 'PNG')
    
    def get_table (self):
        return self.image

    def get_tex_box(self, text, width):
        text_width = self.font.getmask(text).getbbox()[2]
        i = math.ceil(text_width/width)
        if i <= 1:
            return text
        else:
            text_result = ""
            text_for = ""
            for i_t in text:
                text_for+=i_t
                if math.ceil((self.font.getmask(text_for).getbbox()[2]/width)) > 1:
                    text_result += text_for[:-3] + "\n"
                    text_for = "" + text_for[-3] + text_for[-2] + text_for[-1]
            return text_result + text_for

    def __search_cout_columns(self):
        return len(self.df.columns)


    def __search_cout_rows(self):
        return len(self.df)
