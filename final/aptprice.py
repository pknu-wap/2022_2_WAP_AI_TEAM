import sys
import os
import pickle
import pandas as pd
import numpy as np
import joblib
# conda install joblib 또한, 필요합니다.
from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import lightgbm as lgb
# conda install -c "conda-forge/label/cf201901" lightgbm
# lightgbm이 최신 버전일경우 에러가 발생할 가능성이 있습니다.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import QUrl
#pip install pyqt5
#pip install pyqtwebengine

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
# pyinstaller 파일 가져오기.

main_ui = resource_path('main (3).ui')
form_class = uic.loadUiType(main_ui)[0]  # ui 가져오기

#filename1 = resource_path('pure_apt.csv')
modelfile = resource_path('lgb.pkl') 
dong_listfile = resource_path('dong_list.pkl')
gu_listfile = resource_path('gu_list.pkl')
gu_dongfile = resource_path('gu_dong.pkl')

with open(dong_listfile, "rb") as f:
    dong_list = pickle.load(f)

with open(gu_listfile, "rb") as f:
    gu_list = pickle.load(f)

with open(gu_dongfile, 'rb') as f:
    gu_dong_list = pickle.load(f)

x_day = 4805  # 2022년 12월 1일
# 처음 20100101 -> 0
# 마지막 20221118 -> 4792
i_area, i_floor, i_aptage = 0, 0, 0
i_gu, i_dong = '', ''

class WindowClass(QWidget, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        for i in gu_dong_list:
            self.comboBox.addItem(i)
        self.comboBox.activated[str].connect(
            lambda: self.selectedComboItem(self.comboBox))
        self.comboBox_2.addItem('구를 먼저 선택해주세요!')

        area = self.lineEdit_area
        area.textChanged[str].connect(self.onChanged_area)

        floor = self.lineEdit_floor
        floor.textChanged[str].connect(self.onChanged_floor)

        aptage = self.lineEdit_aptage
        aptage.textChanged[str].connect(self.onChanged_aptage)

        self.spinBox_1.valueChanged.connect(self.spinBoxFunction_1)

        lbl = self.label_10
        lbl.setText("얼마일까나??")

        self.btn_1.clicked.connect(self.button1Function)
        self.btn_2.clicked.connect(self.button2Function)
        self.spinBox_2.valueChanged.connect(self.spinBoxFunction_2)

        self.show()


    def selectedComboItem(self, text):
        global i_gu, i_dong
        i_gu = self.comboBox.currentText()
        for key in gu_dong_list.keys():
            if text.currentText() == key:
                self.comboBox_2.clear()
                for i in gu_dong_list[key]:
                    self.comboBox_2.addItem(i)
        i_dong = self.comboBox_2.currentText()

    def onChanged_area(self, text):
        global i_area
        i_area = text

    def onChanged_floor(self, text):
        global i_floor
        i_floor = text

    def onChanged_aptage(self, text):
        global i_aptage
        i_aptage = text

    def spinBoxFunction_1(self): 
        values = self.spinBox_1.value()
        global x_day
        x_day = 4805
        x_day += values * 30

    # 예측 버튼이 눌리면 작동할 함수
    def button1Function(self):
        for dong in dong_list:
            if dong[1] == i_dong:
                x_dong = dong[0]

        for gu in gu_list:
            if gu[1] == i_gu:
                x_gu = gu[0]

        x_floor = int(i_floor) + 2
        x_apt_year = int(i_aptage)

        x_area_pyeong = float(i_area)  # 평
        x_area_m2 = x_area_pyeong * 3.3058  # m^2
        x = {"trade_day": [x_day], "dong": [x_dong], "floor": [x_floor], "gu": [
            x_gu], "apt_year": [x_apt_year], 'area_m2': [x_area_m2]}
        y = pd.DataFrame(x)

        x_area = np.log1p(y['area_m2'])        
        y['log_area'] = x_area
        y.drop('area_m2', axis=1, inplace=True)

        final_lgb_model = joblib.load(modelfile)
        final_lgb_pred = final_lgb_model.predict(y)
        final_pred_sub = int(np.expm1(final_lgb_pred))

        if final_pred_sub > 100000:
            eok = str(final_pred_sub)[0:2]
            man = str(final_pred_sub)[2:]
            txt = f'{eok}억{man}만'  
            self.label_10.setText(txt)

        elif final_pred_sub > 10000:
            eok = str(final_pred_sub)[0]
            man = str(final_pred_sub)[1:]
            txt = f'{eok}억{man}만'
            self.label_10.setText(txt)
        else :
            txt = f'{str(final_pred_sub)}만'
            self.label_10.setText(txt)
    
 # spinbox 함수

    def spinBoxFunction_2(self): 
        values = self.spinBox_2.value()
        c = resource_path(f'AptMap/count{values}.html')
        p = resource_path(f'AptMap/price{values}.html')

        url_c = QUrl.fromLocalFile(c)
        url_p = QUrl.fromLocalFile(p)

        self.webEngineView_1.load(url_c)
        self.webEngineView_2.load(url_p)
    
    def button2Function(self):
        for dong in dong_list:
            if dong[1] == i_dong:
                x_dong = dong[0]

        for gu in gu_list:
            if gu[1] == i_gu:
                x_gu = gu[0]

        x_floor = int(i_floor) + 2
        x_apt_year = int(i_aptage)

        x_area_pyeong = float(i_area)  # 평
        x_area_m2 = x_area_pyeong * 3.3058  # m^2
        x = {"trade_day": [x_day], "dong": [x_dong], "floor": [x_floor], "gu": [
            x_gu], "apt_year": [x_apt_year], 'area_m2': [x_area_m2]}
        y = pd.DataFrame(x)

        x_area = np.log1p(y['area_m2'])        
        y['log_area'] = x_area
        y.drop('area_m2', axis=1, inplace=True)

        want_data_x = pd.DataFrame()
        
        for i in range(1,4800):
            want_data_x = want_data_x.append(pd.DataFrame([[i]],columns=['trade_day']), ignore_index=True)
        want_data_x["dong"] = x_dong
        want_data_x["floor"] = x_floor
        want_data_x["gu"] = x_gu
        want_data_x["apt_Year"] = x_apt_year
        want_data_x["log_area"] = x_area
        want_data_x = want_data_x.fillna(method='ffill')

        final_lgb_model = joblib.load(modelfile)
        final_lgb_pred = final_lgb_model.predict(want_data_x)
        final = np.expm1(final_lgb_pred)

        canvas = FigureCanvas(Figure(figsize=(15, 8)))
        vbox = QVBoxLayout(self.tab_3)
        vbox.addWidget(canvas)

        self.ax = canvas.figure.subplots()
        self.ax.plot([x for x in range(1,4799)], final[1:], label="prediction")
        self.ax.set_xlabel("2010-01-01 ~ 2022-12-01")
        self.ax.set_ylabel("price")

if __name__ == "__main__":
    app = QApplication(sys.argv)  # QApplication : 프로그램을 실행시켜주는 클래스
    myWindow = WindowClass()  # WindowClass의 인스턴스 생성
    myWindow.show()  # 프로그램 화면을 보여주는 코드
    app.exec_()  # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드


