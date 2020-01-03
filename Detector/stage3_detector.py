# -*- coding:utf-8 -*-
# Author: xzq
# Date: 2019-12-24 17:45

import torch
import torch.nn as nn
import argparse
from stage3_data import get_train_test_set
import torch.optim as optim
import numpy as np
import os
import matplotlib.pyplot as plt
import cv2


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # 卷积in_channels, out_channels, kernel_size, stride, padding
        self.conv1_1 = nn.Conv2d(1, 8, 5, 2, 0)
        self.conv2_1 = nn.Conv2d(8, 16, 3, 1, 0)
        self.conv2_2 = nn.Conv2d(16, 16, 3, 1, 0)
        self.conv3_1 = nn.Conv2d(16, 24, 3, 1, 0)
        self.conv3_2 = nn.Conv2d(24, 24, 3, 1, 0)
        self.conv4_1 = nn.Conv2d(24, 40, 3, 1, 1)
        # 激活函数
        self.relu_conv1_1 = nn.PReLU()
        self.relu_conv2_1 = nn.PReLU()
        self.relu_conv2_2 = nn.PReLU()
        self.relu_conv3_1 = nn.PReLU()
        self.relu_conv3_2 = nn.PReLU()
        self.relu_conv4_1 = nn.PReLU()
        # pooling
        self.avg_pool = nn.AvgPool2d(2, 2, ceil_mode=True)
        # 分支1 分类（是否人脸）
        self.conv4_2_cls = nn.Conv2d(40, 40, 3, 1, 1)
        self.relu_conv4_2_cls = nn.PReLU()
        self.ip1_cls = nn.Linear(4 * 4 * 40, 128)
        self.relu_ip1_cls = nn.PReLU()
        self.ip2_cls = nn.Linear(128, 128)
        self.relu_ip2_cls = nn.PReLU()
        self.ip3_cls = nn.Linear(128, 2)
        self.face_score = nn.Softmax(dim=1)
        # 分支2 回归（人脸坐标）
        self.conv4_2 = nn.Conv2d(40, 80, 3, 1, 1)
        self.relu_conv4_2 = nn.PReLU()
        self.ip1 = nn.Linear(4 * 4 * 80, 128)
        self.relu_ip1 = nn.PReLU()
        self.ip2 = nn.Linear(128, 128)
        self.relu_ip2 = nn.PReLU()
        self.landmarks = nn.Linear(128, 42)

    def forward(self, x):
        x = self.avg_pool(self.relu_conv1_1(self.conv1_1(x)))
        x = self.relu_conv2_1(self.conv2_1(x))
        x = self.avg_pool(self.relu_conv2_2(self.conv2_2(x)))
        x = self.relu_conv3_1(self.conv3_1(x))
        x = self.avg_pool(self.relu_conv3_2(self.conv3_2(x)))
        x = self.relu_conv4_1(self.conv4_1(x))
        # 分支1 分类（是否人脸）
        x_cls = self.relu_conv4_2_cls(self.conv4_2_cls(x))
        # flatten
        x_cls = x_cls.view(-1, 4 * 4 * 40)
        x_cls = self.relu_ip1_cls(self.ip1_cls(x_cls))
        x_cls = self.relu_ip2_cls(self.ip2_cls(x_cls))
        x_cls = self.ip3_cls(x_cls)
        face_score = self.face_score(x_cls)
        # 分支2 回归（人脸坐标）
        x_face = self.relu_conv4_2(self.conv4_2(x))
        # flatten
        x_face = x_face.view(-1, 4 * 4 * 80)
        x_face = self.relu_ip1(self.ip1(x_face))
        x_face = self.relu_ip2(self.ip2(x_face))
        landmarks = self.landmarks(x_face)
        return face_score, landmarks


def show_train_and_val_loss(train_loss_result, val_loss_result, num_epoches):
    x = range(0, num_epoches)
    # 生成训练集与验证集上的loss对比图
    y1 = val_loss_result
    y2 = train_loss_result
    plt.plot(x, y1, color="r", linestyle="-", marker="o", linewidth=1, label="val")
    plt.plot(x, y2, color="b", linestyle="-", marker="o", linewidth=1, label="train")
    plt.legend()
    plt.title('train and val loss vs. epoches')
    plt.ylabel('loss')
    plt.savefig("train and val loss vs epoches-stage3.jpg")
    plt.close('all')


def show_train_and_val_cls_loss(train_loss_result, val_loss_result, num_epoches):
    x = range(0, num_epoches)
    # 生成训练集与验证集上的loss对比图
    y1 = val_loss_result
    y2 = train_loss_result
    plt.plot(x, y1, color="r", linestyle="-", marker="o", linewidth=1, label="val")
    plt.plot(x, y2, color="b", linestyle="-", marker="o", linewidth=1, label="train")
    plt.legend()
    plt.title('train and val cls_loss vs. epoches')
    plt.ylabel('loss')
    plt.savefig("train and val cls_loss vs epoches-stage3.jpg")
    plt.close('all')


def show_train_and_val_pts_loss(train_loss_result, val_loss_result, num_epoches):
    x = range(0, num_epoches)
    # 生成训练集与验证集上的loss对比图
    y1 = val_loss_result
    y2 = train_loss_result
    plt.plot(x, y1, color="r", linestyle="-", marker="o", linewidth=1, label="val")
    plt.plot(x, y2, color="b", linestyle="-", marker="o", linewidth=1, label="train")
    plt.legend()
    plt.title('train and val pts_loss vs. epoches')
    plt.ylabel('loss')
    plt.savefig("train and val pts_loss vs epoches-stage3.jpg")
    plt.close('all')


def show_train_and_val_total_acc(train_acc_result, val_acc_result, num_epoches):
    x = range(0, num_epoches)
    # 生成训练集与验证集上的loss对比图
    y1 = val_acc_result
    y2 = train_acc_result
    plt.plot(x, y1, color="r", linestyle="-", marker="o", linewidth=1, label="val")
    plt.plot(x, y2, color="b", linestyle="-", marker="o", linewidth=1, label="train")
    plt.legend()
    plt.title('train and val total_acc vs. epoches')
    plt.ylabel('loss')
    plt.savefig("train and val total_acc vs epoches-stage3.jpg")
    plt.close('all')


def train(args, train_loader, valid_loader, model, criterion_is_face, criterion_face_pts, optimizer, device):
    """
    模型训练
    :param args:
    :param train_loader:
    :param valid_loader:
    :param model:
    :param criterion_is_face:
    :param criterion_face_pts:
    :param optimizer:
    :param device:
    :return:
    """
    # 如果要保存模型，设置模型保存路径
    if args.save_model:
        if not os.path.exists(args.save_directory):
            os.makedirs(args.save_directory)
    # 训练次数
    epochs = args.epochs
    train_losses, valid_losses = [], []
    train_cls_losses, valid_cls_losses = [], []
    train_pts_losses, valid_pts_losses = [], []
    train_positive_correctes, valid_positive_correctes = [], []
    train_negative_correctes, valid_negative_correctes = [], []
    train_total_correctes, valid_total_correctes = [], []
    for epoch in range(epochs):
        # 训练
        train_loss = 0.0
        train_cls_loss = 0.0
        train_pts_loss = 0.0
        num_positive = 0
        num_positive_correct = 0
        num_negative = 0
        num_negative_correct = 0
        model.train()
        train_batch_cnt = 0
        for batch_idx, batch in enumerate(train_loader):
            train_batch_cnt += 1
            img = batch['image']
            img = img.type(torch.FloatTensor)
            landmark = batch['landmarks']
            face = batch['face'].to(device)
            input_img = img.to(device)
            target_pts = landmark.to(device)
            optimizer.zero_grad()
            is_face, output_pts = model(input_img)
            # 返回x_classes中每行的最大值
            _, preds_is_face = torch.max(is_face, 1)
            is_face = is_face.view(-1, 2)
            # 分类loss
            loss_cls = criterion_is_face(is_face, face)
            # 回归loss
            mask = face.view(-1, 1)
            mask = mask.type(torch.BoolTensor)
            masked_outputs = torch.masked_select(output_pts, mask)
            masked_targets = torch.masked_select(target_pts, mask)
            loss_pts = criterion_face_pts(masked_outputs, masked_targets)
            # 带权重的总体loss
            loss = loss_cls * 0.4 + loss_pts * 0.6
            loss.backward()
            optimizer.step()
            train_loss += loss
            train_cls_loss += loss_cls
            train_pts_loss += loss_pts
            # 准确率
            for c1, c2 in zip(face, preds_is_face):
                if c1 == 1:
                    num_positive += 1
                    if c1 == c2:
                        num_positive_correct += 1
                elif c1 == 0:
                    num_negative += 1
                    if c1 == c2:
                        num_negative_correct += 1
            if batch_idx % args.log_interval == 0:
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\t loss: {:.6f}\t cls_loss: {:.6f}\t pts_loss: {:.6f}\t '
                      'total_acc: {:.6f}\t p_acc: {:.6f}\t n_acc: {:.6f}'
                      .format(epoch, batch_idx * len(img), len(train_loader.dataset),
                              100. * batch_idx / len(train_loader),
                              loss.item(), loss_cls.item(), loss_pts.item(),
                              (num_positive_correct + num_negative_correct) / (num_positive + num_negative),
                              num_positive_correct / num_positive, num_negative_correct / num_negative))
        train_loss /= train_batch_cnt * 1.0
        train_losses.append(train_loss)
        train_cls_loss /= train_batch_cnt * 1.0
        train_cls_losses.append(train_cls_loss)
        train_pts_loss /= train_batch_cnt * 1.0
        train_pts_losses.append(train_pts_loss)
        positive_correct = num_positive_correct / num_positive
        train_positive_correctes.append(positive_correct)
        negative_correct = num_negative_correct / num_negative
        train_negative_correctes.append(negative_correct)
        total_correct = (num_positive_correct + num_negative_correct) / (num_positive + num_negative)
        train_total_correctes.append(total_correct)
        # 验证
        valid_loss = 0.0
        valid_cls_loss = 0.0
        valid_pts_loss = 0.0
        num_positive = 0
        num_positive_correct = 0
        num_negative = 0
        num_negative_correct = 0
        model.eval()
        with torch.no_grad():
            valid_batch_cnt = 0
            for valid_batch_idx, batch in enumerate(valid_loader):
                valid_batch_cnt += 1
                img = batch['image']
                img = img.type(torch.FloatTensor)
                landmark = batch['landmarks']
                face = batch['face'].to(device)
                input_img = img.to(device)
                target_pts = landmark.to(device)
                optimizer.zero_grad()
                is_face, output_pts = model(input_img)
                # 返回x_classes中每行的最大值
                _, preds_is_face = torch.max(is_face, 1)
                is_face = is_face.view(-1, 2)
                # 分类loss
                loss_cls = criterion_is_face(is_face, face)
                # 回归loss
                mask = face.view(-1, 1)
                mask = mask.type(torch.BoolTensor)
                masked_outputs = torch.masked_select(output_pts, mask)
                masked_targets = torch.masked_select(target_pts, mask)
                loss_pts = criterion_face_pts(masked_outputs, masked_targets)
                # 带权重的总体loss
                loss = loss_cls * 0.4 + loss_pts * 0.6
                valid_loss += loss
                valid_cls_loss += loss_cls
                valid_pts_loss += loss_pts
                # 准确率
                for c1, c2 in zip(face, preds_is_face):
                    if c1 == 1:
                        num_positive += 1
                        if c1 == c2:
                            num_positive_correct += 1
                    elif c1 == 0:
                        num_negative += 1
                        if c1 == c2:
                            num_negative_correct += 1
                if valid_batch_idx % (args.log_interval / 4) == 0:
                    print('Valid Epoch: {} [{}/{} ({:.0f}%)]\t loss: {:.6f}\t cls_loss: {:.6f}\t pts_loss: {:.6f}\t '
                          'total_acc: {:.6f}\t p_acc: {:.6f}\t n_acc: {:.6f}'
                          .format(epoch, valid_batch_idx * len(img), len(valid_loader.dataset),
                                  100. * valid_batch_idx / len(valid_loader),
                                  loss.item(), loss_cls.item(), loss_pts.item(),
                                  (num_positive_correct + num_negative_correct) / (num_positive + num_negative),
                                  num_positive_correct / num_positive, num_negative_correct / num_negative))
            valid_loss /= valid_batch_cnt * 1.0
            valid_losses.append(valid_loss)
            valid_cls_loss /= valid_batch_cnt * 1.0
            valid_cls_losses.append(valid_cls_loss)
            valid_pts_loss /= valid_batch_cnt * 1.0
            valid_pts_losses.append(valid_pts_loss)
            positive_correct = num_positive_correct / num_positive
            valid_positive_correctes.append(positive_correct)
            negative_correct = num_negative_correct / num_negative
            valid_negative_correctes.append(negative_correct)
            total_correct = (num_positive_correct + num_negative_correct) / (num_positive + num_negative)
            valid_total_correctes.append(total_correct)
    if args.save_model:
        # save_model_name = os.path.join(args.save_directory,
        #                                'detector_MSELOSS_SGD_(batch_size=10)_(lr=0.0001)_stage3.pt')
        save_model_name = os.path.join(args.save_directory,
                                       'detector_MSELOSS_SGD_(batch_size=10)_(lr=0.0001)_stage3-finetune.pt')
        torch.save(model.state_dict(), save_model_name)
    return train_losses, train_cls_losses, train_pts_losses, train_positive_correctes, train_negative_correctes,\
        train_total_correctes, valid_losses, valid_cls_losses, valid_pts_losses, valid_positive_correctes, \
        valid_negative_correctes, valid_total_correctes


def test(test_loader, model, criterion_is_face, criterion_face_pts):
    """
    利用已训练好model作用在test数据集上查看效果
    :param test_loader:
    :param model:
    :param criterion_is_face:
    :param criterion_face_pts:
    :return:
    """
    test_mean_loss = 0.0
    test_mean_cls_loss = 0.0
    test_mean_pts_loss = 0.0
    num_positive = 0
    num_positive_correct = 0
    num_negative = 0
    num_negative_correct = 0
    count = 0
    for batch_idx, batch in enumerate(test_loader):
        count += 1
        img = batch['image']
        img = img.type(torch.FloatTensor)
        target_pts = batch['landmarks']
        face = batch['face']
        is_face, output_pts = model(img)
        # 返回x_classes中每行的最大值
        _, preds_is_face = torch.max(is_face, 1)
        is_face = is_face.view(-1, 2)
        # 分类loss
        loss_cls = criterion_is_face(is_face, face)
        # 回归loss
        mask = face.view(-1, 1)
        mask = mask.type(torch.BoolTensor)
        masked_outputs = torch.masked_select(output_pts, mask)
        masked_targets = torch.masked_select(target_pts, mask)
        loss_pts = criterion_face_pts(masked_outputs, masked_targets)
        # 带权重的总体loss
        loss = loss_cls * 0.4 + loss_pts * 0.6
        test_mean_loss += loss.item()
        test_mean_cls_loss += loss_cls.item()
        test_mean_pts_loss += loss_pts.item()
        # 准确率
        for c1, c2 in zip(face, preds_is_face):
            if c1 == 1:
                num_positive += 1
                if c1 == c2:
                    num_positive_correct += 1
            elif c1 == 0:
                num_negative += 1
                if c1 == c2:
                    num_negative_correct += 1
        print("Predict：{}，loss：{}，loss_cls：{}，loss_pts：{}".format(count, loss.item(), loss_cls.item(), loss_pts.item()))
    print("Test ave loss：{}".format(test_mean_loss / count))
    print("Test ave loss_cls：{}".format(test_mean_cls_loss / count))
    print("Test ave loss_pts：{}".format(test_mean_pts_loss / count))
    print("Test ave acc：{}".format((num_positive_correct + num_negative_correct) / (num_positive + num_negative)))
    print("Test ave acc_positive：{}".format(num_positive_correct / num_positive))
    print("Test ave acc_negative：{}".format(num_negative_correct / num_negative))


def finetune(net):
    ignored_params = list(map(id, net.landmarks.parameters()))  # 返回的是parameters的 内存地址
    base_params = filter(lambda p: id(p) not in ignored_params, net.parameters())
    optimizer_new = optim.SGD([{'params': base_params}, {'params': net.landmarks.parameters(), 'lr': 0.00001}],
                              0.000001, momentum=0.5, weight_decay=1e-4)
    return optimizer_new


def predict(images, model):
    """
    预测
    :param images:
    :param model:
    :return:
    """
    model.eval()
    for image in images:
        predict_image = cv2.resize(image, (112, 112))
        show_image = predict_image
        show_image = cv2.resize(show_image, (112, 112))
        predict_image = cv2.cvtColor(predict_image, cv2.COLOR_BGR2GRAY)
        predict_image = np.expand_dims(predict_image, axis=2)
        predict_image = predict_image.transpose((2, 0, 1))
        predict_image = np.expand_dims(predict_image, axis=0)
        predict_image = torch.from_numpy(predict_image)
        predict_image = predict_image.type(torch.FloatTensor)
        is_face, output_pts = model(predict_image)
        is_face_cls = is_face.view(-1, 2)
        _, preds_is_face = torch.max(is_face_cls, 1)
        if preds_is_face.item() == 1:
            output_pts = output_pts.detach().numpy()
            output_pts = output_pts[0]
            for i in range(0, len(output_pts), 2):
                # 由于关键点坐标是相对于人脸矩形框的，绘制时需要调整
                center = (int(output_pts[i]), int(output_pts[i + 1]))
                cv2.circle(show_image, center, 1, (255, 0, 0), -1)
            cv2.imshow("image", show_image)
            cv2.waitKey(0)


def main_test():
    # 参数设置部分
    # 创建解析器
    parser = argparse.ArgumentParser(description='Detector')
    # 添加参数
    # 批量训练集size
    parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
    # 批量测试集size
    parser.add_argument('--test-batch-size', type=int, default=64, metavar='N',
                        help='input batch size for testing (default: 64)')
    # 训练epochs次数
    parser.add_argument('--epochs', type=int, default=100, metavar='N',
                        help='number of epochs to train (default: 100)')
    # 学习率
    parser.add_argument('--lr', type=float, default=0.001, metavar='LR',
                        help='learning rate (default: 0.001)')
    # SGD动量
    parser.add_argument('--momentum', type=float, default=0.5, metavar='M',
                        help='SGD momentum (default: 0.5)')
    # 是否GPU不可用
    parser.add_argument('--no-cuda', action='store_true', default=False,
                        help='disables CUDA training')
    # 随机种子
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')
    # 记录培训状态之前要等待多少批次
    parser.add_argument('--log-interval', type=int, default=20, metavar='N',
                        help='how many batches to wait before logging training status')
    # 保存当前模型
    parser.add_argument('--save-model', action='store_true', default=True,
                        help='save the current Model')
    # 模型保存路径
    parser.add_argument('--save-directory', type=str, default='trained_models',
                        help='learnt models are saving here')
    # Train/train, Predict/predict, Finetune/finetune
    parser.add_argument('--phase', type=str, default='Train',
                        help='training, predicting or finetuning')
    # 解析参数
    args = parser.parse_args()

    # 设置随机数种子
    torch.manual_seed(args.seed)

    # 设置是否使用GPU 若使用GPU设置只使用1个
    use_cuda = not args.no_cuda and torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    # kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}

    # 加载数据集
    train_set, test_set = get_train_test_set()
    train_loader = torch.utils.data.DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    valid_loader = torch.utils.data.DataLoader(test_set, batch_size=args.test_batch_size)

    # 构建网络模型
    model = Net().to(device)
    # 设置分类loss
    criterion_cls = nn.CrossEntropyLoss(weight=torch.from_numpy(np.array([0.4, 0.6], dtype=np.float32)))
    # 设置坐标loss
    criterion_pts = nn.MSELoss()
    # 设置优化器
    optimizer = optim.Adam(model.parameters(), lr=args.lr, betas=(0.9, 0.999))
    if args.phase == 'Train' or args.phase == 'train':
        # train
        train_losses_result, train_cls_losses_result, train_pts_losses_result, \
            train_positive_correctes_result, train_negative_correctes_result, train_total_correctes_result, \
            valid_losses_result, valid_cls_losses_result, valid_pts_losses_result, valid_positive_correctes_result, \
            valid_negative_correctes_result, valid_total_correctes_result = \
            train(args, train_loader, valid_loader, model, criterion_cls, criterion_pts, optimizer, device)
        # train与valid总体loss
        show_train_and_val_loss(train_losses_result, valid_losses_result, args.epochs)
        # train与valid分类loss
        show_train_and_val_cls_loss(train_cls_losses_result, valid_cls_losses_result, args.epochs)
        # train与valid回归loss
        show_train_and_val_pts_loss(train_pts_losses_result, valid_pts_losses_result, args.epochs)
        # train与valid分类总体acc
        show_train_and_val_total_acc(train_total_correctes_result, valid_total_correctes_result, args.epochs)
    elif args.phase == 'Test' or args.phase == 'test':
        # test
        model.load_state_dict(torch.load('./trained_models/detector_MSELOSS_SGD_(batch_size=10)_(lr=0.0001)_stage3.pt'))
        test(valid_loader, model, criterion_cls, criterion_pts)
    elif args.phase == 'Finetune' or args.phase == 'finetune':
        # finetune
        model.load_state_dict(torch.load('./trained_models/detector_MSELOSS_SGD_(batch_size=10)_(lr=0.0001)_stage3.pt'))
        optimizer_new = finetune(model)
        train_losses_result, train_cls_losses_result, train_pts_losses_result, \
            train_positive_correctes_result, train_negative_correctes_result, train_total_correctes_result, \
            valid_losses_result, valid_cls_losses_result, valid_pts_losses_result, valid_positive_correctes_result, \
            valid_negative_correctes_result, valid_total_correctes_result = \
            train(args, train_loader, valid_loader, model, criterion_cls, criterion_pts, optimizer_new, device)
        print(train_losses_result)
    elif args.phase == 'Predict' or args.phase == 'predict':
        # predict
        image1 = cv2.imread("../Data/Predict/stage3_predict1.jpg", 1)
        image2 = cv2.imread("../Data/Predict/stage3_predict2.jpg", 1)
        predict_images = list()
        predict_images.append(image1)
        predict_images.append(image2)
        model.load_state_dict(torch.load('./trained_models/detector_MSELOSS_SGD_(batch_size=10)_(lr=0.0001)_stage3.pt'))
        predict(predict_images, model)


if __name__ == "__main__":
    main_test()
