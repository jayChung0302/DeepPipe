from pytorch_grad_cam import GradCAM, ScoreCAM, GradCAMPlusPlus, AblationCAM, XGradCAM, EigenCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from torchvision.models import resnet50
import torchvision.transforms as transforms

import PIL.Image as Image
import matplotlib.pyplot as plt
import numpy as np

model = resnet50(pretrained=True)
target_layer = model.layer4[-1]
input = Image.open('../Image.jpeg')
transform = transforms.Compose([
    # transforms.Resize((224,224)),
    transforms.ToTensor()
])
input_tensor = transform(input)
# Create an input tensor image for your model..
# Note: input_tensor can be a batch tensor with several images!

# Construct the CAM object once, and then re-use it on many images:
cam = GradCAM(model=model, target_layer=target_layer, use_cuda=False)

# If target_category is None, the highest scoring category
# will be used for every image in the batch.
# target_category can also be an integer, or a list of different integers
# for every image in the batch.
target_category = 1

# You can also pass aug_smooth=True and eigen_smooth=True, to apply smoothing.
grayscale_cam = cam(input_tensor=input_tensor.unsqueeze(0), target_category=target_category)

# In this example grayscale_cam has only one image in the batch:
grayscale_cam = grayscale_cam[0, :]
x = input_tensor.numpy()
x = np.transpose(x, (1,2,0))
visualization = show_cam_on_image(x, grayscale_cam)
print(grayscale_cam.shape)

plt.imsave('awef3.jpg',visualization)
plt.imshow(visualization)

