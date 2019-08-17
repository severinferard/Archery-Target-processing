import cv2
import numpy as np
import pandas as pd
import io
import logging
import math
import inspect
import os
import math


class ArrowHandler:

    def __init__(self, side):
        assert side == "LEFT" or side == "RIGHT"
        self.side = side

    def __repr__(self):
        return "{}(side:{})".format(__class__, self.side)

    def no_display(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result[0]
        return wrapper

    def display(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            n = 1
            for mask in result[1]:
                cv2.imshow(f"mask {n}", cv2.resize(mask, (500, 500)))
                cv2.waitKey(1)
                n += 1
            return result[0]
        return wrapper

    def prep_for_houghline(self, scale=1, delta=9, ksize=3, thresh_para=120):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        ddepth = cv2.CV_16S
        grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=ksize,
                            scale=scale, delta=delta,
                            borderType=cv2.BORDER_DEFAULT)
        grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=ksize,
                            scale=scale, delta=delta,
                            borderType=cv2.BORDER_DEFAULT)
        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

        return cv2.threshold(grad, thresh_para, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    def calibrate(self, image):
        if self.side == "RIGHT":
            self.img = cv2.flip(image, 1)
            self.img = cv2.resize(self.img, (2000, 2000))
        else:
            self.img = cv2.resize(image, (2000, 2000))
        ret, th1 = self.prep_for_houghline()
        self.last_lines = cv2.HoughLinesP(image=th1, rho=1,
                                            theta=np.pi / 180,
                                            threshold=80,
                                            lines=None,
                                            minLineLength=100,
                                            maxLineGap=5)
        self.findTarget(self.img)
        return

    @no_display
    def findTarget(self, image):
        copy = image.copy()

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 150])
        upper_white = np.array([145,60, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        res = cv2.bitwise_and(image, image, mask= mask)

        imgray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
        inverted = cv2.bitwise_not(imgray)
        inverted = cv2.blur(inverted, (5,5))

        ret,thresh = cv2.threshold(inverted,127,255,0)
        border = 0
        with_border = cv2.copyMakeBorder(thresh, border, border, border, border,
                                     cv2.BORDER_CONSTANT, value=(255, 255, 255))
        copy = cv2.copyMakeBorder(copy, border, border, border, border,
                                     cv2.BORDER_CONSTANT, value=(255, 255, 255))
        contours, hierarchy = cv2.findContours(with_border, cv2.cv2.RETR_LIST,
                                                cv2.CHAIN_APPROX_NONE)

        contours_sized = sorted(contours, key = cv2.contourArea)
        try:
            self.target_space = contours_sized[-2]
        except IndexError:
            print("no target found")
            self.target_space = contours_sized[-1]
        cv2.drawContours(image, self.target_space, -1, (0,255,0), 3)
        return None, (image,)

    @no_display
    def newest_impact(self, image):
        if self.side == "RIGHT":
            self.img = cv2.flip(image, 3)
            self.img = cv2.resize(self.img, (2000, 2000))
        else:
            self.img = cv2.resize(image, (2000, 2000))

        ret, th1 = self.prep_for_houghline()
        self.lines = cv2.HoughLinesP(image=th1, rho=1,
                                    theta=np.pi / 180,
                                    threshold=200,
                                    lines=None,
                                    minLineLength=100,
                                    maxLineGap=5)

        self.mask = np.zeros(self.img.shape, dtype=np.uint8)
        coefth = 0
        for line in self.lines:
            x1, y1, x2, y2 = line[0]
            if x1 > x2:
                x1, y1, x2, y2 = x2, y2, x1, y1

            coef = (y2 - y1) / (x2 - x1)
            if coef > coefth and coef < coefth + 1:
                cv2.line(img=self.mask,
                            pt1=(x1, y1),
                            pt2=(x2, y2),
                            color=(0, 0, 255),
                            thickness=3)

        first_mask = self.mask.copy()

        for line in self.last_lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img=self.mask,
                            pt1=(x1, y1),
                            pt2=(x2, y2),
                            color=(0, 0, 0),
                            thickness=20)

        second_mask = self.mask.copy()

        self.grayed_mask = cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)
        self.new_lines = cv2.HoughLinesP(image=self.grayed_mask, rho=1,
                                            theta=np.pi / 180,
                                            threshold=80,
                                            lines=None,
                                            minLineLength=100,
                                            maxLineGap=5)

        if self.new_lines is not None:
            for line in self.new_lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(img=self.img,
                            pt1=(x1, y1),
                            pt2=(x2, y2),
                            color=(0, 255, 0),
                            thickness=4)

            xmincoord = (2000, None)
            for line in self.new_lines:
                x1, y1, x2, y2 = line[0]
                xmin = xmincoord[0]
                if x1 < xmin:
                    xmincoord = (x1, y1)

            cv2.circle(self.img, xmincoord, 8, (0, 255, 255), -1)
            self.last_lines = np.concatenate((self.last_lines, self.new_lines),
                                                axis=0)

            if cv2.pointPolygonTest(self.target_space, xmincoord, False) == 1:
                return(xmincoord, (first_mask, second_mask))

        return(None, (first_mask, second_mask))

    def get_point(self, impact, zones):
        black = np.zeros((2000, 2000, 3), dtype=np.uint8)
        sorted_zones = sorted(zones, key=cv2.contourArea, reverse=False)
        score = 10
        for zone in sorted_zones:
            cv2.drawContours(black, zone, -1, (255, 0, 0), 5)
            if cv2.pointPolygonTest(zone, impact, False) == 1:
                return score

            score -= 1
        return 0


class TargetHandler:

    def __init__(self, side):
        assert side == "LEFT" or side == "RIGHT"
        self.side = side

    def findZones(self, image):
        if self.side == "RIGHT":
            image = cv2.flip(image, 1)
            image = cv2.resize(image, (2000, 2000))
        else:
            image = cv2.resize(image, (2000, 2000))

        img = cv2.medianBlur(image, 5)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_red = np.array([20, 100, 100])
        upper_red = np.array([100, 255, 200])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        res = cv2.bitwise_and(image, image, mask=mask)

        contours, hierarchy = cv2.findContours(mask,
                                            cv2.cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_NONE)
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

        
        for contour in sorted_contours[:1]:
            cv2.drawContours(image, contour, -1, (0, 0, 255), 3)
            e = cv2.fitEllipse(contour)

        xc = int(e[0][0])
        yc = int(e[0][1])
        a = int(e[1][0] / 2)
        b = int(e[1][1] / 2)
        theta = e[2]
        black = np.zeros(image.shape, dtype=np.uint8)
        for i in range(1, 7, 1):
            A = int((i / 6) * a)
            B = int((i / 6) * b)
            cv2.ellipse(black, (xc, yc), (A, B), theta, 0, 360, (255, 255, 255), 3)

        gray_ellipses = cv2.cvtColor(black, cv2.COLOR_BGR2GRAY)
        ellipse_contours, _ = cv2.findContours(gray_ellipses, cv2.RETR_LIST,
                                                    cv2.CHAIN_APPROX_NONE)
        sorted_ellipse_contours = sorted(ellipse_contours, key=cv2.contourArea,
                                                            reverse=True)
        result = []
        for i in range(0, len(sorted_ellipse_contours), 2):
            result.append(sorted_ellipse_contours[i])

        for contour in result:
            cv2.drawContours(image, contour, -1, (255, 0, 0), 1)

        self.zones = result
        self.main_ellipse = {"center":(xc, yc), "a":a, "b":b, "angle": theta}
        return result

    def change_to_flat(self, ellipse_center, ellipse_axe_a, ellipse_axe_b, point):
        new_points = []

        xc = ellipse_center[0]
        yc = ellipse_center[1]
        A = ellipse_axe_a
        B = ellipse_axe_b
        angle = 1
        # angle = math.radians(angle)
        # cv2.ellipse(black, (xc, yc), (A, B), 0, 0, 360, (255, 255, 255), 3)
        angle = -1 * math.radians(angle)

        xp = point[0]
        yp = point[1]
        # cv2.circle(black, (xp, yp), 8, (255, 255, 255), -1)
        # cv2.circle(black, (xc, yc), 8, (255, 0, 0), -1)

        r = math.sqrt((xp - xc)**2 + (yp - yc)**2)
        alpha = math.atan2(yp-yc, xp-xc)

        xn = A * math.cos(alpha + angle)+xc
        yn = B * math.sin(alpha + angle)+xc
        print(xn, yn)

        # cv2.circle(black, (int(xn), int(yn)), 20, (255, 255, 255), -1)

        beta = alpha - angle
        print("alpha", alpha)
        print("angle", angle)
        print("beta", beta)
        x = (A*B*math.cos(beta)) / math.sqrt( (B**2) * (math.cos(beta))**2 + (A**2) * (math.sin(beta))**2)+xc
        y = (A*B*math.sin(beta)) / math.sqrt( (B**2) * (math.cos(beta))**2 + (A**2) * (math.sin(beta))**2)+yc
        # cv2.circle(black, (int(x), int(y)), 20, (0, 0, 255), -1)

        r_ellipse = math.sqrt((x - xc)**2 + (y - yc)**2)
        ratio = r / r_ellipse
        print("ratio", ratio)

        return((ratio, alpha))
