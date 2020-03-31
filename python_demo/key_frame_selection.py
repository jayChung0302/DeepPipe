import torch
import cv2
import operator
import numpy as np


def smooth(x, window_len=13, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.
    output:
        the smoothed signal

    example:
    import numpy as np
    t = np.linspace(-2,2,0.1)
    x = np.sin(t)+np.random.randn(len(t))*0.1
    y = smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
    """
    if x.ndim != 1:
        print("smooth only accepts 1 dimension arrays.")
        raise ValueError

    if x.size < window_len:
        print("Input vector needs to be bigger than window size.")
        raise ValueError

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        print("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
        raise ValueError

    s = np.r_[2 * x[0] - x[window_len:1:-1],
              x, 2 * x[-1] - x[-1:-window_len:-1]]
    # print(len(s))

    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w / w.sum(), s, mode='same')
    return y[window_len - 1:-window_len + 1]


# Class to hold information about each frame


class Frame:
    def __init__(self, id, frame, value):
        self.id = id
        self.frame = frame
        self.value = value

    def __lt__(self, other):
        if self.id == other.id:
            return self.id < other.id
        return self.id < other.id

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.id == other.id and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


def rel_change(a, b):
    x = (b - a) / max(a, b)
    # print(x)
    return x


def key_extraction(video_tensor, USE_TOP_ORDER=True, USE_THRESH=False, USE_LOCAL_MAXIMA=False,
                   THRESH=0.6, NUM_TOP_FRAMES=1, len_window=13, dir=''):

    # cap = cv2.VideoCapture(str(videopath))

    curr_frame = None
    prev_frame = None

    frame_diffs = []
    frames = []
    # ret, frame = cap.read()
    i = 1
    key_list = []
    for j in range(video_tensor.size(0)):
        for i in range(video_tensor.size(2)):
            frame = video_tensor[j, :, i, :, :]
            frame = frame.numpy().transpose((1, 2, 0))
            b, g, r = frame[:, :, 0], frame[:, :, 1], frame[:, :, 2]
            frame = np.asarray((r, g, b), dtype=np.uint8).transpose((1, 2, 0))

            luv = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
            curr_frame = luv
            if curr_frame is not None and prev_frame is not None:
                # logic here
                diff = cv2.absdiff(curr_frame, prev_frame)
                count = np.sum(diff)
                frame_diffs.append(count)
                frame = Frame(i, frame, count)
                frames.append(frame)
            prev_frame = curr_frame
            i = i + 1
            # ret, frame = cap.read()

            # cv2.imshow('frame',luv)
            # # if cv2.waitKey(1) & 0xFF == ord('q'):
            # #     break


        if USE_TOP_ORDER:
            # sort the list in descending order
            frames.sort(key=operator.attrgetter("value"), reverse=True)

            for keyframe in frames[:NUM_TOP_FRAMES]:
                key_list.append(keyframe.id)

        curr_frame = None
        prev_frame = None

        frame_diffs = []
        frames = []

    return key_list



if __name__ == '__main__':
    video = torch.randn(5, 3, 64, 224, 224)
    k = key_extraction(video, True, False, False, dir='video_demo', NUM_TOP_FRAMES=1)
    print(k)