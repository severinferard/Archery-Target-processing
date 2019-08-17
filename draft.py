import cv2
import numpy as np
import math

def change_to_flat(ellipse_center, ellipse_axe_a, ellipse_axe_b, points):
    new_points = []
    for point in points:
        xc = ellipse_center[0]
        yc = ellipse_center[1]
        A = ellipse_axe_a
        B = ellipse_axe_b
        angle = 1
        # angle = math.radians(angle)
        cv2.ellipse(black, (xc, yc), (A, B), 0, 0, 360, (255, 255, 255), 3)
        angle = -1 * math.radians(angle)

        xp = point[0]
        yp = point[1]
        cv2.circle(black, (xp, yp), 8, (255, 255, 255), -1)
        cv2.circle(black, (xc, yc), 8, (255, 0, 0), -1)




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
        cv2.circle(black, (int(x), int(y)), 20, (0, 0, 255), -1)

        r_ellipse = math.sqrt((x - xc)**2 + (y - yc)**2)
        ratio = r / r_ellipse
        print("ratio", ratio)



        new_points.append((ratio, alpha))
    return(new_points)


black = np.zeros((2000, 2000, 3), dtype=np.uint8)

points = [(1227, 1470), (1286, 1049), (1254, 974), (1081, 1358)]
new_points = change_to_flat((1170, 1200), 282, 484, points)


cv2.circle(black, (1000, 1000), 300, (0, 255, 0), 3)
for point in new_points:
    ratio = point[0]
    alpha = point[1]
    circle_r = 300
    new_x = (circle_r * ratio) * math.cos(alpha)
    new_y = (circle_r * ratio) * math.sin(alpha)
    cv2.circle(black, (int(new_x + 1000), int(new_y + 1000)), 20, (0, 255, 0), -1)



cv2.imshow("black", cv2.resize(black, (500, 500)))
cv2.waitKey(0)
