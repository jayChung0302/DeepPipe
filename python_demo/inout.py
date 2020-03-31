import os
import sys
import time
import argparse
import csv
import datetime

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
# from torchvision.utils import save_image
from key_frame_selection import key_extraction


parser = argparse.ArgumentParser()
parser.add_argument('--video_dir', type=str, help='set video directory', default='sample/GR504.AVI')
parser.add_argument('--output_dir', type=str, help='set directory for saving defect images and txt file',
                    default='jpegs/')

args = parser.parse_args()


def save_image(tensor, filename, nrow=1, padding=1,
               normalize=False, range=None, scale_each=False, pad_value=0):
    """Save a given Tensor into an image file.

    Args:
        tensor (Tensor or list): Image to be saved. If given a mini-batch tensor,
            saves the tensor as a grid of images by calling ``make_grid``.
        **kwargs: Other arguments are documented in ``make_grid``.
    """
    from PIL import Image
    grid = make_grid(tensor, nrow=nrow, padding=padding, pad_value=pad_value,
                     normalize=normalize, range=range, scale_each=scale_each)
    ndarr = grid.mul(255).clamp(0, 255).byte().permute(1, 2, 0).cpu().numpy()
    im = Image.fromarray(ndarr)
    im.save(filename)

def make_grid(tensor, nrow=8, padding=2,
              normalize=False, range=None, scale_each=False, pad_value=0):
    """Make a grid of images.

    Args:
        tensor (Tensor or list): 4D mini-batch Tensor of shape (B x C x H x W)
            or a list of images all of the same size.
        nrow (int, optional): Number of images displayed in each row of the grid.
            The Final grid size is (B / nrow, nrow). Default is 8.
        padding (int, optional): amount of padding. Default is 2.
        normalize (bool, optional): If True, shift the image to the range (0, 1),
            by subtracting the minimum and dividing by the maximum pixel value.
        range (tuple, optional): tuple (min, max) where min and max are numbers,
            then these numbers are used to normalize the image. By default, min and max
            are computed from the tensor.
        scale_each (bool, optional): If True, scale each image in the batch of
            images separately rather than the (min, max) over all images.
        pad_value (float, optional): Value for the padded pixels.

    Example:
        See this notebook `here <https://gist.github.com/anonymous/bf16430f7750c023141c562f3e9f2a91>`_

    """
    if not (torch.is_tensor(tensor) or
            (isinstance(tensor, list) and all(torch.is_tensor(t) for t in tensor))):
        raise TypeError('tensor or list of tensors expected, got {}'.format(type(tensor)))

    # if list of tensors, convert to a 4D mini-batch Tensor
    if isinstance(tensor, list):
        tensor = torch.stack(tensor, dim=0)

    if tensor.dim() == 2:  # single image H x W
        tensor = tensor.view(1, tensor.size(0), tensor.size(1))
    if tensor.dim() == 3:  # single image
        if tensor.size(0) == 1:  # if single-channel, convert to 3-channel
            tensor = torch.cat((tensor, tensor, tensor), 0)
        tensor = tensor.view(1, tensor.size(0), tensor.size(1), tensor.size(2))

    if tensor.dim() == 4 and tensor.size(1) == 1:  # single-channel images
        tensor = torch.cat((tensor, tensor, tensor), 1)

    if normalize is True:
        tensor = tensor.clone()  # avoid modifying tensor in-place
        if range is not None:
            assert isinstance(range, tuple), \
                "range has to be a tuple (min, max) if specified. min and max are numbers"

        def norm_ip(img, min, max):
            img.clamp_(min=min, max=max)
            img.add_(-min).div_(max - min + 1e-5)

        def norm_range(t, range):
            if range is not None:
                norm_ip(t, range[0], range[1])
            else:
                norm_ip(t, float(t.min()), float(t.max()))

        if scale_each is True:
            for t in tensor:  # loop over mini-batch dimension
                norm_range(t, range)
        else:
            norm_range(tensor, range)

    if tensor.size(0) == 1:
        return tensor.squeeze()

    # make the mini-batch of images into a grid
    nmaps = tensor.size(0)
    xmaps = min(nrow, nmaps)
    ymaps = int(math.ceil(float(nmaps) / xmaps))
    height, width = int(tensor.size(2) + padding), int(tensor.size(3) + padding)
    grid = tensor.new(3, height * ymaps + padding, width * xmaps + padding).fill_(pad_value)
    k = 0
    for y in irange(ymaps):
        for x in irange(xmaps):
            if k >= nmaps:
                break
            grid.narrow(1, y * height + padding, height - padding)\
                .narrow(2, x * width + padding, width - padding)\
                .copy_(tensor[k])
            k = k + 1
    return grid


# input : video directory, output image directory
# output : defect image, text file with time and location
def main(args):
    start_time = time.time()
    dt = datetime.datetime.now()
    logname = 'defects.txt'
    with open(args.output_dir + logname, 'w') as f:
        f.write(str(dt.year))
        f.write(str(dt.month))
        f.write(str(dt.day))
        f.write(' pipe inspection results\n')

    # TODO: loading pre-trained neural network
    """
    net = torch.load('')
    """
    vid = cv2.VideoCapture(args.video_dir)
    fps = int(vid.get(cv2.CAP_PROP_FPS))

    frameCount = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    frameWidth = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print('# of video frames : {}\nwidth : {} \nheight : {}\nfps : {}'.format(frameCount, frameWidth, frameHeight, fps))
    uf = np.empty((64, frameHeight, frameWidth, 3), dtype=np.float32)
    idx, j = 0, 0
    while vid.isOpened():

        ret, frame = vid.read()
        if ret:
            frame = np.asarray((frame / 255.) * 2 - 1, dtype=np.float32)
            uf[j] = frame[:, :, [2, 1, 0]]

        else:

            break

        idx = idx + 1
        j = j + 1

        # Early stopping, for simplifying demo
        if idx == 641:
            print('process exiting ..')
            print('processing time : {}'.format(time.time() - start_time))
            sys.exit()

        # suspicious image is inspected every 1 second.
        if idx % 64 == 0:
            j = 0

            vid_tensor = torch.from_numpy(uf).permute(3, 0, 1, 2).unsqueeze(0)

            key_index = key_extraction(vid_tensor)
            time_stamp = idx / fps

            save_image((vid_tensor[:, :, key_index, :, :].squeeze() + 1) / 2,
                       args.output_dir + 'defectName' + str(idx) + '.png')

            # TODO : label 2 defect name

            uf = np.empty((64, frameHeight, frameWidth, 3), dtype= np.float32)

            with open(args.output_dir + logname, 'a') as logfile:
                logfile.write('{:.4f}, defectName, {}\n'.format(time_stamp, idx))

    vid.release()
    print('process exiting ..')
    print('processing time : {}'.format(time.time() - start_time))


if __name__ == '__main__':
    main(args)
