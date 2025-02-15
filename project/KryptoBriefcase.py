from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QPainter
from PyQt6.QtSvg import QSvgRenderer
import pyqtgraph as pg

import requests
import bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import ccxt
import webbrowser

from threading import Thread
from threading import Timer
from time import sleep

import sys
import winreg
from elevate import elevate
from datetime import datetime

import gc
import numpy as np
from source.model_data.model import KryptoModelWithAttention, cyclic_encode
from torch import load, device, float32, tensor, exp, cat



class ValuteCard(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.isPressed = False
        self.setFixedSize(QtCore.QSize(250, 61))
        self.setParent(parent)
        self.parent = parent
        self.valute = None
        self.name = None
        self.img_url = None
        self.place = None
        self.amount = None
        self.change = None
        self.capitalization = None
        self.cap_ind = None
        self.value = None
        self.V_ind = None
        self.offer = None
        self.offer_ind = None

        self.setVisible(False)
        self.animLabel = QtWidgets.QLabel(parent = self)
        self.animLabel.setGeometry(QtCore.QRect(self.pos().x(), self.pos().y(), self.size().width(), self.height()))
        self.animLabel.setStyleSheet('background-color: rgb(215, 215, 215)')
        self.animEffect = QtWidgets.QGraphicsOpacityEffect(self)
        self.animEffect.setOpacity(0)
        self.animEffect2 = QtWidgets.QGraphicsOpacityEffect(self)
        self.animEffect2.setOpacity(0)
        self.animEffect3 = QtWidgets.QGraphicsOpacityEffect(self)
        self.animEffect3.setOpacity(0)
        self.animLabel.setGraphicsEffect(self.animEffect)
        font3 = QtGui.QFont('Builder Sans', 9)
        self.cap_holder = QtWidgets.QLabel(parent = self)
        self.cap_holder.setStyleSheet('color: rgb(10, 10, 255)')
        self.cap_holder.setFont(font3)
        self.cap_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.font1 = QtGui.QFont('Builder Sans', 15)
        self.font1.setBold(True)
        self.sym_BG = QtWidgets.QLabel(self)
        self.sym_BG.setPixmap(QtGui.QPixmap('source/GUI/sym_BG.png'))

        self.sym_BG_upper = QtWidgets.QLabel(self)
        self.sym_BG_upper.setPixmap(QtGui.QPixmap('source/GUI/sym_BG_blue.png'))
        self.sym_BG_upper.setGraphicsEffect(self.animEffect3)

        self.sym_holder = QtWidgets.QLabel(parent = self)
        self.sym_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.sym_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font2 = QtGui.QFont('Builder Sans', 9)
        self.nameHolder = QtWidgets.QLabel(parent = self)
        self.nameHolder.setFont(font2)
        self.nameHolder.setStyleSheet('color: rgb(0, 0, 0)')
        self.img = QtWidgets.QLabel(parent = self)
        self.bottom_line = QtWidgets.QLabel(parent = self)
        self.bottom_line.setPixmap(QtGui.QPixmap('source/GUI/bot_line.png'))
        self.place_num_holder = QtWidgets.QLabel(parent = self)
        self.place_num_holder.setFont(font2)
        self.place_num_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.place_num_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.amount_holder = QtWidgets.QLabel(parent = self)
        self.amount_holder.setFont(font3)
        self.amount_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.amount_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.change_holder = QtWidgets.QLabel(parent = self)
        font4 = QtGui.QFont('Builder Sans', 8)
        self.change_holder.setFont(font4)
        self.change_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.img_size = (45, 45)
        self.coin_frame = QtWidgets.QLabel(parent = self)
        self.coin_frame.setPixmap(QtGui.QPixmap('source/GUI/coin_frame.png'))
        self.upper_frame = QtWidgets.QLabel(parent = self)
        self.upper_frame.setPixmap(QtGui.QPixmap('source/GUI/coin_upper_frame.png'))
        self.upper_frame.setGraphicsEffect(self.animEffect2)

    def set_image(self):
        data = requests.get(self.img_url).content
        with open('img.svg','r+') as img:
            img.truncate(0)

        with open('img.svg','wb') as img:
            img.write(data)
            img.close()

        pixmap = QtGui.QPixmap(QtCore.QSize(self.img_size[0], self.img_size[1]))
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        MainWindow.last_pen = painter
        svgRenderer = QSvgRenderer("img.svg")
        svgRenderer.render(painter)
        painter.end()
        del painter

        self.img.setPixmap(pixmap)

    def optimize_card(self):
        self.sym_holder.setGeometry(QtCore.QRect(self.pos().x() + self.img_size[0] + 10, self.pos().y() + 20, 60, 20))
        self.nameHolder.setGeometry(QtCore.QRect(self.sym_holder.pos().x() + 4, self.size().height() - 20, 168, 20))
        self.bottom_line.setGeometry(QtCore.QRect(self.pos().x() + 2, self.pos().y() + self.size().height() - 3, 250, 3))
        self.img.setGeometry(QtCore.QRect(self.pos().x() + 5, self.pos().y() + 8, self.img_size[0], self.img_size[1]))
        if self.valute != 'USD':
            self.coin_frame.setGeometry(QtCore.QRect(self.img.pos().x(), self.img.pos().y(), self.img_size[0], self.img_size[1]))
            self.upper_frame.setGeometry(QtCore.QRect(self.img.pos().x(), self.img.pos().y(), self.img_size[0], self.img_size[1]))
        self.sym_BG.setGeometry(QtCore.QRect(self.pos().x() + self.img_size[0] + 13, self.pos().y() + 18, 54, 24))
        self.sym_BG_upper.setGeometry(QtCore.QRect(self.pos().x() + self.img_size[0] + 13, self.pos().y() + 18, 54, 24))
        self.place_num_holder.setGeometry(QtCore.QRect(self.width() - 23, self.pos().y() + self.size().height() - 17, 20, 20))
        self.amount_holder.setGeometry(QtCore.QRect(self.pos().x() + self.img_size[0] + 76, self.sym_holder.pos().y() - 3, 130, 25))
        self.change_holder.setGeometry(QtCore.QRect(self.pos().x() + self.img_size[0] + 74, self.sym_holder.pos().y() + 10, 100, 25))
        self.cap_holder.setGeometry(QtCore.QRect(self.pos().x() + self.img_size[0] + 14, 1, 190, 25))

    def mousePressEvent(self, event):
        if self.parent.last != self and self.parent.last != None:
            if (self.name == 'Briefcase' and self.parent.isParsed == False) == False:
                if self.name != 'Briefcase':
                    Thread(target = self.parent.interface.setup, name = 'interface_setup', args = (self.valute, self.name, self.img_url, self.place, self.amount, self.change, self.capitalization, self.value, self.offer, self.cap_ind, self.V_ind, self.offer_ind)).start()
                else:
                    Thread(target = self.parent.interface.setup, name = 'interface_setup', args = (self.valute, self.name, 'source/GUI/big_case.png', self.place, self.amount, self.change, self.capitalization, self.value, self.offer, self.cap_ind, self.V_ind, self.offer_ind)).start()

                Thread(target = self.startCardAnim, name = 'card_animation').start()
                if (self.parent.last.name == 'Briefcase' and self.parent.isParsed == False) == False:
                    Thread(target = self.parent.last.startHolderAnim_rev, name = 'card_animation_rev').start()


                if (self.parent.last.name == 'Briefcase' and self.parent.isParsed == False) == False:
                    self.parent.last.isPressed = False
                    self.parent.last.animLabel.setVisible(False)
                    Thread(target = MainWindow.last.startHolderAnim_rev, name = 'card_animation_rev').start()
                    if self.parent.last.name != 'Briefcase':
                        self.parent.last.upper_frame.setVisible(False)

                self.parent.last = self
                self.isPressed = True

        elif self.parent.last == None:
            if self.parent.isParsed != False:
                if self.name != 'Briefcase':
                    Thread(target = self.parent.interface.setup, name = 'interface_setup', args = (self.valute, self.name, self.img_url, self.place, self.amount, self.change, self.capitalization, self.value, self.offer, self.cap_ind, self.V_ind, self.offer_ind)).start()
                else:
                    Thread(target = self.parent.interface.setup, name = 'interface_setup', args = (self.valute, self.name, 'source/GUI/big_case.png', self.place, self.amount, self.change, self.capitalization, self.value, self.offer, self.cap_ind, self.V_ind, self.offer_ind)).start()
                Thread(target = self.startCardAnim, name = 'card_animation').start()
                self.parent.last = self
                self.isPressed = True
            else:
                if self.name != 'Briefcase':
                    valute = self.valute
                    name = self.name
                    img_url = self.img_url
                    place = self.place
                    amount = self.amount
                    change = self.change
                    cap = self.capitalization
                    V = self.value
                    offer = self.offer

                    if self.name != 'Briefcase':
                        Thread(target = self.parent.interface.setup, name = 'card_animation', args = (valute, name, img_url, place, amount, change, cap, V, offer, self.cap_ind, self.V_ind, self.offer_ind)).start()
                    else:
                        Thread(target = self.parent.interface.setup, name = 'card_animation', args = (valute, name, 'source/GUI/big_case.png', place, amount, change, cap, V, offer, self.cap_ind, self.V_ind, self.offer_ind)).start()
                    Thread(target = self.startCardAnim, name = 'card_animation').start()
                    self.parent.last = self
                    self.isPressed = True

    def startCardAnim(self):
        self.animLabel.setVisible(True)
        if self.name != 'Briefcase':
            self.upper_frame.setVisible(True)
        for i in range(10, 51, 10):
            self.animEffect.setOpacity(i / 100)
            self.animLabel.setGraphicsEffect(self.animEffect)
            if self.name != 'Briefcase':
                self.animEffect2.setOpacity(i / 100)
                self.upper_frame.setGraphicsEffect(self.animEffect2)
            self.animEffect3.setOpacity(i / 100)
            self.sym_BG_upper.setGraphicsEffect(self.animEffect3)
            sleep(0.05)

    def startHolderAnim_rev(self):
            for i in range(50, -10, -10):
                self.animEffect3.setOpacity(i / 100)
                self.sym_BG_upper.setGraphicsEffect(self.animEffect3)
                sleep(0.05)

    def enterEvent(self, event):
        if (self.valute == 'USD' and self.parent.isParsed == False) == False:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))

    def set_new_params(self, valute: str, name: str, img: str, place: int, amount: int, change: str, cap: str, V: str, offer: str, cap_ind: float, V_ind: float, offer_ind: float):
        self.valute = valute
        self.name = name
        if img != '':
            self.img_url = img
        self.place = place
        self.amount = amount
        self.change = change
        self.capitalization = cap
        self.value = V
        self.offer = offer
        self.cap_ind = cap_ind
        self.V_ind = V_ind
        self.offer_ind = offer_ind

        if self.valute == 'USD':
            self.coin_frame.close()
            self.upper_frame.close()
            self.animLabel.setStyleSheet('background-color: transparent')
            self.animLabel.setPixmap(QtGui.QPixmap('source/GUI/BK_anim.png'))
        else:
            self.animLabel.setStyleSheet('background-color: rgb(215, 215, 215)')

        if len(self.valute) <= 3:
            self.font1.setPointSize(15)
        elif len(self.valute) == 4:
            self.font1.setPointSize(12)
        elif len(self.valute) == 5:
            self.font1.setPointSize(10)
        elif len(self.valute) == 6:
            self.font1.setPointSize(8)
        else:
            self.font1.setPointSize(7)

        self.sym_holder.setFont(self.font1)

        if self.place != 0:
            self.place_num_holder.setText(str(self.place))
        self.sym_holder.setText(str(self.valute))
        self.nameHolder.setText(str(self.name))
        self.amount_holder.setText(str(self.amount) + ' USD')
        self.change_holder.setText(self.change)
        self.cap_holder.setText(self.capitalization)

        if '+' in self.change:
            self.change_holder.setStyleSheet('color: rgb(24, 185, 55)')
        else:
            self.change_holder.setStyleSheet('color: rgb(185, 24, 24)')

        self.optimize_card()

    def update(self, valute: str, name: str, place: int, amount: int, change: str, cap: str, V: str, offer: str, cap_ind: float, V_ind: float, offer_ind: float):
        self.valute = valute
        self.name = name
        self.place = place
        self.amount = amount
        self.change = change
        self.capitalization = cap
        self.value = V
        self.offer = offer
        self.cap_ind = cap_ind
        self.V_ind = V_ind
        self.offer_ind = offer_ind

        if len(self.valute) <= 3:
            self.font1.setPointSize(15)
        elif len(self.valute) == 4:
            self.font1.setPointSize(12)
        elif len(self.valute) == 5:
            self.font1.setPointSize(11)
        elif len(self.valute) == 6:
            self.font1.setPointSize(9)
        else:
            self.font1.setPointSize(8)

        self.sym_holder.setFont(self.font1)

        if self.place != 0:
            self.place_num_holder.setText(str(self.place))
        self.sym_holder.setText(str(self.valute))
        self.nameHolder.setText(str(self.name))
        self.amount_holder.setText(str(self.amount) + ' USD')
        self.change_holder.setText(self.change)
        self.cap_holder.setText(self.capitalization)

        if '+' in self.change:
            self.change_holder.setStyleSheet('color: rgb(10, 255, 10)')
        else:
            self.change_holder.setStyleSheet('color: rgb(255, 10, 10)')

    def place_img(self):
        if self.img_url != None:
            if 'https://' in self.img_url:
                try:
                    self.set_image()
                except:
                    try:
                        self.set_image()
                    except:
                        pass
            else:
                self.img.setPixmap(QtGui.QPixmap(self.img_url))

    def wheelEvent(self, event):
        if self.valute != 'USD':
            delta = event.angleDelta().y()
            if delta > 0 and MainWindow.scroll_value > 0:
                MainWindow.scroll_value = MainWindow.scroll_value - 1
                MainWindow.refresh()
                MainWindow.scrler.setValue(MainWindow.scroll_value)
            elif delta <= 0 and MainWindow.scroll_value <= (MainWindow.max - MainWindow.height() // 61):
                MainWindow.scroll_value = MainWindow.scroll_value + 1
                MainWindow.refresh()
                MainWindow.scrler.setValue(MainWindow.scroll_value)
        else:
            return



class ActionBtn(QtWidgets.QPushButton):
    def __init__(self, parent, action, win):
        super().__init__()
        self.setParent(parent)
        self.action = action
        self.win = win
        self.isMax = False
        self.size = None
        self.position = None

    def mousePressEvent(self, event):
        if self.action == 'cls':
            self.win.close()
        elif self.action == 'rlup':
            self.win.showMinimized()
        elif self.action == 'FS':
            if self.isMax == False:
                self.win.case.animLabel.setPixmap(QtGui.QPixmap('source/GUI/full_BK_anim.png'))
                self.position = MainWindow.pos()
                self.win.cls_anim.stop()
                self.win.FS_anim.stop()
                self.win.rlup_anim.stop()

                self.size = self.win.size()
                self.win.showFullScreen()
                self.win.maximise()
                self.isMax = True
                MainWindow.refresh()
                self.win.raise_()

                Thread(target = self.update_res, name = 'resolution_update').start()
            else:
                self.win.cls_anim.stop()
                self.win.FS_anim.stop()
                self.win.rlup_anim.stop()

                self.win.case.animLabel.setPixmap(QtGui.QPixmap('source/GUI/BK_anim.png'))
                self.win.un_maximize()
                self.win.showNormal()
                self.win.setGeometry(QtCore.QRect(self.position.x(), self.position.y(), self.size.width(), self.size.height()))
                self.isMax = False
                MainWindow.refresh()
                self.win.raise_()
                Thread(target = self.update_res, name = 'resolution_update').start()

                
    def update_res(self):
        with open('source/params/resolution.txt', 'r+') as resol_file:
            resol_file.truncate(0)
        with open('source/params/resolution.txt', 'w') as resol_file:
            resol_file.write(f'{self.win.width()}x{self.win.height()}')

    def enterEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        if self.action == 'cls':
            self.win.cls_anim.start()
        elif self.action == 'rlup':
            self.win.rlup_anim.start()
        elif self.action == 'FS':
            self.win.FS_anim.start()



class Roundler(QtWidgets.QPushButton):
    def __init__(self, parent, action: str, x_arg: int, win):
        super().__init__()
        self.win = win
        self.started = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tech)
        self.setParent(parent)
        self.x_arg = x_arg
        self.action = action

        self.x1 = self.pos().x()
        self.y1 = self.pos().y()

        self.x2 = self.pos().x()
        self.y2 = self.pos().y()

        self.setIconSize(QtCore.QSize(24, 24))
        self.setStyleSheet('background-color: transparent')
        if action == 'move':
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap('source/GUI/roundler_move.png'))
            self.setIcon(icon)
        elif action == 'resize':
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap('source/GUI/roundler_resize.png'))
            self.setIcon(icon)

    def mousePressEvent(self, event):
        self.x = event.pos().x()
        self.y = event.pos().y()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        self.setGeometry(QtCore.QRect((self.pos().x() + event.pos().x()) - self.x, (self.pos().y() + event.pos().y() - self.y), 24, 24))
        self.x2 = self.pos().x()
        self.y2 = self.pos().y()
        if ((self.win.width() - self.x2 - self.x_arg - self.win.place_for_border)**2 + (self.win.height() - self.y2 - 43 - self.win.place_for_border)**2) >= 37:
            self.setGeometry(QtCore.QRect(self.pos().x() - (self.x2 - self.x1), self.pos().y() - (self.y2 - self.y1), 24, 24))
            if self.action == 'move':
                self.win.move(self.win.pos().x() - self.x + event.pos().x(), self.win.pos().y() - self.y + event.pos().y())
            elif self.action == 'resize':
                self.win.resize(self.win.width() + event.pos().x() - self.x, self.win.height() + event.pos().y() - self.y)
                MainWindow.refresh()
                if self.started == False:
                    self.started = True
                    self.timer.start(1700)

        self.x1 = self.pos().x()
        self.y1 = self.pos().y()

    def tech(self):
        self.timer.stop()
        self.started = False
        MainWindow.refresh()

    def mouseReleaseEvent(self, event):
        if self.win == MainWindow:
            self.win.optimize_win()
        else:
            self.win.optimize_dialog()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))

    def enterEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))

    def leaveEvent(self, event):
        if self.action == 'resize':
            Thread(target = self.update_res, name = 'resolution_update').start()
            
    def update_res(self):
        with open('source/params/resolution.txt', 'r+') as resol_file:
            resol_file.truncate(0)
        with open('source/params/resolution.txt', 'w') as resol_file:
            resol_file.write(f'{self.win.width()}x{self.win.height()}')



class RefreshAnimDisplay(QtWidgets.QLabel):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)

    def enterEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ForbiddenCursor))




class refreshBtn(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setFixedSize(QtCore.QSize(15, 15))
        self.setStyleSheet('background-color: transparent;')
        self.setIconSize(QtCore.QSize(self.size().width(), self.size().height()))
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap('source/GUI/refresh_btn_untarget.png'))
        self.setIcon(self.icon)

    def enterEvent(self, event):
        if self.parent().isParsed == True:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.icon.addPixmap(QtGui.QPixmap('source/GUI/refresh_btn_target.png'))
            self.setIcon(self.icon)
        else:
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ForbiddenCursor))

    def leaveEvent(self, event):
        self.icon.addPixmap(QtGui.QPixmap('source/GUI/refresh_btn_untarget.png'))
        self.setIcon(self.icon)

    def mousePressEvent(self, event):
        if MainWindow.isStopped == False:
            MainWindow.isStopped = True
        self.parent().isParsed = True
        if self.parent().last != None:
            if self.parent().last.name == 'Briefcase':
                self.parent().last.isPressed = False
                Thread(target = MainWindow.last.startHolderAnim_rev, name = 'card_animation').start()
                if self.parent().last.valute != 'USD':
                    self.parent().last.upper_frame.setVisible(False)
                self.parent().last.animLabel.setVisible(False)
        self.parent().refresh_anim_holder.setVisible(True)
        self.parent().refresh_anim.start()
        self.parent().isParsed = False
        Thread(name = 'reload_cars', target = MainWindow.reload_cards).start()



class ModeHolder(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        
    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.parent().mode_holder_BG.setPixmap(QtGui.QPixmap('source/GUI/sym_BG_mini_pressed.png'))
        
    def leaveEvent(self, event):
        self.parent().mode_holder_BG.setPixmap(QtGui.QPixmap('source/GUI/sym_BG_mini.png'))
        
        

class SearchBtn(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setIconSize(QtCore.QSize(20, 20))
        self.setStyleSheet('background-color: transparent')
        self.ic = QtGui.QIcon()
        self.ic.addPixmap(QtGui.QPixmap('source/GUI/search_btn_untargeted.png'))
        self.setIcon(self.ic)
        
    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.ic.addPixmap(QtGui.QPixmap('source/GUI/search_btn_targeted.png'))
        self.setIcon(self.ic)
        
    def leaveEvent(self, event):
        self.ic.addPixmap(QtGui.QPixmap('source/GUI/search_btn_untargeted.png'))
        self.setIcon(self.ic)
        
        
        
class SearchLine(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.mods = ['SYM', 'NAME', '$']
        self.timestamps = None
        self.ind = 0
        self.setParent(parent)
        self.setFixedSize(QtCore.QSize(250, 40))
        self.BG = QtWidgets.QLabel(self)
        self.BG.setGeometry(QtCore.QRect(0, 0, 250, 40))
        self.BG.setPixmap(QtGui.QPixmap('source/GUI/search.png'))
        
        font1 = QtGui.QFont('Builder Sans', 10)
        self.line = QtWidgets.QLineEdit(self)
        self.line.setGeometry(QtCore.QRect(60, 4, 160, 21))
        self.line.setStyleSheet('color: rgb(70, 70, 70);\nbackground-color: transparent;')
        self.line.setFont(font1)
        self.line.setPlaceholderText('Type here...')
        
        self.search_btn = SearchBtn(self)
        self.search_btn.setGeometry(QtCore.QRect(212, 0, 28, 28))

        self.search_btn.clicked.connect(self.search)
        
        font2 = QtGui.QFont('Builder Sans', 11)
        font2.setBold(True)
        self.mode_holder_BG = QtWidgets.QLabel(self)
        self.mode_holder_BG.setPixmap(QtGui.QPixmap('source/GUI/sym_BG_mini.png'))
        self.mode_holder_BG.setGeometry(QtCore.QRect(9, 4, 47, 21))
        self.mode_holder = ModeHolder(self)
        self.mode_holder.setGeometry(QtCore.QRect(9, 4, 47, 21))
        self.mode_holder.setStyleSheet('color: black;\nbackground-color: transparent;')
        self.mode_holder.setText(self.mods[self.ind])
        self.mode_holder.setFont(font2)
        self.mode_holder.clicked.connect(self.change_mode)
        
    def change_mode(self):
        if 0 <= self.ind < 2:
            self.ind = self.ind + 1
            self.mode_holder.setText(self.mods[self.ind])
        else:
            self.ind = self.ind - 2
            self.mode_holder.setText(self.mods[self.ind])
            
    def search(self):
        if self.line.text() != '' and self.line.text() != ' ' and (',' in self.line.text() and '.' in self.line.text()) == False:
            if self.mods[self.ind] == 'SYM':
                i = 0
                for card in self.parent().cards:
                    if self.line.text().lower() in card.valute.lower():
                        if len(self.line.text().lower()) == 1 and card.valute.lower()[0] == self.line.text().lower():
                            self.parent().scroll_value = i
                            self.parent().refresh()
                            self.parent().scrler.setValue(self.parent().scroll_value)
                            break   
                        elif len(self.line.text().lower()) > 1:
                            self.parent().scroll_value = i
                            self.parent().refresh()
                            self.parent().scrler.setValue(self.parent().scroll_value)
                            break   
                    i = i + 1                   
            elif self.mods[self.ind] == 'NAME':
                i = 0
                for card in self.parent().cards:
                    if self.line.text().lower() in card.name.lower():
                        if len(self.line.text().lower()) == 1 and card.name.lower()[0] == self.line.text().lower():
                            self.parent().scroll_value = i
                            self.parent().refresh()
                            self.parent().scrler.setValue(self.parent().scroll_value)
                            break    
                        elif len(self.line.text().lower()) > 1: 
                            self.parent().scroll_value = i
                            self.parent().refresh()
                            self.parent().scrler.setValue(self.parent().scroll_value)
                            break    
                    i = i + 1 
            elif self.mods[self.ind] == '$':
                if self.line.text()[-1] == '$':
                    self.line.setText(self.line.text()[:-1])
                if self.line.text()[-1] == ' ':
                    while self.line.text()[-1] == ' ':
                        self.line.setText(self.line.text()[:-1])
                if self.line.text()[0] != '0':
                    if '.' in self.line.text():
                        self.line.setText(self.line.text().split('.')[0])
                    elif ',' in self.line.text():
                        self.line.setText(self.line.text().split(',')[0])
                    
                    i = 0
                    for card in self.parent().cards:
                        try:
                            if int(self.line.text().lower()[0] + '0' * (len(self.line.text()) - 1)) == int(str(card.amount).lower().split(',')[0][0] + '0' * (len(str(card.amount).split(',')[0]) - 1)):
                                self.parent().scroll_value = i
                                self.parent().refresh()
                                self.parent().scrler.setValue(self.parent().scroll_value)
                                break
                            i = i + 1
                        except:
                            i = i + 1
                            continue
                elif self.line.text()[0] == '0' and ('.' in self.line.text() or ',' in self.line.text()):
                    if '.' in self.line.text():
                        i = 0
                        for card in self.parent().cards:
                            try:
                                if '0,' + self.line.text().split('.')[1] in str(card.amount):
                                    self.parent().scroll_value = i
                                    self.parent().refresh()
                                    self.parent().scrler.setValue(self.parent().scroll_value)
                                    break
                                i = i + 1
                            except:
                                i = i + 1
                                continue    
                    elif ',' in self.line.text():
                        i = 0
                        for card in self.parent().cards:
                            try:
                                if '0,' + self.line.text().split(',')[1] in str(card.amount):
                                    self.parent().scroll_value = i
                                    self.parent().refresh()
                                    self.parent().scrler.setValue(self.parent().scroll_value)
                                    break
                                i = i + 1
                            except:
                                i = i + 1
                                continue     
        else:
            return



class PredictDaysField(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setFixedSize(QtCore.QSize(100, 38))
        self.BG = QtWidgets.QLabel(parent = self)
        self.BG.setPixmap(QtGui.QPixmap('source/GUI/predict_days_field_BG.png'))
        self.BG.setGeometry(QtCore.QRect(0, 0, 100, 38))
        self.textField = QtWidgets.QLineEdit(parent = self)
        self.textField.setStyleSheet('color: rgb(70, 70, 70);\nbackground-color: transparent;')
        self.textField.setGeometry(QtCore.QRect(6, 3, 91, 32))
        font = QtGui.QFont('Builder Sans', 14)
        self.textField.setFont(font)
        self.textField.setPlaceholderText('Days')
        self.textField.textChanged.connect(self.changed)
        
    def changed(self):
        try:
            self.parent().days_for_predict = int(self.textField.text())
        except:
            self.textField.setText('1')
            
        

class View(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.widgets = []
        self.scroll_value = 0
        self.time_frame = '1d'
        
        self.timestamps = []
        self.open_prices = []
        self.high_prices = []
        self.low_prices = []
        self.close_prises = []
        self.volume_data = []
        
        self.predicted_prices = []
        self.timestamps_for_predicted = []
        
        self.graph = pg.PlotWidget(self, axisItems = {'bottom': pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')})
        self.graph.setBackground("w")
        self.graph.showGrid(x=True, y=True)
        pen = pg.mkPen(color=(90, 169, 240),  width=4)
        self.graph.setYRange(0, 1000)
        self.plot = self.graph.plot(
            [],
            [],
            pen=pen,
            symbol='o',
            symbolSize=4,
            symbolBrush="b",
        )
        
        pen2 = pg.mkPen(color=(255, 174, 0),  width=4)
        self.predicted_plot = self.graph.plot(
            [],
            [],
            pen=pen2,
            symbolSize=4,
            symbolBrush="y",
        )
        
        self.widgets.append(self.graph)
        
        
    def optimize_view(self):
        self.graph.setGeometry(6, 0, self.width(), self.height() - 50)
        
    def setup_graph(self, sym, exchange):
        if sym != 'USDT':
            symbol = f'{sym}/USDT'
        else:
            symbol = f'{sym}/BTC'
        timeframe = '1d'
        try:
            self.predicted_prices = []
            self.timestamps_for_predicted = []
            self.predicted_plot.setData(self.timestamps_for_predicted, self.predicted_prices)
            
            ohlcv_data = exchange.fetch_ohlcv(symbol, timeframe)
            
            self.timestamps = [x[0] / 1000 for x in ohlcv_data]
            self.open_prices = [x[1] for x in ohlcv_data]
            self.high_prices = [x[2] for x in ohlcv_data]
            self.low_prices = [x[3] for x in ohlcv_data]
            self.close_prices = [x[4] for x in ohlcv_data]
            self.volume_data = [x[5] for x in ohlcv_data]
            
            self.predicted_prices.append(self.close_prices[-1])
            self.timestamps_for_predicted.append(self.timestamps[-1])
            
            feat = []
            for ind in range(60, 0, -1):
                num1 = self.open_prices[-ind]
                num2 = self.high_prices[-ind] 
                num3 = self.low_prices[-ind]
                num4 = self.close_prices[-ind]
                num5 = self.volume_data[-ind]
                            
                dem1 = self.open_prices[-ind - 1]
                dem2 = self.high_prices[-ind - 1]
                dem3 = self.low_prices[-ind - 1]
                dem4 = self.close_prices[-ind - 1]
                dem5 = self.volume_data[-ind - 1]
                
                time_code = self.timestamps[-ind] / 1000
                time_obj: datetime = datetime.fromtimestamp(timestamp=time_code)
                hour_sin, hour_cos = cyclic_encode(time_obj.hour, 'hour')
                day_sin, day_cos = cyclic_encode(time_obj.weekday(), 'day')
                month_sin, month_cos = cyclic_encode(time_obj.month - 1, 'month')
                
                step_data = [np.log((num1 / dem1) + 1),
                            np.log((num2 / dem2) + 1),
                            np.log((num3 / dem3) + 1),
                            np.log((num4 / dem4) + 1),
                            np.log((num5 / dem5) + 1),
                            np.log((num4 / num1) + 1),
                            np.log((num2 / num3) + 1),
                            np.log(((min(num1, num4) - num3) / num4) + 1),
                            np.log(num1 + 1), 
                            np.log(num2 + 1),
                            np.log(num3 + 1), 
                            np.log(num4 + 1),
                            np.log(num5 + 1),
                            hour_sin,
                            hour_cos,
                            day_sin,
                            day_cos,
                            month_sin,
                            month_cos] 
                feat.append(step_data)   
                
            feat = np.array(feat.copy(), dtype=np.float32)
            print(feat.shape)
            feat = feat.reshape((1, 60, 19))
            self.parent().model_input = tensor(feat)
            
            self.max_point = max(self.close_prices)
            self.min_point = min(self.close_prices)
            self.graph.setXRange(min(self.timestamps), max(self.timestamps))  
            self.graph.setYRange(self.min_point, self.max_point)

            self.plot.setData(self.timestamps, self.close_prices)
            self.parent().state_label.setPixmap(QtGui.QPixmap('source/GUI/great_state.png'))
            self.parent().isRefreshed = True
        except Exception as exp:
            print(exp)
            self.parent().state_label.setPixmap(QtGui.QPixmap('source/GUI/wrong_state.png'))
            self.plot.setData([], [])
            self.parent().isRefreshed = True
            
    def process_outputs(self, output, state):
        next_price = (exp(output[3]) - 1).item()
        self.close_prices.append(self.close_prices[-1] * next_price)
        self.timestamps.append(self.timestamps[-1] + 86_400)
        
        self.predicted_prices.append(self.close_prices[-1] * next_price)
        self.timestamps_for_predicted.append(self.timestamps[-1])
        
        self.max_point = max(self.max_point, max(self.predicted_prices))
        self.min_point = min(self.min_point, min(self.predicted_prices))
        
        self.predicted_plot.setData(self.timestamps_for_predicted, self.predicted_prices)
        if state:
            timestamps = self.timestamps + self.timestamps_for_predicted
            self.graph.setXRange(min(timestamps), max(timestamps))  
            self.graph.setYRange(self.min_point, self.max_point)
        
        next_open = (exp(output[0]) - 1).item()
        next_high = (exp(output[1]) - 1).item()
        next_low = (exp(output[2]) - 1).item()
        next_volume = (exp(output[4]) - 1).item()
        
        self.open_prices.append(self.open_prices[-1] * next_open)
        self.high_prices.append(self.high_prices[-1] * next_high)
        self.low_prices.append(self.low_prices[-1] * next_low)
        self.volume_data.append(self.volume_data[-1] * next_volume)
        
        num1 = self.open_prices[-1]
        num2 = self.high_prices[-1] 
        num3 = self.low_prices[-1]
        num4 = self.close_prices[-1]
        num5 = self.volume_data[-1]
                    
        dem1 = self.open_prices[-2]
        dem2 = self.high_prices[-2]
        dem3 = self.low_prices[-2]
        dem4 = self.close_prices[-2]
        dem5 = self.volume_data[-2]
        
        time_code = self.timestamps[-1] / 1000
        time_obj: datetime = datetime.fromtimestamp(timestamp=time_code)
        hour_sin, hour_cos = cyclic_encode(time_obj.hour, 'hour')
        day_sin, day_cos = cyclic_encode(time_obj.weekday(), 'day')
        month_sin, month_cos = cyclic_encode(time_obj.month - 1, 'month')
        
        step_data = [np.log((num1 / dem1) + 1),
                    np.log((num2 / dem2) + 1),
                    np.log((num3 / dem3) + 1),
                    np.log((num4 / dem4) + 1),
                    np.log((num5 / dem5) + 1),
                    np.log((num4 / num1) + 1),
                    np.log((num2 / num3) + 1),
                    np.log(max(((min(num1, num4) - num3) / num4) + 1, 1)),
                    np.log(num1 + 1), 
                    np.log(num2 + 1),
                    np.log(num3 + 1), 
                    np.log(num4 + 1),
                    np.log(num5 + 1),
                    hour_sin,
                    hour_cos,
                    day_sin,
                    day_cos,
                    month_sin,
                    month_cos]
        
        return step_data
              
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            pass
        elif delta <= 0:
            pass
        else:
            return
        
    
     
class ResourceBbt(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__()
        self.setParent(parent)
        self.setStyleSheet('background-color: transparent')
        self.setIconSize(QtCore.QSize(95, 18))
        self.ic = QtGui.QIcon()
        self.ic.addPixmap(QtGui.QPixmap('source/GUI/resource_btn_untargeted.png'))
        self.setIcon(self.ic)
        self.clicked.connect(lambda: webbrowser.open(self.parent().url))
        
    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.ic.addPixmap(QtGui.QPixmap('source/GUI/resource_btn_targeted.png'))
        self.setIcon(self.ic)
        
    def leaveEvent(self, event):
        self.ic.addPixmap(QtGui.QPixmap('source/GUI/resource_btn_untargeted.png'))
        self.setIcon(self.ic)
        
        
    
class graphBtn(QtWidgets.QPushButton):
    def __init__(self, parent, action: str):
        super().__init__()
        self.setParent(parent)
        self.setIconSize(QtCore.QSize(38, 38))
        self.setStyleSheet('background-color: transparent')
        icon = QtGui.QIcon()
        self.action = action
        if action == 'add':
            icon.addPixmap(QtGui.QPixmap('source/GUI/add_btn.png'))
            self.opac_effect = QtWidgets.QGraphicsOpacityEffect(self.parent().add_anim_label)
            self.opac_effect.setOpacity(0)
            self.parent().add_anim_label.setGraphicsEffect(self.opac_effect)
        elif action == 'refresh':
            icon.addPixmap(QtGui.QPixmap('source/GUI/refresh_graph_btn.png'))
            self.opac_effect = QtWidgets.QGraphicsOpacityEffect(self.parent().refresh_anim_label)
            self.opac_effect.setOpacity(0)
            self.parent().refresh_anim_label.setGraphicsEffect(self.opac_effect)
        elif action == 'predict':
            icon.addPixmap(QtGui.QPixmap('source/GUI/predict_btn.png'))
            self.opac_effect = QtWidgets.QGraphicsOpacityEffect(self.parent().predict_anim_label)
            self.opac_effect.setOpacity(0)
            self.parent().predict_anim_label.setGraphicsEffect(self.opac_effect)
        self.setIcon(icon)
        
    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        Thread(target = self.targeted_anim, name = 'untargeted_anim').start()
    
    def leaveEvent(self, event):
        Thread(target = self.untargeted_anim, name = 'untargeted_anim').start()
    
    def targeted_anim(self):
        self.isTargetedActive = True
        for i in range(1, 11):
            self.opac_effect.setOpacity(i / 11)
            if self.action == 'add':
                self.parent().add_anim_label.setGraphicsEffect(self.opac_effect)
            elif self.action == 'refresh':
                self.parent().refresh_anim_label.setGraphicsEffect(self.opac_effect)
            elif self.action == 'predict':
                self.parent().predict_anim_label.setGraphicsEffect(self.opac_effect)
            sleep(0.0201)
    
    def untargeted_anim(self):
        self.isUnTargetedActive = True
        for i in range(10, -1, -1):
            self.opac_effect.setOpacity(i / 11)
            if self.action == 'add':
                self.parent().add_anim_label.setGraphicsEffect(self.opac_effect)
            elif self.action == 'refresh':
                self.parent().refresh_anim_label.setGraphicsEffect(self.opac_effect)
            elif self.action == 'predict':
                self.parent().predict_anim_label.setGraphicsEffect(self.opac_effect)
            sleep(0.0201)
        
        
        
class checkButton(QtWidgets.QPushButton):
    def __init__(self, parent, variable_option):
        super().__init__()
        self.setParent(parent)
        self.parent().resizing_state = variable_option
        self.setIconSize(QtCore.QSize(17, 17))
        self.icon = QtGui.QIcon()
        if variable_option:
            self.icon.addPixmap(QtGui.QPixmap('source/GUI/check_btn_checked.png'))
        else:
            self.icon.addPixmap(QtGui.QPixmap('source/GUI/check_btn_unchecked.png'))
        self.setIcon(self.icon)
        self.setStyleSheet('background-color: transparent')
        
    def mousePressEvent(self, event):
        self.icon = QtGui.QIcon()
        self.parent().resizing_state = not self.parent().resizing_state
        if self.parent().resizing_state:
            self.icon.addPixmap(QtGui.QPixmap('source/GUI/check_btn_checked.png'))
        else:
            self.icon.addPixmap(QtGui.QPixmap('source/GUI/check_btn_unchecked.png'))
        self.setIcon(self.icon)
        
    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        
        
class setupProfileDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.place_for_border = 3
        self.setFixedSize(QtCore.QSize(570, 320))
        self.gray_BG_horiz = QtWidgets.QLabel(parent = self)
        self.gray_BG_horiz.setStyleSheet('background-color: rgb(220, 220, 220)')
        self.gray_BG_vert = QtWidgets.QLabel(parent = self)
        self.gray_BG_vert.setStyleSheet('background-color: rgb(220, 220, 220)')

        self.BG_horiz = QtWidgets.QLabel(parent = self)
        self.BG_horiz.setStyleSheet('background-color: rgb(255, 255, 255)')
        self.BG_vert = QtWidgets.QLabel(parent = self)
        self.BG_vert.setStyleSheet('background-color: rgb(255, 255, 255)')

        self.corner_1 = QtWidgets.QLabel(parent = self)
        self.corner_1.setPixmap(QtGui.QPixmap('source/GUI/0_deegr.png'))
        self.corner_2 = QtWidgets.QLabel(parent = self)
        self.corner_2.setPixmap(QtGui.QPixmap('source/GUI/90_deegr.png'))
        self.corner_3 = QtWidgets.QLabel(parent = self)
        self.corner_3.setPixmap(QtGui.QPixmap('source/GUI/180_deegr.png'))
        self.corner_4 = QtWidgets.QLabel(parent = self)
        self.corner_4.setPixmap(QtGui.QPixmap('source/GUI/270_deegr.png'))
        
        self.cls_btn = ActionBtn(parent = self, action = 'cls', win = self)
        cls_icon = QtGui.QIcon()
        cls_icon.addPixmap(QtGui.QPixmap('source/GUI/cls_btn.png'))
        self.cls_btn.setIcon(cls_icon)
        self.cls_btn.setStyleSheet('background-color: transparent')
        
        self.mvbl_win_BTN = QtWidgets.QLabel(parent = self,)
        self.mvbl_win_BTN.setPixmap(QtGui.QPixmap('source/GUI/MVBl_BTN_border'))
        self.move_roundler = Roundler(self, 'move', 43, self)
        
        self.optimize_dialog()
        
        self.cls_anim = QtCore.QPropertyAnimation(self.cls_btn, b'pos', self)
        self.cls_anim.setDuration(400)
        self.cls_anim.setStartValue(QtCore.QPointF(self.cls_btn.pos().x(), 14))
        self.cls_anim.setKeyValueAt(0.15, QtCore.QPointF(self.cls_btn.pos().x(), 11))
        self.cls_anim.setEndValue(QtCore.QPointF(self.cls_btn.pos().x(), 14))
        
    def optimize_dialog(self):
        self.cls_btn.setGeometry(QtCore.QRect((self.width() - (30 + self.place_for_border)), 14, 16, 16))
        self.gray_BG_horiz.setGeometry(QtCore.QRect(0, 100, self.width(), self.height() - 200))
        self.gray_BG_vert.setGeometry(QtCore.QRect(100, 0, self.width() - 200, self.height()))
        self.corner_1.setGeometry(QtCore.QRect(0, 0, 103, 103))
        self.corner_2.setGeometry(QtCore.QRect(self.width() - 103, 0, 103, 103))
        self.corner_3.setGeometry(QtCore.QRect(self.width() - 103, self.height() - 103, 103, 103))
        self.corner_4.setGeometry(QtCore.QRect(0, self.height() - 103, 103, 103))
        self.BG_horiz.setGeometry(QtCore.QRect(self.place_for_border, 100 + self.place_for_border, self.width() - self.place_for_border*2, self.height() - (200 + self.place_for_border)))
        self.BG_vert.setGeometry(QtCore.QRect(100 + self.place_for_border, self.place_for_border, self.width() - (200 + self.place_for_border*2), self.height() - self.place_for_border*2))
        self.mvbl_win_BTN.setGeometry(QtCore.QRect(self.width() - (51 + self.place_for_border), self.height() - (51 + self.place_for_border), 40, 40))
        self.move_roundler.setGeometry(QtCore.QRect(self.width() - (43 + self.place_for_border), self.height() - (43 + self.place_for_border), 24, 24))
        
        
    
class kryptoInterface(QtWidgets.QWidget):
    def __init__(self, parent, model):
        super().__init__()
        self.setParent(parent)
        self.predict_course_model = model
        self.days_for_predict = 1

        self.url = 'https://ru.tradingview.com/markets/cryptocurrencies/prices-all/'
        self.img_size = (62, 62)
        self.isOpenned = False
        self.exchange = ccxt.binance({'enableRateLimit': True})

        self.valute = None
        self.name = None
        self.img_url = None
        self.place = None
        self.amount = None
        self.change = None
        self.capitalization = None
        self.value = None
        self.offer = None
        self.isRefreshed = True
        self.predict_started = False
        self.is_pressed_again = False
        self.resizing_state = True
        self.cap_ind = None
        self.V_ind = None
        self.offer_ind = None
        
        self.model_input = None # !!!
        
        self.view = View(self)
        self.view.setVisible(False)
        self.img = QtWidgets.QLabel(parent = self)
        self.img_frame = QtWidgets.QLabel(parent = self)
        self.img_frame.setPixmap(QtGui.QPixmap('source/GUI/coin_inter_frame.png'))
        font1 = QtGui.QFont('Builder Sans', 35)
        font1.setBold(True)
        font2 = QtGui.QFont('Builder Sans', 24)
        font3 = QtGui.QFont('Builder Sans', 33)
        font4 = QtGui.QFont('Builder Sans', 22)
        font5 = QtGui.QFont('Builder Sans', 11)
        font6 = QtGui.QFont('Builder Sans', 15)
        self.sym_holder = QtWidgets.QLabel(parent = self)
        self.sym_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.sym_holder.setFont(font1)
        self.sym_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.name_holder = QtWidgets.QLabel(parent = self)
        self.name_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.name_holder.setFont(font6)
        self.name_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.amount_holder = QtWidgets.QLabel(parent = self)
        self.amount_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.amount_holder.setFont(font3)
        self.amount_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.left_part = QtWidgets.QLabel(self)
        self.right_part = QtWidgets.QLabel(self) 
        self.center_part = QtWidgets.QLabel(self) 
        self.change_holder = QtWidgets.QLabel(parent = self)
        self.change_holder.setFont(font2)
        self.change_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.cap_holder = QtWidgets.QLabel(parent = self)
        self.cap_holder.setFont(font4)
        self.cap_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.cap_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.V_holder = QtWidgets.QLabel(parent = self)
        self.V_holder.setFont(font4)
        self.V_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.V_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.offer_holder = QtWidgets.QLabel(parent = self)
        self.offer_holder.setFont(font4)
        self.offer_holder.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.offer_holder.setStyleSheet('color: rgb(0, 0, 0)')
        self.for_cap = QtWidgets.QLabel(parent = self)
        self.for_cap.setFont(font5)
        self.for_cap.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.for_cap.setStyleSheet('color: rgb(0, 0, 0)')
        self.for_value = QtWidgets.QLabel(parent = self)
        self.for_value.setFont(font5)
        self.for_value.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.for_value.setStyleSheet('color: rgb(0, 0, 0)')
        self.for_offer = QtWidgets.QLabel(parent = self)
        self.for_offer.setFont(font5)
        self.for_offer.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.for_offer.setStyleSheet('color: rgb(0, 0, 0)')
        
        self.refresh_anim_label = QtWidgets.QLabel(parent = self)
        self.refresh_anim_label.setPixmap(QtGui.QPixmap('source/GUI/refresh_graph_btn_anim_label.png'))
        self.refresh_anim_label.setVisible(False)
        self.add_anim_label = QtWidgets.QLabel(parent = self)
        self.add_anim_label.setPixmap(QtGui.QPixmap('source/GUI/add_btn_anim_label.png'))
        self.add_anim_label.setVisible(False)
        self.refresh_graph_btn = graphBtn(self, 'refresh')
        self.refresh_graph_btn.setVisible(False)
        self.refresh_graph_btn.clicked.connect(self.refresh_graph)
        self.add_btn = graphBtn(self, 'add')
        self.add_btn.setVisible(False)
        self.add_btn.clicked.connect(self.open_profile_dialog)
        
        self.resource_btn = ResourceBbt(self)
        self.state_label = QtWidgets.QLabel(parent = self)
        
        self.predict_anim_label = QtWidgets.QLabel(parent = self)
        self.predict_anim_label.setPixmap(QtGui.QPixmap('source/GUI/predict_btn_anim_label.png'))
        self.predict_anim_label.setVisible(False)
        self.predict_btn = graphBtn(self, 'predict')
        self.predict_btn.clicked.connect(self.tech_predict)
        self.predict_btn.setVisible(False)
        self.predict_days_field = PredictDaysField(self)
        self.predict_days_field.setVisible(False)
        self.resizing_state_btn = checkButton(self, self.resizing_state)
        self.resizing_state_btn.setVisible(False)
        
        self.refresh_graph_anim_BG = QtWidgets.QLabel(parent = self)
        self.refresh_graph_anim_label = QtWidgets.QLabel(parent = self)
        
        self.graph_refresh_anim = QtGui.QMovie('source/gifs/refresh_graph_anim.gif')
        self.graph_refresh_anim.finished.connect(self.continue_anim)
        
        self.welcome_screen = QtWidgets.QLabel(parent = self)
        
    def open_profile_dialog(self):
        self.profile_dialog = setupProfileDialog()
        self.profile_dialog.exec()
        
    def tech_predict(self):
        if self.predict_started == False:
            Thread(target = self.predict, name = 'predict').start()
        else:
            self.is_pressed_again = True
        
    def predict(self):
        if self.model_input is not None and self.predict_started == False:
            self.predict_started = True
            for iteration in range(self.days_for_predict):
                if self.is_pressed_again:
                    self.is_pressed_again = False
                    self.predict_started = False
                    break
                output = self.predict_course_model(self.model_input).detach()
                step = self.view.process_outputs(output, self.resizing_state)
                self.model_input = self.model_input[:, 1:, :]
                list_tensor = tensor([step], dtype=float32).unsqueeze(0)
                self.model_input = cat((self.model_input, list_tensor), dim=1)
            
        sleep(0.5)
        self.predict_started = False
            
    def refresh_graph(self):
        if self.predict_started:
            self.is_pressed_again = True
        if self.isRefreshed == True:
            self.predict_started = False
            self.predicted_list = []
            self.predicted_list_dates = []
            self.view.predicted_plot.setData([], [])
            self.view.close()
            self.view = View(self)
            self.optimize_interface()
            self.view.show()
            self.view.lower()
            self.isRefreshed = False
            self.start_graph_refresh_anim()
            self.exchange = ccxt.binance({'enableRateLimit': True})
            try:
                Thread(target = self.view.setup_graph, args = (self.valute, self.exchange, ), name = 'setup_graph').start()
            except:
                self.view.plot.setData([], [])
                self.view.predicted_plot.setData([], [])
                self.isRefreshed = True
                
    def start_graph_refresh_anim(self):
        self.refresh_graph_anim_BG.setPixmap(QtGui.QPixmap('source/GUI/refresh_anim_BG.png'))
        self.refresh_graph_anim_label.setMovie(self.graph_refresh_anim)
        self.graph_refresh_anim.start()
        
    def continue_anim(self):
        if self.isRefreshed != True:
            self.graph_refresh_anim.start()
        else:
            self.refresh_graph_anim_label.setPixmap(QtGui.QPixmap())
            self.refresh_graph_anim_BG.setPixmap(QtGui.QPixmap())
                
    def reconnect(self):
        self.exchange = ccxt.binance({'enableRateLimit': True})
        try:
            Thread(target = self.view.setup_graph, args = (self.valute, self.exchange, ), name = 'setup_graph').start()
        except Exception as exp:
            print(exp)
            self.view.predicted_plot.setData([], [])
            self.view.plot.setData([], [])
        print('reconnected')
        QtCore.QTimer.singleShot(4000000, self.reconnect)
        
    def setup(self, valute: str, name: str, img: str, place: int, amount: int, change: str, cap: str, V: str, offer: str, cap_ind: float, V_ind: float, offer_ind: float):
        if self.predict_started:
            self.is_pressed_again = True
        if self.isOpenned == False:
            self.welcome_screen.close()
            self.add_anim_label.setVisible(True)
            self.add_btn.setVisible(True)
            self.refresh_anim_label.setVisible(True)
            self.refresh_graph_btn.setVisible(True)
            self.predict_anim_label.setVisible(True)
            self.predict_btn.setVisible(True)
            self.predict_days_field.setVisible(True)
            self.resizing_state_btn.setVisible(True)
            
        self.isOpenned = True
        self.predict_started = False
        self.url = f'https://ru.tradingview.com/symbols/{valute}USD/?exchange=CRYPTO'
        self.valute = valute
        try:
            Thread(target = self.view.setup_graph, args = (self.valute, self.exchange, ), name = 'setup_graph').start()
        except:
            self.view.predicted_plot.setData([], [])
            self.view.plot.setData([], [])
            
        self.name = name
        self.img_url = img
        self.place = place
        self.amount = amount
        self.change = change[1:-1]
        self.capitalization = cap
        self.value = V
        self.offer = offer
        self.cap_ind = cap_ind
        self.V_ind = V_ind
        self.offer_ind = offer_ind
        
        self.optimize_interface()

        if '+' in change:
            self.change_holder.setStyleSheet('color: rgb(24, 116, 55)')
            self.left_part.setPixmap(QtGui.QPixmap('source/GUI/left_up.png'))
            self.right_part.setPixmap(QtGui.QPixmap('source/GUI/right_up.png'))
            self.center_part.setStyleSheet('background-color: rgb(230, 243, 234)')
        else:
            self.change_holder.setStyleSheet('color: rgb(116, 24, 24)')
            self.left_part.setPixmap(QtGui.QPixmap('source/GUI/left_down.png'))
            self.right_part.setPixmap(QtGui.QPixmap('source/GUI/right_down.png'))
            self.center_part.setStyleSheet('background-color: rgb(243, 230, 230)')

        if 'https://' in self.img_url:
            try:
                self.set_image()
            except:
                try:
                    self.set_image()
                except:
                    pass
        else:
            self.img.setPixmap(QtGui.QPixmap(self.img_url))

        self.for_cap.setText('Market cap:')
        self.for_value.setText('Volume:')
        self.for_offer.setText('Circ supply:')
        self.sym_holder.setText(self.valute)
        self.name_holder.setText(self.name)
        self.amount_holder.setText(str(self.amount) + ' USD')
        self.change_holder.setText(self.change)
        self.cap_holder.setText(self.capitalization)
        self.V_holder.setText(self.value)
        self.offer_holder.setText(self.offer)

        self.optimize_interface()
        self.view.setVisible(True)
        self.optimize_interface()   

        self.view.predicted_plot.setData(self.predicted_list_dates, self.predicted_list)
        QtCore.QTimer.singleShot(400000, self.reconnect)

    def set_image(self):
        data = requests.get(self.img_url).content
        with open('inter_img.svg','wb') as img:
            img.write(data)
            img.close()

        pixmap = QtGui.QPixmap(QtCore.QSize(self.img_size[0], self.img_size[1]))
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        MainWindow.last_pen = painter
        svgRenderer = QSvgRenderer("inter_img.svg")
        svgRenderer.render(painter)
        painter.end()
        del painter

        self.img.setPixmap(pixmap)

        with open('inter_img.svg','r+') as img:
            img.truncate(0)

    def optimize_interface(self):    
        self.resource_btn.setGeometry(QtCore.QRect(21, 10, 95, 18))
        self.state_label.setGeometry(QtCore.QRect(124, 10, 18, 18))
        self.refresh_graph_anim_BG.setGeometry(QtCore.QRect(124, 10, 18, 18))
        self.refresh_graph_anim_label.setGeometry(QtCore.QRect(124  , 10, 18, 18))
        self.img.setGeometry(QtCore.QRect(23, self.size().height() - self.img_size[1] - 13, self.img_size[0], self.img_size[1]))
        self.img_frame.setGeometry(QtCore.QRect(23, self.size().height() - self.img_size[1] - 13, self.img_size[0], self.img_size[1]))
        self.sym_holder.setGeometry(QtCore.QRect(self.img.pos().x() + self.img_size[0] + 14, self.img.pos().y() - 8, self.sym_holder.sizeHint().width() + 15, 60))
        self.name_holder.setGeometry(QtCore.QRect(self.img.pos().x() + self.img_size[0] + 16, self.img.pos().y() + 26, self.name_holder.sizeHint().width() + 15, 40))
        self.view.setGeometry(QtCore.QRect(10, 45, self.width() - 30, self.height() - 150))
        self.view.optimize_view()  
        self.predict_btn.setGeometry(QtCore.QRect(33, self.height() - 133, 38, 38))
        self.predict_days_field.setGeometry(QtCore.QRect(90, self.height() - 133, 100, 38))
        self.resizing_state_btn.setGeometry(QtCore.QRect(209, self.height() - 133, 17, 17))
        self.add_btn.setGeometry(QtCore.QRect(self.width() - 58, self.height() - 133, 38, 38))
        self.refresh_graph_btn.setGeometry(QtCore.QRect(self.width() - 115, self.height() - 133, 38, 38))
        self.predict_anim_label.setGeometry(QtCore.QRect(21, self.height() - 145, 62, 62))
        self.add_anim_label.setGeometry(QtCore.QRect(self.width() - 70, self.height() - 145, 62, 62))
        self.refresh_anim_label.setGeometry(QtCore.QRect(self.width() - 127, self.height() - 145, 62, 62))
        if self.valute != None:
            self.amount_holder.setGeometry(QtCore.QRect(self.img.pos().x() + self.img_size[0] + self.sym_holder.sizeHint().width() + 31, self.img.pos().y() - 8, self.parent().size().width() - 400, 60))       
            self.left_part.setGeometry(QtCore.QRect(self.img.pos().x() + self.amount_holder.sizeHint().width() + self.sym_holder.sizeHint().width() + self.img_size[0] + 45, self.img.pos().y() + 1, 30, 42))
            self.change_holder.setGeometry(QtCore.QRect(self.img.pos().x() + self.amount_holder.sizeHint().width() + self.sym_holder.sizeHint().width() + self.img_size[0] + 78, self.img.pos().y(), self.parent().size().width() - 400, 42))
            self.center_part.setGeometry(QtCore.QRect(self.img.pos().x() + self.amount_holder.sizeHint().width() + self.sym_holder.sizeHint().width() + self.img_size[0] + 75, self.img.pos().y() + 1, self.change_holder.sizeHint().width() + 8, 42))
            self.right_part.setGeometry(QtCore.QRect(self.img.pos().x() + self.amount_holder.sizeHint().width() + self.sym_holder.sizeHint().width() + self.img_size[0] + 83 + self.change_holder.sizeHint().width(), self.img.pos().y() + 1, 30, 42))           
            self.cap_holder.setGeometry(QtCore.QRect(self.img.pos().x() + self.amount_holder.sizeHint().width() + self.sym_holder.sizeHint().width() + self.change_holder.sizeHint().width() + self.img_size[0] + 166, self.img.pos().y() + 7, self.parent().size().width() - 400, 40))
            self.for_cap.setGeometry(QtCore.QRect(self.cap_holder.pos().x(), self.sym_holder.pos().y() - 5, self.cap_holder.width(), 30))
            self.V_holder.setGeometry(QtCore.QRect(self.img.pos().x() + self.amount_holder.sizeHint().width() + self.sym_holder.sizeHint().width() + self.change_holder.sizeHint().width() + self.cap_holder.sizeHint().width() + self.img_size[0] + 216, self.img.pos().y() + 7, self.parent().size().width() - 400, 40))
            self.for_value.setGeometry(QtCore.QRect(self.V_holder.pos().x(), self.sym_holder.pos().y() - 5, self.V_holder.width(), 30))
            self.offer_holder.setGeometry(QtCore.QRect(self.img.pos().x() + self.amount_holder.sizeHint().width() + self.sym_holder.sizeHint().width() + self.change_holder.sizeHint().width() + self.cap_holder.sizeHint().width() + self.V_holder.sizeHint().width() + self.img_size[0] + 266, self.img.pos().y() + 7, self.parent().size().width() - 400, 40))
            self.for_offer.setGeometry(QtCore.QRect(self.offer_holder.pos().x(), self.sym_holder.pos().y() - 5, self.offer_holder.width(), 30))
            
        if self.isOpenned == False:
            self.welcome_screen.setGeometry(QtCore.QRect(0, self.height() - (round((1080/1770) * self.width())) - 7, self.width() - 3, round((1080/1770) * (self.width() - 3))))
            pixmap = QtGui.QPixmap(QtCore.QSize(self.width(), round((1080/1770) * self.width())))
            pixmap.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            svgRenderer = QSvgRenderer('source/GUI/welcome_screen.svg')
            svgRenderer.render(painter)
            painter.end()
            self.welcome_screen.setPixmap(pixmap)



class Scroller(QtWidgets.QScrollBar):
    def __init__(self, parent, mainwin):
        super().__init__()
        self.setMinimum(0)
        self.last = 0
        self.setParent(parent)
        self.win = mainwin
        self.setStyleSheet("""
QScrollBar:vertical {
    border: none;
    background: #ffffff;
}

QScrollBar::handle:vertical {
    background: #888888; /* цвет ползунка */
    min-height: 20px; /* минимальная высота ползунка */
}

QScrollBar::add-line:vertical {
    height: 0px; /* высота кнопки для прокрутки вниз */
}

QScrollBar::sub-line:vertical {
    height: 0px; /* высота кнопки для прокрутки вверх */
}
""")
        self.valueChanged.connect(self.change)

    def change(self, event):
        if self.value() < (MainWindow.max - (MainWindow.height() - 20) // 61) + 2:
            self.last = self.value()
            self.win.scroll_value = self.value()
            self.win.refresh()
        else:
            if self.value() < self.last:
                self.last = self.value()
                self.win.scroll_value = self.value()
                self.win.refresh()
            else:
                return



class MainWin(QtWidgets.QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle('Krypto Briefcase')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('source/icon/icon.png'))
        self.setWindowIcon(icon)
        self.place_for_border = 3
        self.last = None
        self.last_pen = None
        self.error = None
        self.scroll_value = 0
        self.max = 0

        self.cards = []
        self.current_cards = []
        self.isParsed = False
        self.isStopped = False

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.gray_BG_horiz = QtWidgets.QLabel(parent = self.central_widget)
        self.gray_BG_horiz.setStyleSheet('background-color: rgb(220, 220, 220)')
        self.gray_BG_vert = QtWidgets.QLabel(parent = self.central_widget)
        self.gray_BG_vert.setStyleSheet('background-color: rgb(220, 220, 220)')

        self.BG_horiz = QtWidgets.QLabel(parent = self.central_widget)
        self.BG_horiz.setStyleSheet('background-color: rgb(255, 255, 255)')
        self.BG_vert = QtWidgets.QLabel(parent = self.central_widget)
        self.BG_vert.setStyleSheet('background-color: rgb(255, 255, 255)')

        self.corner_1 = QtWidgets.QLabel(parent = self.central_widget)
        self.corner_1.setPixmap(QtGui.QPixmap('source/GUI/0_deegr.png'))
        self.corner_2 = QtWidgets.QLabel(parent = self.central_widget)
        self.corner_2.setPixmap(QtGui.QPixmap('source/GUI/90_deegr.png'))
        self.corner_3 = QtWidgets.QLabel(parent = self.central_widget)
        self.corner_3.setPixmap(QtGui.QPixmap('source/GUI/180_deegr.png'))
        self.corner_4 = QtWidgets.QLabel(parent = self.central_widget)
        self.corner_4.setPixmap(QtGui.QPixmap('source/GUI/270_deegr.png'))

        self.interface = kryptoInterface(self.central_widget, model)

        self.case = ValuteCard(self)
        self.case.set_new_params('USD', 'Briefcase', 'source/GUI/case.png', 0, 0, '+0%', '0 coins', '0 M', '0 T', 0, 0, 0)
        self.case.move(self.place_for_border, self.place_for_border)
        self.case.setVisible(True)
        self.case.place_img()
        
        self.scrler = Scroller(self.central_widget, self)

        self.mvbl_win_BTN = QtWidgets.QLabel(parent = self.central_widget,)
        self.mvbl_win_BTN.setPixmap(QtGui.QPixmap('source/GUI/MVBl_BTN_border'))
        self.move_roundler = Roundler(self.central_widget, 'move', 43, self)

        self.resize_win_BTN = QtWidgets.QLabel(parent = self.central_widget)
        self.resize_win_BTN.setPixmap(QtGui.QPixmap('source/GUI/MVBl_BTN_border'))
        self.resize_roundler = Roundler(self.central_widget, 'resize', 92, self)

        self.cls_btn = ActionBtn(parent = self.central_widget, action = 'cls', win = self)
        cls_icon = QtGui.QIcon()
        cls_icon.addPixmap(QtGui.QPixmap('source/GUI/cls_btn.png'))
        self.cls_btn.setIcon(cls_icon)
        self.cls_btn.setStyleSheet('background-color: transparent')

        self.rlup_btn = ActionBtn(parent = self.central_widget, action = 'rlup', win = self)
        rlup_icon = QtGui.QIcon()
        rlup_icon.addPixmap(QtGui.QPixmap('source/GUI/rlup_btn.png'))
        self.rlup_btn.setIcon(rlup_icon)
        self.rlup_btn.setStyleSheet('background-color: transparent')

        self.FS_btn = ActionBtn(parent = self.central_widget, action = 'FS', win = self)
        FS_icon = QtGui.QIcon()
        FS_icon.addPixmap(QtGui.QPixmap('source/GUI/FS_btn.png'))
        self.FS_btn.setIcon(FS_icon)
        self.FS_btn.setStyleSheet('background-color: transparent')

        self.refresh_btn = refreshBtn(self)

        self.refresh_anim_holder = RefreshAnimDisplay(parent = self)
        self.refresh_anim_holder.setVisible(False)

        self.refresh_anim = QtGui.QMovie('source/gifs/refresh_btn_anim.gif')
        self.refresh_anim.finished.connect(self.continue_refresh_anim)
        self.refresh_anim_holder.setMovie(self.refresh_anim)
        
        self.search = SearchLine(self)
        
        self.cover_line = QtWidgets.QLabel(parent = self.central_widget)
        self.cover_line.setStyleSheet('background-color: rgb(220, 220, 220)')

        self.checkIfFirst()
        self.optimize_win()
        self.objectNameChanged.connect(self.parsing)

        self.t = thread(self)
        self.t.start()
        self.check()
        QtCore.QTimer.singleShot(1500, lambda: self.time_refresh())
        self.maximise()
        self.un_maximize()

    def time_refresh(self):
        self.refresh_btn.clicked.emit()
        QtCore.QTimer.singleShot(1500, lambda: self.time_refresh())
        
    def keyPressEvent(self, event):
        if event.key() == 16777220:
            self.search.search_btn.clicked.emit()

    def continue_refresh_anim(self):
        if self.isParsed != True:
            self.refresh_anim.start()
        else:
            self.refresh_anim_holder.setVisible(False)

    def checkIfFirst(self):
        with open('isFirst.txt', 'r+') as file:
            self.text = file.read()
            file.truncate(0)

        if self.text != '1':
            self.loadFont('source/fonts/BuilderSans-Regular-400.otf')

        if self.error == None:
            with open('isFirst.txt', 'r+') as file_:
                file_.write('1')
        else:
            with open('isFirst.txt', 'r+') as file_:
                file_.write('0')

    def reload_cards(self):
        print('started')
        while self.isParsed == False:
            try:
                self.isParsed = False
                options = Options()
                options.add_argument("--headless")
                driver = webdriver.Firefox(options = options)
                driver.get('https://ru.tradingview.com/markets/cryptocurrencies/prices-all/')

                button_element = True

                while button_element:
                    try:
                        if self.isParsed == False:
                            button_element = ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".gray-D4RPB3ZC.secondary-D4RPB3ZC")))
                            button_element.click()
                            sleep(0.5)
                        else:
                            break
                    except:
                        button_element = False

                html = driver.page_source
                driver.quit()
                pars_data = bs4.BeautifulSoup(html, 'html.parser')
                tds = pars_data.find_all('td')
                self.links = []
                self.syms = []
                self.names = []
                self.amounts = []
                self.changes = []
                self.caps = []
                self.Vs = []
                self.offers = []

                i = 1
                for td in tds:
                    if td.img and 'svg' in td.img['src']:
                        self.links.append(td.img['src'])
                    if td.a:
                        self.syms.append(td.a.contents[0])
                    if td.sup:
                        self.names.append(td.sup.contents[0])
                    if td.span:
                        if 'positive' in td.span.attrs['class'][0] or 'negative' in td.span.attrs['class'][0]:
                            self.changes.append(td.span.contents[0])
                    if ',' in td.contents[0]:
                        if td.contents[0][-1].isdigit() == True:
                            self.amounts.append(td.contents[0])
                        else:
                            if i == 1:
                                self.caps.append(td.contents[0])
                                i = i + 1
                            elif i == 2:
                                self.Vs.append(td.contents[0])
                                i = i + 1
                            elif i == 3:
                                self.offers.append(td.contents[0])
                                i = 1

                i = 0
                print(len(self.links))
                ind_dict = {'K': 0, 'B': 0.3, 'T': 0.6, 'M': 0.9}

                for card in self.cards:
                    try:
                        if self.isParsed == False:
                            card.update(self.syms[i], self.names[i], i + 1, self.amounts[i], self.changes[i], self.caps[i], self.Vs[i], self.offers[i], ind_dict[self.caps[i][-1]], ind_dict[self.Vs[i][-1]], ind_dict[self.offers[i][-1]])
                            if self.syms[i] == self.interface.valute:
                                self.interface.setup(self.syms[i], self.names[i], self.links[i], i + 1, self.amounts[i], self.changes[i], self.caps[i], self.Vs[i], self.offers[i], ind_dict[self.caps[i][-1]], ind_dict[self.Vs[i][-1]], ind_dict[self.offers[i][-1]])
                            i = i + 1
                        else:
                            break
                    except Exception as exc:
                        print(exc)

                for card in self.cards:
                    try:
                        if self.isParsed == False:
                            card.place_img()
                        else:
                            break
                    except Exception as exc:
                        print(exc)
                        
                gc.collect()

                print(i)

                self.isParsed = True
                print('parsed')

            except Exception as exp:
                print(exp)
                self.isParsed = False

    def loadFont(self, font_path: str):
        self.error = None
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts")
        font_name = font_path.split("\\")[-1]

        try:
            winreg.SetValueEx(key, font_name, 0, winreg.REG_SZ, font_path)
            print(f"Шрифт {font_name} успешно добавлен в реестр компьютера.")
        except OSError as e:
            print(f"Ошибка при добавлении шрифта в реестр: {e}")
            self.error = e

        winreg.CloseKey(key)

    def check(self):
        if self.t.win.isStarted == False:
            print('-')
            Timer(function = self.check, interval = 1.0).start()
        else:
            print('+')
            self.setObjectName('+')

    def parsing(self):
        self.objectNameChanged.disconnect()
        self.objectNameChanged.connect(self.show)
        self.pars_valutes()
        self.t = Thread(target = self.set_up, name = 'setup')
        self.t.start()
        self.upload_resolution()
        self.raise_()

    def set_up(self):
        self.isParsed = False
        ind_dict = {'K': 0, 'B': 0.3, 'T': 0.6, 'M': 0.9}
        i = 0
        y = 61 + self.place_for_border
        for link in self.links:
            try:
                if self.isParsed == False:
                    self.cards[i].set_new_params(self.syms[i], self.names[i], link, i + 1, self.amounts[i], self.changes[i], self.caps[i], self.Vs[i], self.offers[i], ind_dict[self.caps[i][-1]], ind_dict[self.Vs[i][-1]], ind_dict[self.offers[i][-1]])
                    if self.cards[i] in self.cards[0:((self.height() - 20) // 61 - 2)]:
                        self.current_cards.append(self.cards[i])
                        self.cards[i].move(self.place_for_border, y)
                        self.cards[i].setVisible(True)
                        y = y + 61
                    i = i + 1
                    self.max = i
                    self.case.cap_holder.setText(f'{i} coins')
                    self.scrler.setMaximum(i + 1)
                else:
                    break
            except:
                continue

        for card in self.cards[i:]:
            card.close()
            self.cards.remove(card)

        self.isParsed = True

        for card in self.cards:
            if self.isStopped == False:
                card.place_img()
                
        gc.collect()

    def pars_valutes(self):
        print('started')
        while self.isParsed == False:
            self.cards = []
            self.current_cards = []
            try:
                options = Options()
                options.add_argument("--headless")
                driver = webdriver.Firefox(options = options)
                driver.get('https://ru.tradingview.com/markets/cryptocurrencies/prices-all/')

                button_element = True

                while button_element:
                    try:
                        if self.isParsed == False:
                            button_element = ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".gray-D4RPB3ZC.secondary-D4RPB3ZC")))
                            button_element.click()
                            sleep(5)
                        else:
                            break
                    except:
                        button_element = False

                html = driver.page_source
                driver.quit()
                pars_data = bs4.BeautifulSoup(html, 'html.parser')
                tds = pars_data.find_all('td')
                self.links = []
                self.syms = []
                self.names = []
                self.amounts = []
                self.changes = []
                self.caps = []
                self.Vs = []
                self.offers = []

                i = 1
                for td in tds:
                    if td.img and 'svg' in td.img['src']:
                        self.links.append(td.img['src'])
                    if td.a:
                        self.syms.append(td.a.contents[0])
                    if td.sup:
                        self.names.append(td.sup.contents[0])
                    if td.span:
                        if 'positive' in td.span.attrs['class'][0] or 'negative' in td.span.attrs['class'][0]:
                            self.changes.append(td.span.contents[0])
                    if ',' in td.contents[0]:
                        if td.contents[0][-1].isdigit() == True:
                            self.amounts.append(td.contents[0])
                        else:
                            if i == 1:
                                self.caps.append(td.contents[0])
                                i = i + 1
                            elif i == 2:
                                self.Vs.append(td.contents[0])
                                i = i + 1
                            elif i == 3:
                                self.offers.append(td.contents[0])
                                i = 1

                i = 0
                for link in self.links:
                    try:
                        wid = ValuteCard(self)
                        self.cards.append(wid)
                        i = i + 1
                    except:
                        continue

                print(len(self.cards))
                self.scrler.setMaximum(len(self.cards))
                self.search.close()
                self.search = SearchLine(self)
                self.search.show()

                self.isParsed = True
                print('parsed')
            except Exception as exp:
                print(exp)
                self.isParsed = False

    def optimize_win(self):
        self.cover_line.setGeometry(QtCore.QRect(self.width() - 3, 30, 3, self.height() - 60))
        self.gray_BG_horiz.setGeometry(QtCore.QRect(0, 100, self.width(), self.height() - 200))
        self.gray_BG_vert.setGeometry(QtCore.QRect(100, 0, self.width() - 200, self.height()))
        self.corner_1.setGeometry(QtCore.QRect(0, 0, 103, 103))
        self.corner_2.setGeometry(QtCore.QRect(self.width() - 103, 0, 103, 103))
        self.corner_3.setGeometry(QtCore.QRect(self.width() - 103, self.height() - 103, 103, 103))
        self.corner_4.setGeometry(QtCore.QRect(0, self.height() - 103, 103, 103))
        self.BG_horiz.setGeometry(QtCore.QRect(self.place_for_border, 100 + self.place_for_border, self.width() - self.place_for_border*2, self.height() - (200 + self.place_for_border)))
        self.BG_vert.setGeometry(QtCore.QRect(100 + self.place_for_border, self.place_for_border, self.width() - (200 + self.place_for_border*2), self.height() - self.place_for_border*2))

        self.interface.setGeometry(QtCore.QRect(self.place_for_border + 250, self.place_for_border, self.size().width() - (self.place_for_border + 250), self.size().height() - self.place_for_border * 2))
        self.interface.optimize_interface()
        self.scrler.setGeometry(QtCore.QRect(253, 3, 12, self.height() - 6))
        self.refresh_btn.move(self.place_for_border + 233, self.place_for_border + 41)
        self.refresh_anim_holder.setGeometry(QtCore.QRect(self.place_for_border + 231, self.place_for_border + 39, 19, 19))
        self.mvbl_win_BTN.setGeometry(QtCore.QRect(self.width() - (51 + self.place_for_border), self.height() - (51 + self.place_for_border), 40, 40))
        self.resize_win_BTN.setGeometry(QtCore.QRect(self.width() - (100 + self.place_for_border), self.height() - (51 + self.place_for_border), 40, 40))
        self.move_roundler.setGeometry(QtCore.QRect(self.width() - (43 + self.place_for_border), self.height() - (43 + self.place_for_border), 24, 24))
        self.resize_roundler.setGeometry(QtCore.QRect(self.width() - (92 + self.place_for_border), self.height() - (43 + self.place_for_border), 24, 24))
        self.cls_btn.setGeometry(QtCore.QRect((self.width() - (30 + self.place_for_border)), 14, 16, 16))
        self.rlup_btn.setGeometry(QtCore.QRect((self.width() - (54 + self.place_for_border)), 14, 16, 16))
        self.FS_btn.setGeometry(QtCore.QRect((self.width() - (78 + self.place_for_border)), 14, 16, 16))
        self.search.setGeometry(QtCore.QRect(3, self.height() - 43, 250, 40))
        
        self.cls_anim = QtCore.QPropertyAnimation(self.cls_btn, b'pos', self.central_widget)
        self.cls_anim.setDuration(400)
        self.cls_anim.setStartValue(QtCore.QPointF(self.cls_btn.pos().x(), 14))
        self.cls_anim.setKeyValueAt(0.15, QtCore.QPointF(self.cls_btn.pos().x(), 11))
        self.cls_anim.setEndValue(QtCore.QPointF(self.cls_btn.pos().x(), 14))

        self.rlup_anim = QtCore.QPropertyAnimation(self.rlup_btn, b'pos', self.central_widget)
        self.rlup_anim.setDuration(400)
        self.rlup_anim.setStartValue(QtCore.QPointF(self.rlup_btn.pos().x(), 14))
        self.rlup_anim.setKeyValueAt(0.15, QtCore.QPointF(self.rlup_btn.pos().x(), 11))
        self.rlup_anim.setEndValue(QtCore.QPointF(self.rlup_btn.pos().x(), 14))

        self.FS_anim = QtCore.QPropertyAnimation(self.FS_btn, b'pos', self.central_widget)
        self.FS_anim.setDuration(400)
        self.FS_anim.setStartValue(QtCore.QPointF(self.FS_btn.pos().x(), 14))
        self.FS_anim.setKeyValueAt(0.15, QtCore.QPointF(self.FS_btn.pos().x(), 11))
        self.FS_anim.setEndValue(QtCore.QPointF(self.FS_btn.pos().x(), 14))

    def maximise(self):
        self.cover_line.setVisible(False)

        self.corner_1.setVisible(False)
        self.corner_2.setVisible(False)
        self.corner_3.setVisible(False)
        self.corner_4.setVisible(False)
        self.BG_horiz.setGeometry(QtCore.QRect(0, 0, self.width(), self.height()))
        self.BG_vert.setVisible(False)
        self.gray_BG_horiz.setVisible(False)
        self.gray_BG_vert.setVisible(False)

        self.scrler.setGeometry(QtCore.QRect(253, 0, 12, self.height()))
        self.search.BG.setPixmap(QtGui.QPixmap('source/GUI/FS_search.png'))
        self.search.mode_holder.setGeometry(QtCore.QRect(9, 13, 47, 21))
        self.search.mode_holder_BG.setGeometry(QtCore.QRect(9, 13, 47, 21))
        self.search.search_btn.setGeometry(QtCore.QRect(211, 9, 28, 28))
        self.search.line.setGeometry(QtCore.QRect(59, 13, 160, 21))

        self.mvbl_win_BTN.setVisible(False)
        self.resize_win_BTN.setVisible(False)
        self.move_roundler.setVisible(False)
        self.resize_roundler.setVisible(False)
        self.cls_btn.setGeometry(QtCore.QRect((self.width() - (35 + self.place_for_border)), 14, 16, 16))
        self.rlup_btn.setGeometry(QtCore.QRect((self.width() - (59 + self.place_for_border)), 14, 16, 16))
        self.FS_btn.setGeometry(QtCore.QRect((self.width() - (83 + self.place_for_border)), 14, 16, 16))

        self.interface.setGeometry(QtCore.QRect(self.place_for_border + 250, self.place_for_border, self.size().width() - (self.place_for_border + 250), self.size().height() - self.place_for_border * 2))
        self.interface.optimize_interface()
        
        self.cls_anim = QtCore.QPropertyAnimation(self.cls_btn, b'pos', self.central_widget)
        self.cls_anim.setDuration(400)
        self.cls_anim.setStartValue(QtCore.QPointF(self.cls_btn.pos().x(), 14))
        self.cls_anim.setKeyValueAt(0.15, QtCore.QPointF(self.cls_btn.pos().x(), 11))
        self.cls_anim.setEndValue(QtCore.QPointF(self.cls_btn.pos().x(), 14))

        self.rlup_anim = QtCore.QPropertyAnimation(self.rlup_btn, b'pos', self.central_widget)
        self.rlup_anim.setDuration(400)
        self.rlup_anim.setStartValue(QtCore.QPointF(self.rlup_btn.pos().x(), 14))
        self.rlup_anim.setKeyValueAt(0.15, QtCore.QPointF(self.rlup_btn.pos().x(), 11))
        self.rlup_anim.setEndValue(QtCore.QPointF(self.rlup_btn.pos().x(), 14))

        self.FS_anim = QtCore.QPropertyAnimation(self.FS_btn, b'pos', self.central_widget)
        self.FS_anim.setDuration(400)
        self.FS_anim.setStartValue(QtCore.QPointF(self.FS_btn.pos().x(), 14))
        self.FS_anim.setKeyValueAt(0.15, QtCore.QPointF(self.FS_btn.pos().x(), 11))
        self.FS_anim.setEndValue(QtCore.QPointF(self.FS_btn.pos().x(), 14))

    def un_maximize(self):
        self.cover_line.setVisible(True)
        self.gray_BG_horiz.setVisible(True)
        self.gray_BG_vert.setVisible(True)

        self.scrler.setGeometry(QtCore.QRect(253, 3, 12, self.height() - 6))
        self.search.BG.setPixmap(QtGui.QPixmap('source/GUI/search.png'))
        self.search.mode_holder.setGeometry(QtCore.QRect(9, 4, 47, 21))
        self.search.mode_holder_BG.setGeometry(QtCore.QRect(9, 4, 47, 21))
        self.search.search_btn.setGeometry(QtCore.QRect(212, 0, 28, 28))
        self.search.line.setGeometry(QtCore.QRect(60, 4, 160, 21))

        self.corner_1.setVisible(True)
        self.corner_2.setVisible(True)
        self.corner_3.setVisible(True)
        self.corner_4.setVisible(True)
        self.BG_vert.setVisible(True)
        self.mvbl_win_BTN.setVisible(True)
        self.resize_win_BTN.setVisible(True)
        self.move_roundler.setVisible(True)
        self.resize_roundler.setVisible(True)
        self.optimize_win()

    def resizeEvent(self, event):
        self.scrler.setMaximum((MainWindow.max - (MainWindow.height() - 20) // 61))
        self.optimize_win()

    def refresh(self):
        for card in self.current_cards:
            card.setVisible(False)

        self.current_cards = []

        if self.scroll_value > len(self.cards) - (self.height() - 20) // 61 - 1:
            i = 61 + self.place_for_border
            for card in self.cards[(len(self.cards) - (self.height() - 10) // 61 + 1):]:
                self.current_cards.append(card)
                card.move(self.place_for_border, i)
                card.setVisible(True)
                i = i + 61
        else:
            i = 61 + self.place_for_border
            for card in self.cards[self.scroll_value:((self.height() - 10) // 61 - 1 + self.scroll_value)]:
                self.current_cards.append(card)
                card.move(self.place_for_border, i)
                card.setVisible(True)
                i = i + 61

    def upload_resolution(self):
        resolution = ''
        with open('source/params/resolution.txt', 'r') as resolution_file:
            resolution = resolution_file.read()
            if resolution != '' and 'x' in resolution:
                width = int(resolution.split('x')[0])
                height = int(resolution.split('x')[1])

        if resolution != '':
            if width != self.maximumWidth() or height != self.maximumHeight():
                if width < self.maximumWidth() and height < self.maximumHeight():
                    self.resize(QtCore.QSize(width, height))
                    self.refresh()
            else:
                self.case.animLabel.setPixmap(QtGui.QPixmap('source/GUI/full_BK_anim.png'))
                self.FS_btn.position = MainWindow.pos()

                self.FS_btn.size = MainWindow.size()
                self.showFullScreen()
                self.maximise()
                self.FS_btn.isMax = True
                self.refresh()
        else:
            return

    def closeEvent(self, event):
        self.isStopped = True
        self.isParsed = True
        if self.last_pen != None:
            try:
                self.last_pen.device()
                self.last_pen.end()
            except:
                pass
            del self.last_pen



class WaitWin(QtWidgets.QDialog):
    def __init__(self, main, th):
        super().__init__()
        self.thread_ = th
        self.isStarted = False
        self.main_win = main
        self.setWindowTitle('Loading...')
        self.BG = QtWidgets.QLabel(self)
        self.BG.setGeometry(QtCore.QRect(0, 0, 370, 204))
        self.BG.setPixmap(QtGui.QPixmap('source/GUI/wait_load_BG.png'))
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(370, 204)
        self.scr = QtWidgets.QLabel(self)
        self.scr.setGeometry(QtCore.QRect(0, 0, 370, 204))
        self.scr.show()
        self.top = QtWidgets.QLabel(self)
        self.top.setGeometry(QtCore.QRect(0, 0, 370, 204))
        self.top.setPixmap(QtGui.QPixmap('source/GUI/load_gif_top.png'))

        self.movie = QtGui.QMovie('source/gifs/load_gif.gif')
        self.scr.setMovie(self.movie)
        self.movie.finished.connect(self.check)
        self.movie.start()


    def check(self):
        self.isStarted = True
        if self.main_win.isParsed == False:
            self.movie.start()
        else:
            self.movie.stop()
            self.destroy()
            self.close()
            self.main_win.setObjectName('=')
            self.thread_.quit()



class thread(QtCore.QThread):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.win = WaitWin(main, self)

    def run(self):
        self.win = WaitWin(self.main, self)
        self.win.exec()
        


if __name__ == "__main__":
    np.errstate(all='ignore')
    prediction_model = KryptoModelWithAttention(size=(19, 32, 64, 128, 256), dropout=0, avg=1)
    weights = load('source/model_data/weights.pth', weights_only=True, map_location=device('cpu'))
    prediction_model.load_state_dict(weights)
    prediction_model = prediction_model.to(float32)
    prediction_model.eval()
    print('model loaded\n')
    
    with open('isFirst.txt', 'r') as file_:
            if file_.read() != '1':
                try:
                    elevate(show_console = False, graphical = True)
                except:
                    pass
                
    
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Windows')
    app.setApplicationName('Krypto Briefcase')
    # icon = QtGui.QIcon()
    # icon.addPixmap(QtGui.QPixmap('source/icon/icon.png'))
    # app.setWindowIcon(icon)
    
    MainWindow = MainWin(prediction_model)

    MainWindow.setMinimumSize(QtCore.QSize(800 + MainWindow.place_for_border*2, 420 + MainWindow.place_for_border*2))
    MainWindow.setMaximumSize(QtCore.QSize(app.primaryScreen().size().width(), app.primaryScreen().size().height()))
    MainWindow.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
    MainWindow.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    MainWindow.raise_()

    sys.exit(app.exec())