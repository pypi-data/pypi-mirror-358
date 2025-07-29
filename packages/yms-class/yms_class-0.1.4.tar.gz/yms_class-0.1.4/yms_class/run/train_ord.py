import os
import time
from datetime import timedelta

import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchvision import transforms

from yms_class.models.OrdinalRegression import ContinuousTransitionCNN, train_model, val_model
from yms_class.tools.dataset import create_dataloaders
from yms_class.tools.tool import make_save_dirs, initialize_results_file, save_model_structure_to_txt, \
    append_to_results_file, calculate_metric


def main(args):
    # 创建输出文件夹
    save_dir = args.save_dir
    img_dir, model_dir = make_save_dirs(save_dir)

    results_file = os.path.join(save_dir, 'results.txt')
    column_order = ['epoch', 'train_losses', 'val_losses', 'accuracies', 'precisions', 'recalls',
                    'f1-scores', 'lrs']
    initialize_results_file(results_file, column_order)
    custom_column_widths = {'epoch': 5, 'train_loss': 12, 'val_loss': 10, 'accuracy': 10, 'precision': 9, 'recall': 7,
                            'f1-score': 8, 'lr': 3}

    device = torch.device('cuda:0' if torch.cuda.is_available() else "cpu")
    print("Using {} device training.".format(device.type))

    transform = transforms.Compose([
        transforms.Resize((100, 100)),
        transforms.ToTensor(),
        # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    train_loader, val_loader = create_dataloaders(args.data_dir, args.batch_size, transform=transform)
    classes = train_loader.dataset.classes
    metrics = {'train_losses': [], 'val_losses': [], 'accuracies': [], 'precisions': [], 'recalls': [], 'f1-scores': [],
               'lrs': []}

    model = ContinuousTransitionCNN(lambda_reg=0.5)
    save_model_structure_to_txt(model, os.path.join(model_dir, 'model_structure.txt'))
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    lr_scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.5, patience=5, min_lr=1e-9)
    best = -1
    num_epochs = args.epochs

    # 添加早停相关参数
    patience = args.patience  # 从外部参数获取耐心值
    early_stop_counter = 0  # 早停计数器
    best_epoch = 0  # 最佳模型的epoch

    start_time = time.time()
    for epoch in range(0, num_epochs):
        training_lr = lr_scheduler.get_last_lr()[0]
        train_loss, train_accuracy = train_model(model=model, train_loader=train_loader, device=device,
                                                     optimizer=optimizer, epoch=epoch)
        print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy:.2%},'
              f'lr: {training_lr}')

        result = val_model(model=model, val_loader=val_loader,
                                device=device, epoch=epoch)

        metric = calculate_metric(result['y_true'], result['y_pred'], classes)
        print(f'val epoch {epoch + 1}, val loss: {result["val_loss"]:.4f}, accuracy: {metric["accuracy"]:.2%}')
        metrics['train_losses'].append(train_loss)
        metrics['val_losses'].append(result['val_loss'])
        metrics['accuracies'].append(metric['accuracy'])
        metrics['precisions'].append(metric['precision'])
        metrics['recalls'].append(metric['recall'])
        metrics['f1-scores'].append(metric['f1-score'])
        metrics['lrs'].append(training_lr)

        metric.update({'epoch': epoch, 'train_loss': train_loss, 'val_loss': result['val_loss'], 'lr': training_lr})
        append_to_results_file(results_file, metric, column_order,
                               custom_column_widths=custom_column_widths)
        # 早停逻辑
        current_score = metric['f1-score']
        if current_score > best:
            best = current_score
            best_epoch = epoch
            early_stop_counter = 0  # 重置早停计数器
            torch.save(model, os.path.join(model_dir, 'best_model.pt'))
            print(f'Best model saved at epoch {epoch + 1} with F1-score: {best:.4f}')
        elif patience > 0 and training_lr < (args.lr * 0.01) and epoch > (num_epochs * 0.6):  # 仅当patience>0时执行早停计数
            early_stop_counter += 1
            print(f'Early stopping counter: {early_stop_counter}/{patience}')

            # 如果早停计数器达到耐心值，停止训练
            if early_stop_counter >= patience:
                print(f'Early stopping triggered after {epoch + 1} epochs')
                print(f'Best model was saved at epoch {best_epoch + 1} with F1-score: {best:.4f}')
                break

        lr_scheduler.step(result['val_loss'])  # 更新学习率

    total_time = time.time() - start_time
    total_time_str = str(timedelta(seconds=int(total_time)))
    print('Training time {}'.format(total_time_str))

def parse_args(args=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data_dir', default=r'D:\Code\0-data\7-images\2-wear\Nscales(1-3)')
    parser.add_argument('--save_dir', default=r'resnet50-2')
    parser.add_argument('--epochs', default=100, type=int)
    parser.add_argument('--batch_size', default=10, type=int)
    parser.add_argument('--lr', default=1e-3, type=float)
    parser.add_argument('--weight_decay', default=1e-5, type=float)
    parser.add_argument('--patience', default=10, type=int)


    return parser.parse_args(args if args else [])

if __name__ == '__main__':
    opts = parse_args()
    print(opts)
    main(opts)

