import argparse
import os

import torch
from torch.nn import MSELoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchvision import transforms

from yms_class.models.DECAE import DRCAE
from yms_class.models.autoencoder import Autoencoder
from yms_class.tools.dataset import create_dataloaders
from yms_class.tools.tool import append_to_results_file, initialize_results_file, make_save_dirs, \
    save_model_structure_to_txt
from yms_class.tools.train_eval_utils import train_decae_one_epoch, visualize_latent_space


def main(args):
    save_dir = args.save_dir
    img_dir, model_dir = make_save_dirs(save_dir)

    results_file = os.path.join(save_dir, 'decae_results.txt')
    decae_column_order = ['epoch', 'train_losses', 'val_losses', 'lrs']
    initialize_results_file(results_file, decae_column_order)
    custom_column_widths = {'epoch': 5, 'train_loss': 12, 'val_loss': 10, 'lr': 3}

    device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")
    print("Using {} device training.".format(device.type))
    transform = transforms.Compose([
        transforms.Resize((100, 100)),
        transforms.ToTensor(),
    ])
    train_loader, val_loader = create_dataloaders(args.data_dir, args.batch_size,transform=transform)
    metrics = {'train_losses': [], 'val_losses': [], 'lrs': []}

    model = DRCAE().to(device)
    save_model_structure_to_txt(model, os.path.join(model_dir, 'model_structure.txt'))
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.5, patience=5, min_lr=1e-9)
    criterion = MSELoss()
    best = 1e8
    for epoch in range(0, args.epochs):
        result = train_decae_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch)
        lr = lr_scheduler.get_last_lr()[0]
        lr_scheduler.step(result['val_loss'])

        metrics['val_losses'].append(result['val_loss'])
        metrics['train_losses'].append(result['train_loss'])
        metrics['lrs'].append(lr)
        result.update({'lr': lr})

        append_to_results_file(results_file, result, decae_column_order,
                               custom_column_widths=custom_column_widths)

        # save_file = {
        #     'epoch': epoch,
        #     'model_state_dict': model,
        #     'optimizer_state_dict': optimizer,
        #     'lr_scheduler_state_dict': lr_scheduler,
        # }
        # torch.save(save_file, os.path.join(model_dir, 'last_decoder.pt'))
        if result['val_loss'] < best:
            best = result['val_loss']
            torch.save(model, os.path.join(model_dir, 'model.pt'))
            model.save(os.path.join(model_dir, 'encoder.pt'))
            visualize_latent_space(model, train_loader, device, img_dir, epoch)
            print(f'Best model saved at epoch {epoch + 1} with F1-val_loss: {best:.6f}')

    # plot_all_metrics(metrics, args.epochs, 'decoder', img_dir)
    # os.remove(os.path.join(model_dir, 'last_decoder.pt'))


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default=r'D:\Code\0-data\7-images\2-wear\Nscales(1-3)')
    parser.add_argument('--save_dir', type=str, default=r'test')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch_size', type=int, default=10)
    parser.add_argument('--lr', type=float, default=1e-3)
    return parser.parse_args(args if args else [])


if __name__ == '__main__':
    opts = parse_args()
    print(opts)
    main(opts)
