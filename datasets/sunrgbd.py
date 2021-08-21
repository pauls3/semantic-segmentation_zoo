import torch 
from torch import Tensor
from torch.utils.data import Dataset, DataLoader
from torchvision import io
from pathlib import Path
from typing import Tuple


class SunRGBD(Dataset):
    """
    num_classes: 150
    """
    CLASSES = []

    PALETTE = torch.tensor()

    def __init__(self, root: str, split: str = 'train', transform = None) -> None:
        super().__init__()
        assert split in ['train', 'val']
        split = 'training' if split == 'train' else 'validation'

        self.transform = transform
        self.n_classes = len(self.CLASSES)
        self.ignore_label = -1

        img_path = Path(root) / 'images' / split 
        self.files = list(img_path.glob('*.jpg'))
    
        if not self.files:
            raise Exception(f"No images found in {img_path}")

        print(f"Found {len(self.files)} {split} images.")

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, index: int) -> Tuple[Tensor, Tensor]:
        img_path = str(self.files[index])
        lbl_path = str(self.files[index]).replace('images', 'annotations').replace('.jpg', '.png')

        image = io.read_image(img_path)
        label = io.read_image(lbl_path)
        
        if self.transform:
            image, label = self.transform(image, label)
        return image, label.squeeze().long() - 1    # subtract -1 since original label index starts from 1
        
    def decode(self, label: Tensor) -> Tensor:
        return self.PALETTE[label.to(int)]


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from torchvision import transforms as T
    from torchvision.utils import make_grid
    from transforms import Compose, ResizePad, Normalize, RandomResizedCrop

    root = 'C:\\Users\\sithu\\Documents\\Datasets\\ADEChallenge\\ADEChallengeData2016'
    transform = Compose([RandomResizedCrop((512, 512)), Normalize()])

    dataset = ADE20K(root, split="train", transform=transform)
    dataloader = DataLoader(dataset, shuffle=True, batch_size=4)
    image, label = next(iter(dataloader))
    print(image.shape, label.shape)
    print(label.unique())
    label[label == -1] = 0
    labels = [dataset.decode(lbl).permute(2, 0, 1) for lbl in label]
    labels = torch.stack(labels)

    inv_normalize = T.Normalize(
        mean=(-0.485/0.229, -0.456/0.224, -0.406/0.225),
        std=(1/0.229, 1/0.224, 1/0.225)
    )
    image = inv_normalize(image)
    image *= 255
    images = torch.vstack([image, labels])
    
    plt.imshow(make_grid(images, nrow=4).to(torch.uint8).numpy().transpose((1, 2, 0)))
    plt.show()