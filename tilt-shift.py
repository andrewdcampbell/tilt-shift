import argparse
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt

SHOULD_RESIZE = True
RESIZE_WIDTH = 1600

def resize(image, width):
    h, w = image.shape[:2]
    dim = (width, int(h * width / float(w)))
    return cv2.resize(image, dim)

def boost_colors(im, value=10.0):
    hsv_im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    # increase saturation
    hsv_im[...,1] = cv2.add(hsv_im[...,1], np.array([value]))
    # increase brightness
    hsv_im[...,2] = cv2.add(hsv_im[...,2], np.array([value]))
    return cv2.cvtColor(hsv_im, cv2.COLOR_HSV2BGR)

def choose_focus_height(im):
    plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    x, y = plt.ginput(1)[0]
    plt.close()
    return int(y)

def tilt_shift(im, dof=60, enhance=True, focus_height=None):
    if focus_height is None:
        focus_height = choose_focus_height(im)

    assert dof >= 10, "DOF width too small"
    assert focus_height > 2*dof and focus_height < im.shape[0] - 2*dof, "Out of range"

    above_focus, below_focus = im[:focus_height,:], im[focus_height:,:]
    above_focus = increasing_blur(above_focus[::-1,...], dof)[::-1,...]
    below_focus = increasing_blur(below_focus, dof)
    out = np.vstack((above_focus, below_focus))
    if enhance:
        out = boost_colors(out)
    return out

def increasing_blur(im, dof=60):
    BLEND_WIDTH = dof
    blur_region = cv2.GaussianBlur(im[dof:,:], ksize=(15,15), sigmaX=0)
    if blur_region.shape[0] > dof*2:
        blur_region = increasing_blur(blur_region, dof)
    blend_col = np.linspace(1.0, 0, num=BLEND_WIDTH)
    blend_mask = np.tile(blend_col, (im.shape[1], 1)).T
    res = np.zeros_like(im)
    res[:dof,:] = im[:dof,:]
    # alpha blend region of width BLEND_WIDTH to hide seams between blur layers
    res[dof:dof+BLEND_WIDTH,:] = im[dof:dof+BLEND_WIDTH,:] * blend_mask[:, :, None] + \
        blur_region[:BLEND_WIDTH,:] * (1-blend_mask[:, :, None])
    res[dof+BLEND_WIDTH:,:] = blur_region[BLEND_WIDTH:]
    return res

def tilt_shift_video(vid_files, dof=30, enhance=True, FPS=25.0):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out, w, h = None, None, None

    for vid_path in vid_files:
        focus_height = None
        cap = cv2.VideoCapture(vid_path)

        if out is None:
            # w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            # h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # hardcoding dimensions to be 1280x720
            out = cv2.VideoWriter('output.mp4', fourcc, FPS, (1280, 720))

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            frame = resize(frame, width=1280)
            if focus_height is None:
                focus_height = choose_focus_height(frame)            
            tilt_shift_frame = tilt_shift(frame, dof, enhance, focus_height)
            out.write(tilt_shift_frame)
            cv2.imshow("window", tilt_shift_frame); cv2.waitKey(1)
        cap.release()
    
    out.release()
    cv2.destroyAllWindows(); cv2.waitKey(1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)   
    group.add_argument("-im", help="Path to image")
    group.add_argument("-vid", help="Path to directory of videos (with same aspect ratio)")
    ap.add_argument("-dof", help="DOF (in pixels)", type=int, default=60)
    ap.add_argument("-no_enhance", help="Do not increase saturation/brightness", 
        action='store_true')
    args = vars(ap.parse_args())

    IM_FILE, VID_DIR, DOF, NO_ENHANCE = args["im"], args["vid"], args["dof"], args["no_enhance"]

    if IM_FILE:
        im = cv2.imread(IM_FILE)
        if SHOULD_RESIZE:
            im = resize(im, width=RESIZE_WIDTH)
        out = tilt_shift(im, DOF, enhance=not NO_ENHANCE)
        filename = os.path.basename(IM_FILE).split('.')[0]
        output_name = "{}_{}.jpg".format(filename, DOF)
        cv2.imwrite(output_name, out.astype(np.uint8))
    
    elif VID_DIR:
        valid_formats = [".mp4"] # haven't tested with other formats
        get_ext = lambda f: os.path.splitext(f)[1].lower()
        VID_FILES = [VID_DIR+"/"+f for f in os.listdir(VID_DIR) if get_ext(f) in valid_formats]
        tilt_shift_video(VID_FILES, dof=DOF, enhance=not NO_ENHANCE)
    
